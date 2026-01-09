import plotly.graph_objects as go


def plot_heatmap_matrix(matrix_pcts, matrix_counts, x_labels, y_labels):
    """
    Plots a Heatmap Matrix using Subplots to allow distinct colors for each row.
    
    Args:
        matrix_pcts: 2D list of probabilities (z-axis, color).
        matrix_counts: 2D list of raw counts (for hover).
        x_labels: List of strings for X-axis (Reversal Bins).
        y_labels: List of strings for Y-axis (Impulse Ranges).
    """
    if not matrix_pcts:
        return go.Figure()


    # Prepare text matrix (Count + Probability) for display inside cells
    text_matrix = []
    for i in range(len(matrix_counts)):
        row_text = []
        for j in range(len(matrix_counts[i])):
            count = matrix_counts[i][j]
            pct = matrix_pcts[i][j]
            if count > 0:
                # Format: "5<br>(12.5%)"
                # Using <b> for count to make it pop like the example image
                row_text.append(f"<b>{count}</b><br>({pct:.1f}%)")
            else:
                row_text.append("")
        text_matrix.append(row_text)

    # Risk Matrix Style: Single Grid
    # We use matrix_pcts for the Color (Heat)
    fig = go.Figure(data=go.Heatmap(
        z=matrix_pcts,
        x=x_labels,
        y=y_labels,
        # Custom Colorscale: 0=White (Background), then Green->Yellow->Red
        # We start green immediately after 0 to distinguish "No Data/Zero" from "Low Risk"
        colorscale=[
            [0.0, 'white'],       # 0% = White
            [0.01, '#90EE90'],    # >0% = Light Green
            [0.5, 'yellow'],      # 50% = Yellow
            [1.0, 'red']          # 100% = Red
        ],
        reversescale=False,
        zmin=0, zmax=50,       # Cap at 50% for visibility
        text=text_matrix,
        texttemplate="%{text}",
        customdata=matrix_counts,
        hoverongaps=False,
        hovertemplate='<b>%{y}</b><br>Reversal: %{x}<br>Probability: %{z:.1f}%<br>Count: %{customdata}<extra></extra>'
    ))

    fig.update_layout(
        title="Impulse vs. Reversal Matrix (Count & Probability)",
        xaxis_title="Reversal % Zone",
        yaxis_title="Impulse Range",
        template="plotly_dark",
        height=len(y_labels) * 50 + 200,
        xaxis=dict(side="bottom") # Ensure labels are at bottom
    )

    return fig
