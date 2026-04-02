import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import pandas as pd

# ==========================================
# 1. 구글 스프레드시트 연결 설정 (최적화 버전)
# ==========================================
def connect_to_gsheet():
    try:
        # Streamlit Cloud의 Secrets에서 'JSON_DATA' 문자열을 가져옴
        if "JSON_DATA" not in st.secrets:
            st.error("Secrets 설정에서 'JSON_DATA'를 찾을 수 없습니다.")
            return None
            
        creds_info = json.loads(st.secrets["JSON_DATA"])
        
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # 딕셔너리 정보를 사용하여 인증 객체 생성
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        client = gspread.authorize(creds)
        
        # 제공해주신 스프레드시트 ID
        SPREADSHEET_ID = '1MTL6k_cLqXkUUbxv0JKZtykC_81LYOK6Qxb4VYm-1rE'
        sheet = client.open_by_key(SPREADSHEET_ID).get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"인증 실패: {e}")
        return None

# ==========================================
# 2. 웹 앱 인터페이스 (UI)
# ==========================================
st.set_page_config(page_title="영업 이슈 등록 시스템", layout="centered")

st.title("🚀 영업 이슈 리포트")
st.info("현장에서 발생한 이슈를 입력하면 스프레드시트에 자동 저장됩니다.")

with st.form("issue_form", clear_on_submit=True):
    # 담당자 선택
    manager = st.radio(
        "담당자 선택",
        ["이광호", "문정수", "박원덕"],
        horizontal=True
    )

    # 상품 다중 선택
    products = st.multiselect(
        "가입(예정/실패) 상품 (중복 선택 가능)",
        ["위멤버스 프리미엄", "위멤버스 스탠다드", "세모리포트 플러스", "세모리포트 베이직", "링크패스", "경리나라T"]
    )

    # 상세 이슈 작성
    issue_detail = st.text_area(
        "상세 이슈 내용", 
        placeholder="특이사항을 자유롭게 작성하세요.",
        height=200
    )

    # 제출 버튼
    submit_button = st.form_submit_button("이슈 등록 완료")

# ==========================================
# 3. 데이터 저장 로직
# ==========================================
if submit_button:
    if not products:
        st.warning("상품을 하나 이상 선택해 주세요.")
    elif not issue_detail.strip():
        st.warning("내용을 입력해 주세요.")
    else:
        sheet = connect_to_gsheet()
        if sheet:
            try:
                # 한국 시간 기준 등 기록을 위한 시간 생성
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                product_str = ", ".join(products)
                
                # 데이터 추가 (등록일시, 담당자, 상품명, 상세이슈)
                sheet.append_row([now, manager, product_str, issue_detail])
                
                st.success(f"✅ 성공적으로 등록되었습니다! ({now})")
                st.balloons()
            except Exception as e:
                st.error(f"데이터 저장 실패: {e}")