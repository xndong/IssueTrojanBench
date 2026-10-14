#!/usr/bin/env python3
"""
regenerate_tables.py

Regenerates the paper's Table III (EEM success rates) and Table IV
(rejection attribution) directly from the per-run result files.

Usage:
    python regenerate_tables.py IssueTrojanBench_SymPy_Results_final.xlsx \
                                IssueTrojanBench_Requests_Results_final.xlsx

Reads every data sheet (skips the 'Metrics' sheet) from each file, concatenates
them, and prints the tables. Requires: pandas, openpyxl.
"""
import sys
import pandas as pd

ATTACKS = ["Supply Chain", "Policy Bypass", "Persistence Hook", "Resource Exhaustion"]
MODELS  = ["GPT-5.3 Codex", "GPT-5.4", "Sonnet 4.6"]
AGENTS  = ["Cursor", "Claude Code", "Codex Desktop"]
VECTORS = ["PDF", "Website", "Source Code", "Issue Comment", "GitHub Issue", "Image Alt-text"]


def load(paths):
    frames = []
    for p in paths:
        xl = pd.ExcelFile(p)
        for sheet in xl.sheet_names:
            if sheet.lower() == "metrics":
                continue
            frames.append(xl.parse(sheet))
    df = pd.concat(frames, ignore_index=True)
    return df


def pct(df):
    return round(100 * (df["EEM_Score"] == 1).mean(), 1) if len(df) else 0.0


def table_iii(df):
    print("=" * 70)
    print("TABLE III: EEM Success Rates")
    print("=" * 70)
    print(f"\nOverall: {(df.EEM_Score==1).sum()}/{len(df)} = {pct(df)}%\n")

    print("By Underlying Model:")
    for m in MODELS:
        s = df[df.Model == m]
        print(f"  {m:16s}: {pct(s)}%")

    print("\nBy Agent Framework:")
    for a in AGENTS:
        s = df[df.Agent_Framework == a]
        print(f"  {a:16s}: {pct(s)}%")

    print("\nBy Attack Category:")
    for a in ATTACKS:
        s = df[df.Attack_Category == a]
        print(f"  {a:22s}: {pct(s)}%")

    print("\nBy Delivery Vector:")
    for v in VECTORS:
        s = df[df.Delivery_Vector == v]
        print(f"  {v:16s}: {pct(s)}%")

    print("\nAttack x Model matrix (success %):")
    mat = (df.pivot_table(index="Attack_Category", columns="Model",
                          values="EEM_Score", aggfunc="mean")
             .mul(100).round(1).reindex(ATTACKS)[MODELS])
    print(mat.to_string())


def table_iv(df):
    print("\n" + "=" * 70)
    print("TABLE IV: Rejection Attribution (EEM = 0)")
    print("=" * 70)
    z = df[df.EEM_Score == 0]
    total = len(z)
    mr = (z.Rejection_Attribution == "Model Refusal").sum()
    tc = (z.Rejection_Attribution == "Trust Classification").sum()
    print(f"\nTotal rejected: {total}")
    print(f"  Model Refusal:        {mr} ({round(100*mr/total,1)}%)")
    print(f"  Trust Classification: {tc} ({round(100*tc/total,1)}%)\n")
    print(f"{'Model':16s} {'EEM=0':>7s} {'Refusal':>9s} {'Trust':>7s}")
    for m in MODELS:
        zm = z[z.Model == m]
        print(f"{m:16s} {len(zm):7d} "
              f"{(zm.Rejection_Attribution=='Model Refusal').sum():9d} "
              f"{(zm.Rejection_Attribution=='Trust Classification').sum():7d}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python regenerate_tables.py <file1.xlsx> [<file2.xlsx> ...]")
        sys.exit(1)
    df = load(sys.argv[1:])
    print(f"Loaded {len(df)} runs from {len(sys.argv)-1} file(s).\n")
    table_iii(df)
    table_iv(df)


if __name__ == "__main__":
    main()
