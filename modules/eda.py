"""
EDA (Exploratory Data Analysis) 시각화 모듈
plotly를 이용한 대화형 차트 생성
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


def get_summary_stats(df):
    """
    기초 통계 요약 반환

    Args:
        df (pd.DataFrame): 분석 대상 데이터

    Returns:
        dict: 통계 정보
    """
    return {
        'total_rows': len(df),
        'date_range': {
            'start': df['BASE_DATE'].min(),
            'end': df['BASE_DATE'].max()
        },
        'items': df['ITEM_MST_ID'].nunique(),
        'accounts': df['ACCOUNT_ID'].nunique(),
        'qty': {
            'total': df['QTY'].sum(),
            'mean': df['QTY'].mean(),
            'median': df['QTY'].median(),
            'min': df['QTY'].min(),
            'max': df['QTY'].max()
        },
        'amt': {
            'total': df['AMT'].sum(),
            'mean': df['AMT'].mean(),
            'median': df['AMT'].median(),
            'min': df['AMT'].min(),
            'max': df['AMT'].max()
        }
    }


def plot_monthly_trend(df):
    """
    월별 QTY/AMT 추이 (라인 차트)

    Args:
        df (pd.DataFrame): 분석 대상 데이터

    Returns:
        plotly.graph_objects.Figure: 차트 객체
    """
    df_monthly = df.groupby(df['BASE_DATE'].dt.to_period('M')).agg({
        'QTY': 'sum',
        'AMT': 'sum'
    }).reset_index()

    df_monthly['BASE_DATE'] = df_monthly['BASE_DATE'].astype(str)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=df_monthly['BASE_DATE'],
            y=df_monthly['QTY'],
            name='QTY',
            mode='lines',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='%{x}<br>QTY: %{y:,.0f}<extra></extra>'
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df_monthly['BASE_DATE'],
            y=df_monthly['AMT'],
            name='AMT',
            mode='lines',
            line=dict(color='#ff7f0e', width=2),
            hovertemplate='%{x}<br>AMT: %{y:,.0f}<extra></extra>'
        ),
        secondary_y=True
    )

    fig.update_layout(
        title='월별 QTY/AMT 추이',
        xaxis_title='기간',
        yaxis_title='QTY (수량)',
        yaxis2_title='AMT (금액)',
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )

    return fig


def plot_item_top10(df):
    """
    품목별 QTY Top10 (바 차트)

    Args:
        df (pd.DataFrame): 분석 대상 데이터

    Returns:
        plotly.graph_objects.Figure: 차트 객체
    """
    df_item = df.groupby('ITEM_MST_ID')['QTY'].sum().sort_values(ascending=False).head(10)

    fig = go.Figure(data=[
        go.Bar(
            y=df_item.index,
            x=df_item.values,
            orientation='h',
            marker=dict(color='#2ca02c'),
            hovertemplate='%{y}<br>QTY: %{x:,.0f}<extra></extra>'
        )
    ])

    fig.update_layout(
        title='품목별 QTY Top 10',
        xaxis_title='QTY (수량)',
        yaxis_title='품목 ID',
        height=400,
        template='plotly_white'
    )

    return fig


def plot_account_distribution(df):
    """
    고객사별 AMT 분포 (파이 차트)

    Args:
        df (pd.DataFrame): 분석 대상 데이터

    Returns:
        plotly.graph_objects.Figure: 차트 객체
    """
    df_account = df.groupby('ACCOUNT_ID')['AMT'].sum().sort_values(ascending=False).head(15)

    fig = go.Figure(data=[
        go.Pie(
            labels=df_account.index,
            values=df_account.values,
            hovertemplate='%{label}<br>AMT: %{value:,.0f}<br>비중: %{percent}<extra></extra>'
        )
    ])

    fig.update_layout(
        title='고객사별 AMT 분포 (Top 15)',
        height=400
    )

    return fig


def plot_qty_histogram(df):
    """
    QTY 히스토그램 (QTY > 0 기준)

    Args:
        df (pd.DataFrame): 분석 대상 데이터

    Returns:
        plotly.graph_objects.Figure: 차트 객체
    """
    df_qty = df[df['QTY'] > 0]['QTY']

    fig = go.Figure(data=[
        go.Histogram(
            x=df_qty,
            nbinsx=50,
            marker=dict(color='#d62728'),
            hovertemplate='QTY: %{x}<br>건수: %{y}<extra></extra>'
        )
    ])

    fig.update_layout(
        title=f'QTY 분포 히스토그램 (QTY > 0, n={len(df_qty):,})',
        xaxis_title='QTY (수량)',
        yaxis_title='건수',
        height=400,
        template='plotly_white'
    )

    return fig


def plot_yearly_heatmap(df):
    """
    연도별 월별 히트맵 (연 x 월)

    Args:
        df (pd.DataFrame): 분석 대상 데이터

    Returns:
        plotly.graph_objects.Figure: 차트 객체
    """
    df['Year'] = df['BASE_DATE'].dt.year
    df['Month'] = df['BASE_DATE'].dt.month

    df_heatmap = df.groupby(['Year', 'Month'])['AMT'].sum().reset_index()
    df_pivot = df_heatmap.pivot(index='Year', columns='Month', values='AMT').fillna(0)

    fig = go.Figure(data=go.Heatmap(
        z=df_pivot.values,
        x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][:df_pivot.shape[1]],
        y=df_pivot.index,
        colorscale='Viridis',
        hovertemplate='연도: %{y}<br>월: %{x}<br>AMT: %{z:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title='연도별 월별 AMT 히트맵',
        xaxis_title='월',
        yaxis_title='연도',
        height=400,
        template='plotly_white'
    )

    return fig


def plot_qty_vs_amt_scatter(df):
    """
    QTY vs AMT 산점도 (상관관계)

    Args:
        df (pd.DataFrame): 분석 대상 데이터

    Returns:
        plotly.graph_objects.Figure: 차트 객체
    """
    df_sample = df.sample(min(5000, len(df)))

    fig = px.scatter(
        df_sample,
        x='QTY',
        y='AMT',
        opacity=0.5,
        title='QTY vs AMT 산점도',
        labels={'QTY': 'QTY (수량)', 'AMT': 'AMT (금액)'},
        height=400
    )

    fig.update_layout(template='plotly_white')

    return fig


def get_status_distribution(df):
    """
    수주 상태별 분포

    Args:
        df (pd.DataFrame): 분석 대상 데이터

    Returns:
        plotly.graph_objects.Figure: 차트 객체
    """
    df_status = df.groupby('SO_STATUS_ID').size().sort_values(ascending=False)

    fig = go.Figure(data=[
        go.Bar(
            x=df_status.index,
            y=df_status.values,
            marker=dict(color='#9467bd'),
            hovertemplate='상태: %{x}<br>건수: %{y}<extra></extra>'
        )
    ])

    fig.update_layout(
        title='수주 상태별 분포',
        xaxis_title='상태',
        yaxis_title='건수',
        height=400,
        template='plotly_white'
    )

    return fig
