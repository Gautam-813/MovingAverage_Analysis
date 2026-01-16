import plotly.graph_objects as go


def plot_heatmap_matrix(matrix_pcts, matrix_counts, matrix_atrs, matrix_total_pcts, x_labels, y_labels, title_suffix=""):
    """
    Plots a Heatmap Matrix with 3rd-line display and Grand Total in title.
    """
    if not matrix_pcts:
        return go.Figure()

    grand_total_n = sum([sum(row) for row in matrix_counts])
    text_matrix = []
    custom_data = [] 
    
    for i in range(len(matrix_counts)):
        row_text = []
        row_custom = []
        for j in range(len(matrix_counts[i])):
            count = matrix_counts[i][j]
            row_pct = matrix_pcts[i][j]
            atr = matrix_atrs[i][j]
            total_pct = matrix_total_pcts[i][j]
            
            row_custom.append([count, atr, total_pct])
            
            if count > 0:
                # 3-Line format: Count, Row %, ATR
                row_text.append(f"<b>N: {count}</b><br>{row_pct:.1f}%<br>ATR: {atr:.1f}")
            else:
                row_text.append("")
        text_matrix.append(row_text)
        custom_data.append(row_custom)

    fig = go.Figure(data=go.Heatmap(
        z=matrix_pcts,
        x=x_labels,
        y=y_labels,
        colorscale=[
            [0.0, 'white'],       
            [0.01, '#90EE90'],    
            [0.5, 'yellow'],      
            [1.0, 'red']          
        ],
        reversescale=False,
        zmin=0, zmax=50,       
        text=text_matrix,
        texttemplate="%{text}",
        textfont={"size": 11, "family": "Arial", "color": "black"}, 
        customdata=custom_data,
        hoverongaps=False,
        hovertemplate='<b>%{y}</b><br>Reversal: %{x}<br>Count: %{customdata[0]}<br>Row Prob: %{z:.1f}%<br>Avg ATR: %{customdata[1]:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title=f"Impulse vs. Reversal Matrix{title_suffix}<br><span style='font-size:12px'><b>Grand Total: N={grand_total_n}</b> | Legenda: N:Count | %:Row Probability | ATR:Volatility</span>",
        xaxis_title="Reversal % Zone",
        yaxis_title="Impulse Range",
        template="plotly_dark",
        height=len(y_labels) * 75 + 230, 
        xaxis=dict(side="bottom") 
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
