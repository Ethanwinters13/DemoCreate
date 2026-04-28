"""
SQLite 데이터베이스 연결 및 쿼리 처리 모듈 (로컬 개발용)
"""
import sqlite3
import pandas as pd
import streamlit as st
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "demo_configurator.db"

def get_connection():
    """
    SQLite 데이터베이스 연결 반환

    Returns:
        sqlite3.Connection: 데이터베이스 연결 객체

    Raises:
        Exception: 연결 실패 시 예외 발생
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        raise Exception(f"데이터베이스 연결 실패: {str(e)}")


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
        print(f"쿼리 실행 오류: {str(e)}")
        return pd.DataFrame()


def execute_insert(df, table_name, batch_size=1000, if_exists='replace'):
    """
    pandas DataFrame을 SQLite 테이블에 저장

    Args:
        df (pd.DataFrame): 삽입할 데이터프레임
        table_name (str): 대상 테이블명
        batch_size (int): 배치 사이즈 (기본값: 1000)
        if_exists (str): 테이블 존재 시 동작 ('replace', 'append', 'fail')

    Returns:
        bool: 성공 여부
    """
    try:
        conn = get_connection()
        total_rows = len(df)

        df.to_sql(table_name, conn, if_exists=if_exists, index=False)

        conn.close()
        print(f"[OK] {total_rows:,}행이 {table_name}에 저장되었습니다.")
        return True

    except Exception as e:
        print(f"Insert 오류: {str(e)}")
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
        sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = execute_query(sql, (table_name,))
        return len(result) > 0

    except Exception as e:
        print(f"테이블 확인 오류: {str(e)}")
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
        print(f"행 수 조회 오류: {str(e)}")
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
        print(f"연결 테스트 실패: {str(e)}")
        return False
