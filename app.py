import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import pandas as pd

# ==========================================
# 1. 구글 스프레드시트 연결 설정 (가장 안전한 방식)
# ==========================================
def connect_to_gsheet():
    try:
        # Secrets에서 JSON_DATA라는 통문자열을 읽어옴
        if "JSON_DATA" not in st.secrets:
            st.error("Streamlit Secrets 설정에서 'JSON_DATA'를 찾을 수 없습니다.")
            return None
            
        # 원본 문자열을 JSON 객체로 변환 (서명 오류 방지 핵심)
        creds_info = json.loads(st.secrets["JSON_DATA"])
        
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        client = gspread.authorize(creds)
        
        # 스프레드시트 ID
        SPREADSHEET_ID = '1MTL6k_cLqXkUUbxv0JKZtykC_81LYOK6Qxb4VYm-1rE'
        sheet = client.open_by_key(SPREADSHEET_ID).get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"인증 실패: {e}")
        return None

# ==========================================
# 2. UI 구성
# ==========================================
st.set_page_config(page_title="영업 이슈 리포트", layout="centered")

st.title("🚀 영업 이슈 리포트")
st.write("현장 이슈를 입력하면 구글 시트에 즉시 반영됩니다.")

with st.form("issue_form", clear_on_submit=True):
    manager = st.radio("담당자", ["이광호", "문정수", "박원덕"], horizontal=True)
    
    products = st.multiselect(
        "가입(예정/실패) 상품",
        ["위멤버스 프리미엄", "위멤버스 스탠다드", "세모리포트 플러스", "세모리포트 베이직", "링크패스", "경리나라T"]
    )
    
    issue_detail = st.text_area("상세 이슈 내용", height=200, placeholder="특이사항을 입력하세요.")
    
    submit_button = st.form_submit_button("이슈 등록 완료")

# ==========================================
# 3. 데이터 저장
# ==========================================
if submit_button:
    if not products or not issue_detail.strip():
        st.warning("상품과 내용을 모두 입력해 주세요.")
    else:
        sheet = connect_to_gsheet()
        if sheet:
            try:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                product_list = ", ".join(products)
                
                # 시트에 행 추가
                sheet.append_row([now, manager, product_list, issue_detail])
                
                st.success("✅ 등록되었습니다!")
                st.balloons()
            except Exception as e:
                st.error(f"저장 실패: {e}")