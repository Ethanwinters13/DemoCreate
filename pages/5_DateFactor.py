"""
Streamlit Page 5: 일자별 인자 조회 및 변환
"""
import streamlit as st
import pandas as pd
from modules.factor_handler import load_date_factors, transform_date_factors, compare_factors, preview_factors
from modules.converter import get_industry_list
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="일자별 인자", page_icon="📅", layout="wide")

st.title("📅 일자별 인자 (FACTOR)")

CSV_PATH = Path(__file__).parent.parent / "data" / "TB_BF_DATE_FACTOR_202604291639.csv"

@st.cache_data
def load_data():
    return load_date_factors(CSV_PATH)

try:
    df = load_data()

    # 데이터 로드 요약
    st.subheader("1️⃣ 인자 데이터 요약")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 행 수", f"{len(df):,}")
    with col2:
        date_range = (df['BASE_DATE'].max() - df['BASE_DATE'].min()).days
        st.metric("기간 (일)", f"{date_range}")
    with col3:
        factor_cols = [col for col in df.columns if col.startswith('FACTOR')]
        st.metric("FACTOR 개수", f"{len(factor_cols)}")

    # 필터
    st.subheader("2️⃣ 필터")

    date_range = st.date_input(
        "기간 선택",
        value=(df['BASE_DATE'].min().date(), df['BASE_DATE'].max().date()),
        key="date_range_date_factor"
    )
    if len(date_range) == 2:
        df_filtered = df[
            (df['BASE_DATE'].dt.date >= date_range[0]) &
            (df['BASE_DATE'].dt.date <= date_range[1])
        ]
    else:
        df_filtered = df

    st.write(f"필터링된 데이터: {len(df_filtered):,}행 / {len(df):,}행")

    # 필터링된 데이터 미리보기
    st.subheader("3️⃣ 인자 데이터 조회")

    # FACTOR 컬럼 찾기
    factor_cols = [col for col in df.columns if col.startswith('FACTOR')]
    display_cols = ['BASE_DATE'] + factor_cols[:10]  # 상위 10개 FACTOR만 표시

    st.dataframe(preview_factors(df_filtered[display_cols], n=50), use_container_width=True)

    # 인자 통계
    st.subheader("4️⃣ 인자값 통계")

    col1, col2, col3 = st.columns(3)

    with col1:
        if 'FACTOR1' in df_filtered.columns:
            st.write("**FACTOR1**")
            st.write(f"""
            - 평균: {df_filtered['FACTOR1'].mean():.2f}
            - 최소: {df_filtered['FACTOR1'].min():.2f}
            - 최대: {df_filtered['FACTOR1'].max():.2f}
            - 표준편차: {df_filtered['FACTOR1'].std():.2f}
            """)

    with col2:
        if 'FACTOR2' in df_filtered.columns:
            st.write("**FACTOR2**")
            st.write(f"""
            - 평균: {df_filtered['FACTOR2'].mean():.2f}
            - 최소: {df_filtered['FACTOR2'].min():.2f}
            - 최대: {df_filtered['FACTOR2'].max():.2f}
            - 표준편차: {df_filtered['FACTOR2'].std():.2f}
            """)

    with col3:
        if 'FACTOR3' in df_filtered.columns:
            st.write("**FACTOR3**")
            st.write(f"""
            - 평균: {df_filtered['FACTOR3'].mean():.2f}
            - 최소: {df_filtered['FACTOR3'].min():.2f}
            - 최대: {df_filtered['FACTOR3'].max():.2f}
            - 표준편차: {df_filtered['FACTOR3'].std():.2f}
            """)

    col1, col2 = st.columns(2)

    with col1:
        if 'FACTOR4' in df_filtered.columns:
            st.write("**FACTOR4**")
            st.write(f"""
            - 평균: {df_filtered['FACTOR4'].mean():.2f}
            - 최소: {df_filtered['FACTOR4'].min():.2f}
            - 최대: {df_filtered['FACTOR4'].max():.2f}
            - 표준편차: {df_filtered['FACTOR4'].std():.2f}
            """)

    with col2:
        if 'FACTOR5' in df_filtered.columns:
            st.write("**FACTOR5**")
            st.write(f"""
            - 평균: {df_filtered['FACTOR5'].mean():.2f}
            - 최소: {df_filtered['FACTOR5'].min():.2f}
            - 최대: {df_filtered['FACTOR5'].max():.2f}
            - 표준편차: {df_filtered['FACTOR5'].std():.2f}
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

    # FACTOR 적용 선택
    st.write("**적용할 FACTOR 선택:**")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        apply_factor01 = st.checkbox("FACTOR1", value=True, key="f1")
    with col2:
        apply_factor02 = st.checkbox("FACTOR2", value=True, key="f2")
    with col3:
        apply_factor03 = st.checkbox("FACTOR3", value=True, key="f3")
    with col4:
        apply_factor04 = st.checkbox("FACTOR4", value=True, key="f4")
    with col5:
        apply_factor05 = st.checkbox("FACTOR5", value=True, key="f5")

    # 스케일 설정
    st.write("**FACTOR 스케일 설정:**")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        scale_factor01 = st.slider(
            "FACTOR1 스케일",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            key="s1"
        )

    with col2:
        scale_factor02 = st.slider(
            "FACTOR2 스케일",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            key="s2"
        )

    with col3:
        scale_factor03 = st.slider(
            "FACTOR3 스케일",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            key="s3"
        )

    with col4:
        scale_factor04 = st.slider(
            "FACTOR4 스케일",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            key="s4"
        )

    with col5:
        scale_factor05 = st.slider(
            "FACTOR5 스케일",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            key="s5"
        )

    # 변환 버튼
    st.subheader("6️⃣ 변환 실행")

    if st.button("🔄 인자 변환", use_container_width=True, type="primary"):
        with st.spinner("인자 변환 중..."):
            try:
                options = {
                    'apply_factors': {
                        'FACTOR1': apply_factor01,
                        'FACTOR2': apply_factor02,
                        'FACTOR3': apply_factor03,
                        'FACTOR4': apply_factor04,
                        'FACTOR5': apply_factor05,
                    },
                    'custom_scales': {
                        'FACTOR1': scale_factor01,
                        'FACTOR2': scale_factor02,
                        'FACTOR3': scale_factor03,
                        'FACTOR4': scale_factor04,
                        'FACTOR5': scale_factor05,
                    }
                }

                df_converted = transform_date_factors(df_filtered, selected_industry_id, options)
                st.session_state['df_date_factors_converted'] = df_converted
                st.session_state['selected_industry_id_date'] = selected_industry_id
                st.session_state['selected_industry_name_date'] = selected_industry_name

                st.success("✅ 변환 완료!")
                st.info("아래에서 변환된 인자를 확인하고 다운로드하세요.")

            except Exception as e:
                st.error(f"변환 실패: {str(e)}")

    # 변환 결과
    if 'df_date_factors_converted' in st.session_state:
        st.subheader("7️⃣ 변환 결과 비교")

        df_converted = st.session_state['df_date_factors_converted']
        industry_name = st.session_state.get('selected_industry_name_date', '알 수 없음')

        comparison = compare_factors(df_filtered, df_converted)
        orig = comparison['original']
        conv = comparison['transformed']

        col1, col2 = st.columns(2)

        with col1:
            st.write("**원본 인자 통계**")
            st.write(f"""
            - 행 수: {orig['rows']:,}
            - FACTOR1 평균: {orig['factor_means'].get('FACTOR1', 0):.2f}
            - FACTOR2 평균: {orig['factor_means'].get('FACTOR2', 0):.2f}
            - FACTOR3 평균: {orig['factor_means'].get('FACTOR3', 0):.2f}
            """)

        with col2:
            st.write("**변환된 인자 통계**")
            st.write(f"""
            - 행 수: {conv['rows']:,}
            - FACTOR1 평균: {conv['factor_means'].get('FACTOR1', 0):.2f}
            - FACTOR2 평균: {conv['factor_means'].get('FACTOR2', 0):.2f}
            - FACTOR3 평균: {conv['factor_means'].get('FACTOR3', 0):.2f}
            """)

        # 변환 결과 미리보기
        st.subheader("8️⃣ 변환 결과 미리보기")
        st.dataframe(preview_factors(df_converted[display_cols], n=20), use_container_width=True)

        # 다운로드
        st.subheader("9️⃣ 데이터 다운로드")

        col1, col2 = st.columns(2)

        with col1:
            csv_data = df_converted.to_csv(index=False, encoding='utf-8-sig')
            filename = f"date_factors_{industry_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv_data,
                file_name=filename,
                mime="text/csv"
            )

        with col2:
            excel_data = df_converted.to_excel(index=False)
            filename_excel = f"date_factors_{industry_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            st.download_button(
                label="📥 Excel 다운로드",
                data=excel_data,
                file_name=filename_excel,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

except Exception as e:
    st.error(f"오류: {str(e)}")
    st.stop()
