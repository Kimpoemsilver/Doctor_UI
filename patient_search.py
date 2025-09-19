import streamlit as st
import pandas as pd
import sys, os

# 상위 폴더에서 DataBase 모듈 인식
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from DataBase.db_utils import fetch_all

st.set_page_config(page_title="환자 검색", page_icon="🩺", layout="centered")

NEXT_PAGE_PATH = "pages/Consultation.py"
DB_PATH = "DataBase/project_db2.db"

st.title("환자 검색")

# 검색 입력
name_query = st.text_input("환자 이름을 입력하세요:")

# -------------------------------
# ✅ DB에서 환자 리스트 가져오기
# test용 DB 추가 데이터: 홍길동, 이몽룡
# -------------------------------
if name_query:
    # 검색어가 있으면 필터링
    results = fetch_all(DB_PATH, """
        SELECT p.patient_id, i.name, i.birth_date, i.first_visit_date
        FROM patient p
        JOIN patient_info i ON p.patient_id = i.patient_id
        WHERE i.name LIKE ?
        ORDER BY i.first_visit_date DESC
        LIMIT 20
    """, (f"%{name_query}%",))
else:
    # 검색어 없으면 기본 환자 리스트 보여주기
    results = fetch_all(DB_PATH, """
        SELECT p.patient_id, i.name, i.birth_date, i.first_visit_date
        FROM patient p
        JOIN patient_info i ON p.patient_id = i.patient_id
        ORDER BY i.first_visit_date DESC
        LIMIT 20
    """)

# -------------------------------
# ✅ 결과 출력
# -------------------------------
if results:
    st.write("### 환자 목록")

    # DataFrame으로 변환
    # DataFrame으로 변환 (dict 리스트 그대로)
    df = pd.DataFrame.from_records(results)

    # 컬럼명 한국어로 매핑
    df = df.rename(columns={
        "patient_id": "환자ID",
        "name": "이름",
        "birth_date": "생년월일",
        "first_visit_date": "첫 방문일"
    })
    # 선택 컬럼 추가 (기본 False)
    df["선택"] = False

    # 데이터 편집기 표시
    edited_df = st.data_editor(
        df,
        hide_index=True,
        num_rows="fixed",
        width="stretch", 
    )

    # 선택된 행 찾기
    selected_rows = edited_df[edited_df["선택"] == True]

    if not selected_rows.empty:
        selected = selected_rows.iloc[0]  # 첫 번째 선택만 사용 (한 명만 선택)
        pid = selected["환자ID"]
        name = selected["이름"]
        dob = selected["생년월일"]
        first_visit = selected["첫 방문일"]

        # 세션 상태 저장 후 페이지 이동
        st.session_state["patient_id"] = pid
        st.session_state["patient_name"] = name
        st.session_state["patient_dob"] = dob
        st.session_state["patient_first_visit"] = first_visit

        st.success(f"✅ {name} 환자가 선택되었습니다. 페이지를 이동합니다...")
        st.switch_page(NEXT_PAGE_PATH)

else:
    st.warning("검색된 환자가 없습니다.")

# debugging
# st.write("🔍 Raw results:", results)
# st.write("🔍 Results type:", type(results))
# if results:
#     for row in results:
#         st.write("Row:", row)