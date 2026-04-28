"""
Converter Module 변환 엔진 테스트

실행: python test_converter.py
"""
from pathlib import Path
from modules.data_loader import load_csv
from modules.converter import convert, get_industry_list, compare_data, preview
import pandas as pd


CSV_PATH = Path(__file__).parent / "data" / "TB_CM_ACTUAL_SALES_202604281652.csv"


def print_section(title):
    """섹션 제목 출력"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def main():
    print_section("[TEST] Converter Module - 데이터 변환 테스트")

    # Step 1: CSV 로드
    print("\n[Step 1] CSV 데이터 로드")
    try:
        df = load_csv(CSV_PATH)
        print(f"  [OK] 로드 성공: {len(df):,}행")
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return False

    # Step 2: 업종 목록 확인
    print("\n[Step 2] 지원 업종 확인")
    try:
        industries = get_industry_list()
        print(f"  [OK] 지원 업종: {len(industries)}개")
        for ind in industries:
            print(f"      - {ind['id']:10s}: {ind['name']:8s} (QTY scale: {ind['qty_scale']}, AMT scale: {ind['amt_scale']})")
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return False

    # Step 3: 각 업종별 변환 테스트
    print("\n[Step 3] 업종별 변환 테스트")

    test_options = [
        {'apply_noise': False, 'custom_qty_scale': None, 'custom_amt_scale': None},
        {'apply_noise': True, 'custom_qty_scale': 1.5, 'custom_amt_scale': 1.2},
    ]

    for industry in industries[:2]:  # 처음 2개 업종만 테스트
        industry_id = industry['id']
        industry_name = industry['name']

        print(f"\n  [{industry_name}]")

        # 노이즈 없음
        try:
            options = test_options[0]
            df_conv = convert(df, industry_id, options)
            comparison = compare_data(df, df_conv)

            orig = comparison['original']
            conv = comparison['converted']
            qty_change = (conv['qty_total'] / orig['qty_total'] - 1) * 100
            amt_change = (conv['amt_total'] / orig['amt_total'] - 1) * 100

            print(f"    [OK] 변환 완료 (노이즈 미적용)")
            print(f"        - QTY 변화: {qty_change:+.1f}%")
            print(f"        - AMT 변화: {amt_change:+.1f}%")
            print(f"        - 행 수: {conv['rows']:,}행")

        except Exception as e:
            print(f"    [ERROR] {str(e)}")

    # Step 4: 세부 비교 분석
    print("\n[Step 4] 세부 비교 분석")
    try:
        # 첫 번째 업종으로 변환
        industry_id = industries[0]['id']
        industry_name = industries[0]['name']

        options = {'apply_noise': False, 'custom_qty_scale': None, 'custom_amt_scale': None}
        df_converted = convert(df, industry_id, options)

        print(f"\n  업종: {industry_name}")
        print(f"  원본 vs 변환 비교:")

        comparison = compare_data(df, df_converted)
        orig = comparison['original']
        conv = comparison['converted']

        print(f"\n  원본 데이터:")
        print(f"    - 행 수: {orig['rows']:,}")
        print(f"    - QTY 합계: {orig['qty_total']:,.0f}")
        print(f"    - QTY 평균: {orig['qty_avg']:,.0f}")
        print(f"    - AMT 합계: {orig['amt_total']:,.0f}")
        print(f"    - AMT 평균: {orig['amt_avg']:,.0f}")

        print(f"\n  변환된 데이터:")
        print(f"    - 행 수: {conv['rows']:,}")
        print(f"    - QTY 합계: {conv['qty_total']:,.0f}")
        print(f"    - QTY 평균: {conv['qty_avg']:,.0f}")
        print(f"    - AMT 합계: {conv['amt_total']:,.0f}")
        print(f"    - AMT 평균: {conv['amt_avg']:,.0f}")

        # 미리보기
        print(f"\n  변환 결과 미리보기 (상위 5행):")
        preview_df = preview(df_converted, n=5)
        print(f"\n{preview_df.to_string(index=False)}")

        # 컬럼 확인
        print(f"\n  변환 결과 컬럼:")
        print(f"    {list(df_converted.columns)}")

    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return False

    print_section("[OK] Converter 변환 테스트 완료!")
    return True


if __name__ == '__main__':
    import sys
    import warnings
    warnings.filterwarnings('ignore')
    success = main()
    sys.exit(0 if success else 1)
