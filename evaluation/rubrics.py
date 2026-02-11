# ====================================== vvv Profile Inference Judgment Prompts (Synthetic Data) vvv ====================================== 

SPECIFICITY_RUBRIC = {
  "criteria": "Personalization: How specifically tailored and insightful is the inference about the computer science researcher?",
  "score1_description": "Extremely vague or generic; the inference could apply to almost any researcher and offers no meaningful personalization.",
  "score2_description": "Broad and minimally tailored; captures a common area or trait that applies to many researchers in computer science.",
  "score3_description": "Moderately specific; identifies a more refined topic or pattern but still describes a large population of computer science researchers.",
  "score4_description": "Specific and reasonably personalized; reflects a more distinctive sub-area, approach, or motivation of the researcher.",
  "score5_description": "Highly specific and personalized; demonstrates a deep, nuanced inference that could plausibly distinguish this researcher from almost every other researcher in their field."
}

CITATION_EVAL_PROMPT = """
<task>
As an Attribution Validator, your task is to verify whether a given inference can be accurately derived from a list of references. 
A reference is a collection of snippets from a research paper.
Specifically, your response should clearly indicate the relationship: Attributable or Contradictory. 
A contradictory error occurs when you can infer that the inference contradicts the information presented in the reference. If the inference appears true based on the papers, even if some of the papers are irrelevant (i.e. the model "over-cited" the papers), then the inference is Attributable.
</task>

<inference>
{inference}
</inference>

<references>
{ref_excerpt}
</references>

<format>
Output your response as a json with only a single key "output" and a value of one among - ("Attributable", "Contradictory").
</format>
"""

CATEGORY_EVAL_PROMPT = """
<task>
As a Category Validator, your task is to verify whether a given inference can be classified under the specified category. 
Specifically, your response should clearly indicate the relationship between the inference and category: Match or Mismatch. 
A mismatch occurs when you can infer that the inference does not relate at all to the category and its definition. A match occurs when you can infer they do relate to each other
</task> 

<category>
{category}
</category>

<category definition>
{definition}
</category definition>

<inference>
{inference}
</inference>

<format>
Output your response as a json with only a single key "output" and a value of one among - ("Match", "Mismatch").
</format>
"""

RELEVANCE_EVAL_PROMPT = """
<task>
As a Relevance Validator, your task is to determine whether a specific text from a paper provides support for and is relevant to a broader inference intended to span multiple papers. 
If the paper text provides support for at least one aspect of the inference, then it is relevant. If the paper text supports no part of the inference, then it is irrelevant. For example, if the inference claims "Your papers use the terms 'first' and 'novel'" and from the text we can infer that "The paper uses the term 'first'", the paper text is relevant since it relates to the claim about 'first', even though the word 'novel' is not discussed. Thus, for the paper text to be "Relevant", it only needs to support one aspect of the inference.
</task>

Here is the paper text:
<paper text>
{paper_text}
</paper text>

And here is the inference:
<inference>
{hli}
</inference>

<format>
Output your response as a json with only a single key "output" and a value of one among - ("Relevant", "Irrelevant").
</format>
"""

SPECIFICITY_PROMPT = """
<task>
As a Specificity Validator, your task is to rate the specificity of a given inference about a computer science researcher from one to five.
</task>

Use the following criteria:
<criteria>
Criteria: Personalization: How specifically tailored and insightful is the inference about the computer science researcher?
Score 1: Extremely vague or generic; the inference could apply to almost any researcher in computer science.
Score 2: Broad and minimally tailored; captures a common area or trait that applies to many researchers in computer science.
Score 3: Moderately specific; identifies a more refined topic or pattern but still describes a large population of computer science researchers.
Score 4: Specific and reasonably personalized; reflects a more distinctive sub-area, approach, or motivation of the researcher.
Score 5: Highly specific and personalized; demonstrates a deep, nuanced inference that could plausibly distinguish this researcher from almost every other researcher in their field.
</criteria>

Here is the inference you must rate:
<inference>
{inference}
</inference>

<format>
Output your response as a json with only a single key "output" and an integer rating for Specificity from one to five.
</format>
"""

