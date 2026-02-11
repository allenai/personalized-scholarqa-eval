import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import matplotlib.pyplot as plt

# models to evaluate, and how they should appear in the plot (nickname)
MODELS = [
    "gpt-4.1-nano-2025-04-14",
]
MODEL_NICKNAMES = [
    'GPT-4.1 Nano',
]
SAVE_DIR = 'metric_scripts/figures/simulation_results.pdf' # where to save the figure
PREDICTION = 'pred_metric' # 'pred_metric' | 'pred_basic' (which eval run type to assess)
EVAL_RUN_DIR = 'evaluation/eval_runs/simulation_eval/' # folder with the evaluation run

# ---------- AI2 palette ----------
PALETTE = {
    "dark_teal": "#0A3235",
    "off_white": "#FAF2E9",
    "teal": "#105257",
    "pink": "#F0529C",
    "purple": "#B11BE8",
    "green": "#0FCB8C",
}
MODEL_COLORS = [PALETTE[color] for color in ['teal', 'pink', 'purple', 'green'][:len(MODELS)]]
MODEL_COLORS = dict(zip(MODEL_NICKNAMES, MODEL_COLORS))
KEYWORD_MAP = {
    'GENERAL': 'CONVENTION',
    'NEGATION': 'CONTRAST',
    'KEYWORD': 'DOMAIN',
    'OVERGENERAL': 'OVERCLAIM',
    'FAILED': 'IGNORE',
    'STYLE': 'PRESENT',
    'UNINFORMATIVE': 'UNINFORM'
}
# ---------------------------------

# ----- Load results -----
rows = []
for nickname, model in zip(MODEL_NICKNAMES, MODELS):
    with open(EVAL_RUN_DIR + model + '.jsonl', 'r') as json_file:
        json_list = list(json_file)
    for json_str in json_list:
        result = json.loads(json_str)
        result['metric'] = KEYWORD_MAP.get(result['metric'], result['metric'])
        rows.append(result | {'model': nickname})

df = pd.DataFrame(rows)

# ----- Compute correctness -----
pred, true = df[PREDICTION], df['true']
acc = []
for p, t in zip(pred, true):
    if (t == 'good_similar' or t == 'good_random') and p:
        acc.append(1.0)
    elif t == 'bad' and not p:
        acc.append(1.0)
    else:
        acc.append(0.0)
df['correct'] = acc

acc = (
    df.groupby(["split", "metric", "model"], dropna=False)["correct"]
      .mean()
      .reset_index()
)

# ----- Plotting -----
splits = ['profile', 'plan', 'response']
n_splits = len(splits)
fig, axes = plt.subplots(1, n_splits, figsize=(14, 3), sharey=True)

fig.patch.set_facecolor(PALETTE["off_white"])
if n_splits == 1:
    axes = [axes]

n_models = len(MODEL_NICKNAMES)
bar_width = 0.8 / max(n_models, 1)
offsets = (np.arange(n_models) - (n_models - 1) / 2) * bar_width

def add_value_labels(ax, rects):
    for r in rects:
        h = r.get_height()
        if np.isnan(h):
            continue

metric_map = {
    'profile': ['DOMAIN', 'OVERCLAIM', 'CONVENTION', 'CONTRAST'],
    'plan': ['NARROW', 'OFFTOPIC'],
    'response': ['UNINFORM', 'PRESENT', 'IGNORE']
}

counts = (
    df.groupby(["split", "metric"], dropna=False)["correct"]
      .count()
      .to_dict()
)

bars_for_legend = []
for ax, split in zip(axes, splits):
    sub = acc[acc["split"] == split]
    metrics_s = metric_map[split]
    x = np.arange(len(metrics_s))

    for mi, model in enumerate(MODEL_NICKNAMES):
        sub_m = sub[sub["model"] == model].set_index("metric")
        y = pd.Series(index=metrics_s, dtype=float)
        y.loc[:] = np.nan
        common = set(metrics_s).intersection(sub_m.index)
        if common:
            y.loc[list(common)] = sub_m.loc[list(common), "correct"].values

        rects = ax.bar(
            x + offsets[mi], y.values, width=bar_width,
            label=model,
            color=MODEL_COLORS[model],
            edgecolor=PALETTE["dark_teal"], linewidth=0.6,
        )
        add_value_labels(ax, rects)
        if len(bars_for_legend) < n_models:
            bars_for_legend.append(rects[0])

    ax.set_title(f"$\\bf{{{split.replace('response', 'report').replace('plan', 'action').title()}}}$ Satisfaction Prediction", color=PALETTE["dark_teal"])
    ax.set_ylim(0, 1)
    if split == 'profile':
        ax.set_ylabel("Accuracy", color=PALETTE["dark_teal"])
    ax.set_xticks(x)
    metrics_s_names = [m + f"\n(N={counts[(split, m)]})" for m in metrics_s]
    ax.set_xticklabels(metrics_s_names, rotation=0, ha="center", color=PALETTE["dark_teal"])
    ax.tick_params(axis='y', colors=PALETTE["dark_teal"])
    ax.spines[:].set_color(PALETTE["dark_teal"])
    ax.grid(False)

majority_line = axes[0].axhline(
    2/3, color='black', linestyle="--", #fontproperties=manrope_font,
    linewidth=1.2
)

for ax in axes[1:]:
    ax.axhline(2/3, color='black', linestyle="--",
               linewidth=1.2)

leg = fig.legend(
    bars_for_legend + [majority_line],
    MODEL_NICKNAMES + ["Majority Class"],
    loc="lower center", ncol=min(5, n_models + 1),
    #fontproperties=manrope_font,
    frameon=True, facecolor="white", edgecolor=PALETTE["dark_teal"]
)
plt.setp(leg.get_texts(), color=PALETTE["dark_teal"])
plt.setp(leg.get_title(), color=PALETTE["dark_teal"])

fig.tight_layout(rect=[0, 0.075, 1, 0.98])
plt.savefig(SAVE_DIR, facecolor=fig.get_facecolor())
