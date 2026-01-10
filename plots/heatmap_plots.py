import plotly.graph_objects as go


def plot_heatmap_matrix(matrix_pcts, matrix_counts, matrix_atrs, x_labels, y_labels, title_suffix=""):
    """
    Plots a Heatmap Matrix using Subplots to allow distinct colors for each row.
    
    Args:
        matrix_pcts: 2D list of probabilities (z-axis, color).
        matrix_counts: 2D list of raw counts (for hover).
        matrix_atrs: 2D list of Avg ATRs (for display).
        x_labels: List of strings for X-axis (Reversal Bins).
        y_labels: List of strings for Y-axis (Impulse Ranges).
        title_suffix: Optional string to append to chart title (e.g. " - LONDON Session")
    """
    if not matrix_pcts:
        return go.Figure()


    # Prepare text matrix (Count + Probability + ATR) for display inside cells
    text_matrix = []
    # Combine counts and atrs for customdata
    custom_data = [] 
    
    for i in range(len(matrix_counts)):
        row_text = []
        row_custom = []
        for j in range(len(matrix_counts[i])):
            count = matrix_counts[i][j]
            pct = matrix_pcts[i][j]
            atr = matrix_atrs[i][j]
            
            # Pack custom data: [count, atr]
            row_custom.append([count, atr])
            
            if count > 0:
                # Format: "5<br>(12.5%)<br>ATR: 10"
                row_text.append(f"<b>{count}</b><br>({pct:.1f}%)<br><span style='font-size:10px; color: grey'>ATR:{atr:.1f}</span>")
            else:
                row_text.append("")
        text_matrix.append(row_text)
        custom_data.append(row_custom)

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
        customdata=custom_data,
        hoverongaps=False,
        hovertemplate='<b>%{y}</b><br>Reversal: %{x}<br>Probability: %{z:.1f}%<br>Count: %{customdata[0]}<br>Avg ATR: %{customdata[1]:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title=f"Impulse vs. Reversal Matrix{title_suffix}",
        xaxis_title="Reversal % Zone",
        yaxis_title="Impulse Range",
        template="plotly_dark",
        height=len(y_labels) * 50 + 200,
        xaxis=dict(side="bottom") # Ensure labels are at bottom
    )

    return fig

def plot_heatmap_3d(matrix_pcts, x_labels, y_labels, title_suffix=""):
    """
    Plots a 3D Surface Chart of the Heatmap.
    """
    if not matrix_pcts:
        return go.Figure()

    # In 3D Surface, Z is the height (Probabilities)
    # X and Y are the labels
    
    fig = go.Figure(data=[go.Surface(
        z=matrix_pcts,
        x=x_labels, 
        y=y_labels,
        colorscale='Viridis', # 3D usually looks better with Viridis/Plasma
        showscale=True,
        colorbar=dict(title='Probability %'),
        contours_z=dict(show=True, usecolormap=True, highlightcolor="limegreen", project_z=True)
    )])

    fig.update_layout(
        title=f"3D Topography: Impulse vs Reversal{title_suffix}",
        scene=dict(
            xaxis_title="Reversal %",
            yaxis_title="Impulse Range",
            zaxis_title="Probability %"
        ),
        template="plotly_dark",
        height=700,
        margin=dict(l=0, r=0, b=0, t=40)
    )
    
    return fig
