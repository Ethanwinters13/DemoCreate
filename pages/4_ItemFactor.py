"""
Streamlit Page 4: 품목별 인자 조회 및 변환
"""
import streamlit as st
import pandas as pd
from modules.factor_handler import load_item_factors, transform_item_factors, compare_factors, preview_factors
from modules.converter import get_industry_list
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="품목별 인자", page_icon="📦", layout="wide")

st.title("📦 품목별 인자 (SALES_FACTOR)")

CSV_PATH = Path(__file__).parent.parent / "data" / "TB_BF_SALES_FACTOR_202604291639.csv"

@st.cache_data
def load_data():
    return load_item_factors(CSV_PATH)

try:
    df = load_data()

    # 데이터 로드 요약
    st.subheader("1️⃣ 인자 데이터 요약")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 행 수", f"{len(df):,}")
    with col2:
        st.metric("거래처 수", f"{df['ACCOUNT_CD'].nunique()}")
    with col3:
        st.metric("품목 수", f"{df['ITEM_CD'].nunique()}")
    with col4:
        date_range = (df['BASE_DATE'].max() - df['BASE_DATE'].min()).days
        st.metric("기간 (일)", f"{date_range}")

    # 필터
    st.subheader("2️⃣ 필터")
    col1, col2, col3 = st.columns(3)

    with col1:
        date_range = st.date_input(
            "기간 선택",
            value=(df['BASE_DATE'].min().date(), df['BASE_DATE'].max().date()),
            key="date_range_item_factor"
        )
        if len(date_range) == 2:
            df_filtered = df[
                (df['BASE_DATE'].dt.date >= date_range[0]) &
                (df['BASE_DATE'].dt.date <= date_range[1])
            ]
        else:
            df_filtered = df

    with col2:
        accounts = st.multiselect(
            "거래처 선택",
            options=sorted(df['ACCOUNT_CD'].unique()),
            default=None,
            key="accounts_filter_item_factor"
        )
        if accounts:
            df_filtered = df_filtered[df_filtered['ACCOUNT_CD'].isin(accounts)]

    with col3:
        items = st.multiselect(
            "품목 선택",
            options=sorted(df['ITEM_CD'].unique()),
            default=None,
            key="items_filter_item_factor"
        )
        if items:
            df_filtered = df_filtered[df_filtered['ITEM_CD'].isin(items)]

    st.write(f"필터링된 데이터: {len(df_filtered):,}행 / {len(df):,}행")

    # 필터링된 데이터 미리보기
    st.subheader("3️⃣ 인자 데이터 조회")

    # SALES_FACTOR 컬럼 찾기
    factor_cols = [col for col in df.columns if col.startswith('SALES_FACTOR')]
    display_cols = ['BASE_DATE', 'ITEM_CD', 'ACCOUNT_CD'] + factor_cols[:10]  # 상위 10개 FACTOR만 표시

    st.dataframe(preview_factors(df_filtered[display_cols], n=50), use_container_width=True)

    # 인자 통계
    st.subheader("4️⃣ 인자값 통계")

    if 'SALES_FACTOR1' in df_filtered.columns:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**SALES_FACTOR1**")
            st.write(f"""
            - 평균: {df_filtered['SALES_FACTOR1'].mean():.3f}
            - 최소: {df_filtered['SALES_FACTOR1'].min():.3f}
            - 최대: {df_filtered['SALES_FACTOR1'].max():.3f}
            - 표준편차: {df_filtered['SALES_FACTOR1'].std():.3f}
            """)

        with col2:
            st.write("**SALES_FACTOR2**")
            st.write(f"""
            - 평균: {df_filtered['SALES_FACTOR2'].mean():.3f}
            - 최소: {df_filtered['SALES_FACTOR2'].min():.3f}
            - 최대: {df_filtered['SALES_FACTOR2'].max():.3f}
            - 표준편차: {df_filtered['SALES_FACTOR2'].std():.3f}
            """)

        with col3:
            st.write("**SALES_FACTOR3**")
            st.write(f"""
            - 평균: {df_filtered['SALES_FACTOR3'].mean():.3f}
            - 최소: {df_filtered['SALES_FACTOR3'].min():.3f}
            - 최대: {df_filtered['SALES_FACTOR3'].max():.3f}
            - 표준편차: {df_filtered['SALES_FACTOR3'].std():.3f}
            """)

    # 변환 설정
    st.subheader("5️⃣ 인자 변환 설정")

    industries = get_industry_list()
    industry_dict = {ind['name']: ind['id'] for ind in industries}

    selected_industry_name = st.radio(
        "업종을 선택하세요:",
        options=industry_dict.keys(),
        format_func=lambda x: f"{x} - {next(ind['description'] for ind in industries if ind['name'] == x)}"
    )

    selected_industry_id = industry_dict[selected_industry_name]

    col1, col2, col3 = st.columns(3)

    with col1:
        factor1_scale = st.slider(
            "SALES_FACTOR1 스케일",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="FACTOR1에 적용할 스케일 배율"
        )

    with col2:
        factor2_scale = st.slider(
            "SALES_FACTOR2 스케일",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="FACTOR2 적용 확률"
        )

    with col3:
        factor3_scale = st.slider(
            "SALES_FACTOR3 스케일",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="FACTOR3에 적용할 스케일 배율"
        )

    # 변환 버튼
    st.subheader("6️⃣ 변환 실행")

    if st.button("🔄 인자 변환", use_container_width=True, type="primary"):
        with st.spinner("인자 변환 중..."):
            try:
                options = {
                    'custom_sales_factor01_scale': factor1_scale,
                    'custom_sales_factor02_scale': factor2_scale,
                    'custom_sales_factor03_scale': factor3_scale,
                }

                df_converted = transform_item_factors(df_filtered, selected_industry_id, options)
                st.session_state['df_item_factors_converted'] = df_converted
                st.session_state['selected_industry_id_item'] = selected_industry_id
                st.session_state['selected_industry_name_item'] = selected_industry_name

                st.success("✅ 변환 완료!")
                st.info("아래에서 변환된 인자를 확인하고 다운로드하세요.")

            except Exception as e:
                st.error(f"변환 실패: {str(e)}")

    # 변환 결과
    if 'df_item_factors_converted' in st.session_state:
        st.subheader("7️⃣ 변환 결과 비교")

        df_converted = st.session_state['df_item_factors_converted']
        industry_name = st.session_state.get('selected_industry_name_item', '알 수 없음')

        comparison = compare_factors(df_filtered, df_converted)
        orig = comparison['original']
        conv = comparison['transformed']

        col1, col2 = st.columns(2)

        with col1:
            st.write("**원본 인자 통계**")
            st.write(f"""
            - 행 수: {orig['rows']:,}
            - SALES_FACTOR1 평균: {orig['factor_means'].get('SALES_FACTOR1', 0):.3f}
            - SALES_FACTOR2 평균: {orig['factor_means'].get('SALES_FACTOR2', 0):.3f}
            - SALES_FACTOR3 평균: {orig['factor_means'].get('SALES_FACTOR3', 0):.3f}
            """)

        with col2:
            st.write("**변환된 인자 통계**")
            st.write(f"""
            - 행 수: {conv['rows']:,}
            - SALES_FACTOR1 평균: {conv['factor_means'].get('SALES_FACTOR1', 0):.3f}
            - SALES_FACTOR2 평균: {conv['factor_means'].get('SALES_FACTOR2', 0):.3f}
            - SALES_FACTOR3 평균: {conv['factor_means'].get('SALES_FACTOR3', 0):.3f}
            """)

        # 변환 결과 미리보기
        st.subheader("8️⃣ 변환 결과 미리보기")
        st.dataframe(preview_factors(df_converted[display_cols], n=20), use_container_width=True)

        # 다운로드
        st.subheader("9️⃣ 데이터 다운로드")

        col1, col2 = st.columns(2)

        with col1:
            csv_data = df_converted.to_csv(index=False, encoding='utf-8-sig')
            filename = f"item_factors_{industry_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv_data,
                file_name=filename,
                mime="text/csv"
            )

        with col2:
            excel_data = df_converted.to_excel(index=False)
            filename_excel = f"item_factors_{industry_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            st.download_button(
                label="📥 Excel 다운로드",
                data=excel_data,
                file_name=filename_excel,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

except Exception as e:
    st.error(f"오류: {str(e)}")
    st.stop()
