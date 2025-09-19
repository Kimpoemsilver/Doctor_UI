-- ===============================
-- Patient & Info
-- ===============================
CREATE TABLE patient (
    patient_id TEXT PRIMARY KEY,                 -- 환자 고유 ID
    pw TEXT                                      -- 로그인 비밀번호 (해시 저장)
);

CREATE TABLE patient_info (
    patient_id TEXT PRIMARY KEY,                 -- 환자 고유 ID (FK)
    sex INTEGER,                                 -- 성별 (0=여, 1=남)
    age INTEGER,                                 -- 나이
    height REAL,                                 -- 키 (cm)
    weight REAL,                                 -- 몸무게 (kg)
    egfr REAL,                                   -- 사구체 여과율 (eGFR)
    HSI INTEGER,                                 -- 간 지방 지수 (HSI)
    phq9 INTEGER,                                -- PHQ-9 설문 점수
    AST REAL,
    ALT REAL,
    FBG REAL,
    name TEXT,                                   -- 환자 이름 ✅ 추가
    birth_date TEXT,                             -- 생년월일 (YYYY-MM-DD) ✅ 추가
    first_visit_date TEXT,                       -- 첫 방문일 (YYYY-MM-DD) ✅ 추가
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
);

-- ===============================
-- PK Parameters
-- ===============================
CREATE TABLE pk_param (
    patient_id TEXT PRIMARY KEY,                 -- 환자 고유 ID (FK)
    pkpram_CL TEXT,                              -- Clearance(CL)
    pkpram_V TEXT,                               -- Volume of distribution (V)
    covariate TEXT,                              -- 공변량 정보 (JSON 등)
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
);

-- ===============================
-- Patient Predict
-- ===============================
CREATE TABLE patient_predict (
    patient_id TEXT,                             -- 환자 고유 ID (FK)
    prescription_date TEXT,                      -- 처방 날짜
    dose INTEGER,                                -- 하루 총 복용량 (mg)
    frequency INTEGER,                           -- 복용 주기 (시간 단위)
    prescription_days INTEGER,                   -- 총 처방 일수
    day_drug INTEGER,                            -- 하루 약 복용 횟수
    note TEXT,                                   -- 의사 코멘트 ✅ 추가
    PRIMARY KEY (patient_id, prescription_date),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
);

-- ===============================
-- Patient Daily
-- ===============================
CREATE TABLE patient_daily (
    patient_id TEXT,                             -- 환자 고유 ID (FK)
    prescription_date TEXT,                      -- 참조한 처방 날짜 (FK)
    record_date TEXT,                            -- 일일 기록 날짜
    emotion_text TEXT,                           -- 감정 텍스트
    side_eff_severity INTEGER,                   -- ASEC 합산 점수
    day_num_dose INTEGER,                        -- 하루 복용 약봉지 개수
    pdc REAL,                                    -- 약물 복용 순응도
    medication_id TEXT,                          -- 약물 ID (예: fluoxetine)
    dose_mg REAL,                                -- 해당일 총 복용량
    note TEXT,                                   -- 메모
    PRIMARY KEY (patient_id, prescription_date, record_date),
    FOREIGN KEY (patient_id, prescription_date) REFERENCES patient_predict(patient_id, prescription_date)
);

-- ===============================
-- Daily Predict
-- ===============================
CREATE TABLE daily_predict (
    patient_id TEXT,                             -- 환자 고유 ID (FK)
    predict_dt TEXT,                             -- 예측 기준 날짜
    pred_dose INTEGER,                           -- 예측 복용량
    pred_frequency INTEGER,                      -- 예측 복용 주기
    PRIMARY KEY (patient_id, predict_dt),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
);

-- ===============================
-- Side Effect Dictionary
-- ===============================
CREATE TABLE side_effect (
    code TEXT PRIMARY KEY,                       -- 부작용 코드 (S01~S21)
    name_en TEXT,                                -- 영어 이름
    name_ko TEXT,                                -- 한글 이름
    sort_order INTEGER,                          -- 순서값
    is_core INTEGER                              -- 약물 관련 여부 (1/0)
);

-- ===============================
-- ASEC Response (Side Effect 기록)
-- ===============================
CREATE TABLE asec_response (
    patient_id TEXT,
    prescription_date TEXT,
    record_date TEXT,
    side_effect_code TEXT,
    due_to_med INTEGER,                          -- 약물로 인한 부작용 여부
    severity INTEGER,                            -- 심각도 (0~3)
    PRIMARY KEY (patient_id, prescription_date, record_date, side_effect_code),
    FOREIGN KEY (patient_id, prescription_date, record_date) REFERENCES patient_daily(patient_id, prescription_date, record_date),
    FOREIGN KEY (side_effect_code) REFERENCES side_effect(code)
);

-- ===============================
-- Daily PHQ-9 (감정 텍스트 분석 결과)
-- ===============================
CREATE TABLE daily_phq9 (
    patient_id TEXT,
    prescription_date TEXT,
    record_date TEXT,
    phq9_score INTEGER,                          -- 분석된 PHQ-9 점수
    model_version TEXT,                          -- 모델 버전
    PRIMARY KEY (patient_id, prescription_date, record_date),
    FOREIGN KEY (patient_id, prescription_date, record_date) REFERENCES patient_daily(patient_id, prescription_date, record_date)
);
