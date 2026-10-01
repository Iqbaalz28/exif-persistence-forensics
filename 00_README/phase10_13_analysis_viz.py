# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')
"""
DF06 Kelompok 6 - FASE 10-11-12-13: Retention Analysis + File Size + Replikasi + Visualisasi
Operator : Iqbal Rizky Maulana
Date     : 2026-10-01

FASE 10: Metadata retention analysis (per transform, per tag, per tool, overall)
FASE 11: File size + SHA-256 analysis (file_hash_size.csv)
FASE 12: Replikasi analysis (3x replikasi hash consistency check)
FASE 13: Minimal 4 visualisasi (matplotlib)

Output:
  07_ANALYSIS/retention_summary.csv
  07_ANALYSIS/file_hash_size.csv
  07_ANALYSIS/replication_log.csv
  07_ANALYSIS/figures/fig1_retention_per_transform.png
  07_ANALYSIS/figures/fig2_heatmap_transform_tag.png
  07_ANALYSIS/figures/fig3_parser_agreement.png
  07_ANALYSIS/figures/fig4_filesize_distribution.png
"""

import csv
import hashlib
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

BASELINE_DIR   = Path(__file__).parent.parent / "01_BASELINE"
TRANS_DIR      = Path(__file__).parent.parent / "03_TRANSFORMED"
TAG_RESULTS    = Path(__file__).parent.parent / "07_ANALYSIS" / "tag_results.csv"
OUT_DIR        = Path(__file__).parent.parent / "07_ANALYSIS"
FIG_DIR        = OUT_DIR / "figures"
TIMESTAMP      = datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

FIG_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("DF06 Kelompok 6 - Fase 10/11/12/13: Analysis + Visualisasi")
print("=" * 70)
print(f"Timestamp: {TIMESTAMP}")

# ============================================================================
# FASE 10: RETENTION ANALYSIS
# ============================================================================
print("\n[FASE 10] Metadata Retention Analysis")
print("-" * 60)

df = pd.read_csv(TAG_RESULTS, encoding="utf-8")
print(f"Rows loaded: {len(df)}")
print(f"Columns    : {list(df.columns)}")

# Define eligible: retained + changed + missing (exclude unsupported)
df_eligible = df[df["status"].isin(["retained", "changed", "missing"])].copy()
df_retained = df[df["status"] == "retained"]

# ── Overall retention rate ────────────────────────────────────────────────────
total_eligible = len(df_eligible)
total_retained = len(df_retained)
overall_rate = round(total_retained / total_eligible * 100, 2) if total_eligible > 0 else 0
print(f"\nOverall Retention Rate: {total_retained}/{total_eligible} = {overall_rate}%")

# ── Per transformation ────────────────────────────────────────────────────────
print("\nPer Transformation (ExifTool only):")
df_et = df[df["tool"] == "ExifTool_13.59"]
df_et_elig = df_et[df_et["status"].isin(["retained", "changed", "missing"])]

trans_summary = []
for trans in sorted(df_et_elig["transformation"].unique()):
    sub = df_et_elig[df_et_elig["transformation"] == trans]
    ret = (sub["status"] == "retained").sum()
    chg = (sub["status"] == "changed").sum()
    mis = (sub["status"] == "missing").sum()
    elig = ret + chg + mis
    rate = round(ret / elig * 100, 1) if elig > 0 else 0
    trans_summary.append({
        "transformation": trans,
        "retained": int(ret), "changed": int(chg), "missing": int(mis),
        "eligible": int(elig), "retention_rate_pct": rate,
        "tool": "ExifTool_13.59"
    })
    print(f"  {trans:<22}: {ret:>3} retained / {elig:>3} eligible = {rate:>5.1f}%")

# ── Per tag ─────────────────────────────────────────────────────────────────
print("\nPer Tag (ExifTool only):")
tag_summary = []
for tag in df_et_elig["tag_name"].unique():
    sub = df_et_elig[df_et_elig["tag_name"] == tag]
    ret = (sub["status"] == "retained").sum()
    chg = (sub["status"] == "changed").sum()
    mis = (sub["status"] == "missing").sum()
    elig = ret + chg + mis
    rate = round(ret / elig * 100, 1) if elig > 0 else 0
    tag_summary.append({
        "tag_name": tag, "retained": int(ret), "changed": int(chg),
        "missing": int(mis), "eligible": int(elig), "retention_rate_pct": rate,
        "tool": "ExifTool_13.59"
    })
    print(f"  {tag:<25}: {ret:>3} retained / {elig:>3} eligible = {rate:>5.1f}%")