# ====================================== vvv Plan Evaluation Prompts (Synthetic Data) vvv ====================================== 

PLAN_CONTRADICT_QUERY = """
<task>
As a Plan Contradiction Validator, your task is to determine if a plan step directly conflicts the instructions in the query.
The query will be a question related to scientific research.
The plan will describe a list of suggestions an external question answering model could execute to generate a better response.

Your output should denote whether the plan has a "CONFLICT" or "NO_CONFLICT" with the query. For example, if the query asks "What are the best question answering datasets?" and a plan step says "Focus search on summarization benchmarks", there would be a "CONFLICT", since the model cannot focus on summarization benchmarks without ignoring question answering datasets, and thus would have to ignore the query to follow the instruction. However, if a plan step for this query said "Focus on Extractive Question Answering" it would be "NO_CONFLICT", since the model could follow this step while still answering the query. Similarly, if the plan step said "Draw connections to summarization benchmarks" it would be "NO_CONFLICT", as drawing a connection does not mean ignoring the request in the query.

</task>

<query>
{query}
</query>

<plan step>
{plan}
</plan step>

<format>
Output your response as a json with two keys: 1) "output" with a value of one among - ("CONFLICT", "NO_CONFLICT"); and 2) "explanation" with a brief explanation as to why.
</format>
"""

PLAN_JUDGE_PROMPT_PERSONALIZATION = """As a Plan Validator, your task is to determine which of two plans for how to tailor a response best matches a user's profile.
The user profile will be a series of inferences about a user derived from their research papers, organized under various categories.
The two plans will be labled as "Plan A" or "Plan B" and describe a list of suggestions an external question answering model could execute to generate a more personalized response.
Your output should denote whether plan "A" or "B" is better aligned with suggestions that the user described in the profile would prefer.

Here is the profile:
<profile>
{profile}
</profile>

Here is Plan A:
<plan A>
{plan_a}
</plan A>

Here is Plan B:
<plan B>
{plan_b}
</plan B>

<format>
Output your response as a json with only a single key "output" and a value of one among - ("A", "B").
</format>
"""

PLAN_CATEGORY_QUERY = """
<task>
As a Category Validator, your task is to verify whether a given plan step can be classified under the specified category. 
Specifically, your response should clearly indicate the relationship between the inference and category: Match or Mismatch. 
A mismatch occurs when you can infer that the plan step does not relate at all to the category and its definition. A match occurs when you can infer they do relate to each other
</task> 

<category>
{category}
</category>

<category definition>
{definition}
</category definition>

<plan step>
{plan_step}
</plan step>

<format>
Output your response as a json with only a single key "output" and a value of one among - ("Match", "Mismatch").
</format>
"""

# ====================================== vvv User Simulation (Predicting Real User Data) vvv ====================================== 


