
model_type="open_ai"
model_name="gpt-4.1-nano-2025-04-14"
prompt_dir="prompt/user_prediction_prompts"
qual_coding_input_dir="data/local_datasets/qualitative_coding_data"
output_dir="evaluation/eval_runs/simulation_eval/"
num_examples=2

python -m evaluation.predict_user_data \
  --model_name "$model_name" \
  --model_type "$model_type" \
  --prompt_dir "$prompt_dir" \
  --input_dir "$qual_coding_input_dir" \
  --output_dir "$output_dir" \
  --num_examples 2

python -m metric_scores.simulation_plot