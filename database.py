#uvicorn database:app --reload --port 8000
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymysql
import pymysql.cursors
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv
load_dotenv()   # 自動載入同目錄下的 .env
 
DB_CONFIG = {
    "host":        os.getenv("DB_HOST", "localhost"),
    "port":        int(os.getenv("DB_PORT", 3306)),
    "user":        os.getenv("DB_USER"),
    "password":    os.getenv("DB_PASSWORD"),
    "database":    os.getenv("DB_NAME"),
    "charset":     "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}
app = FastAPI(title="SmartAOI-Lite", version="1.0.0")
def get_conn():
    return pymysql.connect(**DB_CONFIG)

class InspectionResult(BaseModel):
    sn_id:          str
    defect_area:    int
    defect_position: tuple        # (x, y, w, h, type)

def init_db():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS production_logs (
                id             INT AUTO_INCREMENT PRIMARY KEY,
                sn_id          VARCHAR(64)  NOT NULL,
                fail INT   NOT NULL,
                defect_area    INT          NOT NULL,
                defect_position_X INT        NULL,
                defect_position_Y INT        NULL,
                defect_position_W INT        NULL,
                defect_position_H INT        NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
    conn.commit()
    conn.close()
    print("production_logs就緒")

init_db()  
@app.post("/api/v1/line-capture")
def line_capture(data: InspectionResult):
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO production_logs (sn_id, fail, defect_area, defect_position_X, defect_position_Y, defect_position_W, 
                defect_position_H)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (data.sn_id,  data.defect_position[4],data.defect_area,
                  data.defect_position[0], data.defect_position[1], data.defect_position[2], data.defect_position[3]),
            )
        conn.commit()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"資料庫寫入失敗: {e}")
    print(f"寫入成功 -> {data.sn_id} | 失敗類型:{data.defect_position[4]} | 面積:{data.defect_area}")
    return {"status": "ok", "message": "寫入 production_logs"}

@app.get("/api/v1/logs")
def get_logs(limit: int = 20):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM production_logs ORDER BY id DESC LIMIT %s", (limit,))
        rows = cur.fetchall()
    conn.close()
    return rows

@app.get("/")
def root():
    return {"message": "SmartAOI-Lite ，POST /api/v1/line-capture 接收辨識結果"}
