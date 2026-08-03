#!/usr/bin/env python3
"""Build the verified figures used in the English course report.

Figure contract
---------------
Core conclusions:
1. The three linked evidence layers have different coverage and analytical
   roles; they are complementary rather than an attrition funnel.
2. Reported academic difficulty clustered at concrete language, task, and
   assessment interfaces; later rule understanding is a separate construct.
3. Recalled early peer boundaries and recalled later belonging indicators were
   both present, but they measure different constructs and periods.
4. Open-text accounts described entry, distance, and mixed experiences through
   multiple, overlapping events rather than one fixed sequence.
5. Support states and support priorities varied, so availability, usefulness,
   unmet desire, and non-need must remain separate.
6. Platform retention, adoption, and perceived functions support repertoire
   expansion, not platform replacement or an identity proxy.
7. The synthesis connects three primary analytical areas and one supplementary
   communication channel with multidimensional outcomes, without presenting a
   causal model.

Archetypes:
- Method map and final framework: schematic-led synthesis.
- Empirical figures: quantitative grid.

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
- The method map uses parallel evidence layers, not a sample-attrition funnel;
  literature is interpretive context rather than participant evidence.
- Platform transition states are within-platform classifications and do not
  establish simultaneous cross-platform configurations.
- Digital communication is supplementary in the final framework.
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


def add_panel_header(
    ax: mpl.axes.Axes,
    label: str,
    title: str,
    color: str,
    *,
    y: float = 1.08,
    title_x: float = 0.075,
    fontsize: float = 9.4,
) -> None:
    """Add a compact, aligned panel tag and heading above an axis."""
    ax.text(
        0.0,
        y,
        label,
        transform=ax.transAxes,
        fontsize=7.2,
        fontweight="bold",
        va="center",
        ha="left",
        color="white",
        clip_on=False,
        bbox={
            "boxstyle": "round,pad=0.24,rounding_size=0.12",
            "facecolor": color,
            "edgecolor": color,
            "linewidth": 0,
        },
    )
    ax.text(
        title_x,
        y,
        title,
        transform=ax.transAxes,
        fontsize=fontsize,
        fontweight="semibold",
        va="center",
        ha="left",
        color=INK,
        linespacing=1.05,
        clip_on=False,
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


def build_public_sample_profile_table() -> None:
    """Create a grouped, public-safe sample table from the cleaned survey."""
    survey = pd.read_csv(
        ROOT / "data" / "processed" / "survey_clean.csv",
        encoding="utf-8-sig",
    )
    if len(survey) != 35:
        raise ValueError(f"Expected 35 cleaned records; got {len(survey)}")

    specifications = [
        (
            "First Hong Kong school entry grade",
            "Primary 4–6",
            "q1_3_entry_grade",
            {"小学四年级", "小学五年级", "小学六年级"},
            False,
        ),
        (
            "First Hong Kong school entry grade",
            "Secondary 1–3",
            "q1_3_entry_grade",
            {"中学一年级", "中学二年级", "中学三年级"},
            False,
        ),
        (
            "First Hong Kong school entry grade",
            "Secondary 4–6 or other",
            "q1_3_entry_grade",
            {"中学四年级", "中学五年级", "中学六年级", "其他"},
            False,
        ),
        (
            "Time in Hong Kong local schools",
            "Less than 2 years",
            "q2_5_hk_school_duration",
            {"不足1年", "1年至不足2年"},
            False,
        ),
        (
            "Time in Hong Kong local schools",
            "2 to less than 3 years",
            "q2_5_hk_school_duration",
            {"2年至不足3年"},
            False,
        ),
        (
            "Time in Hong Kong local schools",
            "3 to less than 5 years",
            "q2_5_hk_school_duration",
            {"3年至不足5年"},
            False,
        ),
        (
            "Time in Hong Kong local schools",
            "5 years or more",
            "q2_5_hk_school_duration",
            {"5年或以上"},
            False,
        ),
        (
            "School attended for longest",
            "Aided school",
            "q2_7_school_type",
            {"资助学校"},
            False,
        ),
        (
            "School attended for longest",
            "Direct Subsidy Scheme school",
            "q2_7_school_type",
            {"直接资助计划学校"},
            False,
        ),
        (
            "School attended for longest",
            "Government school",
            "q2_7_school_type",
            {"官立学校"},
            False,
        ),
        (
            "School attended for longest",
            "Private or unknown",
            "q2_7_school_type",
            {"私立本地学校", "不知道"},
            False,
        ),
        (
            "Teaching language (multiple response)",
            "Cantonese",
            "q2_8_language_cantonese",
            {"选择"},
            True,
        ),
        (
            "Teaching language (multiple response)",
            "English",
            "q2_8_language_english",
            {"选择"},
            True,
        ),
        (
            "Teaching language (multiple response)",
            "Mixed or other classroom language",
            "q2_8_language_mixed",
            {"选择"},
            True,
        ),
        (
            "Teaching language (multiple response)",
            "Putonghua",
            "q2_8_language_mandarin",
            {"选择"},
            True,
        ),
    ]

    rows = []
    for dimension, category, variable, accepted, multiple_response in specifications:
        n = int(survey[variable].isin(accepted).sum())
        rows.append(
            {
                "dimension": dimension,
                "category": category,
                "n": n,
                "denominator": 35,
                "percentage": round(n / 35 * 100, 1),
                "multiple_response": multiple_response,
                "privacy_note": "Categories grouped so no displayed cell is below 3.",
            }
        )

    profile = pd.DataFrame(rows)
    expected = [6, 13, 16, 3, 12, 12, 8, 14, 10, 7, 4, 30, 26, 14, 11]
    if profile["n"].tolist() != expected:
        raise ValueError(
            "Unexpected grouped sample counts: "
            f"{profile['n'].tolist()} (expected {expected})"
        )
    profile.to_csv(
        TABLES / "course_report_sample_profile.csv",
        index=False,
        encoding="utf-8-sig",
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
    height: float = 0.62,
) -> None:
    if y_positions is None:
        y_positions = np.arange(len(labels))[::-1]
    percentages = np.array(values) / np.array(denominators) * 100
    ax.barh(
        y_positions,
        percentages,
        height=height,
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


def build_method_evidence_map() -> None:
    """Show parallel evidence layers and their non-substitutable roles."""
    fig, ax = plt.subplots(figsize=(7.2, 3.55))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5,
        0.955,
        "LINKED MIXED-METHOD EVIDENCE",
        ha="center",
        va="center",
        fontsize=9.2,
        fontweight="bold",
        color=BLUE,
    )
    ax.text(
        0.5,
        0.905,
        "Parallel evidence layers with different coverage and analytical roles",
        ha="center",
        va="center",
        fontsize=7.8,
        color=GREY_DARK,
    )

    boxes = [
        {
            "x": 0.035,
            "title": "CLOSED QUESTIONNAIRE",
            "n": "n = 35",
            "role": "Sample\ndistributions",
            "scope": "RQ1 · RQ2 · RQ3",
            "note": "Item denominator\nvaries",
            "face": "#EDF4F8",
            "edge": BLUE,
        },
        {
            "x": 0.355,
            "title": "OPEN TEXT",
            "n": "Q8.1 n = 26\nQ8.2 n = 26",
            "role": "Events & support\npriorities",
            "scope": "RQ1 · RQ2  |  RQ3 sparse",
            "note": "Spontaneous,\nnot prevalence",
            "face": "#EAF4F3",
            "edge": TEAL,
        },
        {
            "x": 0.675,
            "title": "LINKED INTERVIEWS",
            "n": "n = 3",
            "role": "Case process, context\n& divergence",
            "scope": "RQ1 · RQ2  |  RQ3 sparse",
            "note": "Case depth,\nnot representation",
            "face": "#FBF5E7",
            "edge": GOLD,
        },
    ]

    box_width = 0.29
    box_y = 0.33
    box_height = 0.41
    for spec in boxes:
        patch = FancyBboxPatch(
            (spec["x"], box_y),
            box_width,
            box_height,
            boxstyle="round,pad=0.012,rounding_size=0.018",
            linewidth=0.9,
            facecolor=spec["face"],
            edgecolor=spec["edge"],
        )
        ax.add_patch(patch)
        centre_x = spec["x"] + box_width / 2
        ax.text(
            centre_x,
            0.695,
            spec["title"],
            ha="center",
            va="center",
            fontsize=7.1,
            fontweight="bold",
            color=spec["edge"],
        )
        ax.text(
            centre_x,
            0.61,
            spec["n"],
            ha="center",
            va="center",
            fontsize=8.7,
            fontweight="bold",
            color=INK,
        )
        ax.text(
            centre_x,
            0.515,
            spec["role"],
            ha="center",
            va="center",
            fontsize=7.5,
            fontweight="bold",
            color=INK,
        )
        ax.text(
            centre_x,
            0.425,
            spec["scope"],
            ha="center",
            va="center",
            fontsize=7.0,
            color=GREY_DARK,
        )
        ax.text(
            centre_x,
            0.355,
            spec["note"],
            ha="center",
            va="center",
            fontsize=6.8,
            color=GREY_DARK,
            style="italic",
        )

    # A shared bracket denotes record linkage without depicting attrition.
    ax.plot([0.18, 0.82], [0.785, 0.785], color=GREY, lw=0.9)
    for x in (0.18, 0.50, 0.82):
        ax.plot([x, x], [0.765, 0.805], color=GREY, lw=0.9)
    ax.text(
        0.5,
        0.815,
        "participant-level linkage where available",
        ha="center",
        va="bottom",
        fontsize=6.9,
        color=GREY_DARK,
    )

    literature = FancyBboxPatch(
        (0.13, 0.135),
        0.74,
        0.13,
        boxstyle="round,pad=0.010,rounding_size=0.015",
        linewidth=0.9,
        linestyle=(0, (3, 2)),
        facecolor="#F7F8FA",
        edgecolor=GREY,
    )
    ax.add_patch(literature)
    ax.text(
        0.5,
        0.215,
        "LITERATURE CONTEXT",
        ha="center",
        va="center",
        fontsize=7.4,
        fontweight="bold",
        color=GREY_DARK,
    )
    ax.text(
        0.5,
        0.165,
        "Frames interpretation and comparison; it is not evidence about current participants",
        ha="center",
        va="center",
        fontsize=7.2,
        color=INK,
    )
    ax.text(
        0.5,
        0.045,
        "Source-specific analysis  ·  cross-source integration  ·  traceability and privacy checks",
        ha="center",
        va="center",
        fontsize=7.3,
        fontweight="bold",
        color=VIOLET,
    )

    export(fig, "linked_evidence_map")


def build_peer_closed_figure() -> None:
    """Contrast early boundary and later belonging distributions without change arrows."""
    stats = read_survey_stats()
    early_specs = [
        (
            "Local-reference barrier",
            "q3_1_local_knowledge_barrier",
            ORANGE,
        ),
        (
            "Language / humour barrier",
            "q3_1_language_humour_barrier",
            ORANGE_LIGHT,
        ),
        (
            "Participation withdrawal",
            "q3_1_self_withdrawal",
            GREY_DARK,
        ),
    ]
    later_specs = [
        (
            "School / class membership",
            "q3_3_member",
            TEAL,
        ),
        (
            "Trust-and-confiding item¹",
            "q3_3_trusted_peer",
            GREY,
        ),
    ]
    early_counts = [positive_n(stats, variable) for _, variable, _ in early_specs]
    later_counts = [positive_n(stats, variable) for _, variable, _ in later_specs]
    assert early_counts == [(14, 35), (5, 31), (11, 33)]
    assert later_counts == [(30, 33), (35, 35)]

    # Draw at the report's final 150 mm width so the smallest printed labels
    # remain at or above approximately 7 pt.
    fig = plt.figure(figsize=(5.9, 2.85))
    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=[1.1, 0.9],
        wspace=0.62,
        left=0.27,
        right=0.97,
        top=0.78,
        bottom=0.22,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])

    barh_with_n(
        ax_a,
        [x[0] for x in early_specs],
        [x[0] for x in early_counts],
        [x[1] for x in early_counts],
        [x[2] for x in early_specs],
    )
    add_panel_header(
        ax_a,
        "a",
        "Recalled first three months\n(often or very often)",
        ORANGE,
        y=1.13,
        title_x=0.09,
        fontsize=9.0,
    )
    finish_percent_axis(ax_a, "Percentage of valid responses")

    barh_with_n(
        ax_b,
        [x[0] for x in later_specs],
        [x[0] for x in later_counts],
        [x[1] for x in later_counts],
        [x[2] for x in later_specs],
    )
    add_panel_header(
        ax_b,
        "b",
        "Recalled later period\n(selecting 4 or 5)",
        TEAL,
        y=1.13,
        title_x=0.10,
        fontsize=9.0,
    )
    finish_percent_axis(ax_b, "Percentage of valid responses")

    fig.text(
        0.5,
        0.045,
        "¹ Composite item combining trust and confiding; not equivalent to a verified close friendship.",
        ha="center",
        va="center",
        fontsize=7.0,
        color=GREY_DARK,
        style="italic",
    )
    export(fig, "peer_boundaries_belonging")


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
        ("Understood assessment\nrules", "q5_2_assessment_rules", VIOLET),
        (
            "Distinguished rules\nfrom ability",
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

    # The unequal item counts make a stacked composition more legible than two
    # side-by-side axes. Both panels therefore use the full final report width.
    fig = plt.figure(figsize=(5.9, 5.15))
    gs = fig.add_gridspec(
        2,
        1,
        height_ratios=[3.8, 1.25],
        hspace=0.72,
        left=0.33,
        right=0.97,
        top=0.91,
        bottom=0.10,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[1, 0])

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
    add_panel_header(
        ax_a,
        "a",
        "Recalled initial difficulty\n(selecting 4 or 5)",
        BLUE,
        y=1.09,
        title_x=0.065,
        fontsize=9.2,
    )
    finish_percent_axis(ax_a, "Percentage of valid responses")

    barh_with_n(
        ax_b,
        [x[0] for x in later_specs],
        [x[0] for x in later_counts],
        [x[1] for x in later_counts],
        [x[2] for x in later_specs],
        y_positions=np.array([0.70, 0.20]),
        height=0.22,
    )
    ax_b.set_ylim(-0.02, 0.92)
    add_panel_header(
        ax_b,
        "b",
        "Recalled later understanding\n(selecting 4 or 5)",
        VIOLET,
        y=1.24,
        title_x=0.065,
        fontsize=9.2,
    )
    finish_percent_axis(ax_b, "Percentage of valid responses")

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

    fig = plt.figure(figsize=(5.9, 3.25))
    gs = fig.add_gridspec(
        2,
        1,
        height_ratios=[0.65, 2.2],
        hspace=0.40,
        left=0.30,
        right=0.97,
        top=0.89,
        bottom=0.15,
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
    add_panel_header(
        ax_a,
        "a",
        "Focal direction of the Q8.1 account",
        BLUE,
        y=1.25,
        title_x=0.055,
        fontsize=9.2,
    )

    barh_with_n(
        ax_b,
        [x[0] for x in events],
        [x[0] for x in event_counts],
        [x[1] for x in event_counts],
        [x[2] for x in events],
    )
    add_panel_header(
        ax_b,
        "b",
        "Spontaneously mentioned events (themes overlap)",
        TEAL,
        y=1.09,
        title_x=0.055,
        fontsize=9.2,
    )
    finish_percent_axis(ax_b, "Percentage of Q8.1 respondents (n = 26)")

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
    fig = plt.figure(figsize=(5.9, 4.45))
    gs = fig.add_gridspec(
        2,
        1,
        height_ratios=[0.9, 1.55],
        hspace=0.54,
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
    add_panel_header(
        ax_a,
        "a",
        "Reported support status",
        BLUE,
        y=1.34,
        title_x=0.055,
        fontsize=9.2,
    )
    handles = [
        mpl.patches.Patch(facecolor=color, label=label)
        for label, _, color in category_columns
    ]
    ax_a.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0, 1.04),
        ncol=4,
        fontsize=7.0,
        columnspacing=0.8,
        handlelength=1.2,
    )
    barh_with_n(
        ax_b,
        [x[0] for x in priority_specs],
        [x[0] for x in priority_counts],
        [x[1] for x in priority_counts],
        [x[2] for x in priority_specs],
    )
    add_panel_header(
        ax_b,
        "b",
        "Q8.2 support priorities (spontaneous, overlapping mentions)",
        TEAL,
        y=1.10,
        title_x=0.055,
        fontsize=9.2,
    )
    finish_percent_axis(ax_b, "Percentage of Q8.2 respondents (n = 26)")

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
            "#6FAAA7",
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

    # Stack the panels at final report width so long labels remain readable and
    # the two evidence types are not mistaken for person-level pairings.
    fig = plt.figure(figsize=(5.9, 5.25))
    gs = fig.add_gridspec(
        2,
        1,
        height_ratios=[1.25, 2.0],
        hspace=0.58,
        left=0.35,
        right=0.97,
        top=0.91,
        bottom=0.10,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[1, 0])

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
    add_panel_header(
        ax_a,
        "a",
        "Within-platform transition states",
        BLUE,
        y=1.10,
        title_x=0.065,
        fontsize=9.0,
    )
    finish_percent_axis(ax_a, "Percentage of respondents")

    barh_with_n(
        ax_b,
        [x[0] for x in function_specs],
        [x[0] for x in function_counts],
        [x[1] for x in function_counts],
        [x[2] for x in function_specs],
    )
    add_panel_header(
        ax_b,
        "b",
        "Self-reported platform functions\n(selecting 4 or 5)",
        TEAL,
        y=1.10,
        title_x=0.065,
        fontsize=9.0,
    )
    finish_percent_axis(ax_b, "Percentage of valid responses")

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
    linewidth: float = 0.9,
    linestyle: str | tuple[int, tuple[float, ...]] = "solid",
) -> FancyBboxPatch:
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=linewidth,
        linestyle=linestyle,
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
    fig, ax = plt.subplots(figsize=(5.9, 4.55))
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
        (0.06, "Institutional\ndemands", "#DCE8F3", BLUE),
        (0.375, "Relational\nopportunities\n& boundaries", "#DDEEEE", TEAL),
        (0.69, "Usable\nsupport", "#F6E9C9", GOLD),
    ]
    for x, text_value, face, edge in domain_specs:
        add_box(
            ax,
            (x, 0.53),
            0.25,
            0.15,
            text_value,
            face,
            edge,
            fontsize=8.1,
        )

    add_box(
        ax,
        (0.18, 0.405),
        0.64,
        0.075,
        "Supplementary communication channel:\nplatforms",
        "#F7F5FA",
        VIOLET,
        fontsize=7.2,
        linewidth=0.8,
        linestyle=(0, (3, 2)),
    )
    ax.text(
        0.5,
        0.345,
        "Observed in different combinations; the arrangement is analytical, not causal",
        ha="center",
        va="center",
        fontsize=7.7,
        color=GREY_DARK,
        style="italic",
    )
    ax.plot(
        [0.11, 0.89],
        [0.305, 0.305],
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
            (float(x), 0.09),
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
    build_public_sample_profile_table()
    build_method_evidence_map()
    build_academic_figure()
    build_peer_closed_figure()
    build_peer_open_text_figure()
    build_support_figure()
    build_digital_figure()
    build_framework_figure()
    print(f"Generated report figures in {FIGURES}")


if __name__ == "__main__":
    main()
