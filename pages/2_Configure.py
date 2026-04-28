"""
Streamlit Page 2: 업종 선택 및 변환 설정
"""
import streamlit as st
from modules.converter import convert, get_industry_list, preview
from modules.data_loader import load_csv
from pathlib import Path

st.set_page_config(page_title="설정", page_icon="⚙️", layout="wide")

st.title("⚙️ 업종 설정 및 변환")

CSV_PATH = Path(__file__).parent.parent / "data" / "TB_CM_ACTUAL_SALES_202604281652.csv"

@st.cache_data
def load_data():
    return load_csv(CSV_PATH)

try:
    df = load_data()

    # 업종 선택
    st.subheader("1️⃣ 업종 선택")

    industries = get_industry_list()
    industry_dict = {ind['name']: ind['id'] for ind in industries}

    selected_industry_name = st.radio(
        "업종을 선택하세요:",
        options=industry_dict.keys(),
        format_func=lambda x: f"{x} - {next(ind['description'] for ind in industries if ind['name'] == x)}"
    )

    selected_industry_id = industry_dict[selected_industry_name]
    st.session_state['selected_industry_name'] = selected_industry_name

    # 선택한 업종 상세 정보
    industry_info = next(ind for ind in industries if ind['id'] == selected_industry_id)
    st.write(f"""
    **선택 업종: {industry_info['name']}**
    - 설명: {industry_info['description']}
    - QTY 스케일: {industry_info['qty_scale']}
    - AMT 스케일: {industry_info['amt_scale']}
    - 단가 범위: {industry_info['unit_price_range'][0]:,} ~ {industry_info['unit_price_range'][1]:,}
    - 계절성: {industry_info['seasonality']}
    - 품목 패턴: {', '.join(industry_info['item_name_pattern'][:3])}...
    """)

    # 변환 설정
    st.subheader("2️⃣ 변환 설정")

    col1, col2 = st.columns(2)

    with col1:
        qty_scale = st.slider(
            "QTY 스케일 배율",
            min_value=0.01,
            max_value=10.0,
            value=float(industry_info['qty_scale']),
            step=0.1,
            help="원본 QTY에 적용할 스케일 배율"
        )

    with col2:
        amt_scale = st.slider(
            "AMT 스케일 배율",
            min_value=0.01,
            max_value=20.0,
            value=float(industry_info['amt_scale']),
            step=0.1,
            help="단가에 적용할 스케일 배율"
        )

    apply_noise = st.checkbox(
        "랜덤 노이즈 적용",
        value=True,
        help="데이터에 ±5% 랜덤 노이즈를 추가합니다"
    )

    # 변환 버튼
    st.subheader("3️⃣ 변환 실행")

    if st.button("🚀 데이터 변환", use_container_width=True, type="primary"):
        with st.spinner("데이터 변환 중..."):
            try:
                options = {
                    'custom_qty_scale': qty_scale,
                    'custom_amt_scale': amt_scale,
                    'apply_noise': apply_noise
                }

                df_converted = convert(df, selected_industry_id, options)
                st.session_state['df_converted'] = df_converted
                st.session_state['selected_industry_id'] = selected_industry_id

                st.success("✅ 변환 완료!")
                st.info("'결과 확인' 페이지에서 변환된 데이터를 확인하고 다운로드하세요.")

            except Exception as e:
                st.error(f"변환 실패: {str(e)}")

    # 미리보기
    if 'df_converted' in st.session_state:
        st.subheader("📋 변환 결과 미리보기")
        df_converted = st.session_state['df_converted']

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("변환된 행 수", f"{len(df_converted):,}")
        with col2:
            st.metric("QTY 합계", f"{df_converted['QTY'].sum():,.0f}")
        with col3:
            st.metric("AMT 합계", f"{df_converted['AMT'].sum():,.0f}")

        st.dataframe(preview(df_converted, n=10), use_container_width=True)
        st.write("👆 위는 변환된 데이터의 상위 10행입니다")

except Exception as e:
    st.error(f"오류: {str(e)}")
    st.stop()