# Save retention summary CSV
ret_csv = OUT_DIR / "retention_summary.csv"
ret_rows = trans_summary + tag_summary
with open(ret_csv, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["transformation","tag_name","retained","changed","missing","eligible","retention_rate_pct","tool"])
    w.writeheader()
    for row in ret_rows:
        w.writerow({k: row.get(k, "") for k in w.fieldnames})
print(f"\nRetention summary saved: {ret_csv}")

# ============================================================================
# FASE 11: FILE SIZE + SHA-256 ANALYSIS
# ============================================================================
print("\n[FASE 11] File Size + SHA-256 Analysis")
print("-" * 60)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

size_rows = []

# Baseline
for p in sorted(BASELINE_DIR.glob("*.jpg")):
    sha = sha256_file(p)
    size_rows.append({
        "stage": "baseline", "transformation": "original",
        "filename": p.name, "filepath": str(p),
        "size_bytes": p.stat().st_size, "sha256": sha
    })

# Transformed
image_exts = {".jpg", ".jpeg", ".png"}
for p in sorted(TRANS_DIR.glob("*/*")):
    if p.suffix.lower() not in image_exts:
        continue
    sha = sha256_file(p)
    trans = p.parent.name
    size_rows.append({
        "stage": "transformed", "transformation": trans,
        "filename": p.name, "filepath": str(p),
        "size_bytes": p.stat().st_size, "sha256": sha
    })

size_csv = OUT_DIR / "file_hash_size.csv"
with open(size_csv, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["stage","transformation","filename","filepath","size_bytes","sha256"])
    w.writeheader()
    w.writerows(size_rows)
print(f"File hash/size CSV: {size_csv}  ({len(size_rows)} rows)")

df_size = pd.DataFrame(size_rows)
baseline_sizes = df_size[df_size["transformation"] == "original"]["size_bytes"].values

print("\nSize statistics per transformation:")
for trans in sorted(df_size["transformation"].unique()):
    sub = df_size[df_size["transformation"] == trans]
    median_size = sub["size_bytes"].median()
    mean_size   = sub["size_bytes"].mean()
    print(f"  {trans:<22}: median={int(median_size):>8} bytes  mean={int(mean_size):>8} bytes")

# ============================================================================
# FASE 12: REPLIKASI (3x hash consistency check)
# ============================================================================
print("\n[FASE 12] Replikasi Analysis")
print("-" * 60)
print("Checking hash consistency across 3 runs (deterministic transformations)...")

# For deterministic PIL transforms, re-run 2 more times and compare SHA-256
# We'll compare just a sample (IMG_01 for each transformation)
repl_log = []
EXIFTOOL = r"E:\UNIVERSITAS PENDIDIKAN INDONESIA\APP\exiftool\exiftool.exe"

def run_transform_sample(trans, sample_file, run_idx):
    """Run one sample transform, return SHA-256."""
    import tempfile, shutil
    from PIL import Image

    tmp_dir = Path(__file__).parent.parent / "06_RAW_RESULTS" / "replication_tmp"
    tmp_dir.mkdir(exist_ok=True)
    out_name = f"repl_R{run_idx}_{sample_file.name}"
    out = tmp_dir / out_name

    t0 = time.time()
    try:
        if trans == "resize":
            with Image.open(sample_file) as im:
                im.resize((320, 240), Image.LANCZOS).save(out, "JPEG", quality=90)
        elif trans == "recompress_q75":
            with Image.open(sample_file) as im:
                im.save(out, "JPEG", quality=75)
        elif trans == "stripped":
            shutil.copy2(sample_file, out)
            subprocess.run([EXIFTOOL, "-overwrite_original", "-all=", str(out)],
                           capture_output=True, timeout=30)
        else:
            with Image.open(sample_file) as im:
                im.save(out, "JPEG", quality=90)
        elapsed = round(time.time() - t0, 4)
        sha = sha256_file(out)
        return sha, elapsed, None
    except Exception as e:
        return None, round(time.time() - t0, 4), str(e)