DESCRIPTION_MAP = {
    "profile": """Given a set of research papers selected by a user, a model must generate a profile containing a series of inferences about the user, each of which cite the papers from which the inferences were derived. These inferences are supposed to capture information about the user that would help a question-answering system personalize its responses when the user asks questions. You will be given one of the model-generated profile inferences that the user reviewed, and will be asked to predict if the user was satisfied with the profile inference.

Here are the research papers the user selected to represent their profile:
<papers>
{source_text}
</papers>

Here is an inference the model generated about the user that you must evaluate:
<profile inference>
{generation}
</profile inference>

Here is the categorization of the above profile inference:
<profile inference category>
{category}
</profile inference category>

Your job is to evaluate if the user would be satisfied or dissatisfied with this inference in the profile. Satisfied means that the user believes the inference perfectly captures one part of their preferences and interests. If the user is satisfied with the inference they would leave it unaltered in their profile, with no desire for modifications or noting any issues (no matter how minor).
""",

"plan": """Given a query asked by a user and a profile that captures that same user's preferences and interests, a model must generate suggested actions (which we refer to as plan steps) that a system could also perform when answering the question. The plan steps, when followed, are supposed to result in more useful information for the user in the final response. The usefulness  of a response depends on the user’s intent in the query, but is likely intended to help them learn new information, find relevant papers they can save, propose new ideas for them to explore, or give implementation advice. You will be given one of the model-generated plan steps that the user reviewed, and will be asked to predict if the user was satisfied with the plan step and wanted the model to execute it when answering the query.
  
Here is the query the user provided:
<query>
{query}
</query>

Here is the user's profile:
<profile>
{source_text}
</profile>

Here is one of the plan steps the model generated:
<plan step>
{generation}
</plan step>

Here is the categorization of the above plan step:
<plan step category>
{category}
</plan step category>

Your job is to evaluate if the user would be satisfied or dissatisfied with the plan step that the model proposed. If the user is satisfied with the plan step, they would want a model to follow this extra request in addition to answering their query, with no desire for modifications or noting any issues (no matter how minor).
""",
    "response": """Given a query asked by a user and a plan step containing additional instructions for the model to perform when answering the query, a model must generate a multi-section response that answers the query and follows the extra steps. The response is supposed to contain information related to the plan step that the user would find useful in the entire response, but particularly in the spans of highlighted text. The usefulness of a response depends on the user’s intent in the query, but is likely intended to help them learn new information, find relevant papers they can save, propose new ideas for them to explore, or give implementation advice. You will be given one of the model-generated responses and the plan step that the user reviewed, and will be asked to predict if the user was satisfied with how the plan step was followed in the response.
  
Here is the query the user provided:
<query>
{query}
</query>

Here is the plan step the user asked the model to follow:
<plan step>
{generation}
</plan step>

Here is the categorization of the above plan step:
<plan step category>
{category}
</plan step category>

Here is the response the model generated:
<response>
{source_text}
</response>

Your job is to evaluate if the user would be satisfied or dissatisfied with how the model followed the plan step in its response. If the user is satisfied with how a plan step was followed in the response, they would find that the information related to the plan step in the response is perfectly described and useful, with no desire for modifications or noting any issues (no matter how minor).
""",
}

EXAMPLE_MAP = {
'profile': '''
Here are three examples for {n} unique users who were each satisfied or dissatisfied with the profile inferences that the model generated.
<examples>
{examples}
</examples>
''',

'plan': '''
Here are three examples for {n} unique users who were each satisfied or dissatisfied with the plan steps that the model generated.
<examples>
{examples}
</examples>
''',

'response': '''
Here are three examples for {n} unique users who were each satisfied or dissatisfied with how the model followed each plan step in the response:
<examples>
{examples}
</examples>
'''
}

