from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from datetime import datetime
from typing import Optional

app = FastAPI(title="工廠管理系統 API - Pydantic V2 修正版")

# --- 1. 全域異常處理器：自定義中文錯誤訊息 ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    攔截所有參數驗證錯誤。
    若是欄位缺失或為空，回傳：{"status": "error", "message": "XXX 參數不得為空"}
    """
    errors = exc.errors()
    if errors:
        # 取得出錯的最後一個欄位路徑
        field_name = str(errors[0].get("loc")[-1])
        
        # 檢查原始錯誤訊息，如果已經是我們在 Validator 寫好的中文，就直接用
        raw_msg = errors[0].get("msg", "")
        if "不得為空" in raw_msg:
            # 去除 Pydantic 自動加上的 "Value error, " 前綴
            error_msg = raw_msg.split(", ")[-1] if ", " in raw_msg else raw_msg
        else:
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
    # Field(..., min_length=1) 確保 JSON 裡必須有這個 Key 且不是 ""
    staff_id: str = Field(..., min_length=1)
    station_id: str = Field(..., min_length=1)

    @field_validator('staff_id', 'station_id')
    @classmethod
    def check_not_blank(cls, v: str, info: ValidationInfo) -> str:
        # 防止只輸入空格 "  "
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} 參數不得為空")
        return v.strip()

class JobAction(BaseModel):
    job_id: str = Field(..., min_length=1)
    station_id: str = Field(..., min_length=1)

    @field_validator('job_id', 'station_id')
    @classmethod
    def check_not_blank(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} 參數不得為空")
        return v.strip()

# --- 3. 模擬資料庫 ---
FAKE_STAFF_RECORDS = [
    {"staff_id": "S001", "station_id": "A1", "action": "check-in", "timestamp": "2024-03-18 08:00:00"}
]
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

# --- 5. 查詢紀錄 API (Query Parameter 防呆) ---

@app.get("/staff/records", tags=["查詢"])
async def get_staff_records(staff_id: Optional[str] = None):
    # 檢查 URL 參數是否為空字串或空格
    if staff_id is not None and not staff_id.strip():
        return JSONResponse(
            status_code=400, 
            content={"status": "error", "message": "staff_id 參數不得為空"}
        )
    
    if staff_id:
        filtered = [r for r in FAKE_STAFF_RECORDS if r["staff_id"] == staff_id.strip()]
        return {"count": len(filtered), "data": filtered}
    
    return {"count": len(FAKE_STAFF_RECORDS), "data": FAKE_STAFF_RECORDS}

@app.get("/job/records", tags=["查詢"])
async def get_job_records(job_id: Optional[str] = None):
    if job_id is not None and not job_id.strip():
        return JSONResponse(
            status_code=400, 
            content={"status": "error", "message": "job_id 參數不得為空"}
        )
    
    if job_id:
        filtered = [r for r in FAKE_JOB_RECORDS if r["job_id"] == job_id.strip()]
        return {"count": len(filtered), "data": filtered}
        
    return {"count": len(FAKE_JOB_RECORDS), "data": FAKE_JOB_RECORDS}