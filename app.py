import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# ==========================================
# 1. 구글 스프레드시트 연결 설정
# ==========================================
def connect_to_gsheet():
    # 사용자가 저장한 인증 파일명 (app.json)
    SERVICE_ACCOUNT_FILE = 'app.json'
    
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
        client = gspread.authorize(creds)
        
        # 알려주신 스프레드시트 ID
        SPREADSHEET_ID = '1MTL6k_cLqXkUUbxv0JKZtykC_81LYOK6Qxb4VYm-1rE'
        # 첫 번째 워크시트 선택
        sheet = client.open_by_key(SPREADSHEET_ID).get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"인증 실패: {e}")
        return None

# ==========================================
# 2. 웹 앱 인터페이스 (UI) 구성
# ==========================================
st.set_page_config(page_title="영업 이슈 등록 (모바일)", layout="centered")

# 헤더 부분
st.title("🚀 영업 이슈 리포트")
st.write("방문 업체 정보를 입력하면 스프레드시트에 자동 기록됩니다.")
st.divider()

# 입력 폼 시작
with st.form("issue_form", clear_on_submit=True):
    # 담당자 선택 (라디오 버튼으로 더 편하게 선택 가능)
    manager = st.radio(
        "담당자",
        ["이광호", "문정수", "박원덕"],
        horizontal=True
    )

    # 가입(예정/실패) 상품 다중 선택
    st.write("**가입(예정/실패) 상품**")
    products = st.multiselect(
        "해당하는 상품을 모두 선택하세요",
        ["위멤버스 프리미엄", "위멤버스 스탠다드", "세모리포트 플러스", "세모리포트 베이직", "링크패스", "경리나라T"]
    )

    # 상세 이슈 자유 작성
    st.write("**상세 이슈**")
    issue_detail = st.text_area(
        label="내용 작성",
        placeholder="업체 피드백, 특이사항 등을 자유롭게 적어주세요.",
        height=150
    )

    # 제출 버튼
    submit_button = st.form_submit_button("이슈 등록 완료")

# ==========================================
# 3. 데이터 전송 로직
# ==========================================
if submit_button:
    if not products:
        st.warning("상품을 하나 이상 선택해 주세요.")
    elif not issue_detail.strip():
        st.warning("상세 이슈 내용을 입력해 주세요.")
    else:
        sheet = connect_to_gsheet()
        if sheet:
            try:
                # 현재 날짜와 시간 (예: 2024-05-20 14:30:05)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 선택된 상품들을 하나의 문자열로 결합 (예: "링크패스, 경리나라T")
                product_list = ", ".join(products)
                
                # 스프레드시트에 추가할 행 (날짜시간, 담당자, 상품명, 이슈내용)
                row_to_add = [now, manager, product_list, issue_detail]
                
                # 시트의 맨 아래에 데이터 추가
                sheet.append_row(row_to_add)
                
                st.success("✅ 스프레드시트에 성공적으로 저장되었습니다!")
                st.balloons()
            except Exception as e:
                st.error(f"데이터 저장 중 오류가 발생했습니다: {e}")

# ==========================================
# 4. 하단 안내 사항
# ==========================================
st.divider()
st.caption("데이터 확인은 공유된 구글 스프레드시트를 참조해 주세요.")