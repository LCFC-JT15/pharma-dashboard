# ============================================================
# PHARMA RESEARCH ANALYST DASHBOARD
# Global Drug Development & Clinical Trials Intelligence
# ============================================================
# Built with Streamlit — run with: streamlit run pharma_dashboard.py
# ============================================================

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

# ============================================================
# SECTION 1: PAGE CONFIGURATION
# ============================================================
# Must be the first Streamlit command in the script.
# Sets the browser tab title, layout, and sidebar state.
# ============================================================

st.set_page_config(
    page_title="Pharma Pipeline Intelligence",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SECTION 2: SAMPLE DATA
# ============================================================
# All three datasets in one place.
# When you connect real data, replace these with
# pd.read_excel("your_file.xlsx") calls.
# ============================================================

# ---- Pipeline data (waterfall chart) ----
pipeline_data = pd.DataFrame({
    "Drug":        ["Veltorinib", "Rontuzimab", "Dalvitinib",
                    "Mevoseltib", "Ciptanib", "Zolrafenib", "Arxitinib"],
    "Phase":       ["Phase 3", "Phase 3", "Phase 2",
                    "Phase 2", "Phase 2", "Phase 1", "Phase 1"],
    "TherapyArea": ["Oncology", "Oncology", "Oncology",
                    "CNS", "Rare Disease", "Oncology", "CNS"],
    "Sponsor":     ["Pfizer", "Roche", "Novartis",
                    "AstraZeneca", "Merck", "BMS", "Eli Lilly"],
    "Status":      ["Active", "Active", "Active",
                    "On Hold", "Active", "Terminated", "Active"]
})

# ---- Enrollment data (curve chart) ----
enrollment_data = pd.DataFrame({
    "Month":   ["Jan","Feb","Mar","Apr","May",
                "Jun","Jul","Aug","Sep","Oct"],
    "Planned": [20, 45, 75, 110, 150, 195, 245, 295, 340, 380],
    "Actual":  [18, 38, 60,  85, 112, 140, 165, 190, 215, 238]
})
target_enrollment = 380

# ---- Forest plot data ----
forest_data = pd.DataFrame({
    "Trial":    ["LUMINAR-301\n(Veltorinib + pembro)",
                 "KEYNOTE-189\n(Pembro + chemo)",
                 "IMpower150\n(Atezo + bev + chemo)",
                 "POSEIDON\n(Durva + treme + chemo)",
                 "CheckMate-9LA\n(Nivo + ipi + chemo)"],
    "HR":       [0.58, 0.52, 0.61, 0.63, 0.66],
    "CI_low":   [0.46, 0.43, 0.52, 0.52, 0.55],
    "CI_high":  [0.73, 0.64, 0.72, 0.76, 0.80],
    "N":        [612,  616,  692,  675,  719],
    "Indication": ["1L NSCLC"] * 5
})

# ============================================================
# SECTION 3: SIDEBAR FILTERS
# ============================================================
# st.sidebar places widgets in the collapsible left panel.
# multiselect lets users pick one or many options.
# The selected values are used to filter the dataframes below.
# ============================================================

st.sidebar.title("🔬 Filters")
st.sidebar.markdown("---")

# Therapy area filter
all_areas = sorted(pipeline_data["TherapyArea"].unique())
selected_areas = st.sidebar.multiselect(
    "Therapy Area",
    options=all_areas,
    default=all_areas      # All selected by default
)

# Status filter
all_statuses = sorted(pipeline_data["Status"].unique())
selected_statuses = st.sidebar.multiselect(
    "Trial Status",
    options=all_statuses,
    default=all_statuses
)

# Phase filter
all_phases = ["Phase 1", "Phase 2", "Phase 3"]
selected_phases = st.sidebar.multiselect(
    "Phase",
    options=all_phases,
    default=all_phases
)

st.sidebar.markdown("---")
st.sidebar.caption("Pharma Pipeline Intelligence Dashboard\nData: Q2 2026")

# ---- Apply filters to pipeline data ----
filtered_pipeline = pipeline_data[
    (pipeline_data["TherapyArea"].isin(selected_areas)) &
    (pipeline_data["Status"].isin(selected_statuses)) &
    (pipeline_data["Phase"].isin(selected_phases))
].copy()

# ============================================================
# SECTION 4: DASHBOARD HEADER
# ============================================================

st.title("💊 Pharma Pipeline Intelligence Dashboard")
st.caption("Global Drug Development & Clinical Trials — Q2 2026")

# Summary metric cards — updates automatically with filters
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Assets",    len(filtered_pipeline))
col2.metric("Active Trials",   len(filtered_pipeline[filtered_pipeline["Status"] == "Active"]))
col3.metric("Phase 3 Assets",  len(filtered_pipeline[filtered_pipeline["Phase"] == "Phase 3"]))
col4.metric("Therapy Areas",   filtered_pipeline["TherapyArea"].nunique())

st.markdown("---")

# ============================================================
# SECTION 5: TABS
# ============================================================
# st.tabs creates clickable tab headers.
# Content inside each "with" block appears under that tab.
# ============================================================

tab1, tab2, tab3 = st.tabs([
    "📊 Pipeline Waterfall",
    "📈 Enrollment Tracking",
    "🎯 Competitive Forest Plot"
])

# ============================================================
# TAB 1: PIPELINE WATERFALL
# ============================================================

with tab1:
    st.subheader("Global Pipeline Overview")
    st.caption("Grouped by therapy area · Color coded by trial status · Bar length reflects phase")

    if filtered_pipeline.empty:
        st.warning("No assets match the current filters. Adjust the sidebar filters to display data.")
    else:
        # ---- Sort logic (mirrors the final working version) ----
        therapy_order = {"Oncology": 0, "CNS": 1, "Rare Disease": 2}
        status_order  = {"Active": 2, "On Hold": 1, "Terminated": 0}
        phase_order   = {"Phase 1": 2, "Phase 2": 1, "Phase 3": 0}

        df = filtered_pipeline.copy()
        df["TherapyOrder"] = df["TherapyArea"].map(therapy_order).fillna(99)
        df["StatusOrder"]  = df["Status"].map(status_order).fillna(0)
        df["PhaseOrder"]   = df["Phase"].map(phase_order).fillna(0)
        df = df.sort_values(
            ["TherapyOrder", "StatusOrder", "PhaseOrder"],
            ascending=[False, True, True]
        ).reset_index(drop=True)

        status_color_map = {
            "Active":     "#2E86AB",
            "On Hold":    "#F18F01",
            "Terminated": "#C73E1D"
        }
        phase_width_map = {"Phase 3": 0.85, "Phase 2": 0.60, "Phase 1": 0.35}
        area_bg_colors  = {
            "Oncology":     "#EBF5FB",
            "CNS":          "#F4ECF7",
            "Rare Disease": "#FEF9E7"
        }

        df["Color"]    = df["Status"].map(status_color_map).fillna("#999999")
        df["BarWidth"] = df["Phase"].map(phase_width_map).fillna(0.35)

        fig, ax = plt.subplots(figsize=(13, max(4, len(df) * 0.85)))

        for i, row in df.iterrows():
            ax.barh(i, row["BarWidth"], color=row["Color"],
                    height=0.55, alpha=0.88,
                    edgecolor="white", linewidth=0.8)
            ax.text(0.01, i, row["Drug"], va="center", ha="left",
                    fontsize=10, fontweight="bold", color="white")
            ax.text(0.01, i - 0.18, row["Sponsor"], va="center",
                    ha="left", fontsize=8, color="white", alpha=0.85)
            ax.text(row["BarWidth"] + 0.01, i, row["Phase"],
                    va="center", ha="left", fontsize=8.5, color="#555555")

        # Therapy area group labels and dividers
        for area in df["TherapyArea"].unique():
            area_rows = df[df["TherapyArea"] == area].index
            y_min = area_rows.min() - 0.45
            y_max = area_rows.max() + 0.45
            ax.axhspan(y_min, y_max, xmin=0, xmax=0.065,
                       color=area_bg_colors.get(area, "#F5F5F5"), zorder=0)
            ax.text(-0.005, (y_min + y_max) / 2, area,
                    va="center", ha="right", fontsize=8.5,
                    color="#555555", fontweight="500")

        ax.set_yticks([])
        ax.set_xlim(0, 1.15)
        ax.set_xticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_facecolor("#FAFAFA")
        fig.patch.set_facecolor("white")

        # Legend
        present_statuses = df["Status"].unique()
        legend_handles = [
            mpatches.Patch(color=status_color_map.get(s, "#999999"), label=s)
            for s in present_statuses
        ]
        ax.legend(handles=legend_handles, title="Trial Status",
                  title_fontsize=9, fontsize=9,
                  loc="lower right", framealpha=0.9, edgecolor="#DDDDDD")

        ax.set_title("Global Pipeline — Q2 2026", fontsize=13,
                     fontweight="bold", color="#1A1A2E", pad=12, loc="left")

        plt.tight_layout()
        st.pyplot(fig, dpi=150)
        plt.close()

# ============================================================
# TAB 2: ENROLLMENT TRACKING
# ============================================================

with tab2:
    st.subheader("Trial Enrollment Tracking")
    st.caption("Cumulative actual vs planned enrollment · Gap analysis · Projected completion")

    fig, ax = plt.subplots(figsize=(13, 6))
    x = np.arange(len(enrollment_data))

    ax.plot(x, enrollment_data["Planned"], color="#AAAAAA",
            linewidth=2, linestyle="--", label="Planned enrollment")
    ax.plot(x, enrollment_data["Actual"], color="#2E86AB",
            linewidth=2.5, linestyle="-", label="Actual enrollment",
            marker="o", markersize=6, markerfacecolor="white",
            markeredgecolor="#2E86AB", markeredgewidth=2)
    ax.fill_between(x, enrollment_data["Actual"], enrollment_data["Planned"],
                    where=(enrollment_data["Planned"] >= enrollment_data["Actual"]),
                    color="#C73E1D", alpha=0.12, label="Enrollment deficit")
    ax.axhline(y=target_enrollment, color="#57A773",
               linewidth=1.5, linestyle=":")
    ax.text(len(x) - 0.05, target_enrollment + 6,
            f"Target: {target_enrollment}", ha="right",
            va="bottom", fontsize=9, color="#57A773", fontweight="500")

    # Gap annotation
    final_gap     = enrollment_data["Planned"].iloc[-1] - enrollment_data["Actual"].iloc[-1]
    final_gap_pct = (final_gap / enrollment_data["Planned"].iloc[-1]) * 100
    recent_rate   = (enrollment_data["Actual"].iloc[-1] - enrollment_data["Actual"].iloc[-4]) / 3
    mid_y = (enrollment_data["Planned"].iloc[-1] + enrollment_data["Actual"].iloc[-1]) / 2

    ax.annotate(
        f"Gap: {final_gap} pts\n({final_gap_pct:.0f}% below plan)",
        xy=(x[-1], mid_y),
        xytext=(x[-1] - 1.8, mid_y + 35),
        fontsize=9, color="#C73E1D", fontweight="500",
        arrowprops=dict(arrowstyle="->", color="#C73E1D", lw=1.2)
    )

    # Data point labels
    for i, row in enrollment_data.iterrows():
        ax.text(i, row["Actual"] + 8, str(int(row["Actual"])),
                ha="center", va="bottom", fontsize=8, color="#2E86AB")

    ax.set_xticks(x)
    ax.set_xticklabels(enrollment_data["Month"], fontsize=10)
    ax.set_ylabel("Cumulative Patients Enrolled", fontsize=10, color="#555555")
    ax.set_ylim(0, target_enrollment * 1.15)
    ax.yaxis.grid(True, color="#EEEEEE", linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#DDDDDD")
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("white")
    ax.legend(loc="upper left", fontsize=9,
              framealpha=0.9, edgecolor="#DDDDDD")
    ax.set_title("LUMINAR-301 — Cumulative Enrollment vs Plan",
                 fontsize=13, fontweight="bold",
                 color="#1A1A2E", pad=12, loc="left")

    plt.tight_layout()
    st.pyplot(fig, dpi=150)
    plt.close()

    # Enrollment summary metrics below the chart
    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Current Enrollment",  f"{enrollment_data['Actual'].iloc[-1]} pts")
    m2.metric("Enrollment Gap",      f"{int(final_gap)} pts ({final_gap_pct:.0f}% below plan)")
    m3.metric("Recent Rate",         f"{recent_rate:.0f} pts / month")

# ============================================================
# TAB 3: COMPETITIVE FOREST PLOT
# ============================================================

with tab3:
    st.subheader("Competitive Efficacy Comparison")
    st.caption("PFS hazard ratios with 95% confidence intervals · 1L NSCLC")

    def hr_color(hr):
        if hr < 0.65:   return "#2E86AB"
        elif hr <= 0.75: return "#F18F01"
        else:            return "#C73E1D"

    df_forest = forest_data.copy()
    df_forest["Color"] = df_forest["HR"].apply(hr_color)
    df_forest = df_forest.sort_values("HR", ascending=False).reset_index(drop=True)

    y = np.arange(len(df_forest))

    fig, (ax_table, ax_plot) = plt.subplots(
        1, 2, figsize=(14, 5.5),
        gridspec_kw={"width_ratios": [2.2, 3]}
    )

    # Left panel
    ax_table.set_xlim(0, 1)
    ax_table.set_ylim(-0.5, len(df_forest) - 0.5)
    ax_table.text(0.02, len(df_forest) - 0.15, "Trial",
                  fontsize=9, fontweight="bold", color="#333333", va="bottom")
    ax_table.text(0.82, len(df_forest) - 0.15, "N",
                  fontsize=9, fontweight="bold", color="#333333",
                  va="bottom", ha="center")
    ax_table.axhline(y=len(df_forest) - 0.3, color="#CCCCCC", linewidth=0.8)

    for i, row in df_forest.iterrows():
        if i % 2 == 0:
            ax_table.axhspan(i - 0.45, i + 0.45, color="#F7F7F7", zorder=0)
        ax_table.text(0.02, i, row["Trial"], fontsize=8.5,
                      va="center", ha="left", color="#1A1A2E", linespacing=1.4)
        ax_table.text(0.82, i, f"{row['N']:,}", fontsize=8.5,
                      va="center", ha="center", color="#555555")
    ax_table.axis("off")

    # Right panel
    ax_plot.set_xlim(0.25, 1.05)
    ax_plot.set_ylim(-0.5, len(df_forest) - 0.5)
    ax_plot.axvline(x=1.0, color="#AAAAAA", linewidth=1.2, linestyle="--")
    ax_plot.text(1.01, len(df_forest) - 0.55, "HR = 1.0\n(no effect)",
                 fontsize=7.5, color="#AAAAAA", va="top")

    for i, row in df_forest.iterrows():
        if i % 2 == 0:
            ax_plot.axhspan(i - 0.45, i + 0.45, color="#F7F7F7", zorder=0)
        ax_plot.plot([row["CI_low"], row["CI_high"]], [i, i],
                     color=row["Color"], linewidth=1.8, zorder=3)
        for cap_x in [row["CI_low"], row["CI_high"]]:
            ax_plot.plot([cap_x, cap_x], [i - 0.18, i + 0.18],
                         color=row["Color"], linewidth=1.8, zorder=3)
        ax_plot.scatter(row["HR"], i, s=120, color=row["Color"],
                        marker="D", zorder=4,
                        edgecolors="white", linewidths=0.8)
        ax_plot.text(1.06, i,
                     f"{row['HR']:.2f} ({row['CI_low']:.2f}–{row['CI_high']:.2f})",
                     fontsize=8.5, va="center", ha="left", color="#333333")

    ax_plot.text(1.06, len(df_forest) - 0.15, "HR (95% CI)",
                 fontsize=9, fontweight="bold", color="#333333",
                 va="bottom", ha="left")
    ax_plot.axhline(y=len(df_forest) - 0.3, color="#CCCCCC", linewidth=0.8)
    ax_plot.set_xlabel(
        "Hazard Ratio (95% CI)\n← Favors treatment          Favors control →",
        fontsize=9, color="#555555", labelpad=10)
    ax_plot.set_xticks([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax_plot.set_xticklabels(
        ["0.30","0.40","0.50","0.60","0.70","0.80","0.90","1.00"],
        fontsize=8.5)
    ax_plot.set_yticks([])
    ax_plot.xaxis.grid(True, color="#EEEEEE", linewidth=0.8, zorder=0)
    ax_plot.set_axisbelow(True)
    for spine in ax_plot.spines.values():
        spine.set_visible(False)
    ax_plot.spines["bottom"].set_visible(True)
    ax_plot.spines["bottom"].set_color("#DDDDDD")
    ax_plot.set_facecolor("#FAFAFA")

    legend_handles = [
        mpatches.Patch(color="#2E86AB", label="HR < 0.65  (strong benefit)"),
        mpatches.Patch(color="#F18F01", label="HR 0.65–0.75  (moderate benefit)"),
        mpatches.Patch(color="#C73E1D", label="HR > 0.75  (modest benefit)"),
    ]
    ax_plot.legend(handles=legend_handles, loc="lower left",
                   fontsize=8, framealpha=0.9, edgecolor="#DDDDDD",
                   title="Benefit category", title_fontsize=8)

    fig.suptitle("PFS Hazard Ratio Comparison — 1L NSCLC Trials",
                 fontsize=13, fontweight="bold", color="#1A1A2E",
                 x=0.02, ha="left", y=1.02)

    plt.tight_layout()
    st.pyplot(fig, dpi=150)
    plt.close()