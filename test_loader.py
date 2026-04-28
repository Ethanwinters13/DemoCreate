"""
CSV 적재 모듈 테스트

실행: python test_loader.py
"""
from pathlib import Path
from modules.data_loader import load_csv, insert_to_db, get_table_summary

CSV_PATH = Path(__file__).parent / "data" / "TB_CM_ACTUAL_SALES_202604281652.csv"

def print_section(title):
    """섹션 제목 출력"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def main():
    print_section("[TEST] CSV Loader - 적재 모듈 테스트")

    # Step 1: CSV 로드
    print("\n[Step 1] CSV 파일 로드")
    try:
        df = load_csv(CSV_PATH)
        print(f"  [OK] 로드 성공: {len(df):,}행 × {len(df.columns)}컬럼")
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return False

    # Step 2: 데이터 검증
    print("\n[Step 2] 데이터 검증")
    print(f"  ID 고유값: {df['ID'].nunique():,}")
    print(f"  NULL 검사:")
    null_counts = df.isna().sum()
    for col, count in null_counts[null_counts > 0].items():
        print(f"    - {col}: {count:,}")

    # Step 3: 기존 데이터 확인
    print("\n[Step 3] 기존 테이블 상태")
    summary = get_table_summary("TB_CM_ACTUAL_SALES")
    if summary.get('exists'):
        print(f"  [OK] 테이블 존재")
        print(f"  현재 행 수: {summary.get('row_count', 0):,}")
        print(f"  데이터 기간: {summary.get('min_date')} ~ {summary.get('max_date')}")
    else:
        print(f"  테이블이 비어있습니다 (초기 적재 필요)")

    # Step 4: CSV 적재 (중복 제외)
    print("\n[Step 4] CSV 데이터 적재")
    result = insert_to_db(df, skip_duplicates=True)

    if result['success']:
        print(f"  [OK] 적재 완료")
        print(f"  적재된 행: {result['inserted']:,}")
        print(f"  스킵된 행: {result['skipped']:,}")
        print(f"  총 행: {result['total']:,}")
    else:
        print(f"  [ERROR] {result.get('error', '알 수 없는 오류')}")
        return False

    # Step 5: 적재 후 통계
    print("\n[Step 5] 적재 후 테이블 통계")
    summary = get_table_summary("TB_CM_ACTUAL_SALES")
    if summary.get('exists'):
        print(f"  행 수: {summary.get('row_count', 0):,}")
        print(f"  품목 수: {summary.get('item_count', 0)}")
        print(f"  고객사 수: {summary.get('account_count', 0)}")
        print(f"  데이터 기간: {summary.get('min_date')} ~ {summary.get('max_date')}")
        print(f"  QTY 평균: {summary.get('avg_qty', 0):,.0f}")
        print(f"  AMT 평균: {summary.get('avg_amt', 0):,.0f}")
        print(f"  QTY 합계: {summary.get('total_qty', 0):,.0f}")
        print(f"  AMT 합계: {summary.get('total_amt', 0):,.0f}")

    print_section("[OK] CSV 적재 테스트 완료!")
    return True


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
