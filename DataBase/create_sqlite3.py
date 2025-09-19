import sqlite3

# 새로 만들 DB 파일 경로
DB_PATH = "project_db2.db"

# schema.sql 내용 그대로 복붙
schema_sql = """
-- ===============================
-- Patient & Info
-- ===============================
CREATE TABLE patient (
    patient_id TEXT PRIMARY KEY,
    pw TEXT
);

CREATE TABLE patient_info (
    patient_id TEXT PRIMARY KEY,
    sex INTEGER,
    age INTEGER,
    height REAL,
    weight REAL,
    egfr REAL,
    HSI INTEGER,
    phq9 INTEGER,
    AST REAL,
    ALT REAL,
    FBG REAL,
    name TEXT,
    birth_date TEXT,
    first_visit_date TEXT,
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
);

-- ===============================
-- PK Parameters
-- ===============================
CREATE TABLE pk_param (
    patient_id TEXT PRIMARY KEY,
    pkpram_CL TEXT,
    pkpram_V TEXT,
    covariate TEXT,
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
);

-- ===============================
-- Patient Predict
-- ===============================
CREATE TABLE patient_predict (
    patient_id TEXT,
    prescription_date TEXT,
    dose INTEGER,
    frequency INTEGER,
    prescription_days INTEGER,
    day_drug INTEGER,
    note TEXT,
    PRIMARY KEY (patient_id, prescription_date),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
);

-- ===============================
-- Patient Daily
-- ===============================
CREATE TABLE patient_daily (
    patient_id TEXT,
    prescription_date TEXT,
    record_date TEXT,
    emotion_text TEXT,
    side_eff_severity INTEGER,
    day_num_dose INTEGER,
    pdc REAL,
    medication_id TEXT,
    dose_mg REAL,
    note TEXT,
    PRIMARY KEY (patient_id, prescription_date, record_date),
    FOREIGN KEY (patient_id, prescription_date) REFERENCES patient_predict(patient_id, prescription_date)
);

-- ===============================
-- Daily Predict
-- ===============================
CREATE TABLE daily_predict (
    patient_id TEXT,
    predict_dt TEXT,
    pred_dose INTEGER,
    pred_frequency INTEGER,
    PRIMARY KEY (patient_id, predict_dt),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
);

-- ===============================
-- Side Effect Dictionary
-- ===============================
CREATE TABLE side_effect (
    code TEXT PRIMARY KEY,
    name_en TEXT,
    name_ko TEXT,
    sort_order INTEGER,
    is_core INTEGER
);

-- ===============================
-- ASEC Response (Side Effect 기록)
-- ===============================
CREATE TABLE asec_response (
    patient_id TEXT,
    prescription_date TEXT,
    record_date TEXT,
    side_effect_code TEXT,
    due_to_med INTEGER,
    severity INTEGER,
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
    phq9_score INTEGER,
    model_version TEXT,
    PRIMARY KEY (patient_id, prescription_date, record_date),
    FOREIGN KEY (patient_id, prescription_date, record_date) REFERENCES patient_daily(patient_id, prescription_date, record_date)
);
"""

# DB 파일 새로 생성 + 스키마 적용
with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()
    cur.executescript(schema_sql)
    conn.commit()

print("✅ project_db2.db 생성 완료 (schema.sql 기준)")
