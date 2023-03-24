---
title: RFC: <your RFC title here>
name: Request for Comments
---

<!---What is an RFC?


The process of creating an RFC is a tool to communicate with the team regarding a technical problem needing to be solved. The result of this process is a consensus on how we will approach the problem. It also documents how we arrived at our decision so that future engineers (and even ourselves) are able to reference the choice that was made.


When do I write an RFC?


RFCs should ideally be reserved for technical problems of higher complexity/difficulty or problems that will impact the team or projects in a broader sense. Smaller problems are more appropriate for less formal tools like Slack, GitHub Issues, or Pull Requests.


How do I use this template?


Sections boxed in BLUE like this are guidelines on how to fill out this document. Step through this document completing each of them in order and remove the blue boxes as you go. 


Keep in mind RFCs are organic documents, it is reasonable and even expected that some portions of it need to be revisited (i.e. adjusting the definition of the Problem Space after some initial investigation into Approaches).


Generally, involve the team as early and often as possible, but there are specific inflection points noted where this is required.
--->


| Author(s)    | Created        | Project |
|--------------|----------------|---------|
| Your name(s) | <Today's Date> |         |


# Goals


<!--- Describe the outcome(s) you’re looking to achieve from this RFC. This should be something that is then actionable. Be specific but keep it to about a paragraph. If it takes more to describe what is trying to be done, then it probably needs to be more than one RFC. Some categories that this could fall under:
   * Making a technology choice that will have medium-to-high impact on the team and/or project(s).
   * Making a decision about the architectural approach to part of a project before implementing it.
   * Determining the best approach to improve an existing codebase that is proving complex / difficult to maintain.
--->

# Prior Art


<!--- Note any existing implementations we may have:
   * For that implementation, did we try anything different from other existing implementations?
   * What worked in this implementation?
   * What was less than ideal in this implementation?
   * Did we make any tradeoffs in our approach that we don’t want to repeat or were specific to that project?
Link any RFCs that have addressed/looked at this in the past. --->


# Problem Space

<!---
1. Describe the problem space for the problem you’re trying to solve, this should be to the level of detail required for a new engineer to read this and comprehend the specifics of the problem and any nuances that may be present.
2. At this point, the RFC should be shared with the team to collect comprehensive knowledge on the entire team’s experience with this problem space. The team should comment on this document in regards to that and the author(s) should incorporate that information into the definition of the problem space.
3. You may choose to defer the Approaches portion of this RFC until after the Problem Space has been satisfactorily defined. However, there may be some obvious solutions from the start that are beneficial to define earlier in the process of developing your RFC.
--->

# Approaches



<!---
1. Taking the Goals and Problem Space, begin to investigate solutions to the Problem Space. This may take the form of (but not limited to):
   * Architectural design
   * Data design
   * Infrastructure requirements
   * R&D into existing tools/solutions
2. The goal here is to consider as many options as possible with a practical amount of time and effort.
3. An iterative approach is best here:
   * Start with outlining broadly the approaches that could be used. 
   * Determine along which lines the solutions partition themselves - level of effort, complexity, alignment to team skills/experience, etc.
   * This is a good point to involve the rest of the team again. There may be additional questions or perhaps some early feedback on which approaches we might rule out early on.
   * Continue to iterate on defining the approaches until there is adequate information to proceed to a Conclusion. Some good artifacts out of these stages are:
      1. Psuedocode: rough code samples that illustrate the general idea of an implementation
      2. Visual Mockups: rough visual mockups might be useful in illustrating user flows in an application
      3. Architectural diagrams: these should have a reasonable effort put into them quality-wise. One of them is likely to be used later for the real work.
      4. Proof-of-concept: this should be a very narrowly scoped proof of concept, particularly useful for RFCs around technology choices. It should be the absolute minimum required to demonstrate to the rest of the team how an approach would work.
4. It is just as important to know why certain approaches don’t work as it is to understand which ones do. These are also most likely not at one extreme or the other, it is more likely that each approach has its own distinct tradeoffs.
   * It’s useful to list out Pros and Cons to each approach.
   * Consider grading each approach on one or more axes to try to quantify the tradeoffs. This may even be well represented as a combined table for easy comparison across approaches.
   * If there is one solution that sticks out as the best, it’s often necessary to push back on the urge to stop here. Dig deeper on that approach and on others to ensure you’re not avoiding considering alternative solutions (Congruence Bias).
--->

# Conclusion

<!---
1. At this point the team should be involved again. Collect final comments on the approaches that have been detailed, paying attention to any concerns the team raises.
2. The goal here is to get a consensus amongst the team. If there’s a clear winner from Approaches, it’s fair to be direct and ask if the team agrees.
--->
