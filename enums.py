"""
Enums for specific models to load and experiments to run
"""
from enum import Enum

class ModelType(Enum):
    open_ai = 'open_ai' # OpenAI
    anthropic = 'anthropic' # Anthropic
    gemini = 'gemini' # Gemini
    litellm = 'litellm' # LiteLLM

class ConstitutionCategory(Enum):
    knowledge = 'knowledge'
    research_style = 'research_style'
    writing_style = 'writing_style'
    positions = 'positions'
    epistemology = 'epistemology'
    audience = 'audience'
    conclusions = 'conclusions'

class PersonalizationStrategy(Enum):
    content = 'content'
    usefulness = 'usefulness'
    specificity = 'specificity'
    explanation_style = 'explanation_style'

class PersonalizationFramework(Enum):
    search_add = 'search_add'
    search_refine = 'search_refine'
    organization = 'organization'
    generation = 'generation'

class PersonalizationExperimentGroup(Enum):
    personalized = 'personalized'
    normal = 'normal'
    anti_personalized = 'anti_personalized'

class PaperVenue(Enum):
    ACL = 'Annual Meeting of the Association for Computational Linguistics'
    ICLR = 'International Conference on Learning Representations'
    EMNLP = 'Conference on Empirical Methods in Natural Language Processing'
    CVPR = 'Computer Vision and Pattern Recognition'
    CHI = 'International Conference on Human Factors in Computing Systems'
    AAAI = 'AAAI Conference on Artificial Intelligence'
    ICCV = 'IEEE International Conference on Computer Vision'
    HRI = 'IEEE/ACM International Conference on Human-Robot Interaction'
    NEURIPS = 'Neural Information Processing Systems'

class PaperField(Enum):
    HCI = 'Human Computer Interaction'
    NLP = 'Natural Language Processing'
    ML = 'Machine Learning'
    CV = 'Computer Vision'
    Mixed = 'Mixed'

class PersonalizationResponseType(Enum):
    both = 'both'
    personalized = 'personalized'
    normal = 'normal'

CONSTITUTION_DEFINITION_RUBRIC = {
    ConstitutionCategory.knowledge: """\
**Definition:** Inferences from the paper about what the researcher *knows or doesn't know*. This includes:
1. **Topic expertise or interest** - What domains the researcher seems fluent in or newly exploring.  
2. **Familiarity with methods** - Implicit or explicit comfort with specific techniques or paradigms.  
3. **Awareness of prior work** - The breadth and specificity of citations or conceptual framing.
**Distinguishing Focus:** What knowledge the researcher holds or lacks.
""",

    ConstitutionCategory.research_style: """\
**Definition:** Inferences about *how the researcher prefers to conduct research*. This includes:
1. **Methodological preferences** - Use of qualitative, quantitative, computational, or hybrid approaches.  
2. **Types of research questions** - Empirical, theoretical, exploratory, evaluative, etc.  
3. **Study or experiment strategies** - How data is collected, analyzed, or operationalized.
**Distinguishing Focus:** How the researcher approaches doing research.
""",

    ConstitutionCategory.writing_style: """\
**Definition:** Inferences about *how the researcher writes and explains ideas*. This includes:
1. **Argumentation and structure** - How ideas are developed, ordered, and emphasized.  
2. **Tone and voice** - Formality, assertiveness, didacticism, etc.  
3. **Explanation preferences** - Use of examples, metaphors, definitions, or technical language.  
4. **Stylistic quirks** - Repetition, narrative devices, or particular rhetorical habits.
**Distinguishing Focus:** How the researcher communicates in writing.
""",

    ConstitutionCategory.positions: """\
**Definition:** Inferences about *what the researcher believes or argues*. This includes:
1. **Claims and conclusions** - What stances are taken or avoided.  
2. **Normative views** - Ethical, political, or philosophical commitments evident in the writing.  
3. **Arguments emphasized** - Which perspectives are advanced or critiqued.
**Distinguishing Focus:** What positions the researcher is taking or signaling.
""",

    ConstitutionCategory.audience: """\
**Definition:** Inferences about *who the researcher is writing for or trying to impact*. This includes:
1. **Assumed audience background** - What the researcher expects the reader to already know.  
2. **Stakeholder relevance** - Who is likely to be affected by or benefit from the work.  
3. **Audience alignment** - Whether the writing aligns with academic, practitioner, policy, or public communities.
**Distinguishing Focus:** Who the researcher is addressing or aiming to influence.
"""
}

