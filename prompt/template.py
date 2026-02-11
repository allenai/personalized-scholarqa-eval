"""
Abstract base class implementation of a Prompt Template. Uses a specified experiment to obtain a prompt template (e.g. f-string) that can include data inputs.
"""

from abc import ABC, abstractmethod
from data import Paper, UserConstitution
from enums import CONSTITUTION_DEFINITION_RUBRIC, ConstitutionCategory, PERSONALIZATION_STRATEGY_RUBRIC, PERSONALIZATION_FRAMEWORK_RUBRIC
from prompt.shared_instructions import (
    PERSONALIZATION_INSTRUCTIONS, ACTION_INSTRUCTIONS, STRATEGY_INSTRUCTIONS, TLDR_INSTRUCTIONS,
    PERSONALIZED_STRATEGY_INSTRUCTIONS, NONPERSONALIZED_STRATEGY_INSTRUCTIONS,
    get_rubric_strings, get_personalizedqa_description, get_personalization_strategy_description,
    get_implementation_distribution_requirement, get_usefulness_requirement
)

NUMBER_WORDS = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen",
    "twenty", "twenty-one", "twenty-two", "twenty-three", "twenty-four", "twenty-five", "twenty-six", "twenty-seven", "twenty-eight", "twenty-nine",
    "thirty", "thirty-one", "thirty-two", "thirty-three", "thirty-four", "thirty-five", "thirty-six", "thirty-seven", "thirty-eight", "thirty-nine",
    "forty", "forty-one", "forty-two", "forty-three", "forty-four", "forty-five", "forty-six", "forty-seven", "forty-eight", "forty-nine", "fifty"
]

# Abstract base class for implementing prompts
class Prompt(ABC):

    def __init__(self, prompt_file: str | None = None):
        if prompt_file == None:
            self.base_prompt = ''
        else:
            with open(prompt_file, 'r') as f:
                self.base_prompt = f.read()
            f.close()

    @abstractmethod
    def create_inference_prompt(self, **kwargs) -> str:
        """Create the inference part of the prompt"""
        pass

    def create_prompt(self, **kwargs):
        """Create the full prompt"""
        return self.base_prompt + self.create_inference_prompt(**kwargs)
    
# ========================= Prompts for Constitution Generation =========================
    
