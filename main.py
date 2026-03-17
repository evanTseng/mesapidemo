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