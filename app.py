"""
T³ Demo Configurator - Main Streamlit Application
데이터 변환 플랫폼: 원본 데이터 분석 및 업종별 변환
"""
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="T³ Demo Configurator",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔄 T³ Demo Configurator")
st.markdown("---")

st.markdown("""
## 소개

T³ Demo Configurator는 판매 데이터를 업종별 특성에 맞게 변환하고 분석하는 플랫폼입니다.

### 주요 기능

1. **📊 데이터 분석 (EDA)**
   - 원본 데이터의 통계 분석 및 시각화
   - 필터링을 통한 세부 분석
   - 월별 추이, 품목별 분포, 고객사 분석

2. **⚙️ 업종 설정 및 변환**
   - 5가지 업종(반도체, 자동차, 식품, 화학, 물류) 지원
   - 업종별 QTY/AMT 스케일 조정
   - 랜덤 노이즈 적용 옵션

3. **📈 결과 확인 및 다운로드**
   - 원본 vs 변환 데이터 비교
   - CSV/Excel 형식 다운로드
   - 상세 통계 비교

### 사용 방법

좌측 사이드바의 메뉴에서 다음 단계를 따르세요:

1. **1️⃣ 데이터 분석** → 원본 데이터 탐색
2. **2️⃣ 설정 및 변환** → 업종 선택 및 변환 실행
3. **3️⃣ 결과 확인** → 변환 결과 확인 및 다운로드

---

### 지원 업종

| 업종 | 설명 | QTY 스케일 | AMT 스케일 |
|------|------|-----------|----------|
| **반도체** | 반도체 산업용 변환 | 0.5x | 1.2x |
| **자동차** | 자동차 산업용 변환 | 1.0x | 1.0x |
| **식품** | 식품 산업용 변환 | 2.0x | 0.8x |
| **화학** | 화학 산업용 변환 | 1.5x | 1.5x |
| **물류** | 물류 산업용 변환 | 0.8x | 0.9x |

### 데이터 변환 프로세스

데이터 변환은 다음 10단계를 거칩니다:

1. ID 재생성 (UUID)
2. 품목 매핑 (업종별 패턴)
3. 고객사 재매핑
4. QTY 스케일 적용
5. 금액 계산
6. 날짜 유지
7. 상태 유지
8. 메타데이터 업데이트
9. 최종 정리
10. 컬럼 정렬

---

### 개발 정보

- **프레임워크**: Streamlit
- **데이터 처리**: Pandas
- **시각화**: Plotly
- **저장소**: https://github.com/Ethanwinters13/DemoCreate
- **데이터 소스**: TB_CM_ACTUAL_SALES_202604281652.csv

### 기술 사양

- Python 3.8+
- Streamlit 1.0+
- Pandas 1.3+
- Plotly 5.0+

---

**문의**: 프로젝트 저장소의 Issues 탭에서 문제를 보고하거나 제안을 해주세요.
""")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 12px;'>
T³ Demo Configurator | 데이터 변환 플랫폼 | v1.0.0
</div>
""", unsafe_allow_html=True)
