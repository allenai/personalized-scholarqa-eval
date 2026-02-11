from data import Paper, AtomicInference, HighLevelInference
from enums import ConstitutionCategory 
from typing import List
from enums import ModelType

from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')

import argparse

def enum_type(enum):
    enum_members = {e.name: e for e in enum}

    def converter(input):
        out = []
        for x in input.split():
            if x in enum_members:
                out.append(enum_members[x])
            else:
                raise argparse.ArgumentTypeError(f"You used {x}, but value must be one of {', '.join(enum_members.keys())}")
        return out[0]

    return converter

def setup_profile_args():

    # hyperparameters
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_name",
        type=str,
        help="Name of the model on the official API",
        required=True
    )
    parser.add_argument(
        "--model_type",
        type=enum_type(ModelType),
        help="Enum for the model type/API provider",
        required=True
    )
    parser.add_argument(
        "--num_inferences",
        type=int,
        help="Number of inferences to generate per category",
        required=True
    )
    parser.add_argument(
        "--paper_dir",
        type=str,
        help="Directory where papers are stored",
        required=True
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        help="Directory where inputs are stored",
        required=True
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        help="Directory where outputs should be stored",
        required=True
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Number of examples to run (0 for all)",
        required=True
    )
    args = parser.parse_args()
    print(args)
    return args

def setup_plan_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_name",
        type=str,
        help="Name of the model on the official API",
        required=True
    )
    parser.add_argument(
        "--model_type",
        type=enum_type(ModelType),
        help="Enum for the model type/API provider",
        required=True
    )
    parser.add_argument(
        "--num_actions",
        type=int,
        help="Number of actions to generate per category",
        required=True
    )
    parser.add_argument(
        "--use_implementation_strategy",
        action="store_true",
        help="Controls whether to generate actions categorized by how they impact the execution (true), or by how they qualitative implact the report (false)"
    )
    parser.add_argument(
        "--profile_dir",
        type=str,
        help="Directory where profiles are saved",
        required=True
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        help="Directory where inputs are stored",
        required=True
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        help="Directory where outputs should be stored",
        required=True
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Number of examples to run (0 for all)",
        required=True
    )
    args = parser.parse_args()
    print(args)
    return args

def setup_model():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_name",
        type=str,
        help="Name of the model on the official API",
        required=True
    )
    parser.add_argument(
        "--model_type",
        type=enum_type(ModelType),
        help="Enum for the model type/API provider",
        required=True
    )
    args = parser.parse_args()
    print(args)
    return args

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

def parse_llm_response_to_inferences(llm_response: dict, papers: List[Paper], category: ConstitutionCategory):
    paper_titles = [paper.title for paper in papers]

    category_inferences = []
    for inference_obj in llm_response[category.value]:   
        atomic_inferences = []
        for atomic_inf_obj in inference_obj['atomic_inferences']:
            atomic_inf_text, cited_title, paragraph_nums = atomic_inf_obj['atomic_inference'], atomic_inf_obj['paper_title'], atomic_inf_obj['paragraph_numbers']
            closest_title = closest_paper(paper_titles=paper_titles, cited_title=cited_title)
            title_idx = None if closest_title == '' else paper_titles.index(closest_title)

            sources = []
            if closest_title:                        
                for cited_para in paragraph_nums:
                    try:
                        sources.append(papers[title_idx][int(cited_para.strip()) if type(cited_para) == str else int(cited_para)])
                    except Exception as e:
                        pass
                        
            atomic = AtomicInference(text=atomic_inf_text, sources=sources)
            atomic_inferences.append(atomic)

        high_level = HighLevelInference(text=inference_obj['inference'], sources=atomic_inferences)
        category_inferences.append(high_level)

    return category_inferences