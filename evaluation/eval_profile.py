
from .evaluator import ProfileEvaluator
from enums import EVALUATOR_MODEL, EVALUATOR_MODEL_TYPE
import os
import argparse

os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')

from data.dataset_loader import DatasetLoader

def setup():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      "--profile_dir",
      type=str,
      help="Directory of the profile to evaluate",
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
  ds_loader = DatasetLoader(ds_name=args.input_dir)
  evaluator = ProfileEvaluator(judge_model_name=EVALUATOR_MODEL, judge_model_type=EVALUATOR_MODEL_TYPE)

  model_name = args.model_name
  profile_dir = f'{args.profile_dir}/{model_name}/'

  constitutions, user_ids = ds_loader.load_constitution_outputs(output_dir=profile_dir, num_examples=args.limit)
  assert len(constitutions) == len(user_ids)
  evaluator.evaluate(user_ids=user_ids, constitutions=constitutions, run_name=model_name, output_dir=args.output_dir + '/' + args.model_name)

if __name__ == '__main__':
  main()