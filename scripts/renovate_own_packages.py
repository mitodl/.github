"""Regenerate the list of our own packages that skip Renovate's release-age wait.

A package counts as ours when the `mitx-devops` account has a role on it:
- npm: the registry search `maintainer:mitx-devops`, intersected with the names declared in
  public mitodl repos' package.json (an npm owner can add mitx-devops to their own package
  without its consent). @mitodl/* is covered by the scope glob, so only unscoped names are listed.
- PyPI: there is no "projects of user X" API, so candidates come from PyPI names with our
  prefixes plus the package names declared in public mitodl repos, and each is kept only
  if its JSON API `ownership.roles` includes mitx-devops.

Usage:
  python3 scripts/renovate_own_packages.py                 # print the lists as JSON
  python3 scripts/renovate_own_packages.py --write renovate-config.json
Needs Python 3.11+ and an authenticated `gh` (GH_TOKEN) for the repo file listings.
"""

import argparse
import concurrent.futures as cf
import json
import re
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request

OWNER = "mitx-devops"
# Ours, but stale or not something apps depend on, so they don't get the exemption (reviewed 2026-11-18)
EXCLUDE = {"agent-config-kit", "mitol-django-uvtestapp", "ol-concoursepy", "ol-jupyter-authoring", "ol-themed-jupyter"}
PREFIXES = ("ol-", "mitol-")
VALID_NAME = re.compile(r"[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?")  # PEP 508 project name
SKIP_PATH = re.compile(r"(^|/)(node_modules|tests?|test_data|fixtures|examples?|\.venv)/")
NPM_SCOPE_GLOB = "@mitodl/**"
# Fail closed: more removals than this in one run looks like a broken crawl, not real churn
MAX_REMOVALS = 3


def get_json(url, accept="application/json"):
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "mitodl-renovate-own-packages"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def names_from_manifest(path, text):
    """Return the distribution name declared in a pyproject.toml or setup.py, if any."""
    if path.endswith("pyproject.toml"):
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError:
            return []
        name = data.get("project", {}).get("name") or data.get("tool", {}).get("poetry", {}).get("name")
    else:
        m = re.search(r"""\bname\s*=\s*["']([^"']+)["']""", text)
        name = m.group(1) if m else None
    # template placeholders like "<replace me>" or "{{ name }}" aren't distribution names
    return [name] if isinstance(name, str) and VALID_NAME.fullmatch(name) else []


def npm_name_from_package_json(text):
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    name = data.get("name") if isinstance(data, dict) and not data.get("private") else None
    return [name] if isinstance(name, str) else []


def repo_manifest_names(repo):
    """Return (PyPI names, npm names) declared in a repo. Any failure raises, so a run never silently shrinks."""
    try:
        listing = json.loads(gh("api", f"repos/mitodl/{repo}/git/trees/HEAD?recursive=1"))
    except subprocess.CalledProcessError as e:
        if "Git Repository is empty" in e.stderr:
            return [], []
        raise RuntimeError(f"listing {repo}: {e.stderr.strip()}") from e
    if listing.get("truncated"):
        raise RuntimeError(f"{repo}: file listing truncated by the GitHub API")
    pypi, npm = [], []
    for t in listing["tree"]:
        path = t["path"]
        filename = path.rsplit("/", 1)[-1]
        if t["type"] != "blob" or filename not in ("pyproject.toml", "setup.py", "package.json") or SKIP_PATH.search(path):
            continue
        # raw.githubusercontent.com doesn't count against the API rate limit
        with urllib.request.urlopen(f"https://raw.githubusercontent.com/mitodl/{repo}/HEAD/{path}", timeout=30) as resp:
            text = resp.read().decode()
        if filename == "package.json":
            npm += npm_name_from_package_json(text)
        else:
            pypi += names_from_manifest(path, text)
    return pypi, npm


def pypi_is_ours(name):
    d = get_json(f"https://pypi.org/pypi/{name}/json")
    roles = ((d or {}).get("ownership") or {}).get("roles") or []
    return any(r.get("user") == OWNER for r in roles)


def declared_names():
    """(PyPI names, npm names) declared in public, non-archived mitodl repos."""
    repos = gh("repo", "list", "mitodl", "--no-archived", "--visibility", "public", "--limit", "1000",
               "--json", "name", "--jq", ".[].name").split()
    with cf.ThreadPoolExecutor(8) as ex:
        results = list(ex.map(repo_manifest_names, repos))
    return {normalize(n) for pypi, _ in results for n in pypi}, {n for _, npm in results for n in npm}


def our_pypi_packages(declared_pypi):
    candidates = set(declared_pypi)
    simple = get_json("https://pypi.org/simple/", accept="application/vnd.pypi.simple.v1+json")
    candidates |= {normalize(p["name"]) for p in simple["projects"] if normalize(p["name"]).startswith(PREFIXES)}
    candidates -= EXCLUDE
    with cf.ThreadPoolExecutor(16) as ex:
        return sorted(n for n, ours in zip(sorted(candidates), ex.map(pypi_is_ours, sorted(candidates))) if ours)


def our_unscoped_npm_packages(declared_npm):
    names, offset = [], 0
    while True:
        d = get_json(f"https://registry.npmjs.org/-/v1/search?text=maintainer:{OWNER}&size=250&from={offset}")
        names += [o["package"]["name"] for o in d["objects"]]
        offset += len(d["objects"])
        if not d["objects"] or offset >= d["total"]:
            break
    return sorted(n for n in names if not n.startswith("@mitodl/") and n in declared_npm and n not in EXCLUDE)


def exemption_rule(config, datasource):
    """The packageRule that sets minimumReleaseAge to null for one datasource."""
    rules = [r for r in config["packageRules"]
             if r.get("matchDatasources") == [datasource] and "minimumReleaseAge" in r and r["minimumReleaseAge"] is None]
    if len(rules) != 1:
        sys.exit(f"expected one {datasource} release-age exemption rule, found {len(rules)}")
    return rules[0]


def update_config(config, pypi, npm_unscoped):
    """Set both exemption lists; return {datasource: (added, removed)}."""
    changes = {}
    for datasource, names in (("pypi", pypi), ("npm", [NPM_SCOPE_GLOB, *npm_unscoped])):
        rule = exemption_rule(config, datasource)
        old = rule["matchPackageNames"]
        added, removed = sorted(set(names) - set(old)), sorted(set(old) - set(names))
        if len(removed) > MAX_REMOVALS:
            sys.exit(f"refusing to remove {len(removed)} {datasource} names in one run (limit {MAX_REMOVALS}): {removed}")
        rule["matchPackageNames"] = names
        changes[datasource] = (added, removed)
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", metavar="CONFIG", help="update the exemption rules in this Renovate config")
    args = parser.parse_args()

    declared_pypi, declared_npm = declared_names()
    pypi, npm_unscoped = our_pypi_packages(declared_pypi), our_unscoped_npm_packages(declared_npm)
    if not args.write:
        json.dump({"pypi": pypi, "npm_unscoped": npm_unscoped}, sys.stdout, indent=2)
        print()
        return
    with open(args.write) as f:
        config = json.load(f)
    changes = update_config(config, pypi, npm_unscoped)
    with open(args.write, "w") as f:
        f.write(json.dumps(config, indent=2) + "\n")
    # Markdown summary, used as the PR body
    for datasource, (added, removed) in changes.items():
        for label, names in (("Added", added), ("Removed", removed)):
            if names:
                print(f"**{label} ({datasource}):** " + ", ".join(f"`{n}`" for n in names))


if __name__ == "__main__":
    main()