"""Generate inferences across multiple paper (used in long-context, third-party format)"""
class MultiPaperAuthorInferencesPromptThirdParty(Prompt):

    def create_inference_prompt(self, papers: list[Paper], num_inferences: int, categories: list[ConstitutionCategory]):
        str_rubric = '\n'.join(
            f"<{k.value.replace('_', ' ').title()}>\n{v}\n</{k.value.replace('_', ' ').title()}>" for k, v in CONSTITUTION_DEFINITION_RUBRIC.items() if k in categories
        )
        category_keys = ', '.join([f'"{k.value}"' for k in CONSTITUTION_DEFINITION_RUBRIC.keys() if k in categories])
        paper_str = '\n\n'.join([str(p) for p in papers])
        return f"""Here are a list of paragraphs from research papers that the author has selected (either written or read)
<papers>
{paper_str}
</papers>

Based on the papers, generate a list of inferences about the author of the paper, categorized as:
<rubric>
{str_rubric}
</rubric>

<format instructions>
Generate your output as a JSON object with {len(CONSTITUTION_DEFINITION_RUBRIC)} keys: {category_keys}---where each key has a list of inference objects categorized under that type. An inference object should have the key "inference" with a string high-level inference of the author's preferences that spans across multiple papers and the key "atomic_inferences" with a list of strings specific to the paper with evidence that supports "inference". Each "inference" should be a single brief sentence with a hypothesis about the author's preferences in the form "Your papers..." that is more general and derived across multiple papers; it does not need an explanation. Each item in "atomic_inferences" should have three keys: 1) string "atomic_inference" with a single brief sentence conveying an explanation of how the paper relates to that inference in the form "One paper..." which will be more specific to the paper; 2) string "paper_title" which has the title of the paper from which the inference was derived; and 3) list of integer "paragraph_numbers" for the paragraphs (not sections) in "paper_title" from which the inference was derived. There should be {NUMBER_WORDS[num_inferences]} inference objects for each category, and each object should have a list of "atomic_inferences" that cite all of the author's papers that are relevant. No two atomic inferences under the same inference object should cite the same paper. Use each paper at least once. Do not cite section titles.
</format instructions>

<personalization requirements>
- Inferences must be extremely personalized to the author; they should not apply to many authors in the field. For example, the inference "You know about issues in LLMs" under knowledge is too vague; you should point to a specific type of issue (e.g. memorization) that is more specific to just this author. The more specific the better.
- Do not make inferences that are conventions for certain fields in research papers. 
    * Limitation sections, listing contributions, using tables and figures, having related work, pointing out problems and proposing solutions, and using footnotes are all common conventions across conference papers for "writing style" and should thus NEVER be used as inferences. Instead, you should focus on aspects like tone, argumentation, and quirks that are specific to the author and would infrequently be found by other authors submitting similar papers.
    * Similarly, when stating which audience an author writes for, do not stop at just the field or intersection of fields (e.g. computer vision for scientists). Drill down into this fields, like the type of computer vision researcher (e.g. image recognition) or type of scientist (e.g. doctor).
    * Many researchers who work on the same topic often believe the same things that appear specific at first. For example, many researchers working on biases believe that biases are harmful. So instead of this, try to carve out a more unique preference for that author. For example, you might say that the researcher believes biases are harmful because they cause mistrust in high-stakes domains.
- Each high-level inference should not group multiple aspects together, and instead should focus on aspects that are most important for the researcher. For example, instead of saying the researcher works on training, evaluating, and deploying models, you could mention just one of the aspects the researcher works on that is unique compared to most researchers.
</personalization requirements>

<inference requirements>
- When generating a high-level inference, do not force atomic inferences from each of the papers. If a paper does not support a high-level inference, do not include it. For example, if you mention the researcher studies generalization, do not claim all of their papers relate to generalization if in reality they do not.
- When generating inferences, you should always briefly mention how this aspect of the researcher is different from most other researchers in their field if it is not obvious. If you say the author prefers X, explain that most other researchers prefer Y, which is different from X. For example, instead of just saying a researcher "prefers hyperparameter sweeps", you could mention "You prefer to test a larger space of hyperparameters compared to most researchers who typically test just a few ablations".
- Do not be excessively flattering. Use simple, clear, and easy-to-understand language. For example, instead of saying that the researcher "has a unique, nuanced skillset in machine learning and psychology" simply say they "are familiar with machine learning and psychology".
- You do not just have to say what the researcher wants to hear. Be honest. You are encouraged to include what the researcher does NOT know, does NOT do, or does NOT prefer. These can be seen as areas of growth.
- Your inferences should not imply that the author has done everything in those papers, as they may not have written them. For example, instead of saying "You use automated red-teaming" under research style if all papers discuss red-teaming, you should infer something like "Your papers use red-teaming".
</inference requirements>
"""

