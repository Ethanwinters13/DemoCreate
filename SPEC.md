# T³ Demo Configurator - 기술 명세서

## 프로젝트 개요

판매 실적 데이터를 업종별 특성에 맞게 변환하고, 인자 데이터를 관리하는 데이터 변환 플랫폼입니다.

---

## 1. 시스템 아키텍처

### 1.1 핵심 데이터 테이블

#### 실적 데이터
**TB_CM_ACTUAL_SALES** (원본 CSV)
```
ID, BASE_DATE, ITEM_MST_ID, ACCOUNT_ID, QTY, AMT, SO_STATUS_ID, 
CORRECTION_YN, PLAN_SCOPE, CREATE_BY, CREATE_DTTM, ...
```

#### 마스터 데이터 (JOIN 테이블)
- **TB_CM_ITEM_MST**: 품목 정보 (ITEM_CD, ITEM_NM, ATTR_01~03)
- **TB_DP_ACCOUNT_MST**: 거래처 정보 (ACCOUNT_CD, ACCOUNT_NM)
- **TB_AD_COMN_CODE**: 공통코드 (수주 상태 등)

#### 인자 데이터 (신규)
- **TB_BF_DATE_FACTOR**: 일자별 인자
  - UK: BASE_DATE
  - 컬럼: FACTOR01~50
  - 예: 날씨, 강수량, 금리, 공휴일 수

- **TB_BF_ITEM_FACTOR**: 품목별 인자
  - UK: ACCOUNT_ID + ITEM_MST_ID + BASE_DATE
  - 컬럼: SALES_FACTOR01~50
  - 예: 할인율, 프로모션 여부, 경쟁사 가격

### 1.2 데이터 저장소
- **실적 데이터**: CSV 파일 (`data/TB_CM_ACTUAL_SALES_202604281652.csv`)
- **인자 데이터**: CSV 파일 (`data/TB_BF_ITEM_FACTOR.csv`, `data/TB_BF_DATE_FACTOR.csv`)
- **로컬 DB**: SQLite3 (`demo_configurator.db`)

---

## 2. 애플리케이션 구조

### 2.1 페이지 구성

| # | 파일 | 기존/신규 | 기능 |
|----|------|---------|------|
| 0 | `app.py` | 기존 | 홈 페이지 및 전체 구성 |
| 1 | `pages/1_EDA.py` | 기존 | 실적 데이터 EDA (필터, 차트, 통계) |
| 2 | `pages/2_Configure.py` | 기존 | 업종 선택 + 실적 변환 |
| 3 | `pages/3_Result.py` | 기존 | 변환 결과 확인 + 다운로드 |
| 4 | `pages/4_ItemFactor.py` | **신규** | 품목별 인자 조회/편집/변환 |
| 5 | `pages/5_DateFactor.py` | **신규** | 일자별 인자 조회/편집/변환 |

### 2.2 모듈 구성

| 모듈 | 기존/신규 | 주요 함수 |
|------|---------|---------|
| `modules/data_loader.py` | 기존 | `load_csv()`, `get_table_summary()` |
| `modules/eda.py` | 기존 | `plot_monthly_trend()` 등 7개 시각화 |
| `modules/converter.py` | 기존 | `convert()`, `compare_data()` |
| `modules/factor_handler.py` | **신규** | `load_factors()`, `transform_factors()`, `save_factors()` |

---

## 3. 신규 기능 상세

### 3.1 인자 데이터 관리

#### 일자별 인자 (TB_BF_DATE_FACTOR)
```python
# 구조
{
    'BASE_DATE': datetime,
    'FACTOR01': float,  # 예: 날씨지수
    'FACTOR02': float,  # 예: 강수량
    'FACTOR03': float,  # 예: 금리
    ...
    'FACTOR50': float
}
```

