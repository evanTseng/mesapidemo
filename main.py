from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="工廠管理系統 API")

# 資料模型定義
class StaffAction(BaseModel):
    staff_id: str
    station_id: str

class JobAction(BaseModel):
    job_id: str
    station_id: str



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





@app.get("/")
def read_root():
    return {"message": "API 運行中，請訪問 /docs 查看文件"}

# (1) 人員上工
@app.post("/staff/check-in")
async def staff_check_in(data: StaffAction):
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
async def get_staff_records(staff_id: Optional[str] = None):
    """查詢人員上下工紀錄，可透過 staff_id 過濾"""
    if staff_id:
        filtered = [r for r in FAKE_STAFF_RECORDS if r["staff_id"] == staff_id]
        return {"count": len(filtered), "data": filtered}
    return {"count": len(FAKE_STAFF_RECORDS), "data": FAKE_STAFF_RECORDS}

@app.get("/job/records", tags=["查詢"])
async def get_job_records(job_id: Optional[str] = None):
    """查詢工單進出站紀錄，可透過 job_id 過濾"""
    if job_id:
        filtered = [r for r in FAKE_JOB_RECORDS if r["job_id"] == job_id]
        return {"count": len(filtered), "data": filtered}
    return {"count": len(FAKE_JOB_RECORDS), "data": FAKE_JOB_RECORDS}