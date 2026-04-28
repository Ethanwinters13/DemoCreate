"""
EDA 모듈 시각화 테스트

실행: python test_eda.py
차트는 각 test_*.html 파일로 저장됩니다.
"""
from pathlib import Path
from modules.data_loader import load_csv
from modules.eda import (
    get_summary_stats,
    plot_monthly_trend,
    plot_item_top10,
    plot_account_distribution,
    plot_qty_histogram,
    plot_yearly_heatmap,
    plot_qty_vs_amt_scatter,
    get_status_distribution
)

CSV_PATH = Path(__file__).parent / "data" / "TB_CM_ACTUAL_SALES_202604281652.csv"

def print_section(title):
    """섹션 제목 출력"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def main():
    print_section("[TEST] EDA Module - 시각화 테스트")

    # Step 1: CSV 로드
    print("\n[Step 1] CSV 데이터 로드")
    try:
        df = load_csv(CSV_PATH)
        print(f"  [OK] 로드 성공: {len(df):,}행")
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return False

    # Step 2: 기초 통계
    print("\n[Step 2] 기초 통계")
    stats = get_summary_stats(df)
    print(f"  기간: {stats['date_range']['start']} ~ {stats['date_range']['end']}")
    print(f"  품목: {stats['items']}, 고객사: {stats['accounts']}")
    print(f"  QTY - 합계: {stats['qty']['total']:,.0f}, 평균: {stats['qty']['mean']:,.0f}")
    print(f"  AMT - 합계: {stats['amt']['total']:,.0f}, 평균: {stats['amt']['mean']:,.0f}")

    # Step 3: 차트 생성 및 저장
    print("\n[Step 3] 시각화 차트 생성")

    charts = {
        'monthly_trend': (plot_monthly_trend, '월별 QTY/AMT 추이'),
        'item_top10': (plot_item_top10, '품목별 QTY Top10'),
        'account_dist': (plot_account_distribution, '고객사별 AMT 분포'),
        'qty_histogram': (plot_qty_histogram, 'QTY 히스토그램'),
        'yearly_heatmap': (plot_yearly_heatmap, '연도별 월별 히트맵'),
        'qty_vs_amt': (plot_qty_vs_amt_scatter, 'QTY vs AMT 산점도'),
        'status_dist': (get_status_distribution, '수주 상태별 분포')
    }

    for chart_name, (chart_func, chart_title) in charts.items():
        try:
            fig = chart_func(df)
            output_file = Path(__file__).parent / f"test_{chart_name}.html"
            fig.write_html(str(output_file))
            print(f"  [OK] {chart_title:30s} -> test_{chart_name}.html")
        except Exception as e:
            print(f"  [ERROR] {chart_title:30s} - {str(e)}")

    print_section("[OK] EDA 시각화 테스트 완료!")
    print(f"\n생성된 파일 위치: {Path(__file__).parent}")
    print(f"HTML 파일을 브라우저에서 열어서 차트를 확인하세요.")
    return True


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