METRIC_MAP = {
    "profile_KEYWORD": """
Metric criteria: Would the user be satisfied with the technical content in the inference, including field-specific terminology, details, and descriptions? Or would the user prefer different technical content that is more consistent with their papers and better captures their preferences and interests?
- Set is_satisfied=true if the profile inference uses technical content that directly and accurately reflects the user's research focus, without being too broad (e.g., overly generic) or too narrow (e.g., misses the user's broader area of interest).
- Set is_satisfied=false if the profile inference uses technical content that is inaccurate, misleading, overly broad so they lose meaning, or so narrow that they fail to capture the user's actual preferences and interests.
""",
    "profile_OVERGENERAL": """
Metric criteria: Would the user be satisfied with how broadly the profile inference claims apply across their papers and in particular, the papers cited in the inference? Or is the profile inference overstating its scope?
- Set is_satisfied=true if the profile inference describes something that genuinely applies to a substantial portion of the user's papers, making it a meaningful part of their profile.
- Set is_satisfied=false if the profile inference is overstated, claiming to apply across the user's papers when in fact it only applies to a small subset or is not significant enough to represent the user's overall work.
""",
    "profile_NEGATION": """
Metric criteria: Would the user be satisfied with the contrasts (e.g. you do X, rather than Y) that the profile inference describes? If there are contrasts, does the profile correctly infer preferences and interests that do not describe the user?
- Set is_satisfied=true if the profile inference either does not include a contrast, or if it includes a contrast that accurately reflects what the user avoids, does not do, or is not interested in.
- Set is_satisfied=false if the profile inference includes a contrast that is inaccurate, overstated, hallucinated, or misrepresents the user’s preferences and interests.
""",
    "profile_GENERAL": """
Metric criteria: Would the user be satisfied with the specificity of the inference? Or is the profile inference just stating a generic convention of their field?
- Set is_satisfied=true if the profile inference is specific enough to highlight something distinctive about the user’s work that would not automatically apply to most researchers in the same field or conference community.
- Set is_satisfied=false if the profile inference is generic or conventional, such that it could apply equally well to nearly all researchers in the domain and therefore fails to add meaningful information about the user’s profile.
""",
    "plan_NARROW": """
Metric criteria: Given their original query, would the user be satisfied with how much exploration this plan step would enable the system to do? Or would the plan step restrict the information in the final response such that it becomes too narrow?
- Set is_satisfied=true if the plan step leaves room to cover multiple relevant aspects of the query and does not confine the response to an overly specific or constrained angle.
- Set is_satisfied=false if the plan step limits the response to something so specific that the resulting information would be incomplete, one-dimensional, or not broadly useful for the user’s needs.
""",
    "plan_OFFTOPIC": """
Metric criteria: Given their original query, would the user be satisfied with the information that this plan step would incorporate in the answer to the query? Or would this add information that is overly distracting?
- Set is_satisfied=true if the plan step stays aligned with the user’s query and directs the response toward information that would be clearly useful for addressing their request.
- Set is_satisfied=false if the plan step shifts the focus away from the query, leading the response toward content that is irrelevant or distracting from what the user actually wants to know.

""",
    "response_UNINFORMATIVE": """
Metric criteria: Would the user be satisfied with the depth of information in this response related to the plan step? Or is the response content related to the plan step too vague, high-level, or general to be useful?
- Set is_satisfied=true if the response content related to the plan step provides concrete, detailed, and specific information tied to the plan step that adds meaningful value for the user.
- Set is_satisfied=false if the response content related to the plan step is vague, superficial, or generic, giving little more than high-level statements without useful depth or detail.
""",
    "response_STYLE": """
Metric criteria: Would the user be satisfied with how the part of the response related to the plan step was presented? Or would they prefer an alternative way for the presentation of the response content related to the plan step?
- Set is_satisfied=true if the response content related to the plan step is presented in a clear, well-structured, and accessible way that makes it easy for the user to understand and apply toward their goals.
- Set is_satisfied=false if the response content related to the plan step is presented in a confusing, poorly structured, or unhelpful way that reduces its usefulness, even if the content itself is correct.
""",
    "response_FAILED": """
Metric criteria: Would the user be satisfied with how well the model response adhered to every requirement in the plan step? Or did the model fail to follow at least one of the requirements in the plan step?
- Set is_satisfied=true if the response fully follows the plan step and meets all of its requirements without omission.
- Set is_satisfied=false if the response fails to meet even one part of the plan step, leaving requirements unaddressed or ignored.
""",
}

JSON_PROMPT = """Structure your output as a JSON with a boolean key "is_satisfied", which is set to true if the user would be fully satisfied and false otherwise, and "explanation", which provides a brief rationale as to why you picked the label in "is_satisfied".
"""

PROMPT_BASIC = """You are an expert at evaluating generated text with respect to user satisfaction.

<task>
{task_description}
</task>
{example_str}
<format>
{format_description}
</format>
"""

PROMPT_METRIC = """You are an expert at evaluating generated text with respect to user satisfaction across specific metrics.

<task>
{task_description}

Specifically, evaluate the response for user satisfaction with the following criteria in mind:
<metric>
{metric_description}
</metric>
</task>
{example_str}
<format>
{format_description}
</format>
"""