rep_conditions = ["resize", "recompress_q75", "stripped"]
sample = BASELINE_DIR / "IMG_01.jpg"

print(f"  Sample file: {sample.name}")
print(f"  Conditions : {rep_conditions}")
print()

for trans in rep_conditions:
    hashes = []
    runtimes = []
    for run in range(1, 4):
        sha, rt, err = run_transform_sample(trans, sample, run)
        hashes.append(sha)
        runtimes.append(rt)
        status = "ok" if sha else "fail"
        print(f"  {trans} R{run}: sha={sha[:16] if sha else 'FAIL'}...  rt={rt:.4f}s  {status}")
        repl_log.append({
            "transformation": trans, "sample": sample.name,
            "run": run, "sha256": sha or "", "runtime_sec": rt,
            "status": status, "error": err or ""
        })

    # Check consistency
    unique_hashes = set(h for h in hashes if h)
    consistent = len(unique_hashes) == 1
    median_rt = sorted(runtimes)[1]  # median of 3
    print(f"  >> {trans}: consistent={'YES' if consistent else 'NO'}  median_rt={median_rt:.4f}s")
    print()

repl_csv = OUT_DIR / "replication_log.csv"
with open(repl_csv, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["transformation","sample","run","sha256","runtime_sec","status","error"])
    w.writeheader()
    w.writerows(repl_log)
print(f"Replication log: {repl_csv}")

# ============================================================================
# FASE 13: VISUALISASI (minimal 4 figures)
# ============================================================================
print("\n[FASE 13] Visualisasi (4 Figures)")
print("-" * 60)

# ── Figure 1: Retention rate per transformation ───────────────────────────────
TRANSFORM_ORDER = ["resize", "recompress_q95", "recompress_q75", "recompress_q50",
                   "convert_png", "convert_jpeg", "stripped", "screenshot_like"]
TRANSFORM_LABELS = {
    "resize": "Resize\n(50%)",
    "recompress_q95": "Recompress\nQ95",
    "recompress_q75": "Recompress\nQ75",
    "recompress_q50": "Recompress\nQ50",
    "convert_png": "Convert\nJPEG>PNG",
    "convert_jpeg": "Convert\nPNG>JPEG",
    "stripped": "Metadata\nStrip",
    "screenshot_like": "Screenshot\nRe-encode",
}

fig1, ax1 = plt.subplots(figsize=(12, 6))
trans_names = [TRANSFORM_LABELS.get(t, t) for t in TRANSFORM_ORDER]
trans_rates = []
for t in TRANSFORM_ORDER:
    rows = [r for r in trans_summary if r["transformation"] == t]
    trans_rates.append(rows[0]["retention_rate_pct"] if rows else 0)

colors = ["#e74c3c" if r == 0 else "#f39c12" if r < 50 else "#27ae60" for r in trans_rates]
bars = ax1.bar(range(len(TRANSFORM_ORDER)), trans_rates, color=colors, width=0.6, edgecolor="white", linewidth=1.5)

# Add value labels
for bar, rate in zip(bars, trans_rates):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f"{rate:.1f}%", ha="center", va="bottom", fontsize=11, fontweight="bold", color="#2c3e50")

ax1.set_xticks(range(len(TRANSFORM_ORDER)))
ax1.set_xticklabels(trans_names, fontsize=10)
ax1.set_ylim(0, 110)
ax1.set_xlabel("Transformation Type", fontsize=12, labelpad=10)
ax1.set_ylabel("Metadata Retention Rate (%)", fontsize=12)
ax1.set_title("Figure 1: EXIF Metadata Retention Rate per Transformation\n"
              "(ExifTool 13.59 | 30 Synthetic JPEG Baseline | 9 Tags | DF06 Kelompok 6)",
              fontsize=13, fontweight="bold", pad=15)