#### 품목별 인자 (TB_BF_ITEM_FACTOR)
```python
# 구조 (Unique Key: ACCOUNT_ID + ITEM_MST_ID + BASE_DATE)
{
    'ACCOUNT_ID': str,
    'ITEM_MST_ID': str,
    'BASE_DATE': datetime,
    'SALES_FACTOR01': float,  # 예: 할인율
    'SALES_FACTOR02': float,  # 예: 프로모션 여부
    'SALES_FACTOR03': float,  # 예: 경쟁사 가격
    ...
    'SALES_FACTOR50': float
}
```

### 3.2 인자 변환 로직

#### 1) 일자별 인자 변환
- 업종별 관련도에 따라 선택적 적용
- 예: 반도체 업종 → 금리 FACTOR 중심
- 예: 식품 업종 → 날씨 FACTOR 중심

#### 2) 품목별 인자 변환
- 할인율 (SALES_FACTOR01): 업종별 할인율 범위로 스케일링
  ```
  변환 할인율 = 원본 할인율 × 업종별 스케일
  ```
- 프로모션 (SALES_FACTOR02): 업종별 패턴으로 대체
- 경쟁사 가격 (SALES_FACTOR03): 유사 범위로 조정

#### 3) 통합 변환 프로세스
```
실적 데이터 변환 (기존)
    ↓
일자별 인자 변환 (신규)
    ↓
품목별 인자 변환 (신규)
    ↓
결과 통합
```

---

## 4. 페이지 상세 명세

### 4.1 pages/4_ItemFactor.py

**목적**: 품목별 인자 데이터 조회, 편집, 변환

**주요 기능**:
1. **인자 데이터 로드**
   - TB_BF_ITEM_FACTOR CSV 로드
   - 행 수, 기간, 품목 수 표시

2. **필터링**
   - 날짜 범위 선택
   - 거래처 (ACCOUNT_ID) 선택
   - 품목 (ITEM_MST_ID) 선택

3. **데이터 조회**
   - 필터링된 인자 데이터 테이블 표시
   - SALES_FACTOR01~50 값 확인

4. **인자 편집** (선택사항)
   - 특정 행의 인자값 수정
   - 새 행 추가

5. **인자 변환**
   - 업종 선택
   - 스케일 팩터 설정 (기본: 업종별 권장값)
   - "변환" 버튼 클릭
   - 변환된 인자 데이터 미리보기

6. **다운로드**
   - 변환된 인자 데이터 CSV/Excel 다운로드

**UI 구성**:
```
[Filter Section]
  ├─ 날짜 범위
  ├─ 거래처 선택
  └─ 품목 선택

[Data Preview]
  ├─ 필터링된 인자 데이터 테이블
  └─ 기본 통계 (행 수, FACTOR 범위)

[Transform Section]
  ├─ 업종 선택 (라디오 버튼)
  ├─ 스케일 설정
  │  ├─ SALES_FACTOR01 스케일
  │  ├─ SALES_FACTOR02 스케일
  │  └─ SALES_FACTOR03 스케일
  └─ [변환] 버튼

[Result Section]
  ├─ 변환 요약 (메트릭)
  ├─ 원본 vs 변환 비교
  ├─ 미리보기 데이터
  └─ [CSV/Excel 다운로드]
```

### 4.2 pages/5_DateFactor.py

**목적**: 일자별 인자 데이터 조회, 편집, 변환

**주요 기능**:
1. **인자 데이터 로드**
   - TB_BF_DATE_FACTOR CSV 로드
   - 행 수, 기간 표시

2. **필터링**
   - 날짜 범위 선택

3. **데이터 조회**
   - 필터링된 인자 데이터 테이블
   - FACTOR01~50 값 확인

4. **인자 편집** (선택사항)
   - 특정 날짜의 인자값 수정
   - 새 날짜 추가

5. **인자 변환**
   - 업종 선택
   - FACTOR 적용 여부 선택 (체크박스)
     - FACTOR01 (날씨): 식품 업종 중심
     - FACTOR02 (강수량): 식품 업종 중심
     - FACTOR03 (금리): 자동차, 화학 업종 중심
   - 스케일 팩터 설정
   - "변환" 버튼 클릭

6. **다운로드**
   - 변환된 인자 데이터 CSV/Excel 다운로드