class PlanGenerationPromptQualitative(Prompt):

    def create_inference_prompt(self, constitution: UserConstitution, query: str, num_requirements: int):
        str_rubric_impl, str_rubric_qual, qual_keys, impl_keys = get_rubric_strings()

        return f"""Here are a list of inferences about a user. The numbered inference is a high-level inference, while the sub bullet points provide evidence for these inferences:
<profile>
{constitution.for_llm()}
</profile>

They are now asking:
<query>
{query}
</query>

{get_personalizedqa_description()}

{get_personalization_strategy_description()}

The qualitative personalization label is based on how the response will be personalized to the user at a qualitative level:
<qualitative personalization strategies>
{str_rubric_qual}
</qualitative personalization strategies>

The implementation personalization label is based on the three-step execution of ScholarQA, categorized as:
<implementation personalization strategies>
{str_rubric_impl}
</implementation personalization strategies>

<format instructions>
Generate your output as a JSON object with {len(PERSONALIZATION_STRATEGY_RUBRIC)} keys based on the implementation personalization strategies: {qual_keys}---where each key has a list of personalization strategy objects. Each strategy object should have four keys: 1) a string "strategy" as a brief high-level requirement for the final output that would lead to a more helpful response that is personalized to this user; 2) a string "tldr" with an extremely brief version of the "strategy" (less than fifteen words); 3) an integer "inference_number" which has the numbered inference from which the strategy was derived; and 4) a string "implementation_strategy" categorizing how the instruction will be implemented in PersonalizedQA (one of {impl_keys}). All requirements should be a concise sentence (<30 words) in the exact form \"I can... [action to take], which might help you... [predicted help]\". Include exactly {NUMBER_WORDS[num_requirements]} {'strategy' if num_requirements == 1 else 'strategies'} for each qualitative category ({NUMBER_WORDS[num_requirements]} personalization {'strategy' if num_requirements == 1 else 'strategies'} for each of {qual_keys}). Make sure all of the strategies directly address the query.
</format instructions>

<personalization instructions>
{PERSONALIZATION_INSTRUCTIONS}
{get_implementation_distribution_requirement()}
</personalization instructions>

<action instructions>
{ACTION_INSTRUCTIONS}
</action instructions>

<strategy instructions>
{STRATEGY_INSTRUCTIONS}
</strategy instructions>

<tldr instructions>
{TLDR_INSTRUCTIONS}
</tldr instructions>
"""

class PlanGenerationPromptQualitativeNonpersonalized(Prompt):

    def create_inference_prompt(self, constitution: UserConstitution, query: str, num_requirements: int):
        str_rubric_impl, str_rubric_qual, qual_keys, impl_keys = get_rubric_strings()

        return f"""The user is now asking:
<query>
{query}
</query>

{get_personalizedqa_description()}

{get_personalization_strategy_description()}

The qualitative personalization label is based on how the response will be personalized to the user at a qualitative level:
<qualitative personalization strategies>
{str_rubric_qual}
</qualitative personalization strategies>

The implementation personalization label is based on the three-step execution of ScholarQA, categorized as:
<implementation personalization strategies>
{str_rubric_impl}
</implementation personalization strategies>

<format instructions>
Generate your output as a JSON object with {len(PERSONALIZATION_STRATEGY_RUBRIC)} keys based on the implementation personalization strategies: {qual_keys}---where each key has a list of personalization strategy objects. Each strategy object should have three keys: 1) a string "strategy" as a brief high-level requirement for the final output that would lead to a more helpful response; 2) a string "tldr" with an extremely brief version of the "strategy" (less than fifteen words); and 3) a string "implementation_strategy" categorizing how the instruction will be implemented in PersonalizedQA (one of {impl_keys}). All requirements should be a concise sentence (<30 words) in the exact form \"I can... [action to take], which might help you... [predicted help]\". Include exactly {NUMBER_WORDS[num_requirements]} {'strategy' if num_requirements == 1 else 'strategies'} for each qualitative category ({NUMBER_WORDS[num_requirements]} personalization {'strategy' if num_requirements == 1 else 'strategies'} for each of {qual_keys}). Make sure all of the strategies directly address the query.
</format instructions>

<action instructions>
{ACTION_INSTRUCTIONS}
</action instructions>

<strategy instructions>
{NONPERSONALIZED_STRATEGY_INSTRUCTIONS}
</strategy instructions>

<tldr instructions>
{TLDR_INSTRUCTIONS}
</tldr instructions>
"""