ax1.axhline(y=100, color="#95a5a6", linestyle="--", linewidth=1, alpha=0.7)
ax1.set_facecolor("#f8f9fa")
ax1.grid(axis="y", alpha=0.3, linestyle="--")
fig1.text(0.5, -0.02, "Source: 07_ANALYSIS/tag_results.csv | ExifTool_13.59",
          ha="center", fontsize=9, color="gray", style="italic")

fig1_path = FIG_DIR / "fig1_retention_per_transform.png"
fig1.tight_layout()
fig1.savefig(fig1_path, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig1)
print(f"Figure 1 saved: {fig1_path}")

# ── Figure 2: Heatmap transformation x EXIF tag ───────────────────────────────
TARGET_TAGS_ORDER = ["DateTimeOriginal", "Make", "Model", "Software", "Artist",
                     "Copyright", "UserComment", "GPSLatitude", "GPSLongitude"]

# Build pivot: rows=transform, cols=tag, values=retention rate
pivot_data = []
for t in TRANSFORM_ORDER:
    row = []
    sub_t = df_et_elig[df_et_elig["transformation"] == t]
    for tag in TARGET_TAGS_ORDER:
        sub = sub_t[sub_t["tag_name"] == tag]
        ret = (sub["status"] == "retained").sum()
        elig = len(sub)
        rate = round(ret / elig * 100, 0) if elig > 0 else 0
        row.append(rate)
    pivot_data.append(row)

pivot_arr = np.array(pivot_data, dtype=float)
tag_labels_short = ["DateTimeOrig", "Make", "Model", "Software", "Artist",
                    "Copyright", "UserComment", "GPSLat", "GPSLon"]
trans_labels_short = [TRANSFORM_LABELS.get(t, t).replace("\n", " ") for t in TRANSFORM_ORDER]

fig2, ax2 = plt.subplots(figsize=(13, 7))
cmap = matplotlib.colormaps.get_cmap("RdYlGn")
im = ax2.imshow(pivot_arr, cmap=cmap, vmin=0, vmax=100, aspect="auto")

cbar = fig2.colorbar(im, ax=ax2, fraction=0.03, pad=0.04)
cbar.set_label("Retention Rate (%)", fontsize=11)

ax2.set_xticks(range(len(TARGET_TAGS_ORDER)))
ax2.set_xticklabels(tag_labels_short, rotation=35, ha="right", fontsize=10)
ax2.set_yticks(range(len(TRANSFORM_ORDER)))
ax2.set_yticklabels(trans_labels_short, fontsize=10)
ax2.set_title("Figure 2: EXIF Tag Retention Heatmap — Transformation x Tag\n"
              "(ExifTool 13.59 | DF06 Kelompok 6 | Red=0% | Green=100%)",
              fontsize=13, fontweight="bold", pad=15)

for i in range(len(TRANSFORM_ORDER)):
    for j in range(len(TARGET_TAGS_ORDER)):
        val = pivot_arr[i, j]
        color = "white" if val < 50 else "black"
        ax2.text(j, i, f"{int(val)}%", ha="center", va="center",
                 fontsize=11, fontweight="bold", color=color)

fig2.text(0.5, -0.02, "Source: 07_ANALYSIS/tag_results.csv | ExifTool_13.59",
          ha="center", fontsize=9, color="gray", style="italic")
fig2_path = FIG_DIR / "fig2_heatmap_transform_tag.png"
fig2.tight_layout()
fig2.savefig(fig2_path, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig2)
print(f"Figure 2 saved: {fig2_path}")

# ── Figure 3: Parser Agreement / Coverage ─────────────────────────────────────
# Compare ExifTool vs Pillow: count of missing vs unsupported per transform
df_grouped = df.groupby(["transformation", "tool", "status"]).size().reset_index(name="count")

