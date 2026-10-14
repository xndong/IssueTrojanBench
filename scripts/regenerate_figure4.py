#!/usr/bin/env python3
"""
regenerate_figure4.py

Regenerates Figure 4 (Rejection Attribution by Model) from the per-run
result files: a stacked bar chart of rejected runs (EEM=0) per model,
split into Model Refusal and Trust Classification.

Usage:
    python regenerate_figure4.py IssueTrojanBench_SymPy_Results_final.xlsx \
                                 IssueTrojanBench_Requests_Results_final.xlsx

Output: figure4_rejection_attribution.png
Requires: pandas, openpyxl, matplotlib
"""
import sys
import pandas as pd
import matplotlib.pyplot as plt

MODELS = ["GPT-5.3 Codex", "GPT-5.4", "Sonnet 4.6"]


def load(paths):
    frames = []
    for p in paths:
        xl = pd.ExcelFile(p)
        for sheet in xl.sheet_names:
            if sheet.lower() == "metrics":
                continue
            frames.append(xl.parse(sheet))
    return pd.concat(frames, ignore_index=True)


def main():
    if len(sys.argv) < 2:
        print("Usage: python regenerate_figure4.py <file1.xlsx> [<file2.xlsx> ...]")
        sys.exit(1)

    df = load(sys.argv[1:])
    z = df[df.EEM_Score == 0]
    total_runs_per_model = len(df) // len(MODELS)  # 1392

    refusal, trust, rej_rate = [], [], []
    for m in MODELS:
        zm = z[z.Model == m]
        refusal.append((zm.Rejection_Attribution == "Model Refusal").sum())
        trust.append((zm.Rejection_Attribution == "Trust Classification").sum())
        rej_rate.append(round(100 * len(zm) / total_runs_per_model, 1))

    fig, ax = plt.subplots(figsize=(7, 5))
    b1 = ax.bar(MODELS, refusal, label="Explicit Model Refusal", color="#2F5496")
    b2 = ax.bar(MODELS, trust, bottom=refusal, label="Trust Classification", color="#ED7D31")

    for i, m in enumerate(MODELS):
        total = refusal[i] + trust[i]
        ax.text(i, total + 8, f"{total}/{total_runs_per_model}\n({rej_rate[i]}%)",
                ha="center", va="bottom", fontsize=10)

    ax.set_ylabel("Number of Rejected Runs (EEM = 0)")
    ax.set_title("Rejection Attribution by Model")
    ax.legend()
    ax.set_ylim(0, max(r + t for r, t in zip(refusal, trust)) * 1.20)
    plt.tight_layout()
    out = "figure4_rejection_attribution.png"
    plt.savefig(out, dpi=200)
    print(f"Saved {out}")
    print("\nPer-model rejection counts:")
    for i, m in enumerate(MODELS):
        print(f"  {m}: refusal={refusal[i]}, trust={trust[i]}, "
              f"total={refusal[i]+trust[i]} ({rej_rate[i]}%)")


if __name__ == "__main__":
    main()
