"""
Streamlit Page 1: 원본 데이터 EDA
"""
import streamlit as st
import pandas as pd
from modules.data_loader import load_csv, get_table_summary
from modules.eda import (
    get_summary_stats,
    plot_monthly_trend,
    plot_item_top10,
    plot_account_distribution,
    plot_qty_histogram,
    plot_yearly_heatmap,
    plot_qty_vs_amt_scatter,
    get_status_distribution
)
from pathlib import Path

st.set_page_config(page_title="데이터 분석", page_icon="📊", layout="wide")

st.title("📊 원본 데이터 분석 (EDA)")

ACTUAL_SALES_PATH = Path(__file__).parent.parent / "data" / "TB_CM_ACTUAL_SALES_202604281652.csv"
ITEM_MST_PATH = Path(__file__).parent.parent / "data" / "TB_CM_ITEM_MST_202604291637.csv"
ACCOUNT_MST_PATH = Path(__file__).parent.parent / "data" / "TB_DP_ACCOUNT_MST_202604291638.csv"
COMN_CODE_PATH = Path(__file__).parent.parent / "data" / "TB_AD_COMN_CODE_202604291638.csv"

# CSV 로드
@st.cache_data
def load_data():
    # 원본 데이터 로드
    df_sales = load_csv(ACTUAL_SALES_PATH)

    # 마스터 데이터 로드 및 JOIN
    try:
        df_item = pd.read_csv(ITEM_MST_PATH, encoding='utf-8-sig')
        df_sales = df_sales.merge(
            df_item[['ID', 'ITEM_NM', 'ITEM_CD']],
            left_on='ITEM_MST_ID',
            right_on='ID',
            how='left'
        ).drop('ID', axis=1)
    except Exception as e:
        st.warning(f"품목 마스터 로드 실패: {str(e)}")

    try:
        df_account = pd.read_csv(ACCOUNT_MST_PATH, encoding='utf-8-sig')
        df_sales = df_sales.merge(
            df_account[['ID', 'ACCOUNT_NM', 'ACCOUNT_CD']],
            left_on='ACCOUNT_ID',
            right_on='ID',
            how='left',
            suffixes=('', '_account')
        ).drop('ID', axis=1)
    except Exception as e:
        st.warning(f"거래처 마스터 로드 실패: {str(e)}")

    try:
        df_comn = pd.read_csv(COMN_CODE_PATH, encoding='utf-8-sig')
        df_comn_status = df_comn[df_comn['SRC_ID'] == 'SO_STATUS']
        df_sales = df_sales.merge(
            df_comn_status[['ID', 'COMN_CD_NM']],
            left_on='SO_STATUS_ID',
            right_on='ID',
            how='left'
        ).drop('ID', axis=1).rename(columns={'COMN_CD_NM': 'SO_STATUS_NM'})
    except Exception as e:
        st.warning(f"공통코드 로드 실패: {str(e)}")

    return df_sales

try:
    df = load_data()
    st.session_state['df_original'] = df

    # 핵심 지표 카드
    st.subheader("📈 핵심 지표")
    stats = get_summary_stats(df)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 건수", f"{stats['total_rows']:,}")
    with col2:
        st.metric("품목 수", f"{stats['items']}")
    with col3:
        st.metric("고객사 수", f"{stats['accounts']}")
    with col4:
        date_range = (stats['date_range']['end'] - stats['date_range']['start']).days
        st.metric("데이터 기간 (일)", f"{date_range}")

    # 필터
    st.subheader("🔍 필터")
    col1, col2, col3 = st.columns(3)

    with col1:
        date_range = st.date_input(
            "기간 선택",
            value=(stats['date_range']['start'].date(), stats['date_range']['end'].date()),
            key="date_range"
        )
        if len(date_range) == 2:
            df_filtered = df[
                (df['BASE_DATE'].dt.date >= date_range[0]) &
                (df['BASE_DATE'].dt.date <= date_range[1])
            ]
        else:
            df_filtered = df

    with col2:
        items = st.multiselect(
            "품목 선택",
            options=sorted(df['ITEM_MST_ID'].unique()),
            default=None,
            key="items_filter"
        )
        if items:
            df_filtered = df_filtered[df_filtered['ITEM_MST_ID'].isin(items)]

    with col3:
        accounts = st.multiselect(
            "고객사 선택",
            options=sorted(df['ACCOUNT_ID'].unique()),
            default=None,
            key="accounts_filter"
        )
        if accounts:
            df_filtered = df_filtered[df_filtered['ACCOUNT_ID'].isin(accounts)]

    st.write(f"필터링된 데이터: {len(df_filtered):,}행 / {len(df):,}행")

    # 차트
    st.subheader("📊 시각화")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**월별 QTY/AMT 추이**")
        try:
            fig = plot_monthly_trend(df_filtered)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"오류: {str(e)}")

    with col2:
        st.write("**품목별 QTY Top10**")
        try:
            fig = plot_item_top10(df_filtered)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"오류: {str(e)}")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**고객사별 AMT 분포**")
        try:
            fig = plot_account_distribution(df_filtered)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"오류: {str(e)}")

    with col2:
        st.write("**QTY 분포**")
        try:
            fig = plot_qty_histogram(df_filtered)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"오류: {str(e)}")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**연도별 월별 히트맵**")
        try:
            fig = plot_yearly_heatmap(df_filtered)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"오류: {str(e)}")

    with col2:
        st.write("**QTY vs AMT**")
        try:
            fig = plot_qty_vs_amt_scatter(df_filtered)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"오류: {str(e)}")

    col1 = st.columns(1)[0]
    with col1:
        st.write("**수주 상태별 분포**")
        try:
            fig = get_status_distribution(df_filtered)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"오류: {str(e)}")

    # 데이터 테이블
    st.subheader("📋 데이터 테이블")
    st.dataframe(df_filtered, use_container_width=True)

except Exception as e:
    st.error(f"데이터 로드 오류: {str(e)}")
    st.stop()