fig3, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax_idx, (tool, tool_label) in enumerate([("ExifTool_13.59", "ExifTool 13.59"), ("Pillow_12.0.0", "Pillow 12.0.0")]):
    sub = df_grouped[df_grouped["tool"] == tool]
    pivot = sub.pivot_table(index="transformation", columns="status", values="count", fill_value=0)
    pivot = pivot.reindex(TRANSFORM_ORDER)

    statuses = [s for s in ["retained", "changed", "missing", "unsupported"] if s in pivot.columns]
    colors_map = {"retained": "#27ae60", "changed": "#f39c12", "missing": "#e74c3c", "unsupported": "#95a5a6"}

    bottom = np.zeros(len(TRANSFORM_ORDER))
    x = np.arange(len(TRANSFORM_ORDER))
    ax = axes[ax_idx]

    for stat in statuses:
        vals = pivot[stat].values if stat in pivot.columns else np.zeros(len(TRANSFORM_ORDER))
        ax.bar(x, vals, bottom=bottom, label=stat.capitalize(), color=colors_map.get(stat, "#bdc3c7"), width=0.6)
        bottom += vals

    ax.set_xticks(x)
    ax.set_xticklabels([TRANSFORM_LABELS.get(t, t).replace("\n", " ") for t in TRANSFORM_ORDER],
                       rotation=35, ha="right", fontsize=9)
    ax.set_ylabel("Tag Count", fontsize=11)
    ax.set_title(f"{tool_label}", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, loc="upper right")
    ax.set_facecolor("#f8f9fa")
    ax.grid(axis="y", alpha=0.3, linestyle="--")

fig3.suptitle("Figure 3: Parser Agreement — ExifTool vs Pillow Tag Status Distribution\n"
              "(9 Tags x 30 Files per Transformation | DF06 Kelompok 6)",
              fontsize=13, fontweight="bold", y=1.02)
fig3.text(0.5, -0.04, "Source: 07_ANALYSIS/tag_results.csv",
          ha="center", fontsize=9, color="gray", style="italic")
fig3_path = FIG_DIR / "fig3_parser_agreement.png"
fig3.tight_layout()
fig3.savefig(fig3_path, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig3)
print(f"Figure 3 saved: {fig3_path}")

# ── Figure 4: File Size Change Distribution ───────────────────────────────────
df_size_pivot = df_size.copy()
df_size_pivot["size_kb"] = df_size_pivot["size_bytes"] / 1024

fig4, ax4 = plt.subplots(figsize=(13, 6))

baseline_sizes_kb = df_size_pivot[df_size_pivot["transformation"] == "original"]["size_kb"].values

all_trans = [t for t in TRANSFORM_ORDER if t in df_size_pivot["transformation"].values]
trans_sizes = [df_size_pivot[df_size_pivot["transformation"] == t]["size_kb"].values for t in all_trans]

data_to_plot = [baseline_sizes_kb] + trans_sizes
labels = ["Baseline\n(Original)"] + [TRANSFORM_LABELS.get(t, t).replace("\n", " ") for t in all_trans]

bp = ax4.boxplot(data_to_plot, patch_artist=True, notch=False,
                 medianprops={"color": "#2c3e50", "linewidth": 2},
                 whiskerprops={"linewidth": 1.5},
                 capprops={"linewidth": 1.5})

box_colors = ["#3498db"] + ["#e74c3c" if t in ("stripped", "screenshot_like", "convert_png", "convert_jpeg")
                              else "#f39c12" for t in all_trans]
for patch, color in zip(bp["boxes"], box_colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax4.set_xticks(range(1, len(labels) + 1))
ax4.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
ax4.set_ylabel("File Size (KB)", fontsize=12)
ax4.set_title("Figure 4: File Size Distribution — Baseline vs Transformed\n"
              "(30 files per condition | DF06 Kelompok 6)",
              fontsize=13, fontweight="bold", pad=15)
ax4.set_facecolor("#f8f9fa")
ax4.grid(axis="y", alpha=0.3, linestyle="--")
fig4.text(0.5, -0.04, "Source: 07_ANALYSIS/file_hash_size.csv",
          ha="center", fontsize=9, color="gray", style="italic")
fig4_path = FIG_DIR / "fig4_filesize_distribution.png"
fig4.tight_layout()
fig4.savefig(fig4_path, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig4)
print(f"Figure 4 saved: {fig4_path}")

print()
print("=" * 70)
print("FASE 10-11-12-13 SELESAI")
print("=" * 70)
print(f"\nOverall Retention Rate (ExifTool): {overall_rate}%")
print(f"Files analyzed: {len(size_rows)}")
print(f"Figures generated: 4 (fig1-fig4 in {FIG_DIR})")
