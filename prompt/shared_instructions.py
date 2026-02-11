"""
Shared instructions and constants for prompt templates.
This module contains common instructions and formatting that are reused across multiple prompt classes.
"""

from enums import PERSONALIZATION_STRATEGY_RUBRIC, PERSONALIZATION_FRAMEWORK_RUBRIC

# ========================= Shared Instructions =========================

PERSONALIZATION_INSTRUCTIONS = """\
- When designing a personalization strategy, do not just consider what the researcher knows or prefers, but also what the researcher does NOT know or does NOT prefer. For example, if a cybersecurity researcher asks for papers genetic sequencing, we likely need to add more background information for this user. This should involve adding a preliminary background section in "organization" or using simple terminology in "generation". On the converse, if the user is an expert in a topic, state that you will not add preliminary sections and avoid basic redefinitions to help save the user time.
- Do not force the personalization strategies to be specific. The specificity of each strategy should depend on how similar the query is to the user's profile. For example, if a user works on knowledge graphs and the query relates to knowledge graphs, the personalization strategies should be very specific based on the user's profile, outlining more concrete actions to take. However, if this same user with interests in knowledge graphs asks about computer vision, the actions to take in the personalization strategies should be more high-level.
- Do not always try to directly copy the user's profile when making requirements. For example, if a user's profile says they are interested in a specific psychological construct and you want to give a strategy involving this (e.g. I will connect the explanation to Ebbinghaus's learning curve), do not mention the specific construct. You should instead write more broadly (e.g. I will connect the explanations to memory constructs).
- If the query is very aligned with the user's profile, provide much more concrete suggestions for personalization. But if the query is quite dissimilar, keep the personalization suggestions very high-level and broad.
- Not every strategy should involve adding information. It is extremely important for you to also propose strategies so that the user can save time, like by ignoring papers in search_add, skipping sections in organization, and not redefining terms they already know in generation. Include at least one of these time-saving strategies, and add even more if the user is closely related to the information in the query.
"""

ACTION_INSTRUCTIONS = """\
- The action X to take in each strategy should be specific to each category:
    * search_add: I can also search for papers on X, I will add X to my list of search terms, I will expand the search to include X, etc.
    * search_refine: I will interpret X in your query to mean Y, I will ignore papers that do X, I will narrow the domain/task to X, etc. 
    * organization: I can add/ignore a section on X, I can have a more/less detailed on section X, etc.
    * generation: I can connect my explanation to concept X, I can add explain X by doing Y, I can use an X style, etc.
- If you are not confident the action is possible (e.g. if you do not know if there are papers that exist on a topic X in search_add or search_refine), use careful, hedged wording to avoid overclaiming, like "I can see if there are papers on X". Always hedge on search actions, but only when you are not fully confident on organization and generation.
- Please include several actions to take that involve saving time and generating shorter responses, like by ignoring papers in search_refine or search_add, skipping sections in organization, and not redefining terms they already know in generation.
"""

STRATEGY_INSTRUCTIONS = """\
- Each strategy should be self-contained, meaning that it can be understood on its own by PersonalizedQA, as the system will not have access to the user's profile. For example, instead of saying "Since you like evaluation, I can do the same", mention what "doing the same" will entail in your response (e.g. I can add summarization to my search terms).
- Each strategy should give a specific action of what you could do, not hedging between multiple actions. For example, instead of saying "I can disambiguate DFS to mean depth-first search or distributed file system", pick one of these, like "I can disambiguate DFS to mean depth-first search".
- Each strategy needs to follow the format of "I can..., which might help you...". Additionally, it must briefly mention how this strategy relates to the user's profile.
- Each strategy should only be a single sentence
- Do not include citations in the text of the strategy (i.e. numbers in square brackets)
- Do not introduce information, jargon, or concepts that the user does not already know about. For example, if the user does not know about machine learning and asks "What are neural networks", none of your personalization strategies should include the phrase "backpropagation" if you are not fully confident the user knows what this means. Be extremely cautious to make sure your language is easy to understand.
- Each strategy must be extremely diverse. Do not repeat information across personalization strategies.
"""

TLDR_INSTRUCTIONS = """\
- Each "tldr" should be a very brief version of the strategy (around ten words)
- Each "tldr" should not be in first-person. It should be a command. For example: "Include papers on X" (search_add), "Focus the scope for X" (search_refine), "Add section on X" (organization), "Do X in the response" (generation)
- Each "tldr" should be uniquely distinct from other "tldr"s.
- Each "tldr" should be understandable on its own without the strategy. So be very clear and specific while remaining concise.
- Each "tldr" should have a one-to-one mapping with the strategy, meaning it should contain all of the key information in the strategy that makes it unique. For example, if a strategy says "I will look for papers on multi-agent workflows in a scientific domain", a good "tldr" is "Look for multi-agent science papers" since it has all the salient terms. A bad "tldr" is "Look for papers involving agents" since it misses out on keywords.
"""

