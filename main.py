from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

app = FastAPI(title="工廠管理系統 API - 精確防呆版")

# --- 1. 精確錯誤處理器 (告訴使用者哪個參數空了) ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    解析 Pydantic 的錯誤清單，抓出第一個出錯的欄位名稱。
    回傳格式：{ "status": "error", "message": "XXX 參數不得為空" }
    """
    errors = exc.errors()
    if errors:
        # loc[0] 是 'body' 或 'query'，loc[1] 通常是參數名稱
        field_name = errors[0].get("loc")[-1]
        error_msg = f"{field_name} 參數不得為空"
    else:
        error_msg = "參數請求錯誤"

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": "error", 
            "message": error_msg
        }
    )

# --- 2. 資料模型定義 ---
class StaffAction(BaseModel):
    # 使用 Field 限制最小長度，若不符會觸發 RequestValidationError
    staff_id: str = Field(..., min_length=1)
    station_id: str = Field(..., min_length=1)

    @validator('staff_id', 'station_id')
    def prevent_empty_spaces(cls, v, field):
        if not v or not v.strip():
            # 這裡拋出的錯誤會被上面的 exception_handler 捕捉
            raise ValueError(f"{field.name} 不得為空")
        return v.strip()

class JobAction(BaseModel):
    job_id: str = Field(..., min_length=1)
    station_id: str = Field(..., min_length=1)

    @validator('job_id', 'station_id')
    def prevent_empty_spaces(cls, v, field):
        if not v or not v.strip():
            raise ValueError(f"{field.name} 不得為空")
        return v.strip()

# --- 3. 模擬資料庫 ---
FAKE_STAFF_RECORDS = []
FAKE_JOB_RECORDS = []

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

# --- 5. 查詢紀錄 API (含精確防呆) ---

@app.get("/staff/records", tags=["查詢"])
async def get_staff_records(staff_id: Optional[str] = None):
    if staff_id is not None and not staff_id.strip():
        return JSONResponse(
            status_code=400, 
            content={"status": "error", "message": "staff_id 參數不得為空"}
        )
    # ... 查詢邏輯 ...
    return {"data": FAKE_STAFF_RECORDS}

@app.get("/job/records", tags=["查詢"])
async def get_job_records(job_id: Optional[str] = None):
    if job_id is not None and not job_id.strip():
        return JSONResponse(
            status_code=400, 
            content={"status": "error", "message": "job_id 參數不得為空"}
        )
    # ... 查詢邏輯 ...
    return {"data": FAKE_JOB_RECORDS}