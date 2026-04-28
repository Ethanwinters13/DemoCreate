"""
데이터 변환 엔진 - 업종별 데이터 변환
"""
import json
import uuid
import pandas as pd
import numpy as np
from pathlib import Path
import streamlit as st


def load_industry_config():
    """
    업종별 변환 규칙 설정 로드

    Returns:
        dict: 업종별 설정
    """
    config_path = Path(__file__).parent.parent / "config" / "industry_config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        raise Exception(f"설정 파일 로드 오류: {str(e)}")


def convert(df, industry_id, options=None):
    """
    원본 데이터를 업종 설정에 맞게 변환

    Args:
        df (pd.DataFrame): 원본 데이터
        industry_id (str): 업종 ID
        options (dict): 추가 옵션
          - apply_noise: 노이즈 적용 여부 (기본값: True)
          - custom_qty_scale: QTY 스케일 배율 (기본값: None, 설정값 사용)
          - custom_amt_scale: AMT 스케일 배율 (기본값: None, 설정값 사용)

    Returns:
        pd.DataFrame: 변환된 데이터

    Raises:
        ValueError: 잘못된 업종 ID
        Exception: 변환 실패
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

        df_converted = df.copy()
        total_rows = len(df_converted)

        # 1. ID 재생성 (UUID)
        st.progress(10, text="1/10: ID 재생성 중...")
        df_converted['ID'] = [uuid.uuid4().hex.upper() for _ in range(len(df_converted))]

        # 2. ITEM_MST_ID 매핑 (품목명으로 매핑)
        st.progress(20, text="2/10: 품목 매핑 중...")
        unique_items = df['ITEM_MST_ID'].unique()
        item_patterns = industry_config['item_name_pattern']
        item_mapping = {
            item: item_patterns[i % len(item_patterns)]
            for i, item in enumerate(unique_items)
        }
        df_converted['ITEM_MST_ID'] = df_converted['ITEM_MST_ID'].map(item_mapping)

        # 3. ACCOUNT_ID 재매핑 (가상 고객사명)
        st.progress(30, text="3/10: 고객사 재매핑 중...")
        unique_accounts = df['ACCOUNT_ID'].unique()
        account_mapping = {
            acc: f"{industry_config['name']}_고객{i:03d}"
            for i, acc in enumerate(unique_accounts)
        }
        df_converted['ACCOUNT_ID'] = df_converted['ACCOUNT_ID'].map(account_mapping)

        # 4. QTY 스케일 적용
        st.progress(40, text="4/10: QTY 변환 중...")
        qty_scale = options.get('custom_qty_scale') or industry_config['qty_scale']
        noise = 1.0
        if options.get('apply_noise', True):
            noise = np.random.uniform(0.95, 1.05, len(df_converted))
        df_converted['QTY'] = df['QTY'].copy()
        non_zero_mask = df_converted['QTY'] > 0
        df_converted.loc[non_zero_mask, 'QTY'] = (
            df_converted.loc[non_zero_mask, 'QTY'] * qty_scale * noise[non_zero_mask]
        ).astype(int)

        # 5. AMT 계산 (변환된 QTY × 단가)
        st.progress(50, text="5/10: 금액 계산 중...")
        amt_scale = options.get('custom_amt_scale') or industry_config['amt_scale']
        price_min, price_max = industry_config['unit_price_range']
        prices = np.random.uniform(price_min, price_max, len(df_converted))
        df_converted['AMT'] = (df_converted['QTY'] * prices * amt_scale).astype(int)

        # 6. BASE_DATE 유지
        st.progress(60, text="6/10: 날짜 처리 중...")
        # BASE_DATE는 그대로 유지

        # 7. SO_STATUS_ID 유지
        st.progress(70, text="7/10: 상태 처리 중...")
        # SO_STATUS_ID는 그대로 유지

        # 8. CREATE_BY 업데이트
        st.progress(80, text="8/10: 메타데이터 업데이트 중...")
        df_converted['CREATE_BY'] = 'demo_configurator'
        df_converted['CREATE_DTTM'] = pd.Timestamp.now()

        # 9. CORRECTION_YN 유지
        # CORRECTION_YN은 그대로 유지

        # 10. 나머지 NULL 컬럼 유지
        st.progress(90, text="9/10: 최종 정리 중...")
        # MODIFY_BY, MODIFY_DTTM, QTY_CORRECTION, CORRECTION_COMMENT_ID, AMT_CORRECTION, OUTLIER_YN
        # 은 NULL로 유지

        # 컬럼 순서 정리
        st.progress(95, text="10/10: 완료 중...")
        column_order = [
            'ID', 'ITEM_MST_ID', 'ACCOUNT_ID', 'BASE_DATE', 'SO_STATUS_ID',
            'QTY', 'AMT', 'CREATE_BY', 'CREATE_DTTM', 'MODIFY_BY', 'MODIFY_DTTM',
            'QTY_CORRECTION', 'CORRECTION_COMMENT_ID', 'CORRECTION_YN',
            'AMT_CORRECTION', 'OUTLIER_YN', 'PLAN_SCOPE'
        ]
        df_converted = df_converted[column_order]

        st.progress(100, text="변환 완료!")
        return df_converted

    except Exception as e:
        st.error(f"변환 오류: {str(e)}")
        raise


def preview(df_converted, n=100):
    """
    변환된 데이터 미리보기

    Args:
        df_converted (pd.DataFrame): 변환된 데이터
        n (int): 표시할 행 수

    Returns:
        pd.DataFrame: 미리보기 데이터
    """
    return df_converted.head(n)


def export_csv(df_converted, filepath):
    """
    변환된 데이터를 CSV로 내보내기

    Args:
        df_converted (pd.DataFrame): 변환된 데이터
        filepath (str): 저장 경로

    Returns:
        bool: 성공 여부
    """
    try:
        df_converted.to_csv(filepath, index=False, encoding='utf-8-sig')
        st.success(f"[OK] CSV 저장 완료: {filepath}")
        return True
    except Exception as e:
        st.error(f"CSV 저장 오류: {str(e)}")
        return False


def get_industry_list():
    """
    지원되는 업종 목록 반환

    Returns:
        list: 업종 목록 (dict 형태)
    """
    config = load_industry_config()
    return config['industries']


def compare_data(df_original, df_converted):
    """
    원본 vs 변환 데이터 비교

    Args:
        df_original (pd.DataFrame): 원본 데이터
        df_converted (pd.DataFrame): 변환된 데이터

    Returns:
        dict: 비교 결과
    """
    return {
        'original': {
            'rows': len(df_original),
            'qty_total': df_original['QTY'].sum(),
            'amt_total': df_original['AMT'].sum(),
            'qty_avg': df_original['QTY'].mean(),
            'amt_avg': df_original['AMT'].mean()
        },
        'converted': {
            'rows': len(df_converted),
            'qty_total': df_converted['QTY'].sum(),
            'amt_total': df_converted['AMT'].sum(),
            'qty_avg': df_converted['QTY'].mean(),
            'amt_avg': df_converted['AMT'].mean()
        }
    }
