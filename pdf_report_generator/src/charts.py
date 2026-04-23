"""
Generate charts/graphs for embedding in PDF reports.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
from typing import List


COLORS = {
    "student": ["#1565C0", "#1976D2", "#1E88E5", "#42A5F5", "#90CAF9"],
    "company": ["#1B5E20", "#2E7D32", "#388E3C", "#43A047", "#81C784"],
}


def student_grade_pie(records, out_path: str):
    """Pie chart of grade distribution."""
    grade_counts = {}
    for r in records:
        g = r.grade
        grade_counts[g] = grade_counts.get(g, 0) + 1

    labels = list(grade_counts.keys())
    sizes = list(grade_counts.values())
    colors = ["#1565C0", "#1976D2", "#42A5F5", "#90CAF9", "#BBDEFB", "#E3F2FD", "#FF5252"][:len(labels)]

    fig, ax = plt.subplots(figsize=(5, 4), facecolor="white")
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors,
        autopct="%1.0f%%", startangle=140,
        textprops={"fontsize": 11, "fontweight": "bold"},
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(10)
    ax.set_title("Grade Distribution", fontsize=13, fontweight="bold", color="#1a1a2e", pad=12)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches="tight", facecolor="white")
    plt.close()


def student_avg_bar(records, out_path: str):
    """Bar chart of student averages."""
    names = [r.name.split()[0] for r in records]
    avgs = [r.average for r in records]

    cmap = plt.cm.Blues
    bar_colors = [cmap(0.4 + 0.5 * (a - min(avgs)) / (max(avgs) - min(avgs) + 1)) for a in avgs]

    fig, ax = plt.subplots(figsize=(7, 4), facecolor="white")
    bars = ax.bar(names, avgs, color=bar_colors, edgecolor="white", linewidth=0.8, width=0.6)

    for bar, avg in zip(bars, avgs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{avg:.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#333")

    ax.set_ylim(0, 105)
    ax.set_xlabel("Student", fontsize=10, color="#444")
    ax.set_ylabel("Average Score", fontsize=10, color="#444")
    ax.set_title("Student Performance Overview", fontsize=13, fontweight="bold", color="#1a1a2e")
    ax.axhline(y=75, color="#FF5722", linestyle="--", linewidth=1, alpha=0.7, label="Pass Mark (75)")
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", rotation=20)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches="tight", facecolor="white")
    plt.close()


def student_subject_radar(records, out_path: str):
    """Radar chart of average subject scores."""
    subjects = ["Math", "Science", "English", "History", "CS"]
    values = [
        np.mean([r.math for r in records]),
        np.mean([r.science for r in records]),
        np.mean([r.english for r in records]),
        np.mean([r.history for r in records]),
        np.mean([r.cs for r in records]),
    ]

    N = len(subjects)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    values_plot = values + values[:1]

    fig, ax = plt.subplots(figsize=(5, 4), subplot_kw=dict(polar=True), facecolor="white")
    ax.plot(angles, values_plot, "o-", linewidth=2, color="#1565C0")
    ax.fill(angles, values_plot, alpha=0.25, color="#42A5F5")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(subjects, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=7)
    ax.set_title("Subject Average Scores", fontsize=12, fontweight="bold", color="#1a1a2e", pad=18)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches="tight", facecolor="white")
    plt.close()


def employee_perf_bar(records, out_path: str):
    """Bar chart of employee performance scores."""
    names = [r.name.split()[0] for r in records]
    scores = [r.performance_score for r in records]

    cmap = plt.cm.Greens
    bar_colors = [cmap(0.3 + 0.5 * s / 5) for s in scores]

    fig, ax = plt.subplots(figsize=(7, 4), facecolor="white")
    bars = ax.bar(names, scores, color=bar_colors, edgecolor="white", linewidth=0.8, width=0.6)

    for bar, s in zip(bars, scores):
        label = {5: "Outstanding", 4: "Excellent", 3: "Good", 2: "Average", 1: "Poor"}.get(s, "")
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                label, ha="center", va="bottom", fontsize=7, color="#333")

    ax.set_ylim(0, 6)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["Poor", "Average", "Good", "Excellent", "Outstanding"], fontsize=8)
    ax.set_xlabel("Employee", fontsize=10, color="#444")
    ax.set_title("Employee Performance Ratings", fontsize=13, fontweight="bold", color="#1a1a2e")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", rotation=20)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches="tight", facecolor="white")
    plt.close()


def employee_dept_pie(records, out_path: str):
    """Pie chart of department distribution."""
    dept_counts = {}
    for r in records:
        dept_counts[r.department] = dept_counts.get(r.department, 0) + 1

    labels = list(dept_counts.keys())
    sizes = list(dept_counts.values())
    colors = ["#1B5E20", "#2E7D32", "#388E3C", "#43A047", "#66BB6A", "#A5D6A7"][:len(labels)]

    fig, ax = plt.subplots(figsize=(5, 4), facecolor="white")
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors,
        autopct="%1.0f%%", startangle=140,
        textprops={"fontsize": 9, "fontweight": "bold"},
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(9)
    ax.set_title("Department Distribution", fontsize=13, fontweight="bold", color="#1a1a2e", pad=12)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches="tight", facecolor="white")
    plt.close()


def employee_salary_bar(records, out_path: str):
    """Horizontal bar chart of salaries."""
    names = [r.name.split()[0] for r in records]
    salaries = [r.salary / 1000 for r in records]

    cmap = plt.cm.Greens
    bar_colors = [cmap(0.4 + 0.4 * s / max(salaries)) for s in salaries]

    fig, ax = plt.subplots(figsize=(6, 4), facecolor="white")
    bars = ax.barh(names, salaries, color=bar_colors, edgecolor="white", height=0.6)

    for bar, sal in zip(bars, salaries):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"PKR {sal:.0f}K", va="center", fontsize=8, color="#333")

    ax.set_xlabel("Salary (PKR Thousands)", fontsize=10, color="#444")
    ax.set_title("Employee Salary Overview", fontsize=13, fontweight="bold", color="#1a1a2e")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(0, max(salaries) * 1.25)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches="tight", facecolor="white")
    plt.close()
