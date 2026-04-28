"""
MSSQL 데이터베이스 연결 및 쿼리 처리 모듈
"""
import os
import pandas as pd
import pyodbc
from dotenv import load_dotenv
import streamlit as st

# .env 파일 로드
load_dotenv()

def get_connection():
    """
    MSSQL 데이터베이스 연결 반환

    Returns:
        pyodbc.Connection: 데이터베이스 연결 객체

    Raises:
        Exception: 연결 실패 시 예외 발생
    """
    try:
        host = os.getenv('DB_HOST')
        port = os.getenv('DB_PORT')
        database = os.getenv('DB_NAME')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASS')
        driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')

        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={host},{port};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
        )

        conn = pyodbc.connect(conn_str)
        return conn

    except pyodbc.Error as e:
        raise Exception(f"데이터베이스 연결 실패: {str(e)}")
    except Exception as e:
        raise Exception(f"환경 설정 오류: {str(e)}")


def execute_query(sql, params=None):
    """
    SQL 쿼리 실행 및 결과를 pandas DataFrame으로 반환

    Args:
        sql (str): 실행할 SQL 쿼리
        params (tuple, optional): SQL 파라미터

    Returns:
        pd.DataFrame: 쿼리 결과
    """
    try:
        conn = get_connection()
        if params:
            df = pd.read_sql_query(sql, conn, params=params)
        else:
            df = pd.read_sql_query(sql, conn)
        conn.close()
        return df

    except Exception as e:
        st.error(f"쿼리 실행 오류: {str(e)}")
        return pd.DataFrame()


def execute_insert(df, table_name, batch_size=1000):
    """
    pandas DataFrame을 MSSQL 테이블에 bulk insert

    Args:
        df (pd.DataFrame): 삽입할 데이터프레임
        table_name (str): 대상 테이블명
        batch_size (int): 배치 사이즈 (기본값: 1000)

    Returns:
        bool: 성공 여부
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 컬럼명 가져오기
        columns = df.columns.tolist()
        placeholders = ','.join(['?' for _ in columns])
        col_str = ','.join(columns)

        insert_sql = f"INSERT INTO {table_name} ({col_str}) VALUES ({placeholders})"

        # 배치 단위로 insert
        total_rows = len(df)
        for i in range(0, total_rows, batch_size):
            batch_df = df.iloc[i:i+batch_size]
            rows = [tuple(row) for row in batch_df.values]
            cursor.executemany(insert_sql, rows)

        conn.commit()
        conn.close()

        st.success(f"✅ {total_rows:,}행이 {table_name}에 삽입되었습니다.")
        return True

    except Exception as e:
        st.error(f"Insert 오류: {str(e)}")
        return False


def check_table_exists(table_name):
    """
    테이블 존재 여부 확인

    Args:
        table_name (str): 확인할 테이블명

    Returns:
        bool: 테이블 존재 여부
    """
    try:
        sql = f"""
            SELECT CASE
                WHEN EXISTS(
                    SELECT 1 FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_NAME = ?
                ) THEN 1 ELSE 0
            END as result
        """
        result = execute_query(sql, (table_name,))
        return bool(result['result'].iloc[0]) if len(result) > 0 else False

    except Exception as e:
        st.error(f"테이블 확인 오류: {str(e)}")
        return False


def get_row_count(table_name):
    """
    테이블 행 수 반환

    Args:
        table_name (str): 테이블명

    Returns:
        int: 행 수
    """
    try:
        sql = f"SELECT COUNT(*) as count FROM {table_name}"
        result = execute_query(sql)
        return int(result['count'].iloc[0]) if len(result) > 0 else 0

    except Exception as e:
        st.error(f"행 수 조회 오류: {str(e)}")
        return 0


def test_connection():
    """
    데이터베이스 연결 테스트

    Returns:
        bool: 연결 성공 여부
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return True
    except Exception as e:
        st.error(f"연결 테스트 실패: {str(e)}")
        return False
