
model_name='gpt-4.1-2025-04-14' # the model that generated profiles

data_input_dir="data/local_datasets/simulated_profile_inputs" # the input dataset
profile_output_dir='outputs/user_profile/profiles/' # the directory with the profiles
output_dir=evaluation/eval_runs/profiles # where to save the eval runs

python -m evaluation.eval_profile  \
  --input_dir "$data_input_dir" \
  --profile_dir "$profile_output_dir" \
  --model_name "$model_name" \
  --output_dir "$output_dir" \
  --limit 1

python -m metric_scores.profile_metrics
