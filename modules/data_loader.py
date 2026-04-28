"""
CSV 데이터 적재 및 DB 삽입 모듈
"""
import pandas as pd
from pathlib import Path
import streamlit as st
from .db_handler import execute_query, execute_insert, check_table_exists, get_row_count

def load_csv(filepath, encoding='utf-8-sig'):
    """
    CSV 파일을 읽어 pandas DataFrame으로 반환

    Args:
        filepath (str): CSV 파일 경로
        encoding (str): 파일 인코딩 (기본값: utf-8-sig)

    Returns:
        pd.DataFrame: 로드된 데이터

    Raises:
        FileNotFoundError: 파일이 없을 때
        Exception: 읽기 실패 시
    """
    try:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filepath}")

        df = pd.read_csv(path, encoding=encoding, low_memory=False)

        # 데이터 타입 변환
        if 'BASE_DATE' in df.columns:
            df['BASE_DATE'] = pd.to_datetime(df['BASE_DATE'], errors='coerce')

        numeric_cols = ['QTY', 'AMT', 'QTY_CORRECTION', 'AMT_CORRECTION', 'OUTLIER_YN']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    except FileNotFoundError as e:
        raise FileNotFoundError(f"CSV 파일 없음: {str(e)}")
    except Exception as e:
        raise Exception(f"CSV 읽기 오류: {str(e)}")


def get_existing_ids(table_name):
    """
    기존 DB에 있는 ID 목록 반환 (중복 체크용)

    Args:
        table_name (str): 테이블명

    Returns:
        set: 기존 ID 집합
    """
    try:
        sql = f"SELECT DISTINCT ID FROM {table_name}"
        result = execute_query(sql)
        return set(result['ID'].tolist()) if not result.empty else set()
    except Exception as e:
        print(f"기존 ID 조회 오류: {str(e)}")
        return set()


def insert_to_db(df, table_name='TB_CM_ACTUAL_SALES', batch_size=1000, skip_duplicates=True):
    """
    pandas DataFrame을 SQLite 테이블에 적재

    Args:
        df (pd.DataFrame): 삽입할 데이터프레임
        table_name (str): 대상 테이블명
        batch_size (int): 배치 사이즈 (기본값: 1000)
        skip_duplicates (bool): 중복 행 스킵 여부

    Returns:
        dict: {'success': bool, 'inserted': int, 'skipped': int, 'total': int}
    """
    try:
        total_rows = len(df)
        inserted_rows = 0
        skipped_rows = 0

        if skip_duplicates and check_table_exists(table_name):
            existing_ids = get_existing_ids(table_name)
            df_new = df[~df['ID'].isin(existing_ids)].copy()
            skipped_rows = total_rows - len(df_new)
            df = df_new

        if len(df) == 0:
            st.warning(f"⚠️ 새로운 데이터가 없습니다. (모두 중복)")
            return {
                'success': True,
                'inserted': 0,
                'skipped': skipped_rows,
                'total': total_rows
            }

        # Streamlit progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # 배치 단위로 insert
        total_batches = (len(df) + batch_size - 1) // batch_size
        for batch_idx in range(0, len(df), batch_size):
            batch_df = df.iloc[batch_idx:batch_idx+batch_size]
            execute_insert(batch_df, table_name, if_exists='append')

            inserted_rows += len(batch_df)
            progress = (batch_idx + batch_size) / len(df)
            progress_bar.progress(min(progress, 1.0))
            status_text.text(f"진행중: {inserted_rows:,}/{len(df):,}")

        progress_bar.progress(1.0)
        status_text.text(f"완료: {inserted_rows:,}/{len(df):,}")

        st.success(
            f"[OK] {inserted_rows:,}행이 {table_name}에 적재되었습니다. "
            f"(스킵: {skipped_rows:,})"
        )

        return {
            'success': True,
            'inserted': inserted_rows,
            'skipped': skipped_rows,
            'total': total_rows
        }

    except Exception as e:
        st.error(f"적재 오류: {str(e)}")
        return {
            'success': False,
            'inserted': 0,
            'skipped': 0,
            'total': total_rows,
            'error': str(e)
        }


def get_table_summary(table_name):
    """
    테이블의 기초 통계 반환

    Args:
        table_name (str): 테이블명

    Returns:
        dict: 통계 정보
    """
    try:
        if not check_table_exists(table_name):
            return {'exists': False, 'row_count': 0}

        row_count = get_row_count(table_name)

        # 기초 통계 쿼리
        stats_query = f"""
            SELECT
                COUNT(*) as total_rows,
                MIN(BASE_DATE) as min_date,
                MAX(BASE_DATE) as max_date,
                COUNT(DISTINCT ITEM_MST_ID) as item_count,
                COUNT(DISTINCT ACCOUNT_ID) as account_count,
                ROUND(AVG(QTY), 2) as avg_qty,
                ROUND(AVG(AMT), 2) as avg_amt,
                SUM(QTY) as total_qty,
                SUM(AMT) as total_amt
            FROM {table_name}
        """
        result = execute_query(stats_query)

        if result.empty:
            return {'exists': True, 'row_count': 0}

        row = result.iloc[0]
        return {
            'exists': True,
            'row_count': row_count,
            'total_rows': int(row['total_rows']),
            'min_date': row['min_date'],
            'max_date': row['max_date'],
            'item_count': int(row['item_count']),
            'account_count': int(row['account_count']),
            'avg_qty': float(row['avg_qty']),
            'avg_amt': float(row['avg_amt']),
            'total_qty': float(row['total_qty']),
            'total_amt': float(row['total_amt'])
        }

    except Exception as e:
        print(f"통계 조회 오류: {str(e)}")
        return {'exists': False, 'error': str(e)}
