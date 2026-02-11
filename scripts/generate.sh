#!/bin/bash

paper_dir="data/local_datasets/paper_objects/" # path to where paper objects are stored
data_input_dir="data/local_datasets/simulated_profile_inputs" # path to where profile inputs/dataset inputs are
profile_output_dir="outputs/user_profile/profiles" # path to save profiles to
plan_output_dir="outputs/user_profile/plans" # path to save plans to

model_name="gpt-4.1-2025-04-14" # model for generating profiles (API endpoint)
model_type="open_ai" # model type/provider, supports any of the ModelType enums in enum.py (`open_ai`, `anthropic`, `gemini`, `litellm`)

# generate user profiles
python -m model.user_profile.generate_profile_batch \
  --model_name "$model_name" \
  --model_type "$model_type" \
  --paper_dir "$paper_dir" \
  --input_dir "$data_input_dir" \
  --output_dir "$profile_output_dir" \
  --num_inferences 5 \
  --limit 1

# generate plans
python -m model.plan.generate_plan_batch \
  --model_name "$model_name" \
  --model_type "$model_type" \
  --profile_dir "$profile_output_dir/gpt-4.1-2025-04-14" \
  --input_dir "$data_input_dir" \
  --output_dir "$plan_output_dir" \
  --num_actions 5 \
  --limit 1