class PlanGenerationPromptImplementation(Prompt):

    def create_inference_prompt(self, constitution: UserConstitution, query: str, num_requirements: int):
        str_rubric_impl, str_rubric_qual, qual_keys, impl_keys = get_rubric_strings()

        return f"""Here are a list of inferences about a user. The numbered inference is a high-level inference, while the sub bullet points provide evidence for these inferences:
<profile>
{constitution.for_llm()}
</profile>

They are now asking:
<query>
{query}
</query>

{get_personalizedqa_description()}

{get_personalization_strategy_description()}

The qualitative personalization label is based on how the response will be personalized to the user at a qualitative level:
<qualitative personalization strategies>
{str_rubric_qual}
</qualitative personalization strategies>

The implementation personalization label is based on the three-step execution of ScholarQA, categorized as:
<implementation personalization strategies>
{str_rubric_impl}
</implementation personalization strategies>

<format instructions>
Generate your output as a JSON object with {len(PERSONALIZATION_FRAMEWORK_RUBRIC)} keys based on the implementation personalization strategies: {impl_keys}---where each key has a list of personalization strategy objects. Each strategy object should have four keys: 1) a string "strategy" as a brief high-level requirement for the final output that would lead to a more helpful response that is personalized to this user; 2) a string "tldr" with an extremely brief version of the "strategy" (less than fifteen words); 3) an integer "inference_number" which has the numbered inference from which the strategy was derived; and 4) a string "qualitative_strategy" categorizing how the output will be affected qualitatively (one of {qual_keys}). All requirements should be a concise sentence (<30 words) in the exact form \"I can... [action to take], which might help you... [predicted help]\". Include exactly {NUMBER_WORDS[num_requirements]} {'strategy' if num_requirements == 1 else 'strategies'} for each implementation category ({NUMBER_WORDS[num_requirements]} personalization {'strategy' if num_requirements == 1 else 'strategies'} for each of {impl_keys}). Make sure all of the strategies directly address the query.
</format instructions>

<personalization instructions>
{PERSONALIZATION_INSTRUCTIONS}
{get_usefulness_requirement()}
</personalization instructions>

<action instructions>
{ACTION_INSTRUCTIONS}
</action instructions>

<strategy instructions>
{PERSONALIZED_STRATEGY_INSTRUCTIONS}
</strategy instructions>

<tldr instructions>
{TLDR_INSTRUCTIONS}
</tldr instructions>
"""

class PlanGenerationPromptImplementationNonpersonalized(Prompt):

    def create_inference_prompt(self, constitution: UserConstitution, query: str, num_requirements: int):
        str_rubric_impl, str_rubric_qual, qual_keys, impl_keys = get_rubric_strings()

        return f"""The user is now asking:
<query>
{query}
</query>

{get_personalizedqa_description()}

{get_personalization_strategy_description()}

The qualitative personalization label is based on how the response will be personalized to the user at a qualitative level:
<qualitative personalization strategies>
{str_rubric_qual}
</qualitative personalization strategies>

The implementation personalization label is based on the three-step execution of ScholarQA, categorized as:
<implementation personalization strategies>
{str_rubric_impl}
</implementation personalization strategies>

<format instructions>
Generate your output as a JSON object with {len(PERSONALIZATION_FRAMEWORK_RUBRIC)} keys based on the implementation personalization strategies: {impl_keys}---where each key has a list of personalization strategy objects. Each strategy object should have three keys: 1) a string "strategy" as a brief high-level requirement for the final output that would lead to a more helpful response that is personalized to this user; 2) a string "tldr" with an extremely brief version of the "strategy" (less than fifteen words); and 3) a string "qualitative_strategy" categorizing how the output will be affected qualitatively (one of {qual_keys}). All requirements should be a concise sentence (<30 words) in the exact form \"I can... [action to take], which might help you... [predicted help]\". Include exactly {NUMBER_WORDS[num_requirements]} {'strategy' if num_requirements == 1 else 'strategies'} for each implementation category ({NUMBER_WORDS[num_requirements]} personalization {'strategy' if num_requirements == 1 else 'strategies'} for each of {impl_keys}). Make sure all of the strategies directly address the query.
</format instructions>

<action instructions>
{ACTION_INSTRUCTIONS}
</action instructions>

<strategy instructions>
{NONPERSONALIZED_STRATEGY_INSTRUCTIONS}
</strategy instructions>

<tldr instructions>
{TLDR_INSTRUCTIONS}
</tldr instructions>
"""