**UI 구성**:
```
[Filter Section]
  └─ 날짜 범위

[Data Preview]
  ├─ 필터링된 인자 데이터 테이블
  └─ 기본 통계 (행 수, FACTOR 범위)

[Transform Section]
  ├─ 업종 선택 (라디오 버튼)
  ├─ FACTOR 적용 선택
  │  ├─ ☑ FACTOR01 (날씨)
  │  ├─ ☑ FACTOR02 (강수량)
  │  └─ ☑ FACTOR03 (금리)
  ├─ 스케일 설정
  │  ├─ FACTOR01 스케일
  │  ├─ FACTOR02 스케일
  │  └─ FACTOR03 스케일
  └─ [변환] 버튼

[Result Section]
  ├─ 변환 요약 (메트릭)
  ├─ 원본 vs 변환 비교
  ├─ 미리보기 데이터
  └─ [CSV/Excel 다운로드]
```

---

## 5. 모듈 상세 명세

### 5.1 modules/factor_handler.py

**목적**: 인자 데이터 로드, 변환, 저장

**주요 함수**:

#### 1) load_date_factors(filepath)
```python
def load_date_factors(filepath):
    """
    일자별 인자 CSV 로드
    
    Args:
        filepath (str): CSV 파일 경로
    
    Returns:
        pd.DataFrame: 일자별 인자 데이터
    """
```

#### 2) load_item_factors(filepath)
```python
def load_item_factors(filepath):
    """
    품목별 인자 CSV 로드
    
    Args:
        filepath (str): CSV 파일 경로
    
    Returns:
        pd.DataFrame: 품목별 인자 데이터
    """
```

#### 3) transform_date_factors(df, industry_id, options=None)
```python
def transform_date_factors(df, industry_id, options=None):
    """
    일자별 인자 변환
    
    Args:
        df (pd.DataFrame): 원본 인자 데이터
        industry_id (str): 업종 ID
        options (dict): 변환 옵션
          - apply_factors: FACTOR 적용 여부 (default: [True]*50)
          - custom_scales: 커스텀 스케일 (default: None, 업종값 사용)
    
    Returns:
        pd.DataFrame: 변환된 인자 데이터
    """
```

#### 4) transform_item_factors(df, industry_id, options=None)
```python
def transform_item_factors(df, industry_id, options=None):
    """
    품목별 인자 변환
    
    Args:
        df (pd.DataFrame): 원본 인자 데이터
        industry_id (str): 업종 ID
        options (dict): 변환 옵션
          - custom_sales_factor01_scale: 할인율 스케일
          - custom_sales_factor02_scale: 프로모션 스케일
          - custom_sales_factor03_scale: 경쟁사가격 스케일
    
    Returns:
        pd.DataFrame: 변환된 인자 데이터
    """
```

#### 5) compare_factors(df_original, df_transformed)
```python
def compare_factors(df_original, df_transformed):
    """
    원본 vs 변환 인자 비교
    
    Returns:
        dict: 비교 결과 (행 수, 값 범위, 통계)
    """
```

#### 6) export_factors_csv(df, filepath)
```python
def export_factors_csv(df, filepath):
    """
    인자 데이터를 CSV로 내보내기
    
    Returns:
        bool: 성공 여부
    """
```

---

## 6. 업종별 인자 설정

### 6.1 일자별 인자 설정 (업종별)

```json
{
  "반도체": {
    "factor_relevance": {
      "FACTOR01": 0.5,   // 날씨: 낮은 관련도
      "FACTOR02": 0.3,   // 강수량: 낮음
      "FACTOR03": 0.9    // 금리: 높음
    },
    "factor_scales": [1.0, 1.0, 1.2, ...]
  },
  "자동차": {
    "factor_relevance": {
      "FACTOR01": 0.6,
      "FACTOR02": 0.7,
      "FACTOR03": 0.8
    },
    "factor_scales": [1.0, 1.0, 1.0, ...]
  },
  "식품": {
    "factor_relevance": {
      "FACTOR01": 0.95,  // 날씨: 높음
      "FACTOR02": 0.9,   // 강수량: 높음
      "FACTOR03": 0.4    // 금리: 낮음
    },
    "factor_scales": [1.5, 1.3, 0.5, ...]
  }
}
```

