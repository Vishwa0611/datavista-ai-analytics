"""
Plotly chart builders — professional, restrained color palette.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any
from ..utils.constants import CHART_PALETTE

def get_palette(n: int = None):
    if n is None:
        return CHART_PALETTE
    return (CHART_PALETTE * ((n // len(CHART_PALETTE)) +1))[:n]

def create_histogram(df: pd.DataFrame, column: str, title: str = None):
    try:
        fig = px.histogram(df, x=column, nbins=30, title=title or f"Distribution of {column}",
                          color_discrete_sequence=[CHART_PALETTE[0]])
        fig.update_layout(template="plotly_white", bargap=0.05, height=350,
                          margin=dict(l=20,r=20,t=40,b=20))
        return fig
    except Exception as e:
        return None

def create_box_plot(df: pd.DataFrame, column: str, title: str = None):
    try:
        fig = px.box(df, y=column, title=title or f"Box Plot — {column} (Outlier detection)",
                     color_discrete_sequence=[CHART_PALETTE[1]])
        fig.update_layout(template="plotly_white", height=350, margin=dict(l=20,r=20,t=40,b=20))
        return fig
    except:
        return None

def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str = None, title: str = None, top_n: int = 15):
    try:
        if y_col is None:
            # Frequency
            counts = df[x_col].value_counts().head(top_n).reset_index()
            counts.columns = [x_col, 'count']
            fig = px.bar(counts, x=x_col, y='count', title=title or f"Top {top_n} {x_col}",
                         color_discrete_sequence=get_palette(1))
        else:
            agg = df.groupby(x_col)[y_col].sum().sort_values(ascending=False).head(top_n).reset_index()
            fig = px.bar(agg, x=x_col, y=y_col, title=title or f"{y_col} by {x_col}",
                         color_discrete_sequence=get_palette(1))
        fig.update_layout(template="plotly_white", height=400, xaxis_tickangle=-30,
                          margin=dict(l=20,r=20,t=40,b=80))
        return fig
    except:
        return None

def create_line_chart(monthly_series: pd.Series, title: str = None, y_label: str = "Value"):
    try:
        df_plot = monthly_series.reset_index()
        df_plot.columns = ['date', 'value']
        fig = px.line(df_plot, x='date', y='value', title=title or f"{y_label} Over Time",
                       markers=True, color_discrete_sequence=[CHART_PALETTE[0]])
        fig.update_layout(template="plotly_white", height=400, margin=dict(l=20,r=20,t=40,b=20))
        return fig
    except:
        return None

def create_scatter_plot(df: pd.DataFrame, x_col: str, y_col: str, title: str = None):
    try:
        fig = px.scatter(df, x=x_col, y=y_col, title=title or f"{y_col} vs {x_col}",
                         color_discrete_sequence=[CHART_PALETTE[0]], opacity=0.6)
        fig.update_layout(template="plotly_white", height=400)
        return fig
    except:
        return None

def create_correlation_heatmap(corr_matrix: pd.DataFrame, title: str = "Correlation Matrix"):
    try:
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            zmin=-1,
            zmax=1,
            text=corr_matrix.round(2).values,
            texttemplate="%{text}",
            hoverongaps=False
        ))
        fig.update_layout(title=title, template="plotly_white", height=500, width=500)
        return fig
    except:
        return None

def create_pareto_chart(grouped_series: pd.Series, title: str = "Pareto Analysis"):
    try:
        df = grouped_series.reset_index()
        df.columns = ['category', 'value']
        df = df.sort_values('value', ascending=False)
        df['cumulative_pct'] = df['value'].cumsum() / df['value'].sum() *100

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['category'], y=df['value'], name='Value', marker_color=CHART_PALETTE[0]))
        fig.add_trace(go.Scatter(x=df['category'], y=df['cumulative_pct'], name='Cumulative %', yaxis='y2', line=dict(color=CHART_PALETTE[1])))
        fig.update_layout(
            title=title,
            template="plotly_white",
            yaxis=dict(title='Value'),
            yaxis2=dict(title='Cumulative %', overlaying='y', side='right', range=[0,100]),
            height=450,
            xaxis_tickangle=-30
        )
        return fig
    except:
        return None

def create_metric_trend_with_rolling(monthly: pd.Series, rolling_3: pd.Series, title: str = "Trend with 3-Month Rolling Avg"):
    try:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly.index, y=monthly.values, mode='lines+markers', name='Monthly', line=dict(color=CHART_PALETTE[0])))
        fig.add_trace(go.Scatter(x=rolling_3.index, y=rolling_3.values, mode='lines', name='3M Rolling Avg', line=dict(color=CHART_PALETTE[1], dash='dash')))
        fig.update_layout(template="plotly_white", title=title, height=400)
        return fig
    except:
        return None
