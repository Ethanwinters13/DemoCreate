"""
인자 데이터 처리 모듈 - 일자별/품목별 인자 변환
"""
import pandas as pd
import numpy as np
from pathlib import Path
import streamlit as st
from modules.converter import load_industry_config


def load_date_factors(filepath):
    """
    일자별 인자 CSV 로드

    Args:
        filepath (str or Path): CSV 파일 경로

    Returns:
        pd.DataFrame: 일자별 인자 데이터
    """
    try:
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        df['BASE_DATE'] = pd.to_datetime(df['BASE_DATE'])
        return df
    except Exception as e:
        raise Exception(f"인자 파일 로드 오류: {str(e)}")


def load_item_factors(filepath):
    """
    품목별 인자 CSV 로드

    Args:
        filepath (str or Path): CSV 파일 경로

    Returns:
        pd.DataFrame: 품목별 인자 데이터
    """
    try:
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        df['BASE_DATE'] = pd.to_datetime(df['BASE_DATE'])
        return df
    except Exception as e:
        raise Exception(f"인자 파일 로드 오류: {str(e)}")


def transform_date_factors(df, industry_id, options=None):
    """
    일자별 인자 변환 (FACTOR1~50)

    Args:
        df (pd.DataFrame): 원본 인자 데이터
        industry_id (str): 업종 ID
        options (dict): 변환 옵션
          - apply_factors: FACTOR 적용 여부 dict
          - custom_scales: 커스텀 스케일 dict

    Returns:
        pd.DataFrame: 변환된 인자 데이터
    """
    try:
        config = load_industry_config()
        options = options or {}

        # 업종 설정 찾기
        industry_config = None
        for ind in config['industries']:
            if ind['id'] == industry_id:
                industry_config = ind
                break

        if not industry_config:
            raise ValueError(f"지원하지 않는 업종: {industry_id}")

        df_transformed = df.copy()

        # FACTOR 컬럼 찾기 (FACTOR1~50)
        factor_columns = [col for col in df.columns if col.startswith('FACTOR') and col[6:].replace('_', '').isdigit()]
        factor_columns = sorted(factor_columns, key=lambda x: int(x.replace('FACTOR', '')))

        st.progress(10, text="1/5: 인자 데이터 복사 중...")

        # 적용할 FACTOR 결정
        apply_factors = options.get('apply_factors', {col: True for col in factor_columns})

        # 커스텀 스케일
        custom_scales = options.get('custom_scales', {col: 1.0 for col in factor_columns})

        st.progress(30, text="2/5: 인자 스케일 적용 중...")

        for col in factor_columns:
            if col in df_transformed.columns and apply_factors.get(col, True):
                scale = custom_scales.get(col, 1.0)
                if pd.api.types.is_numeric_dtype(df_transformed[col]):
                    df_transformed[col] = df_transformed[col] * scale

        st.progress(60, text="3/5: 인자값 정규화 중...")

        # 인자값 정규화 (노이즈 추가)
        for col in factor_columns:
            if col in df_transformed.columns and apply_factors.get(col, True):
                if pd.api.types.is_numeric_dtype(df_transformed[col]):
                    noise = np.random.uniform(0.95, 1.05, len(df_transformed))
                    df_transformed[col] = df_transformed[col] * noise

        st.progress(90, text="4/5: 최종 정리 중...")

        df_transformed = df_transformed[df.columns]

        st.progress(100, text="변환 완료!")

        return df_transformed

    except Exception as e:
        st.error(f"변환 오류: {str(e)}")
        raise


