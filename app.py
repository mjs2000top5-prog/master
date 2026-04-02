import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# ==========================================
# 1. 구글 스프레드시트 연결 설정 (Secrets 활용)
# ==========================================
def connect_to_gsheet():
    # Streamlit Cloud의 Secrets에 저장된 정보를 가져옵니다.
    try:
        # secrets.toml 또는 Streamlit Cloud 설정의 [gcp_service_account] 섹션을 읽음
        creds_info = st.secrets["gcp_service_account"]
        
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # 파일 경로 대신 info(딕셔너리)를 사용하여 인증
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        client = gspread.authorize(creds)
        
        SPREADSHEET_ID = '1MTL6k_cLqXkUUbxv0JKZtykC_81LYOK6Qxb4VYm-1rE'
        sheet = client.open_by_key(SPREADSHEET_ID).get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"인증 실패: {e}")
        return None

# [이후 UI 및 저장 로직은 기존과 동일합니다]
st.set_page_config(page_title="영업 이슈 등록", layout="centered")
st.title("🚀 영업 이슈 리포트")

with st.form("issue_form", clear_on_submit=True):
    manager = st.radio("담당자", ["이광호", "문정수", "박원덕"], horizontal=True)
    products = st.multiselect("상품 선택", ["위멤버스 프리미엄", "위멤버스 스탠다드", "세모리포트 플러스", "세모리포트 베이직", "링크패스", "경리나라T"])
    issue_detail = st.text_area("상세 이슈", height=150)
    submit_button = st.form_submit_button("이슈 등록 완료")

if submit_button:
    if not products or not issue_detail.strip():
        st.warning("항목을 모두 입력해 주세요.")
    else:
        sheet = connect_to_gsheet()
        if sheet:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            product_list = ", ".join(products)
            sheet.append_row([now, manager, product_list, issue_detail])
            st.success("✅ 등록 완료!")
            st.balloons()