PERSONALIZATION_FRAMEWORK_RUBRIC = {
    PersonalizationFramework.search_add: """\
**Definition:** Personalizes the search by **adding new terms or dimensions** to the original query. This includes:
- Introducing related subfields, topics, or concepts the user may not have explicitly mentioned
- Incorporating inferred preferences such as favored methods, datasets, evaluations, or research types
- Expanding the query scope to make responses more relevant or actionable in the user’s workflow
- Suggesting new combinations of fields or terms to enhance discovery
""",

    PersonalizationFramework.search_refine: """\
**Definition:** Personalizes the search by **revising or improving** the original query. This includes:
- Disambiguating unclear or subjective terms
- Making existing search terms more specific or technically precise
- Narrowing or clarifying the focus based on known user preferences or context
- Adjusting query language to better match terminology used in the literature
- Removing irrelevant, redundant, or low-value terms that may dilute the quality of results
""",

    PersonalizationFramework.organization: """\
**Definition:** Personalizes how the papers are grouped into sections for the final response. This includes:
- Which sections should be included or excluded (e.g. skipping intro sections if the user is an expert in the field, adding background sections if the user is a novice)
- High-level structure (e.g. organizing by themes, topic, methods, history, research questions, etc.)
- Additional sections to make the response more useful in the user's research workflow (e.g. a section on follow-up ideas, implementation steps, considerations, suggestions, etc.). This should be heavily prioritized.
""",

    PersonalizationFramework.generation: """\
**Definition:** Personalizes how certain sections are written and explained. This includes:
- What connections the responses should make (e.g. connections to the user's prior frameworks, methods, papers, etc.)
- The strategy of explanations (e.g. definitions-first, example-first, intuitive-first, etc.)
- The writing style and level of elaboration based on the user's expertise (e.g. brief overviews versus deep exposition)
"""
}

PERSONALIZATION_STRATEGY_RUBRIC = {
    PersonalizationStrategy.content: """\
**Definition:** Specifies *what information* the response should include and how it should be conceptually framed. This can include:
1. **Conceptual scope** - Which concepts to emphasize, omit, or define.  
2. **Depth of explanation** - Whether to provide brief overviews (if the user is knowledgable on the area) or in-depth knowledge (if the user is new to the field).  
3. **Terminology alignment** - Tailoring vocab to match the user's disciplinary conventions.
**Distinguishing Focus:** What content is covered and how deeply.
""",

    PersonalizationStrategy.explanation_style: """\
**Definition:** Specifies *how the explanation for the information is communicated*. This can include:
1. **Explanatory style** - Empirical, intuitive, formal/mathematical, or example-led.  
2. **Cognitive structuring** - Layered explanations, definitions first vs. bottom-up learning.  
3. **Framing mechanisms** - Use of analogies, metaphors, or domain-specific language aligned with the researcher's background.  
**Distinguishing Focus:** How the content is explained, formatted, and connected to other concepts.
""",

    PersonalizationStrategy.specificity: """\
**Definition:** Clarifies and narrows the scope of the response to better match the researcher's intended focus. This can include:
1. **Disambiguating vague inputs** - Interpreting terms like "methods, "frameworks", or "best" in the user's specific context.  
2. **Focusing by domain/task** - Aligning content to a subfield, methodology, or research phase.  
3. **Resolving underspecification** - Filling in implicit assumptions (e.g., assuming qualitative when not stated).  
4. **Removing irrelevant scope** - Avoiding generalizations or adjacent topics not central to the task.
**Distinguishing Focus:** What exactly is meant or needed, and how to restrict the response to that.
""",

    PersonalizationStrategy.usefulness: """\
**Definition:** Shapes the response to be *actionable* or *instrumental* for the researcher's goals or workflow. This can include:
1. **Direct application** - Helping write a section, implement a method, interpret results, etc.  
2. **Workflow integration** - Mapping content to stages of research or types of output.  
3. **Next steps** - Suggesting what to do with the information (e.g., adapt, cite, reframe, test).  
4. **Decision support** - Helping choose between options, methods, or framings based on task-fit.
**Distinguishing Focus:** How the information can be turned into research actions or outputs.
"""
}