"""
Comparative charts visualization module for CPU scheduling simulations.
Provides highlighted bar charts and normalized radar charts.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- Color Constants ---
WINNER_COLOR = "#00CC96"     # Emerald Green
DEFAULT_COLOR = "#636EFA"    # Soft Blue
DARK_BG_COLOR = "#111111"    # Charcoal Black


def plot_comparison_bar(
    df_compare: pd.DataFrame,
    column_name: str,
    title: str,
    lower_is_better: bool = True
) -> go.Figure:
    """
    Generates a horizontal or vertical bar chart comparing all algorithms for a single metric.
    The best performing algorithm is highlighted in green.

    Parameters:
        df_compare (pd.DataFrame): DataFrame with algorithm names as index and metrics as columns.
        column_name (str): The column name representing the metric to plot.
        title (str): Title of the bar chart.
        lower_is_better (bool): True if lower values represent better performance (e.g. WT, TAT).
                               False if higher values are better (e.g. Throughput, CPU Util).

    Returns:
        go.Figure: A Plotly Figure.
    """
    fig = go.Figure()

    if df_compare.empty or column_name not in df_compare.columns:
        return fig

    # Get algorithm names and metric values
    algos = list(df_compare.index)
    values = [float(val) for val in df_compare[column_name]]

    # Find the winning value
    if lower_is_better:
        best_val = min(values)
    else:
        best_val = max(values)

    # Assign colors based on winner
    colors = []
    for val in values:
        if val == best_val:
            colors.append(WINNER_COLOR)
        else:
            colors.append(DEFAULT_COLOR)

    fig.add_trace(
        go.Bar(
            x=algos,
            y=values,
            marker_color=colors,
            text=[f"{v:.2f}" for v in values],
            textposition="auto",
            textfont=dict(color="white", size=11, family="Inter, sans-serif"),
            hoverinfo="x+y"
        )
    )

    fig.update_layout(
        title={
            "text": title,
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": {"size": 15, "family": "Outfit, sans-serif", "color": "#FFFFFF"}
        },
        template="plotly_dark",
        paper_bgcolor=DARK_BG_COLOR,
        plot_bgcolor=DARK_BG_COLOR,
        xaxis=dict(
            tickfont=dict(color="#bbbbbb", size=11),
            showgrid=False
        ),
        yaxis=dict(
            title=dict(
                text=column_name,
                font=dict(size=12, color="#bbbbbb", family="Inter, sans-serif")
            ),
            tickfont=dict(color="#bbbbbb"),
            showgrid=True,
            gridcolor="#222222"
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        height=280
    )

    return fig


def plot_radar_comparison(df_compare: pd.DataFrame) -> go.Figure:
    """
    Plots a radar (spider) chart comparing the normalized performance of all algorithms.
    Each raw metric is scaled between 0 and 100 where 100 is the best score.

    Metrics included:
    - Waiting Time (Lower = Better)
    - Turnaround Time (Lower = Better)
    - Response Time (Lower = Better)
    - Throughput (Higher = Better)
    - CPU Utilization (Higher = Better)

    Parameters:
        df_compare (pd.DataFrame): DataFrame containing algorithm metrics.

    Returns:
        go.Figure: A Plotly Figure.
    """
    fig = go.Figure()

    if df_compare.empty:
        return fig

    # Metrics definition mapping (Column Name, Lower Is Better)
    metrics_info = [
        ("Avg Waiting Time", True),
        ("Avg Turnaround Time", True),
        ("Avg Response Time", True),
        ("Throughput", False),
        ("CPU Utilization (%)", False)
    ]

    categories = [info[0] for info in metrics_info]

    # Pre-calculate min/max for normalization
    normalization_bounds = {}
    for col, lower_is_better in metrics_info:
        if col in df_compare.columns:
            vals = df_compare[col].astype(float).values
            normalization_bounds[col] = {
                "min": float(np.min(vals)),
                "max": float(np.max(vals))
            }

    # Map each algorithm to a radar trace
    algo_colors = {
        "FCFS": "#636EFA",
        "SJF": "#00CC96",
        "Priority": "#AB63FA",
        "Round Robin": "#FFA15A"
    }

    for algo in df_compare.index:
        scores = []
        for col, lower_is_better in metrics_info:
            if col not in df_compare.columns:
                scores.append(0.0)
                continue

            val = float(df_compare.loc[algo, col])
            bounds = normalization_bounds[col]
            v_min, v_max = bounds["min"], bounds["max"]

            if v_max == v_min:
                score = 100.0
            else:
                if lower_is_better:
                    score = 100.0 * (v_max - val) / (v_max - v_min)
                else:
                    score = 100.0 * (val - v_min) / (v_max - v_min)

            scores.append(round(score, 2))

        # Close the loop on radar chart
        scores.append(scores[0])
        radar_categories = categories + [categories[0]]

        fig.add_trace(
            go.Scatterpolar(
                r=scores,
                theta=radar_categories,
                fill="toself",
                name=algo,
                line=dict(color=algo_colors.get(algo, DEFAULT_COLOR), width=2),
                marker=dict(size=6),
                hoverinfo="name+theta+r"
            )
        )

    fig.update_layout(
        title={
            "text": "Comparative Efficiency Scorecard (Normalized 0-100, Outer is Better)",
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": {"size": 16, "family": "Outfit, sans-serif", "color": "#FFFFFF"}
        },
        template="plotly_dark",
        paper_bgcolor=DARK_BG_COLOR,
        polar=dict(
            bgcolor="#151515",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color="#888888", size=9),
                gridcolor="#2c2c2c"
            ),
            angularaxis=dict(
                tickfont=dict(color="#cccccc", size=10, family="Inter, sans-serif"),
                gridcolor="#2c2c2c"
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(color="#bbbbbb")
        ),
        margin=dict(l=50, r=50, t=80, b=80),
        height=400
    )

    return fig
