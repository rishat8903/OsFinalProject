"""
Gantt chart visualization module for CPU scheduling simulations.
Generates an interactive, dark-themed Gantt chart using Plotly.
"""

import plotly.graph_objects as go

# --- Color Scheme & Layout Config ---

COLOR_PALETTE = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
    "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52"
]


def _get_color_mapping(timeline: list[tuple]) -> dict[str, str]:
    """
    Creates a consistent mapping from PIDs to colors.
    Sorting the PIDs guarantees that the same PID always maps to the same color
    regardless of the scheduling algorithm used.

    Parameters:
        timeline (list[tuple]): List of (pid, start, end) tuples.

    Returns:
        dict[str, str]: Dictionary mapping PID to a hex color code.
    """
    unique_pids = sorted(
        list(set(pid for pid, _, _ in timeline)),
        key=lambda x: (len(str(x)), str(x))
    )
    return {pid: COLOR_PALETTE[idx % len(COLOR_PALETTE)] for idx, pid in enumerate(unique_pids)}


def plot_gantt(timeline: list[tuple], title: str) -> go.Figure:
    """
    Plots a horizontal bar chart representing the scheduling timeline (Gantt chart).

    Parameters:
        timeline (list[tuple]): List of (pid, start, end) tuples representing execution blocks.
        title (str): Title of the Gantt chart.

    Returns:
        go.Figure: A Plotly Figure representing the Gantt chart.
    """
    fig = go.Figure()

    if not timeline:
        fig.update_layout(
            title=title,
            template="plotly_dark",
            paper_bgcolor="#1e1e1e",
            plot_bgcolor="#1e1e1e",
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[{
                "text": "No timeline data available",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16}
            }]
        )
        return fig

    # Get consistent color mappings
    color_map = _get_color_mapping(timeline)

    # Track which PIDs have already been added to the legend
    legend_added = set()

    for pid, start, end in timeline:
        duration = round(end - start, 2)
        color = color_map[pid]

        # Show in legend only once per PID
        show_legend = pid not in legend_added
        legend_added.add(pid)

        fig.add_trace(
            go.Bar(
                y=[pid],
                x=[duration],
                base=[start],
                orientation="h",
                marker=dict(
                    color=color,
                    line=dict(color="#1e1e1e", width=1.5)
                ),
                name=pid,
                text=f"{pid} ({duration})",
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="white", size=11, family="Inter, sans-serif"),
                hoverinfo="text",
                hovertext=(
                    f"<b>Process {pid}</b><br>"
                    f"Start Time: {start:.2f}<br>"
                    f"End Time: {end:.2f}<br>"
                    f"Execution Duration: {duration:.2f} units"
                ),
                showlegend=show_legend,
                legendgroup=pid
            )
        )

    # Determine dynamic x-axis gridline ticks
    max_time = max(end for _, _, end in timeline)
    if max_time <= 30:
        dtick = 1.0
    elif max_time <= 100:
        dtick = 5.0
    else:
        dtick = 10.0

    # Ensure y-axis ordering puts PID 1/A at the top of the chart
    unique_pids = sorted(
        list(set(pid for pid, _, _ in timeline)),
        key=lambda x: (len(str(x)), str(x)),
        reverse=True
    )

    # Build xaxis and yaxis title dicts (compatible with Plotly 5.15+ and 6.x)
    xaxis_title = dict(
        text="Time Units",
        font=dict(size=13, color="#bbbbbb", family="Inter, sans-serif")
    )
    yaxis_title = dict(
        text="Process ID",
        font=dict(size=13, color="#bbbbbb", family="Inter, sans-serif")
    )

    fig.update_layout(
        title={
            "text": title,
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": {"size": 18, "family": "Outfit, sans-serif", "color": "#FFFFFF"}
        },
        barmode="stack",
        template="plotly_dark",
        paper_bgcolor="#111111",
        plot_bgcolor="#111111",
        xaxis=dict(
            title=xaxis_title,
            showgrid=True,
            gridcolor="#2c2c2c",
            dtick=dtick,
            tickfont=dict(color="#bbbbbb"),
            zeroline=True,
            zerolinecolor="#444444"
        ),
        yaxis=dict(
            title=yaxis_title,
            categoryorder="array",
            categoryarray=unique_pids,
            tickfont=dict(color="#bbbbbb")
        ),
        height=320 + (30 * len(unique_pids)),
        margin=dict(l=60, r=30, t=70, b=50),
        legend=dict(
            title=dict(text="Processes"),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#bbbbbb")
        ),
        hoverlabel=dict(
            bgcolor="#222222",
            font=dict(size=12, family="Inter, sans-serif")
        )
    )

    return fig
