# T³ Demo Configurator

T³SmartSCM 데모용 판매실적 데이터를 고객사 업종에 맞게 자동 변환하는 Streamlit 웹 애플리케이션입니다.

## 🎯 기능

- **EDA**: 원본 판매 실적 데이터 분석
- **업종 설정**: 5가지 업종별 데이터 변환 규칙 적용
- **결과 출력**: CSV 다운로드 및 MSSQL DB 저장

## 🛠 기술 스택

- Python 3.14
- Streamlit
- pandas, plotly
- MSSQL (pyodbc)

## 📋 설치 및 실행

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 설정
`.env.template`을 참고하여 `.env` 파일 생성:
```bash
cp .env.template .env
# .env 파일에 DB 접속 정보 입력
```

### 3. 앱 실행
```bash
streamlit run app.py
```

## 📁 프로젝트 구조

```
DemoCreate/
├── app.py                    # Streamlit 메인 진입점
├── requirements.txt
├── .env.template             # DB 설정 템플릿
├── config/
│   └── industry_config.json  # 업종별 변환 규칙
├── modules/
│   ├── db_handler.py         # DB 연결
│   ├── data_loader.py        # CSV 적재
│   ├── eda.py                # EDA 시각화
│   └── converter.py          # 데이터 변환 엔진
├── pages/
│   ├── 1_EDA.py              # 원본 데이터 분석
│   ├── 2_Configure.py        # 업종 설정
│   └── 3_Result.py           # 결과 출력
└── data/
    └── TB_CM_ACTUAL_SALES_*.csv
```

## 🏢 지원 업종

1. **반도체 제조** - 소량 고단가, 분기말 집중
2. **자동차 부품** - 중량 중단가, 상반기 집중
3. **식품/음료** - 대량 저단가, 여름 성수기
4. **화학/소재** - 중소량 고단가, 균등 납품
5. **물류/유통** - 대량 저단가, 연말 집중

## ⚠️ 주의사항

- `.env` 파일은 절대 Git에 커밋하지 마세요
- 원본 DB 테이블(`TB_CM_ACTUAL_SALES`)은 수정하지 마세요
- 변환 결과는 별도 테이블(`TB_CM_ACTUAL_SALES_DEMO`)에 저장됩니다
