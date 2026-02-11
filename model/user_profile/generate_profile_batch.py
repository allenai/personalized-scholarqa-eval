import os

from llms.model_factory import ModelFactory
from data import UserConstitution
from data.paper_data import NewPaper
from data.dataset_loader import DatasetLoader
from prompt.template import MultiPaperAuthorInferencesPromptThirdParty
from model.util import parse_llm_response_to_inferences, setup_profile_args
from enums import CONSTITUTION_DEFINITION_RUBRIC
from tqdm import tqdm

from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')

def run(papers: list[NewPaper], author_id: str, output_dir: str, args: any):

    constitution = UserConstitution()

    prompt = MultiPaperAuthorInferencesPromptThirdParty()
    inf_prompt = prompt.create_inference_prompt(papers=papers, num_inferences=args.num_inferences, categories=list(CONSTITUTION_DEFINITION_RUBRIC.keys()))

    output_json = {
        k.value: [{'inference': '', 'atomic_inferences': [{'atomic_inference': '', 'paper_title': '', 'paragraph_numbers': []}]}] for k in CONSTITUTION_DEFINITION_RUBRIC.keys()
    }

    factory = ModelFactory()
    llm = factory.get_model(model_type=args.model_type, model_name=args.model_name)
    out = llm.generate_json(prompt=inf_prompt, target_json=output_json)
    
    for category in CONSTITUTION_DEFINITION_RUBRIC.keys():
        constitution[category] = parse_llm_response_to_inferences(llm_response=out, papers=papers, category=category)

    constitution.to_json(output_dir=output_dir, user_id=author_id)

def main():

    args = setup_profile_args()

    ds_loader = DatasetLoader(ds_name=args.input_dir)
    paper_collections, author_ids = ds_loader.load_constitution_inputs(num_examples=args.limit)
    output_dir = args.output_dir + f'/{args.model_name}'

    for entry_idx, collection in enumerate(tqdm(paper_collections)):
        author_id = author_ids[entry_idx]
        papers = []
        for paper_id in collection:
            paper = NewPaper.from_json(paper_id=paper_id, output_dir=args.paper_dir)
            papers.append(paper)

        if os.path.exists(os.path.join(output_dir, f"{author_id}.json")):
            print(f'skipping output: {output_dir}, author: {author_id}')
            continue

        for run_idx in range(3):
            try:
                run(papers=papers, author_id=author_id, output_dir=output_dir, args=args)
                break
            except Exception as e:
                print(f"Error on attempt {run_idx}/3:", e)

if __name__ == '__main__':
    main()