PERSONALIZED_STRATEGY_INSTRUCTIONS = """\
- Each strategy should be self-contained, meaning that it can be understood on its own by PersonalizedQA, as the system will not have access to the user's profile. For example, instead of saying "Since you like evaluation, I can do the same", mention what "doing the same" will entail in your response (e.g. I can add summarization to my search terms)
- Each strategy should give a specific action of what you could do, not hedging between multiple actions. For example, instead of saying "I can disambiguate DFS to mean depth-first search or distributed file system", pick one of these, like "I can disambiguate DFS to mean depth-first search".
- Each strategy needs to follow the format of "I can..., which might help you...". Additionally, it must briefly mention how this strategy relates to the user's profile.
- Each strategy should only be a single sentence
- Do not include citations in the text of the strategy (i.e. numbers in square brackets)
- Do not introduce information, jargon, or concepts that the user does not already know about. For example, if the user does not know about machine learning and asks "What are neural networks", none of your personalization strategies should include the phrase "backpropagation" if you are not fully confident the user knows what this means. Be extremely cautious to make sure your language is easy to understand.
- Each strategy must be extremely diverse. Do not repeat information across personalization strategies.
- Ensure a considerable amount of the strategies (one third) involve giving suggestions for how the user could apply the information in the response for their own research---the qualitative strategy label "usefulness"
"""

NONPERSONALIZED_STRATEGY_INSTRUCTIONS = """\
- Each strategy should be self-contained, meaning that it can be understood on its own by PersonalizedQA. For example, instead of saying "Since you like evaluation, I can do the same", mention what "doing the same" will entail in your response (e.g. I can add summarization to my search terms). Instead of saying you will propose an idea, disambiguate a term, or add a section, specifically mention what that idea, term, or section will be.
- Each strategy should give a specific action of what you could do, not hedging between multiple actions. For example, instead of saying "I can disambiguate DFS to mean depth-first search or distributed file system", pick one of these, like "I can disambiguate DFS to mean depth-first search".
- Each strategy needs to follow the format of "I can..., which might help you...".
- Each strategy should only be a single sentence
- Do not include citations in the text of the strategy (i.e. numbers in square brackets)
- Do not introduce information, jargon, or concepts that you think the user does not already know about. For example, if you think the user does not know about machine learning and asks "What are neural networks", none of your personalization strategies should include the phrase "backpropagation" if you are not fully confident the user knows what this means. Be extremely cautious to make sure your language is easy to understand.
- Each strategy must be extremely diverse. Do not repeat information across personalization strategies.
"""

# ========================= Shared Formatting =========================

def get_rubric_strings():
    """Get formatted rubric strings for both personalization types."""
    str_rubric_impl = '\n'.join(
        f"<{k.value.replace('_', ' ').title()}>\n{v}\n</{k.value.replace('_', ' ').title()}>" for k, v in PERSONALIZATION_FRAMEWORK_RUBRIC.items()
    )
    str_rubric_qual = '\n'.join(
        f"<{k.value.replace('_', ' ').title()}>\n{v}\n</{k.value.replace('_', ' ').title()}>" for k, v in PERSONALIZATION_STRATEGY_RUBRIC.items()
    )
    qual_keys = ', '.join([f'"{k.value}"' for k in PERSONALIZATION_STRATEGY_RUBRIC.keys()])
    impl_keys = ', '.join([f'"{k.value}"' for k in PERSONALIZATION_FRAMEWORK_RUBRIC.keys()])
    
    return str_rubric_impl, str_rubric_qual, qual_keys, impl_keys

def get_personalizedqa_description():
    """Get the standard PersonalizedQA system description."""
    return """\
This query will eventually be fed into a system called PersonalizedQA that executes:
1. retrieval: searches for research papers
2. organization: outlines sections for the final response to include
3. generation: produces text for each of these sections"""

def get_personalization_strategy_description():
    """Get the standard personalization strategy description."""
    return """\
To help PersonalizedQA personalize responses based on the user's profile, come up with a list of personalization strategies that the system should follow. Each personalization strategy should specify two requirements:
1. What kind of response the user will experience (Qualitative Personalization)
2. How the system should behave at each step (Implementation Personalization)"""

# ========================= Shared Requirements =========================

def get_implementation_distribution_requirement():
    """Get the requirement for even distribution across implementation strategies."""
    return """\
- Ensure there is an even split between where the implementation of the personalization strategy in PersonalizedQA should occur---namely an even distribution between "retrieval", "organization", and "generation" in the label "implementation_strategy"."""

def get_usefulness_requirement():
    """Get the requirement for usefulness strategies."""
    return """\
- Ensure a considerable amount of the strategies (one third) involve giving suggestions for how the user could apply the information in the response for their own research---the qualitative strategy label "usefulness" """ 