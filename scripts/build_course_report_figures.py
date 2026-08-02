#!/usr/bin/env python3
"""Build the verified figures used in the English course report.

Figure contract
---------------
Core conclusions:
1. Reported academic difficulty clustered at concrete language, task, and
   assessment interfaces; later rule understanding is a separate construct.
2. Open-text accounts described entry, distance, and mixed experiences through
   multiple, overlapping events rather than one fixed sequence.
3. Support states and support priorities varied, so availability, usefulness,
   unmet desire, and non-need must remain separate.
4. Platform retention, adoption, and perceived functions support repertoire
   expansion, not platform replacement or an identity proxy.
5. The synthesis connects four analytical areas with multidimensional outcomes
   without presenting a causal model.

Archetypes:
- Figures 1--4: quantitative grid.
- Figure 5: schematic-led synthesis.

Backend and export:
- Python / Matplotlib only.
- Editable SVG and vector PDF, plus 300 dpi PNG previews.
- Final width approximately 150 mm for the A4 report text block.

Reviewer risks:
- Denominators vary across closed items, so every mark displays n/N.
- Open-text counts are spontaneous mentions among 26 respondents, not
  prevalence estimates; overlapping themes are labelled as such.
- Recalled early and later-period items are not connected as longitudinal
  change.
- Platform transition states are within-platform classifications and do not
  establish simultaneous cross-platform configurations.
- The final framework is organisational, not causal.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "6a58bbb68d0662ee12b5ab75" / "figures"

BLUE = "#1F4E79"
BLUE_2 = "#4F81BD"
TEAL = "#3A8D8C"
TEAL_LIGHT = "#9BC7C5"
GOLD = "#D6A84B"
ORANGE = "#C9784A"
VIOLET = "#7566A8"
GREY = "#A7ADB4"
GREY_DARK = "#4D5660"
GREY_LIGHT = "#E9EDF1"
BLUE_LIGHT = "#B9CDE3"
ORANGE_LIGHT = "#EDC4B1"
GREY_FILL = "#D8DDE2"
INK = "#263238"


def apply_style() -> None:
    """Apply a restrained, print-safe report style."""
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 8.5,
            "axes.titlesize": 9.5,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 8,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.spines.left": False,
            "axes.linewidth": 0.7,
            "axes.edgecolor": GREY_DARK,
            "xtick.color": GREY_DARK,
            "ytick.color": INK,
            "text.color": INK,
            "axes.labelcolor": INK,
            "legend.frameon": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def export(fig: mpl.figure.Figure, stem: str) -> None:
    """Export editable and preview formats from the same Python figure."""
    FIGURES.mkdir(parents=True, exist_ok=True)
    for suffix, kwargs in (
        (".svg", {}),
        (".pdf", {}),
        (".png", {"dpi": 300}),
    ):
        fig.savefig(
            FIGURES / f"{stem}{suffix}",
            bbox_inches="tight",
            pad_inches=0.08,
            **kwargs,
        )
    plt.close(fig)


def add_panel_label(ax: mpl.axes.Axes, label: str) -> None:
    ax.text(
        -0.02,
        1.04,
        label,
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        va="bottom",
        ha="right",
        color=INK,
    )


def finish_percent_axis(ax: mpl.axes.Axes, xlabel: str) -> None:
    ax.set_xlim(0, 108)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0", "25", "50", "75", "100"])
    ax.set_xlabel(xlabel)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", length=3)
    ax.spines["bottom"].set_color(GREY)


def read_survey_stats() -> pd.DataFrame:
    return pd.read_csv(
        TABLES / "survey_item_statistics.csv", encoding="utf-8-sig"
    )


def positive_n(df: pd.DataFrame, variable: str) -> tuple[int, int]:
    """Return n selecting response 4 or 5 and the valid denominator."""
    rows = df[df["variable_name"].eq(variable)].copy()
    if rows.empty:
        raise KeyError(f"Missing survey variable: {variable}")
    response = rows["response_or_statistic"].astype(str).str.strip()
    n = int(rows.loc[response.isin(["4", "4.0", "5", "5.0"]), "n"].sum())
    valid_values = rows["valid_n"].dropna().astype(int).unique()
    if len(valid_values) != 1:
        raise ValueError(f"Unexpected valid_n values for {variable}: {valid_values}")
    return n, int(valid_values[0])


def barh_with_n(
    ax: mpl.axes.Axes,
    labels: list[str],
    values: list[int],
    denominators: list[int],
    colors: list[str],
    y_positions: np.ndarray | None = None,
) -> None:
    if y_positions is None:
        y_positions = np.arange(len(labels))[::-1]
    percentages = np.array(values) / np.array(denominators) * 100
    ax.barh(
        y_positions,
        percentages,
        height=0.62,
        color=colors,
        edgecolor="white",
        linewidth=0.8,
    )
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels)
    for y, pct, n, denominator in zip(
        y_positions, percentages, values, denominators
    ):
        ax.text(
            min(pct + 1.5, 103),
            y,
            f"{n}/{denominator}",
            va="center",
            ha="left",
            fontsize=7.5,
            fontweight="bold",
            color=INK,
        )


def build_academic_figure() -> None:
    stats = read_survey_stats()

    initial_specs = [
        ("Traditional Chinese", "q5_1_traditional_chinese", BLUE),
        ("Cantonese classroom talk", "q5_1_cantonese_class", BLUE),
        ("English-language materials", "q5_1_english_materials", BLUE),
        ("Group projects", "q5_1_group_project", TEAL),
        ("Oral presentations", "q5_1_presentation", TEAL),
        ("Required answer formats", "q5_1_answer_format", TEAL),
        ("Mixed forms of assessment", "q5_1_assessment_mix", GOLD),
        ("Unstated or assumed rules", "q5_1_hidden_rules", GOLD),
    ]
    later_specs = [
        ("Understood assessment rules", "q5_2_assessment_rules", VIOLET),
        (
            "Distinguished rules from ability",
            "q5_2_distinguish_rules_ability",
            VIOLET,
        ),
    ]

    initial_counts = [positive_n(stats, var) for _, var, _ in initial_specs]
    later_counts = [positive_n(stats, var) for _, var, _ in later_specs]
    assert initial_counts == [
        (23, 32),
        (22, 34),
        (13, 34),
        (23, 34),
        (18, 33),
        (16, 34),
        (22, 35),
        (10, 35),
    ]
    assert later_counts == [(32, 34), (30, 34)]

    fig = plt.figure(figsize=(7.2, 5.0))
    gs = fig.add_gridspec(
        1, 2, width_ratios=[1.75, 1.0], wspace=0.48, left=0.25, right=0.97
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])

    y = np.array([9.0, 8.0, 7.0, 5.3, 4.3, 3.3, 1.6, 0.6])
    barh_with_n(
        ax_a,
        [x[0] for x in initial_specs],
        [x[0] for x in initial_counts],
        [x[1] for x in initial_counts],
        [x[2] for x in initial_specs],
        y_positions=y,
    )
    ax_a.set_ylim(-0.2, 10.2)
    ax_a.text(
        0,
        9.75,
        "LANGUAGE & TEXT",
        color=BLUE,
        fontsize=7.3,
        fontweight="bold",
    )
    ax_a.text(
        0,
        6.05,
        "CLASSROOM TASKS",
        color=TEAL,
        fontsize=7.3,
        fontweight="bold",
    )
    ax_a.text(
        0,
        2.35,
        "ASSESSMENT & EXPECTATIONS",
        color="#9A7225",
        fontsize=7.3,
        fontweight="bold",
    )
    ax_a.set_title(
        "Recalled initial difficulty\n(selecting 4 or 5)", loc="left", pad=18
    )
    finish_percent_axis(ax_a, "Percentage of valid responses")
    add_panel_label(ax_a, "a")

    barh_with_n(
        ax_b,
        [x[0] for x in later_specs],
        [x[0] for x in later_counts],
        [x[1] for x in later_counts],
        [x[2] for x in later_specs],
    )
    ax_b.set_ylim(-1.0, 2.0)
    ax_b.set_title(
        "Recalled later understanding\n(selecting 4 or 5)", loc="left", pad=18
    )
    finish_percent_axis(ax_b, "Percentage of valid responses")
    add_panel_label(ax_b, "b")

    export(fig, "academic_interfaces")


def read_open_text_summary() -> pd.DataFrame:
    return pd.read_csv(
        TABLES / "open_text_theme_summary.csv", encoding="utf-8-sig"
    )


def theme_n(
    df: pd.DataFrame, question: str, counting_basis: str
) -> tuple[int, int]:
    rows = df[
        df["question_id"].eq(question)
        & df["counting_basis"].eq(counting_basis)
    ]
    if len(rows) != 1:
        raise ValueError(
            f"Expected one row for {question}/{counting_basis}; got {len(rows)}"
        )
    row = rows.iloc[0]
    return int(row["unique_respondents"]), int(row["valid_open_text_n"])


def build_peer_open_text_figure() -> None:
    themes = read_open_text_summary()
    directions = [
        ("Entry", "EVENT_DIRECTION=ENTRY", BLUE),
        ("Mixed", "EVENT_DIRECTION=MIXED", GOLD),
        ("Distance", "EVENT_DIRECTION=DISTANCE", VIOLET),
    ]
    events = [
        ("Peer invitation", "OTC02", BLUE),
        ("Shared task", "OTC06", TEAL),
        ("Everyday extension", "OTC12", TEAL_LIGHT),
        ("Local-reference gap", "OTC09", ORANGE),
        ("Spoken-language barrier", "OTC08", GREY_DARK),
    ]
    direction_counts = [theme_n(themes, "Q8.1", code) for _, code, _ in directions]
    event_counts = [theme_n(themes, "Q8.1", code) for _, code, _ in events]
    assert direction_counts == [(16, 26), (6, 26), (4, 26)]
    assert event_counts == [(15, 26), (14, 26), (10, 26), (11, 26), (5, 26)]

    fig = plt.figure(figsize=(7.2, 3.7))
    gs = fig.add_gridspec(
        2,
        1,
        height_ratios=[0.8, 2.2],
        hspace=0.6,
        left=0.25,
        right=0.97,
        top=0.91,
        bottom=0.14,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[1, 0])

    left = 0.0
    for label, (_, denominator), (n, _), color in zip(
        [x[0] for x in directions],
        direction_counts,
        direction_counts,
        [x[2] for x in directions],
    ):
        pct = n / denominator * 100
        ax_a.barh(0, pct, left=left, color=color, height=0.58)
        display_label = (
            f"{label}\n{n}/26" if pct < 20 else f"{label}  {n}/26"
        )
        ax_a.text(
            left + pct / 2,
            0,
            display_label,
            ha="center",
            va="center",
            fontsize=7.6 if pct < 20 else 8,
            linespacing=0.9,
            color="white" if label != "Mixed" else INK,
            fontweight="bold",
        )
        left += pct
    ax_a.set_xlim(0, 100)
    ax_a.set_ylim(-0.65, 0.65)
    ax_a.set_yticks([])
    ax_a.set_xticks([])
    ax_a.spines["bottom"].set_visible(False)
    ax_a.set_title("Focal direction of the Q8.1 account", loc="left", pad=8)
    add_panel_label(ax_a, "a")

    barh_with_n(
        ax_b,
        [x[0] for x in events],
        [x[0] for x in event_counts],
        [x[1] for x in event_counts],
        [x[2] for x in events],
    )
    ax_b.set_title(
        "Spontaneously mentioned events (themes overlap)", loc="left", pad=8
    )
    finish_percent_axis(ax_b, "Percentage of Q8.1 respondents (n = 26)")
    add_panel_label(ax_b, "b")

    export(fig, "peer_entry_open_text")


def build_support_figure() -> None:
    support = pd.read_csv(
        TABLES / "support_gap_analysis.csv", encoding="utf-8-sig"
    )
    themes = read_open_text_summary()
    support_specs = [
        ("Peer-integration support", "q5_5_peer_buddy_support"),
        (
            "Emotional / anti-exclusion support",
            "q5_5_emotional_anti_exclusion_support",
        ),
    ]
    category_columns = [
        ("Major help", "received_major_help_n", BLUE),
        ("Limited help", "received_limited_help_n", BLUE_LIGHT),
        ("Wanted, not received", "unmet_wanted_n", ORANGE_LIGHT),
        ("Not needed", "not_received_not_needed_n", GREY_FILL),
    ]

    support_rows = []
    for label, variable in support_specs:
        row = support[support["variable_name"].eq(variable)]
        if len(row) != 1:
            raise ValueError(f"Expected one support row for {variable}")
        support_rows.append((label, row.iloc[0]))
    assert [
        (
            int(row["valid_n"]),
            *[int(row[column]) for _, column, _ in category_columns],
        )
        for _, row in support_rows
    ] == [(32, 17, 9, 2, 4), (30, 11, 5, 5, 9)]

    priority_specs = [
        ("Adaptation time", "OTC27", BLUE),
        ("Language / terminology", "OTC31", BLUE_2),
        ("Curriculum bridge", "OTC29", TEAL),
        ("Peer contact", "OTC32", TEAL_LIGHT),
        ("Clearer rule explanations", "OTC30", GOLD),
    ]
    priority_counts = [
        theme_n(themes, "Q8.2", code) for _, code, _ in priority_specs
    ]
    assert priority_counts == [(12, 26), (12, 26), (11, 26), (8, 26), (6, 26)]

    # This figure is designed at the report's final 150 mm text width. Stacking
    # the panels prevents long labels from widening the tight bounding box and
    # keeps all on-page labels above 7 pt.
    fig = plt.figure(figsize=(5.9, 4.8))
    gs = fig.add_gridspec(
        2,
        1,
        height_ratios=[0.9, 1.55],
        hspace=0.72,
        left=0.27,
        right=0.97,
        top=0.88,
        bottom=0.13,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[1, 0])

    y_positions = np.array([1, 0])
    for y, (label, row) in zip(y_positions, support_rows):
        denominator = int(row["valid_n"])
        left = 0.0
        for _, column, color in category_columns:
            n = int(row[column])
            pct = n / denominator * 100
            ax_a.barh(
                y,
                pct,
                left=left,
                height=0.58,
                color=color,
                edgecolor="white",
                linewidth=0.7,
            )
            if pct >= 9:
                ax_a.text(
                    left + pct / 2,
                    y,
                    str(n),
                    ha="center",
                    va="center",
                    fontsize=7.6,
                    fontweight="bold",
                    color="white" if color == BLUE else INK,
                )
            else:
                ax_a.annotate(
                    str(n),
                    xy=(left + pct / 2, y + 0.30),
                    xytext=(left + pct / 2, y + 0.52),
                    ha="center",
                    va="bottom",
                    fontsize=7.5,
                    fontweight="bold",
                    arrowprops={
                        "arrowstyle": "-",
                        "color": GREY_DARK,
                        "lw": 0.6,
                    },
                )
            left += pct
    ax_a.set_yticks(y_positions)
    ax_a.set_yticklabels(
        [f"{label}\n(n = {int(row['valid_n'])})" for label, row in support_rows]
    )
    ax_a.set_xlim(0, 100)
    ax_a.set_xticks([0, 25, 50, 75, 100])
    ax_a.set_xlabel("Percentage within valid responses")
    ax_a.tick_params(axis="y", length=0)
    ax_a.spines["bottom"].set_color(GREY)
    ax_a.set_title("Reported support status", loc="left", pad=27)
    handles = [
        mpl.patches.Patch(facecolor=color, label=label)
        for label, _, color in category_columns
    ]
    ax_a.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0, 1.02),
        ncol=4,
        fontsize=7.0,
        columnspacing=0.8,
        handlelength=1.2,
    )
    add_panel_label(ax_a, "a")

    barh_with_n(
        ax_b,
        [x[0] for x in priority_specs],
        [x[0] for x in priority_counts],
        [x[1] for x in priority_counts],
        [x[2] for x in priority_specs],
    )
    ax_b.set_title(
        "Q8.2 support priorities (spontaneous, overlapping mentions)",
        loc="left",
        pad=10,
    )
    finish_percent_axis(ax_b, "Percentage of Q8.2 respondents (n = 26)")
    add_panel_label(ax_b, "b")

    export(fig, "support_states_and_priorities")


def build_digital_figure() -> None:
    transitions = pd.read_csv(
        TABLES / "exploratory_extension_v2.csv", encoding="utf-8-sig"
    )
    stats = read_survey_stats()
    transition_specs = [
        ("WeChat retained", "PLATFORM_wechat_retained", BLUE),
        ("WeChat stopped", "PLATFORM_wechat_stopped", GREY_DARK),
        ("WhatsApp adopted later", "PLATFORM_whatsapp_adopted", TEAL),
        ("Instagram adopted later", "PLATFORM_instagram_adopted", TEAL_LIGHT),
    ]
    transition_counts: list[tuple[int, int]] = []
    for _, finding_id, _ in transition_specs:
        row = transitions[transitions["finding_id"].eq(finding_id)]
        if len(row) != 1:
            raise ValueError(f"Expected one transition row for {finding_id}")
        transition_counts.append(
            (int(row.iloc[0]["numerator"]), int(row.iloc[0]["denominator"]))
        )
    assert transition_counts == [(26, 35), (6, 35), (26, 35), (22, 35)]

    function_specs = [
        (
            "Separate platforms for\nMainland and HK relationships",
            "q6_5_separate_relations",
            BLUE,
        ),
        (
            "HK-classmate platforms\nfor school information",
            "q6_5_hk_platform_participation",
            BLUE_2,
        ),
        (
            "Older Mainland networks\nfor emotional support",
            "q6_5_old_network_emotional_support",
            TEAL,
        ),
        (
            "Different expression\nacross platforms",
            "q6_5_different_expression",
            TEAL_LIGHT,
        ),
        (
            "Multiple platforms\nserve different purposes",
            "q6_5_multiple_roles",
            GOLD,
        ),
        (
            "Online rules or platforms\ncreated access difficulty",
            "q6_5_online_rule_barrier",
            ORANGE,
        ),
    ]
    function_counts = [
        positive_n(stats, variable) for _, variable, _ in function_specs
    ]
    assert function_counts == [
        (32, 32),
        (30, 30),
        (31, 33),
        (32, 33),
        (28, 30),
        (14, 33),
    ]

    fig = plt.figure(figsize=(7.2, 4.15))
    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=[0.9, 1.45],
        wspace=0.65,
        left=0.20,
        right=0.97,
        top=0.90,
        bottom=0.14,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])

    labels = [x[0] for x in transition_specs]
    values = [x[0] for x in transition_counts]
    denominators = [x[1] for x in transition_counts]
    colors = [x[2] for x in transition_specs]
    y_positions = np.arange(len(labels))[::-1]
    percentages = np.array(values) / np.array(denominators) * 100
    bars = ax_a.barh(
        y_positions,
        percentages,
        height=0.62,
        color=colors,
        edgecolor="white",
        linewidth=0.8,
    )
    ax_a.set_yticks(y_positions)
    ax_a.set_yticklabels(labels)
    for bar, pct, n, denominator, color in zip(
        bars, percentages, values, denominators, colors
    ):
        if pct >= 35:
            text_x = pct - 2.0
            ha = "right"
            text_color = "white" if color not in (TEAL_LIGHT,) else INK
        else:
            text_x = pct + 1.7
            ha = "left"
            text_color = INK
        ax_a.text(
            text_x,
            bar.get_y() + bar.get_height() / 2,
            f"{n}/{denominator}",
            va="center",
            ha=ha,
            fontsize=7.5,
            fontweight="bold",
            color=text_color,
        )
    ax_a.set_title("Within-platform transition states", loc="left", pad=10)
    finish_percent_axis(ax_a, "Percentage of respondents")
    add_panel_label(ax_a, "a")

    barh_with_n(
        ax_b,
        [x[0] for x in function_specs],
        [x[0] for x in function_counts],
        [x[1] for x in function_counts],
        [x[2] for x in function_specs],
    )
    ax_b.set_title(
        "Self-reported platform functions\n(selecting 4 or 5)",
        loc="left",
        pad=10,
    )
    finish_percent_axis(ax_b, "Percentage of valid responses")
    add_panel_label(ax_b, "b")

    export(fig, "digital_repertoire")


def add_box(
    ax: mpl.axes.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    facecolor: str,
    edgecolor: str,
    fontsize: float = 8.2,
) -> FancyBboxPatch:
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=0.9,
        facecolor=facecolor,
        edgecolor=edgecolor,
    )
    ax.add_patch(patch)
    ax.text(
        x + width / 2,
        y + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight="bold",
        color=INK,
    )
    return patch


def build_framework_figure() -> None:
    # The framework is organisational rather than causal. A portrait-leaning
    # canvas gives each layer enough room at the final 150 mm report width.
    fig, ax = plt.subplots(figsize=(5.9, 4.3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    context_box = FancyBboxPatch(
        (0.04, 0.76),
        0.92,
        0.20,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=0.9,
        facecolor=GREY_LIGHT,
        edgecolor=GREY,
    )
    ax.add_patch(context_box)
    ax.text(
        0.5,
        0.91,
        "CONTEXT AND PRIOR RESOURCES",
        ha="center",
        va="center",
        fontsize=8.1,
        fontweight="bold",
        color=INK,
    )
    ax.text(
        0.5,
        0.85,
        "language background · previous schooling · family resources · time",
        ha="center",
        va="center",
        fontsize=7.7,
        color=INK,
    )
    ax.text(
        0.5,
        0.79,
        "school arrangements · personality · existing relationships",
        ha="center",
        va="center",
        fontsize=7.7,
        color=INK,
    )

    domain_specs = [
        (0.04, "Institutional\ndemands", "#DCE8F3", BLUE),
        (0.28, "Relational\nopportunities &\nboundaries", "#DDEEEE", TEAL),
        (0.52, "Usable\nsupport", "#F6E9C9", GOLD),
        (0.76, "Communication\nplatforms", "#E7E2F1", VIOLET),
    ]
    for x, text_value, face, edge in domain_specs:
        add_box(
            ax,
            (x, 0.48),
            0.20,
            0.18,
            text_value,
            face,
            edge,
            fontsize=8.1,
        )

    ax.text(
        0.5,
        0.395,
        "Observed in different combinations; analytical links are not causal arrows",
        ha="center",
        va="center",
        fontsize=7.7,
        color=GREY_DARK,
        style="italic",
    )
    ax.plot(
        [0.11, 0.89],
        [0.35, 0.35],
        color=GREY,
        lw=1.0,
        linestyle=(0, (2.5, 2.5)),
    )

    outcomes = [
        "Rule\nunderstanding",
        "School\nmembership",
        "Access\nto help",
        "Trust",
        "Relationship\ndepth",
    ]
    x_positions = np.linspace(0.04, 0.80, len(outcomes))
    for x, outcome in zip(x_positions, outcomes):
        add_box(
            ax,
            (float(x), 0.11),
            0.16,
            0.15,
            outcome,
            "#F7F8FA",
            GREY,
            fontsize=7.8,
        )
    ax.text(
        0.5,
        0.02,
        "MULTIDIMENSIONAL OUTCOMES",
        ha="center",
        va="bottom",
        fontsize=7.6,
        fontweight="bold",
        color=GREY_DARK,
    )

    export(fig, "integrated_analytical_framework")


def main() -> None:
    apply_style()
    build_academic_figure()
    build_peer_open_text_figure()
    build_support_figure()
    build_digital_figure()
    build_framework_figure()
    print(f"Generated report figures in {FIGURES}")


if __name__ == "__main__":
    main()
