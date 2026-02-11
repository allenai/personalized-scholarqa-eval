
from .evaluator import PersonalizedPlanEvaluator
from data.dataset_loader import DatasetLoader
import os
from enums import ModelType
import argparse

from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')

def setup():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      "--profile_dir",
      type=str,
      help="Directory of the profiles used to generate plans",
      required=True
  )
  parser.add_argument(
      "--plan_dir",
      type=str,
      help="Directory of the plans to evaluate",
      required=True
  )
  parser.add_argument(
      "--input_dir",
      type=str,
      help="Where the dataset is saved",
      required=True
  )
  parser.add_argument(
      "--output_dir",
      type=str,
      help="Where to save the eval run",
      required=True
  )
  parser.add_argument(
      "--model_name",
      type=str,
      help="Name of the model to eval",
      required=True
  )
  parser.add_argument(
      "--limit",
      type=int,
      help="Number of instances to evaluate (0 for all)",
      required=True
  )
  return parser.parse_args()


def main():  

  args = setup()
  model_name = args.model_name

  evaluator = PersonalizedPlanEvaluator(judge_model_name='gemini-2.5-flash-preview-09-2025', judge_model_type=ModelType.gemini)

  profile_dir = args.profile_dir
  plan_dir = f'{args.plan_dir}/{model_name}/'
  output_dir = args.output_dir

  ds_loader = DatasetLoader(ds_name=args.input_dir)
  response_data = ds_loader.load_plan_pairs(constitution_dir=profile_dir, plan_dir=plan_dir, num_examples=args.limit)

  eval_run_query, eval_run_personalized, eval_run_category = evaluator.evaluate(personalized_plans=response_data['personalized_plan'], normal_plans=response_data['normal_plan'], constitutions=response_data['constitution'], queries=response_data['query'], query_ids=response_data['query_id'], user_ids=response_data['user_id'])

  eval_run_query.to_json(output_dir=output_dir, run_name=model_name + '_query')
  eval_run_personalized.to_json(output_dir=output_dir, run_name=model_name + '_personalized')
  eval_run_category.to_json(output_dir=output_dir, run_name=model_name + '_category')

if __name__ == '__main__':
  main()