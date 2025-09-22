import streamlit as st
from datetime import date, timedelta
import pandas as pd
import altair as alt
import sys, os

# DB 유틸 불러오기
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from DataBase.db_utils import fetch_all, execute_query

DB_PATH = "DataBase/project_db2.db"

st.set_page_config(page_title="Home", page_icon="💊", layout="wide")

if not st.session_state.get("is_logged_in", True):
    st.error("잘못된 접근입니다.")
    st.stop()

# patient_id 가져오기
patient_id = st.session_state.get("patient_id", None)
if not patient_id:
    st.error("❌ 환자 정보가 없습니다. 환자 검색 페이지에서 먼저 선택해주세요.")
    st.stop()

# --- Header ---
name = st.session_state.get("patient_name", "")
st.markdown(f"""
    <div style="padding: 1.2rem 1.5rem; border-radius: 12px; background-color: #f5f7fa; border: 1px solid #e5e7eb; width: fit-content; color:#111;">
    <span style="font-size: 2rem; font-weight: 800; letter-spacing: 0.5px;">{name} 님 </span> </div>
    """, unsafe_allow_html=True )

# --- 레이아웃: 좌우 1:1 ---
left, right = st.columns([1,1])

# ========== 왼쪽: 의사 처방 입력 ==========
with left:
    st.title("👩‍⚕️ 환자 처방 관리 시스템")

        # --- daily_predict 추천 용량/간격 추세 ---
    st.markdown("---")
    st.subheader("📊 추천 용량 및 복용 간격")

    daily_pred = fetch_all(DB_PATH, """
        SELECT predict_dt, pred_dose, pred_frequency
        FROM daily_predict
        WHERE patient_id=?
        ORDER BY predict_dt
    """, (patient_id,))

    if daily_pred:
        dp_df = pd.DataFrame(daily_pred, columns=["predict_dt","pred_dose","pred_frequency"])
        dp_df = dp_df.rename(columns={
            "predict_dt":"날짜",
            "pred_dose":"추천 용량(mg)",
            "pred_frequency":"추천 간격(h)"
        })

        # 🔑 predict_dt 문자열에서 날짜만 추출
        dp_df["날짜"] = dp_df["날짜"].astype(str).str.split("T").str[0]

        # 🔑 datetime 변환
        dp_df["날짜"] = pd.to_datetime(dp_df["날짜"], format="%Y-%m-%d", errors="coerce")

        # 표용 데이터프레임 (YYYY-MM-DD 형태)
        dp_df_display = dp_df.copy()
        dp_df_display["날짜"] = dp_df_display["날짜"].dt.strftime("%Y-%m-%d")

        # --- 병렬 레이아웃 (그래프:표 = 3:2) ---
        col_chart, col_table = st.columns([3,2])

        with col_chart:
            chart_dose = alt.Chart(dp_df).mark_line(point=True).encode(
                x=alt.X("날짜:T", title="날짜"),
                y=alt.Y("추천 용량(mg):Q", title="추천 용량(mg)"),
                tooltip=["날짜","추천 용량(mg)","추천 간격(h)"]
            ).properties(title="추천 용량 추세")
            st.altair_chart(chart_dose, use_container_width=True)

        with col_table:
            st.markdown("**📋 추천 값 테이블**")
            st.table(dp_df_display)



    else:
        st.info("📭 daily_predict 데이터가 없습니다.")


    # --- 새 처방 입력 ---
    st.subheader("📌 새로운 처방 입력")
    col1, col2, col3 = st.columns(3)

    with col1:
        new_date = st.date_input("처방일자", date.today())
        new_dose = st.number_input("용량 (mg)", min_value=0)

    with col2:
        new_freq = st.number_input("복용 간격 (h)", min_value=1)
        new_days = st.number_input("투여 일수", min_value=1)

    with col3:
        new_day_drug = 24/new_freq
        st.metric("하루 복용 횟수", f"{new_day_drug} 회")

    doctor_comment = st.text_area("📝 의사 코멘트 입력", placeholder="환자 상태, 복용 지도 등 자유롭게 기록")

    if st.button("💾 저장하기"):
        execute_query(DB_PATH, """
            INSERT INTO patient_predict (patient_id, prescription_date, dose, frequency, prescription_days, day_drug, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (patient_id, new_date.isoformat(), new_dose, new_freq, new_days, new_day_drug, doctor_comment))
        
        st.success("✅ 처방이 저장되었습니다!")

        df = pd.DataFrame(fetch_all(DB_PATH, """
            SELECT prescription_date, dose, frequency, prescription_days, day_drug, note
            FROM patient_predict
            WHERE patient_id=?
            ORDER BY prescription_date DESC
        """, (patient_id,)))
        if not df.empty:
            df.columns = ["처방일", "용량(mg)", "투여 횟수", "총 일수", "하루 총 약량(mg)", "의사 코멘트"]
            st.dataframe(df)

# ========== 오른쪽: 환자 정보 ==========
# with right:
#     # 환자 기본 정보
#     st.subheader("🧑‍⚕️ 환자 기본 정보")
#     info = fetch_all(DB_PATH, """
#         SELECT name, age, sex, height, weight, egfr, phq9
#         FROM patient_info
#         WHERE patient_id=?
#     """, (patient_id,))
#     if info:
#         info_row = info[0]
#         st.markdown(f"""
#             <div style="padding: 1rem; border-radius: 12px; background-color: #eef2ff; border: 1px solid #c7d2fe;">
#             <b>이름:</b> {info_row["name"]} <br>
#             <b>나이:</b> {info_row["age"]} <br>
#             <b>성별:</b> {"남" if info_row["sex"]==1 else "여"} <br>
#             <b>키(cm):</b> {info_row["height"]} <br>
#             <b>몸무게(kg):</b> {info_row["weight"]} <br>
#             <b>eGFR:</b> {info_row["egfr"]} <br>
#             <b>PHQ-9 점수:</b> {info_row["phq9"]}
#             </div>
#             """, unsafe_allow_html=True)

#     # 모델 추천 (세션에서 받아옴)
#     st.markdown("---")
#     st.subheader("💉 PK 파라미터")
#     pk = fetch_all(DB_PATH, """
#         SELECT pkpram_CL, pkpram_V, covariate
#         FROM pk_param
#         WHERE patient_id=?
#     """, (patient_id,))
#     if pk:
#         pk_row = pk[0]
#         st.markdown(f"""
#             <div style="padding: 1rem; border-radius: 12px; background-color: #f0fdf4; border: 1px solid #bbf7d0;">
#             <b>CL:</b> {pk_row["pkpram_CL"]} <br>
#             <b>V:</b> {pk_row["pkpram_V"]} <br>
#             <b>공변량:</b> {pk_row["covariate"]}
#             </div>
#             """, unsafe_allow_html=True)
#     else:
#         st.info("📭 PK 파라미터 데이터가 없습니다.")

with right:
    st.subheader("🧑‍⚕️ 환자 정보 & PK 파라미터")

    # 두 개 컬럼으로 분리
    col_info, col_pk = st.columns(2)

    # 환자 기본 정보
    with col_info:
        info = fetch_all(DB_PATH, """
            SELECT name, age, sex, height, weight, egfr, phq9
            FROM patient_info
            WHERE patient_id=?
        """, (patient_id,))
        if info:
            info_row = info[0]
            st.markdown(f"""
                <div style="padding: 1rem; border-radius: 12px; background-color: #eef2ff; border: 1px solid #c7d2fe;">
                <b>이름:</b> {info_row["name"]} <br>
                <b>나이:</b> {info_row["age"]} <br>
                <b>성별:</b> {"남" if info_row["sex"]==1 else "여"} <br>
                <b>키(cm):</b> {info_row["height"]} <br>
                <b>몸무게(kg):</b> {info_row["weight"]} <br>
                <b>eGFR:</b> {info_row["egfr"]} <br>
                <b>PHQ-9 점수:</b> {info_row["phq9"]}
                </div>
            """, unsafe_allow_html=True)

    # PK 파라미터 + 최근 Dose/Frequency
    with col_pk:
        pk = fetch_all(DB_PATH, """
            SELECT pkpram_CL, pkpram_V, covariate
            FROM pk_param
            WHERE patient_id=?
        """, (patient_id,))
        if pk:
            pk_row = pk[0]
            st.markdown(f"""
                <div style="padding: 1rem; border-radius: 12px; background-color: #f0fdf4; border: 1px solid #bbf7d0;">
                <b>CL:</b> {pk_row["pkpram_CL"]} <br>
                <b>V:</b> {pk_row["pkpram_V"]} <br>
                <b>공변량:</b> {pk_row["covariate"]}
                </div>
            """, unsafe_allow_html=True)

        # 최신 처방 (dose/frequency)
        latest = fetch_all(DB_PATH, """
            SELECT dose, frequency
            FROM patient_predict
            WHERE patient_id=?
            ORDER BY prescription_date DESC LIMIT 1
        """, (patient_id,))
        if latest:
            last = latest[0]
            st.markdown(f"""
                <div style="padding: 1rem; border-radius: 12px; background-color: #fff7ed; border: 1px solid #fed7aa;">
                <b>최근 처방 용량:</b> {last["dose"]} mg <br>
                <b>투여 주기:</b> {last["frequency"]} h
                </div>
            """, unsafe_allow_html=True)

    # 최근 부작용 (DB에서 불러오기)
    st.markdown("---")
    st.subheader("⚠️ 최근 부작용 (최근 7일)")

    recent_cutoff = (date.today() - timedelta(days=7)).isoformat()
    sfx = fetch_all(DB_PATH, """
        SELECT a.record_date, s.name_ko AS symptom, a.severity
        FROM asec_response a
        JOIN side_effect s ON a.side_effect_code = s.code
        WHERE a.patient_id=? AND a.record_date>=?
        ORDER BY a.record_date DESC
    """, (patient_id, recent_cutoff))

    if sfx:
        df_sfx = pd.DataFrame(sfx)

        # 심각도 숫자 → 텍스트 매핑
        severity_map = {0:"없음", 1:"경미", 2:"중등도", 3:"심각"}
        df_sfx["심각도"] = df_sfx["severity"].map(severity_map)

        # ✅ 체크박스로 리스트 표시 여부 선택
        if st.checkbox("최근 7일 부작용 리스트 보기"):
            st.table(df_sfx.rename(columns={"record_date":"날짜", "symptom":"부작용"})
                    .drop(columns=["severity"]))

        # 📊 막대 그래프 (항상 표시)
        chart = alt.Chart(df_sfx).mark_bar().encode(
            x="symptom:N",
            y="count():Q",
            color="심각도:N",
            tooltip=["symptom","심각도","count()"]
        ).properties(title="📊 부작용 증상별 심각도 분포")
        st.altair_chart(chart, use_container_width=True)

    else:
        st.info("최근 7일간 보고된 주요 부작용이 없습니다.")

    # PHQ-9 추정치 (DB에서 불러오기)
    st.markdown("---")
    st.subheader("🧠 PHQ-9 추정치")
    phq = fetch_all(DB_PATH, """
        SELECT record_date, phq9_score
        FROM daily_phq9
        WHERE patient_id=?
        ORDER BY record_date
    """, (patient_id,))
    if phq:
        phq_df = pd.DataFrame(phq)
        phq_df = phq_df.rename(columns={"record_date":"날짜","phq9_score":"PHQ-9 점수"})
        phq_df["날짜"] = pd.to_datetime(phq_df["날짜"])
        chart = alt.Chart(phq_df).mark_line(point=True).encode(
            x="날짜:T", y="PHQ-9 점수:Q", tooltip=["날짜","PHQ-9 점수"]
        ).properties(title="📉 PHQ-9 추정 점수 추세")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("📭 PHQ-9 기록이 없습니다.")
        
    # 복용 순응도 (최근 7일 평균)
    st.markdown("---")
    st.subheader("💊 복용 순응도")

    adherence = fetch_all(DB_PATH, """
        SELECT record_date, pdc
        FROM patient_daily
        WHERE patient_id=?
        ORDER BY record_date
    """, (patient_id,))

    if adherence:
        adh_df = pd.DataFrame(adherence)
        adh_df = adh_df.rename(columns={"record_date":"날짜", "pdc":"순응도"})
        adh_df["날짜"] = pd.to_datetime(adh_df["날짜"])
        adh_df["순응도"] = pd.to_numeric(adh_df["순응도"], errors="coerce")

        # 최근 7일 평균
        recent_cutoff = date.today() - timedelta(days=7)
        recent = adh_df[adh_df["날짜"] >= pd.to_datetime(recent_cutoff)]
        adherence_rate = round(recent["순응도"].mean() * 100, 1) if not recent.empty else 0

        st.metric("최근 7일 평균 순응도", f"{adherence_rate}%")

        # 📉 순응도 추세 그래프
        chart = alt.Chart(adh_df).mark_line(point=True).encode(
            x="날짜:T",
            y="순응도:Q",
            tooltip=["날짜","순응도"]
        ).properties(title="📉 일별 복용 순응도 추세")
        st.altair_chart(chart, use_container_width=True)

    else:
        st.info("📭 복용 순응도 기록이 없습니다.")

    