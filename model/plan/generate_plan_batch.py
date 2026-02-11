from data.dataset_loader import DatasetLoader
from llms.model_factory import ModelFactory
from data import UserConstitution, PlanRequirement, Plan
from prompt.template import PlanGenerationPromptImplementation, PlanGenerationPromptImplementationNonpersonalized, PlanGenerationPromptQualitative, PlanGenerationPromptQualitativeNonpersonalized
from model.util import setup_plan_args
from enums import PersonalizationFramework, PersonalizationStrategy, PERSONALIZATION_STRATEGY_RUBRIC, PERSONALIZATION_FRAMEWORK_RUBRIC, PersonalizationExperimentGroup

import tqdm
import random
import os

def closest_paper(cited_title: str, paper_titles: list[str]):
    cited_words = set([w.lower() for w in cited_title.split('_')])
    max_match = 0
    best_title = ''
    for title in paper_titles:
        title_words = set([w.lower() for w in title.split('_')])
        num_match = len(cited_words.intersection(title_words))

        if num_match > max_match:
            max_match = num_match
            best_title = title
    return best_title

def generate_plan(constitution: UserConstitution, query: str, experiment_group: PersonalizationExperimentGroup, model_name: str, model_type: any, use_implementation_strategy: bool = False, num_requirements: int = 1) -> Plan:

    # Choose the appropriate prompt based on experiment group
    if experiment_group == PersonalizationExperimentGroup.personalized:
        prompt = PlanGenerationPromptImplementation() if use_implementation_strategy else PlanGenerationPromptQualitative()
    else:
        prompt = PlanGenerationPromptImplementationNonpersonalized() if use_implementation_strategy else PlanGenerationPromptQualitativeNonpersonalized()

    plan = Plan.default()
    
    flat_infs = constitution.flattened_inferences()
    inf_prompt = prompt.create_inference_prompt(constitution=constitution, query=query, num_requirements=num_requirements)

    RUBRIC = PERSONALIZATION_FRAMEWORK_RUBRIC if use_implementation_strategy else PERSONALIZATION_STRATEGY_RUBRIC
    target_key = 'qualitative_strategy' if use_implementation_strategy else 'implementation_strategy'
    output_json = {strategy.value: [{'strategy': '', 'inference_number': 0, 'tldr': '', target_key: ''}] for strategy in RUBRIC.keys()} if experiment_group == PersonalizationExperimentGroup.personalized else {strategy.value: [{'strategy': '', 'tldr': '', target_key: ''}] for strategy in RUBRIC.keys()}
    output_json_backup = {strategy.value: {'strategy': '', 'inference_number': 0, 'tldr': '', target_key: ''} for strategy in RUBRIC.keys()} if experiment_group == PersonalizationExperimentGroup.personalized else {strategy.value: [{'strategy': '', 'tldr': '', target_key: ''}] for strategy in RUBRIC.keys()}

    factory = ModelFactory()

    llm = factory.get_model(model_type=model_type, model_name=model_name)
    out = llm.generate_json(prompt=inf_prompt, target_json=output_json, backup_json=output_json_backup)
    if out is None:
        return Plan.default()
    
    for k in RUBRIC.keys():
        plan_requirements = []
        out_list = out[k.value] if type(out[k.value]) == type([]) else [out[k.value]]
        for req in out_list:
            req_str = req['strategy']
            tldr = req['tldr']
            inference_cite = req['inference_number'] if experiment_group == PersonalizationExperimentGroup.personalized else -1
            strategy_label = req[target_key]
            try:
                inference_obj = flat_infs[inference_cite] if inference_cite != -1 else None
                category_cite = constitution.lookup_category(inference_obj) if inference_obj is not None else None
            except:
                inference_obj = None
                category_cite = None
            
            try:
                strategy_label = PersonalizationStrategy(strategy_label.lower().replace(' ', '_')) if use_implementation_strategy else PersonalizationFramework(strategy_label.lower().replace(' ', '_'))
            except Exception as e:
                print('Error parsing strategy label:', e)
                strategy_label = PersonalizationStrategy.content if use_implementation_strategy else PersonalizationFramework.generation

            plan_requirements.append(PlanRequirement(text=tldr,
                                                    long_text=req_str,
                                                    source_inference=inference_obj,
                                                    strategy_label=strategy_label,
                                                    source_category=category_cite))

        # failsafe: if we generate too many requirements, we need to truncate the list
        if len(plan_requirements) > num_requirements:
            print('generated too many requirements, truncating')
            plan_requirements = random.sample(plan_requirements, num_requirements)

        plan[k] = plan[k] + plan_requirements

    return plan

def run(query: str, query_id: str, user_id: str, constitution: UserConstitution, output_dir: str, args: any):
    personalized_plan = generate_plan(constitution=constitution, query=query, experiment_group=PersonalizationExperimentGroup.personalized, model_name=args.model_name, model_type=args.model_type, use_implementation_strategy=args.use_implementation_strategy, num_requirements=args.num_actions)
    normal_plan = generate_plan(constitution=constitution, query=query, experiment_group=PersonalizationExperimentGroup.normal, model_name=args.model_name, model_type=args.model_type, use_implementation_strategy=args.use_implementation_strategy, num_requirements=args.num_actions)

    normal_plan.to_json(output_dir=output_dir, query_id=query_id + '_normal', user_id=user_id)
    personalized_plan.to_json(output_dir=output_dir, query_id=query_id + '_personalized', user_id=user_id)


def main():

    args = setup_plan_args()
    
    profile_dir = args.profile_dir
    output_dir = f'{args.output_dir}/{args.model_name}/'    

    ds_loader = DatasetLoader(ds_name=args.input_dir)

    queries, query_ids, constitutions, user_ids = ds_loader.load_plan_inputs(profile_dir=profile_dir, num_examples=args.limit)

    for query, query_id, constitution, user_id in tqdm.tqdm(list(zip(queries, query_ids, constitutions, user_ids))):
        
        if os.path.exists(os.path.join(output_dir, query_id + '_normal', f"{user_id}.json")) and os.path.exists(os.path.join(output_dir, query_id + '_personalized', f"{user_id}.json")):
            print(f'skipping on query: {query_id}, user: {user_id}')
            continue
        
        for run_idx in range(3):
            try:
                run(query=query, query_id=query_id, constitution=constitution, user_id=user_id, output_dir=output_dir, args=args)
                break
            except Exception as e:
                print(f"Error on try {run_idx+1}/3:", e)

if __name__ == '__main__':
    main()