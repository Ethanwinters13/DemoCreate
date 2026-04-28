"""
CSV 로드 및 SQLite 데이터베이스 초기화 테스트

실행: python test_db.py
"""
import pandas as pd
from pathlib import Path
from modules.db_handler import (
    get_connection,
    execute_query,
    execute_insert,
    check_table_exists,
    get_row_count,
    test_connection
)

CSV_PATH = Path(__file__).parent / "data" / "TB_CM_ACTUAL_SALES_202604281652.csv"

def print_section(title):
    """섹션 제목 출력"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def main():
    print_section("[TEST] T3 Demo Configurator - CSV & SQLite 초기화")

    # Step 1: CSV 파일 확인
    print("\n[Step 1] CSV 파일 확인")
    if CSV_PATH.exists():
        size_mb = CSV_PATH.stat().st_size / (1024 * 1024)
        print(f"  OK 파일 존재: {CSV_PATH}")
        print(f"  DATA 파일 크기: {size_mb:.1f} MB")
    else:
        print(f"  ERROR 파일 없음: {CSV_PATH}")
        return False

    # Step 2: CSV 데이터 로드
    print("\n[Step 2] CSV 데이터 로드")
    try:
        df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
        print(f"  OK 로드 성공")
        print(f"  CHART 데이터 크기: {len(df):,} 행 × {len(df.columns)} 컬럼")
        print(f"\n  컬럼 목록:")
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = df[col].isna().sum()
            print(f"    - {col:25s} {dtype:15s} (NULL: {null_count:,})")
    except Exception as e:
        print(f"  ERROR 로드 실패: {str(e)}")
        return False

    # Step 3: 데이터 타입 변환
    print("\n[Step 3] 데이터 타입 변환")
    try:
        if 'BASE_DATE' in df.columns:
            df['BASE_DATE'] = pd.to_datetime(df['BASE_DATE'])
            print(f"  OK BASE_DATE → datetime 변환")

        numeric_cols = ['QTY', 'AMT', 'QTY_CORRECTION', 'AMT_CORRECTION', 'OUTLIER_YN']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        print(f"  OK 숫자 컬럼 변환 완료")
    except Exception as e:
        print(f"  WARN  변환 오류: {str(e)}")

    # Step 4: SQLite 연결 테스트
    print("\n[Step 4] SQLite 데이터베이스 연결")
    if test_connection():
        print(f"  OK 연결 성공")
    else:
        print(f"  ERROR 연결 실패")
        return False

    # Step 5: 데이터 기초 통계
    print("\n[Step 5] 데이터 기초 통계")
    print(f"  기간: {df['BASE_DATE'].min()} ~ {df['BASE_DATE'].max()}")
    print(f"  QTY 합계: {df['QTY'].sum():,.0f}")
    print(f"  AMT 합계: {df['AMT'].sum():,.0f}")
    print(f"  고유 품목: {df['ITEM_MST_ID'].nunique()}")
    print(f"  고유 고객사: {df['ACCOUNT_ID'].nunique()}")
    print(f"  고유 상태: {df['SO_STATUS_ID'].nunique()}")

    # Step 6: SQLite 테이블 생성
    print("\n[Step 6] SQLite 테이블 생성")
    table_name = "TB_CM_ACTUAL_SALES"
    if execute_insert(df, table_name, if_exists='replace'):
        print(f"  OK 테이블 '{table_name}' 생성 완료")
    else:
        print(f"  ERROR 테이블 생성 실패")
        return False

    # Step 7: 테이블 확인
    print("\n[Step 7] 테이블 확인")
    if check_table_exists(table_name):
        row_count = get_row_count(table_name)
        print(f"  OK 테이블 존재")
        print(f"  DATA 행 수: {row_count:,}")

        # 샘플 데이터 조회
        sample_query = f"SELECT * FROM {table_name} LIMIT 5"
        df_sample = execute_query(sample_query)
        if not df_sample.empty:
            print(f"\n  샘플 데이터 (상위 5행):")
            print(f"  {df_sample.to_string()}")
    else:
        print(f"  ERROR 테이블 확인 실패")
        return False

    print_section("OK 초기화 완료! SQLite 준비됨")
    return True


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
