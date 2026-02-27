
model_name='gpt-4.1-2025-04-14' # model-generated plans to evaluate

data_input_dir="data/local_datasets/simulated_profile_inputs" # dataset inputs
profile_output_dir='outputs/user_profile/profiles/gpt-4.1-2025-04-14/' # the profiles these plans were conditioned on
plan_output_dir='outputs/user_profile/plans/' # where the plans are saved
output_dir='evaluation/eval_runs/plans/' # where to save the eval run

python -m evaluation.eval_plans  \
  --input_dir "$data_input_dir" \
  --profile_dir "$profile_output_dir" \
  --plan_dir "$plan_output_dir" \
  --model_name "$model_name" \
  --output_dir "$output_dir" \
  --limit 1

python -m metric_scores.plan_metrics