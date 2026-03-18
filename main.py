from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

app = FastAPI(title="工廠管理系統 API - 最終穩定版")

# --- 1. 全域異常處理器：捕捉所有格式錯誤並轉換為中文 ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    當參數缺失、型別錯誤或不符合長度時，統一回傳中文錯誤。
    例如回傳：{"status": "error", "message": "staff_id 參數不得為空"}
    """
    errors = exc.errors()
    field_name = "參數"
    
    if errors:
        # 取得最後一個路徑名稱，即為出錯的欄位名
        loc = errors[0].get("loc")
        field_name = str(loc[-1]) if loc else "參數"

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": "error", 
            "message": f"{field_name} 參數不得為空"
        }
    )

# --- 2. 資料模型定義 ---
class StaffAction(BaseModel):
    # min_length=1 確保欄位必須存在且長度不為 0
    staff_id: str = Field(..., min_length=1)
    station_id: str = Field(..., min_length=1)

    @field_validator('staff_id', 'station_id')
    @classmethod
    def check_not_blank(cls, v: str) -> str:
        # 手動檢查是否只有空白字元 "  "
        if not v or not v.strip():
            raise ValueError("不得為空")
        return v.strip()

class JobAction(BaseModel):
    job_id: str = Field(..., min_length=1)
    station_id: str = Field(..., min_length=1)

    @field_validator('job_id', 'station_id')
    @classmethod
    def check_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("不得為空")
        return v.strip()

# --- 3. 模擬資料庫 ---
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

# --- 4. API 端點 ---

@app.get("/")
def read_root():
    return {"message": "API 運行中", "docs": "/docs"}

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
        "station": data.station_id,
        "entry_time": datetime.now().isoformat()
    }

# (4) 工單出站
@app.post("/job/exit")
async def job_exit(data: JobAction):
    return {
        "status": "success",
        "job_id": data.job_id,
        "station": data.station_id,
        "exit_time": datetime.now().isoformat()
    }

# --- 5. 查詢紀錄 API (Query Parameter 防呆) ---

@app.get("/staff/records", tags=["查詢"])
async def get_staff_records(staff_id: Optional[str] = None):
    if staff_id is not None and not staff_id.strip():
        return JSONResponse(
            status_code=400, 
            content={"status": "error", "message": "staff_id 參數不得為空"}
        )
    return {"count": len(FAKE_STAFF_RECORDS), "data": FAKE_STAFF_RECORDS}

@app.get("/job/records", tags=["查詢"])
async def get_job_records(job_id: Optional[str] = None):
    if job_id is not None and not job_id.strip():
        return JSONResponse(
            status_code=400, 
            content={"status": "error", "message": "job_id 參數不得為空"}
        )
    return {"count": len(FAKE_JOB_RECORDS), "data": FAKE_JOB_RECORDS}