def transform_item_factors(df, industry_id, options=None):
    """
    품목별 인자 변환 (SALES_FACTOR1~50)

    Args:
        df (pd.DataFrame): 원본 인자 데이터
        industry_id (str): 업종 ID
        options (dict): 변환 옵션
          - custom_sales_factor01_scale: SALES_FACTOR1 스케일
          - custom_sales_factor02_scale: SALES_FACTOR2 스케일
          - custom_sales_factor03_scale: SALES_FACTOR3 스케일

    Returns:
        pd.DataFrame: 변환된 인자 데이터
    """
    try:
        config = load_industry_config()
        options = options or {}

        # 업종 설정 찾기
        industry_config = None
        for ind in config['industries']:
            if ind['id'] == industry_id:
                industry_config = ind
                break

        if not industry_config:
            raise ValueError(f"지원하지 않는 업종: {industry_id}")

        df_transformed = df.copy()

        st.progress(10, text="1/5: 인자 데이터 복사 중...")

        # 스케일 값 설정
        factor1_scale = options.get('custom_sales_factor01_scale', 1.0)
        factor2_scale = options.get('custom_sales_factor02_scale', 1.0)
        factor3_scale = options.get('custom_sales_factor03_scale', 1.0)

        st.progress(30, text="2/5: SALES_FACTOR1 변환 중...")

        # SALES_FACTOR1 변환
        if 'SALES_FACTOR1' in df_transformed.columns:
            df_transformed['SALES_FACTOR1'] = (
                df['SALES_FACTOR1'] * factor1_scale
            )
            df_transformed['SALES_FACTOR1'] = df_transformed['SALES_FACTOR1'].clip(0.5, 1.5)

        st.progress(50, text="3/5: SALES_FACTOR2 변환 중...")

        # SALES_FACTOR2 변환 (프로모션)
        if 'SALES_FACTOR2' in df_transformed.columns:
            promotion_prob = min(factor2_scale, 1.0)
            df_transformed['SALES_FACTOR2'] = (
                np.random.choice([0, 1], size=len(df_transformed), p=[1-promotion_prob, promotion_prob])
            )

        st.progress(70, text="4/5: SALES_FACTOR3 변환 중...")

        # SALES_FACTOR3 변환
        if 'SALES_FACTOR3' in df_transformed.columns:
            df_transformed['SALES_FACTOR3'] = (
                df['SALES_FACTOR3'] * factor3_scale
            )
            df_transformed['SALES_FACTOR3'] = df_transformed['SALES_FACTOR3'].clip(0.8, 1.2)

        st.progress(90, text="5/5: 최종 정리 중...")

        # 나머지 SALES_FACTOR 유지
        sales_factor_columns = [col for col in df.columns if col.startswith('SALES_FACTOR')]
        for col in sales_factor_columns:
            if col not in ['SALES_FACTOR1', 'SALES_FACTOR2', 'SALES_FACTOR3']:
                if col in df_transformed.columns:
                    df_transformed[col] = df[col]

        st.progress(100, text="변환 완료!")

        return df_transformed

    except Exception as e:
        st.error(f"변환 오류: {str(e)}")
        raise


def compare_factors(df_original, df_transformed):
    """
    원본 vs 변환 인자 비교

    Args:
        df_original (pd.DataFrame): 원본 인자 데이터
        df_transformed (pd.DataFrame): 변환된 인자 데이터

    Returns:
        dict: 비교 결과
    """
    # FACTOR 또는 SALES_FACTOR 컬럼 찾기
    factor_columns = [col for col in df_original.columns if col.startswith(('FACTOR', 'SALES_FACTOR')) and col[-1].isdigit()]

    comparison = {
        'original': {
            'rows': len(df_original),
            'factor_means': {col: df_original[col].mean() if pd.api.types.is_numeric_dtype(df_original[col]) else 0
                           for col in factor_columns},
            'factor_stds': {col: df_original[col].std() if pd.api.types.is_numeric_dtype(df_original[col]) else 0
                          for col in factor_columns},
        },
        'transformed': {
            'rows': len(df_transformed),
            'factor_means': {col: df_transformed[col].mean() if pd.api.types.is_numeric_dtype(df_transformed[col]) else 0
                           for col in factor_columns},
            'factor_stds': {col: df_transformed[col].std() if pd.api.types.is_numeric_dtype(df_transformed[col]) else 0
                          for col in factor_columns},
        }
    }

    return comparison


def preview_factors(df_factors, n=10):
    """
    인자 데이터 미리보기

    Args:
        df_factors (pd.DataFrame): 인자 데이터
        n (int): 표시할 행 수

    Returns:
        pd.DataFrame: 미리보기 데이터
    """
    return df_factors.head(n)


def export_factors_csv(df_factors, filepath):
    """
    인자 데이터를 CSV로 내보내기

    Args:
        df_factors (pd.DataFrame): 인자 데이터
        filepath (str): 저장 경로

    Returns:
        bool: 성공 여부
    """
    try:
        df_factors.to_csv(filepath, index=False, encoding='utf-8-sig')
        st.success(f"[OK] CSV 저장 완료: {filepath}")
        return True
    except Exception as e:
        st.error(f"CSV 저장 오류: {str(e)}")
        return False