### 6.2 품목별 인자 설정 (업종별)

```json
{
  "반도체": {
    "sales_factor01": {  // 할인율
      "min_scale": 0.8,
      "max_scale": 1.2,
      "description": "반도체 할인율 범위"
    },
    "sales_factor02": {  // 프로모션
      "pattern": "중단기 집중 프로모션",
      "frequency": 0.3   // 30% 확률
    },
    "sales_factor03": {  // 경쟁사 가격
      "min_scale": 0.9,
      "max_scale": 1.1
    }
  }
}
```

---

## 7. 데이터 흐름

### 7.1 통합 변환 프로세스

```
입력 데이터
├─ 실적 (ACTUAL_SALES)
├─ 일자별 인자 (DATE_FACTOR)
└─ 품목별 인자 (ITEM_FACTOR)

        ↓

[Phase 1] 실적 변환 (기존)
  └─ convert(df_actual, industry_id, options)

[Phase 2] 일자별 인자 변환 (신규)
  └─ transform_date_factors(df_date_factor, industry_id, options)

[Phase 3] 품목별 인자 변환 (신규)
  └─ transform_item_factors(df_item_factor, industry_id, options)

        ↓

출력 데이터
├─ 변환된 실적
├─ 변환된 일자별 인자
└─ 변환된 품목별 인자
```

### 7.2 페이지 네비게이션

```
app.py (홈)
├─ 1_EDA.py (실적 분석)
├─ 2_Configure.py (실적 변환)
├─ 3_Result.py (실적 결과)
├─ 4_ItemFactor.py (품목별 인자)
└─ 5_DateFactor.py (일자별 인자)
```

---

## 8. 배포 및 테스트

### 8.1 테스트 스크립트
- `test_converter.py`: 기존 실적 변환 테스트
- `test_factors.py`: 신규 인자 변환 테스트 (신규)

### 8.2 시작 방법
```bash
streamlit run app.py
```

### 8.3 사용 시나리오
1. 1_EDA에서 실적 데이터 분석
2. 4_ItemFactor에서 품목별 인자 변환
3. 5_DateFactor에서 일자별 인자 변환
4. 2_Configure에서 통합 변환 (예정)
5. 3_Result에서 최종 결과 확인

---

## 9. 버전 히스토리

| 버전 | 날짜 | 변경사항 |
|------|------|---------|
| 1.0.0 | 2026-04-28 | 초기 릴리즈 (실적 변환) |
| 1.1.0 | 2026-04-29 | 인자 데이터 관리 추가 |

---

## 10. 참고 자료

### SQL 쿼리
```sql
-- 실적 + 마스터 데이터 JOIN
SELECT a.ID, a.BASE_DATE, a.QTY, a.AMT,
       b.ITEM_NM, c.ACCOUNT_NM, d.COMN_CD_NM
FROM TB_CM_ACTUAL_SALES a
LEFT JOIN TB_CM_ITEM_MST b ON a.ITEM_MST_ID = b.ID
LEFT JOIN TB_DP_ACCOUNT_MST c ON a.ACCOUNT_ID = c.ID
LEFT JOIN TB_AD_COMN_CODE d ON a.SO_STATUS_ID = d.ID
```

### 파일 경로
```
C:\Users\lotus\DemoCreate\
├─ data/
│  ├─ TB_CM_ACTUAL_SALES_202604281652.csv (실적)
│  ├─ TB_BF_ITEM_FACTOR.csv (품목별 인자)
│  └─ TB_BF_DATE_FACTOR.csv (일자별 인자)
├─ modules/
│  ├─ converter.py
│  └─ factor_handler.py (신규)
├─ pages/
│  ├─ 1_EDA.py
│  ├─ 2_Configure.py
│  ├─ 3_Result.py
│  ├─ 4_ItemFactor.py (신규)
│  └─ 5_DateFactor.py (신규)
└─ app.py
```
