"""
Streamlit Page 3: 변환 결과 확인 및 출력
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from modules.converter import compare_data
from modules.eda import plot_monthly_trend

st.set_page_config(page_title="결과 확인", page_icon="📊", layout="wide")

st.title("📊 변환 결과 확인")

if 'df_original' not in st.session_state or 'df_converted' not in st.session_state:
    st.warning("⚠️ 변환된 데이터가 없습니다. '설정' 페이지에서 데이터를 변환해주세요.")
else:
    df_original = st.session_state['df_original']
    df_converted = st.session_state['df_converted']
    industry_name = st.session_state.get('selected_industry_name', '알 수 없음')

    # 변환 요약
    st.subheader("🎯 변환 요약")

    col1, col2, col3 = st.columns(3)

    comparison = compare_data(df_original, df_converted)
    orig = comparison['original']
    conv = comparison['converted']

    with col1:
        st.metric(
            "행 수",
            f"{conv['rows']:,}",
            f"{conv['rows'] - orig['rows']:+,}"
        )

    with col2:
        st.metric(
            "QTY 합계",
            f"{conv['qty_total']:,.0f}",
            f"{((conv['qty_total'] / orig['qty_total'] - 1) * 100):+.1f}%"
        )

    with col3:
        st.metric(
            "AMT 합계",
            f"{conv['amt_total']:,.0f}",
            f"{((conv['amt_total'] / orig['amt_total'] - 1) * 100):+.1f}%"
        )

    # 상세 비교
    st.subheader("📈 원본 vs 변환 비교")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**원본 데이터**")
        st.write(f"""
        - 행 수: {orig['rows']:,}
        - QTY 합계: {orig['qty_total']:,.0f}
        - QTY 평균: {orig['qty_avg']:,.0f}
        - AMT 합계: {orig['amt_total']:,.0f}
        - AMT 평균: {orig['amt_avg']:,.0f}
        """)

    with col2:
        st.write("**변환된 데이터**")
        st.write(f"""
        - 행 수: {conv['rows']:,}
        - QTY 합계: {conv['qty_total']:,.0f}
        - QTY 평균: {conv['qty_avg']:,.0f}
        - AMT 합계: {conv['amt_total']:,.0f}
        - AMT 평균: {conv['amt_avg']:,.0f}
        """)

    # 월별 추이 비교
    st.subheader("📊 월별 추이 비교")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**원본 데이터 추이**")
        try:
            fig_orig = plot_monthly_trend(df_original)
            st.plotly_chart(fig_orig, use_container_width=True)
        except Exception as e:
            st.error(f"차트 생성 오류: {str(e)}")

    with col2:
        st.write("**변환된 데이터 추이**")
        try:
            fig_conv = plot_monthly_trend(df_converted)
            st.plotly_chart(fig_conv, use_container_width=True)
        except Exception as e:
            st.error(f"차트 생성 오류: {str(e)}")

    # 미리보기 데이터
    st.subheader("📋 변환 데이터 미리보기")
    st.dataframe(df_converted.head(50), use_container_width=True)

    # 다운로드 및 저장
    st.subheader("💾 데이터 출력")

    col1, col2 = st.columns(2)

    with col1:
        csv_data = df_converted.to_csv(index=False, encoding='utf-8-sig')
        filename = f"converted_{industry_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        st.download_button(
            label="📥 CSV 다운로드",
            data=csv_data,
            file_name=filename,
            mime="text/csv"
        )

    with col2:
        excel_data = df_converted.to_excel(index=False)
        filename_excel = f"converted_{industry_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        st.download_button(
            label="📥 Excel 다운로드",
            data=excel_data,
            file_name=filename_excel,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.success("✅ 변환 완료! 위의 버튼으로 데이터를 다운로드하세요.")
