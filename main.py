from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List

app = FastAPI(title="工廠管理系統 API - 穩定版")

# --- 資料模型定義 (Data Models) ---

class StaffAction(BaseModel):
    # Field(..., min_length=1) 確保欄位必填且長度至少為 1
    staff_id: str = Field(..., min_length=1, description="員工編號", example="S001")
    station_id: str = Field(..., min_length=1, description="工站編號", example="A1")

    @validator('staff_id', 'station_id')
    def not_empty_whitespace(cls, v):
        if not v.strip():
            raise ValueError("欄位不能只包含空白字元")
        return v.strip()

class JobAction(BaseModel):
    job_id: str = Field(..., min_length=1, description="工單編號", example="JOB-101")
    station_id: str = Field(..., min_length=1, description="工站編號", example="A1")

    @validator('job_id', 'station_id')
    def not_empty_whitespace(cls, v):
        if not v.strip():
            raise ValueError("欄位不能只包含空白字元")
        return v.strip()

# --- 模擬資料庫 (Fake Database) ---
FAKE_STAFF_RECORDS = [
    {"staff_id": "S001", "station_id": "A1", "action": "check-in", "timestamp": "2024-03-18 08:00:00"},
    {"staff_id": "S001", "station_id": "A1", "action": "check-out", "timestamp": "2024-03-18 17:00:00"},
    {"staff_id": "S002", "station_id": "B2", "action": "check-in", "timestamp": "2024-03-18 09:15:20"}
]

FAKE_JOB_RECORDS = [
    {"job_id": "JOB-101", "station_id": "A1", "action": "entry", "timestamp": "2024-03-18 10:00:00"},
    {"job_id": "JOB-101", "station_id": "A1", "action": "exit", "timestamp": "2024-03-18 10:45:00"},
    {"job_id": "JOB-102", "station_id": "C3", "action": "entry", "timestamp": "2024-03-18 11:00:00"}
]

# --- API 端點 ---

@app.get("/")
def read_root():
    return {"message": "API 運行中", "docs": "/docs"}

# (1) 人員上工
@app.post("/staff/check-in", status_code=status.HTTP_201_CREATED)
async def staff_check_in(data: StaffAction):
    # 若 data 傳入空值，FastAPI 會自動噴出 422 錯誤，無需手動 check
    return {
        "status": "success",
        "message": f"人員 {data.staff_id} 已於 {data.station_id} 上工",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# (2) 人員下工
@app.post("/staff/check-out")
async def staff_check_out(data: StaffAction):
    return {
        "status": "success",
        "message": f"人員 {data.staff_id} 已從 {data.station_id} 下工",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# (3) 工單進站
@app.post("/job/entry")
async def job_entry(data: JobAction):
    return {
        "status": "success",
        "job_id": data.job_id,
        "action": "進站",
        "station": data.station_id,
        "entry_time": datetime.now().isoformat()
    }

# (4) 工單出站
@app.post("/job/exit")
async def job_exit(data: JobAction):
    return {
        "status": "success",
        "job_id": data.job_id,
        "action": "出站",
        "station": data.station_id,
        "exit_time": datetime.now().isoformat()
    }

# --- 查詢紀錄 API ---

@app.get("/staff/records", tags=["查詢"])
async def get_staff_records(staff_id: Optional[str] = Query(None, description="要查詢的員工 ID")):
    """查詢人員紀錄。若提供 staff_id 但查無資料，回傳 404。"""
    if staff_id:
        clean_id = staff_id.strip()
        if not clean_id:
            raise HTTPException(status_code=400, detail="請提供有效的 staff_id")
            
        filtered = [r for r in FAKE_STAFF_RECORDS if r["staff_id"] == clean_id]
        if not filtered:
            raise HTTPException(status_code=404, detail=f"找不到員工編號 {clean_id} 的紀錄")
        return {"count": len(filtered), "data": filtered}
        
    return {"count": len(FAKE_STAFF_RECORDS), "data": FAKE_STAFF_RECORDS}

@app.get("/job/records", tags=["查詢"])
async def get_job_records(job_id: Optional[str] = Query(None, description="要查詢的工單 ID")):
    """查詢工單紀錄。若提供 job_id 但查無資料，回傳 404。"""
    if job_id:
        clean_id = job_id.strip()
        if not clean_id:
            raise HTTPException(status_code=400, detail="請提供有效的 job_id")

        filtered = [r for r in FAKE_JOB_RECORDS if r["job_id"] == clean_id]
        if not filtered:
            raise HTTPException(status_code=404, detail=f"找不到工單編號 {clean_id} 的紀錄")
        return {"count": len(filtered), "data": filtered}
        
    return {"count": len(FAKE_JOB_RECORDS), "data": FAKE_JOB_RECORDS}