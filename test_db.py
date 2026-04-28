"""
데이터베이스 연결 테스트 스크립트

실행: python test_db.py
"""
import os
import sys
from dotenv import load_dotenv
from modules.db_handler import (
    test_connection,
    execute_query,
    check_table_exists,
    get_row_count
)

def print_section(title):
    """섹션 제목 출력"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def main():
    print_section("🔧 T³ Demo Configurator - DB 연결 테스트")

    # .env 파일 확인
    print("\n[1] 환경 설정 확인")
    load_dotenv()

    env_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASS', 'DB_DRIVER']
    missing_vars = []

    for var in env_vars:
        value = os.getenv(var)
        if var == 'DB_PASS':
            status = "✅ 설정됨" if value else "❌ 미설정"
            print(f"  {var}: {status}")
        else:
            status = "✅" if value else "❌"
            print(f"  {var}: {status} {value if value else '(미설정)'}")
            if not value and var != 'DB_PASS':
                missing_vars.append(var)

    if missing_vars:
        print(f"\n⚠️  다음 환경 변수가 미설정되었습니다: {', '.join(missing_vars)}")
        print("📝 .env 파일을 생성하고 설정해주세요.\n")
        return False

    # 연결 테스트
    print("\n[2] 데이터베이스 연결 테스트")
    if test_connection():
        print("  ✅ 데이터베이스 연결 성공!")
    else:
        print("  ❌ 데이터베이스 연결 실패")
        return False

    # TB_CM_ACTUAL_SALES 테이블 확인
    print("\n[3] TB_CM_ACTUAL_SALES 테이블 확인")
    if check_table_exists('TB_CM_ACTUAL_SALES'):
        print("  ✅ 테이블 존재")
        row_count = get_row_count('TB_CM_ACTUAL_SALES')
        print(f"  📊 행 수: {row_count:,}")

        # 테이블 스키마 조회
        print("\n[4] 테이블 컬럼 정보")
        schema_query = """
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'TB_CM_ACTUAL_SALES'
            ORDER BY ORDINAL_POSITION
        """
        df_schema = execute_query(schema_query)
        if not df_schema.empty:
            for idx, row in df_schema.iterrows():
                nullable = "NULL 허용" if row['IS_NULLABLE'] == 'YES' else "NOT NULL"
                print(f"  {row['COLUMN_NAME']:25s} {row['DATA_TYPE']:15s} [{nullable}]")
        else:
            print("  ❌ 스키마 조회 실패")
    else:
        print("  ❌ 테이블이 존재하지 않습니다")
        return False

    # 샘플 데이터 조회
    print("\n[5] 샘플 데이터 (상위 3행)")
    sample_query = "SELECT TOP 3 * FROM TB_CM_ACTUAL_SALES"
    df_sample = execute_query(sample_query)
    if not df_sample.empty:
        print(df_sample.to_string(index=False))
    else:
        print("  ❌ 데이터 조회 실패")

    print_section("✅ DB 연결 테스트 완료!")
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
