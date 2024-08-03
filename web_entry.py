import asyncio
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from concurrent.futures import ThreadPoolExecutor
from fastapi.middleware.cors import CORSMiddleware
from bn_future_ma_str import bn_future_ma_trader
from lb_logger import log
from contextlib import asynccontextmanager
import uvicorn

app = FastAPI()

# 允许跨域请求
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建多个trader对象
traders = [
    bn_future_ma_trader(),
]

executor = ThreadPoolExecutor(max_workers=len(traders))
tasks = []
shutdown_event = asyncio.Event()

async def process_strategy_background(trader):
    while not shutdown_event.is_set():
        if trader.tradeswitch:
            trader.process_stategy()
        await asyncio.sleep(5)  # 每隔5秒调用一次

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting up...")
    loop = asyncio.get_event_loop()

    for trader in traders:
        task = loop.create_task(process_strategy_background(trader))
        tasks.append(task)

    yield

    log.info("Shutting down...")
    shutdown_event.set()

    for task in tasks:
        await task

app.router.lifespan_context = lifespan

@app.get("/strategy_data/{trader_id}")
async def get_strategy_data(trader_id: int):
    if trader_id >= len(traders):
        raise HTTPException(status_code=404, detail="Trader not found")
    return {"strategy_data": "Data for trader {}".format(trader_id)}

@app.get("/api/trading_data/{trader_id}")
async def get_trade_data(trader_id: int):
    if trader_id >= len(traders):
        raise HTTPException(status_code=404, detail="Trader not found")
    # return {"tradeing_data": "Data for trader {}".format(trader_id)}
    trading_data = traders[trader_id].show_tradingdata()
    return trading_data

@app.get("/trading_data/{trader_id}")
async def serve_frontend(trader_id: int):
    return FileResponse('frontend/trading_data.html')  #0?trader_id=0 

@app.get("/chart/{trader_id}")
async def get_chart(trader_id: int):
    if trader_id >= len(traders):
        raise HTTPException(status_code=404, detail="Trader not found")
    return {"chart": "Chart for trader {}".format(trader_id)}

@app.get("/strategy_and_trade_info/{trader_id}")
async def get_strategy_and_trade_info(trader_id: int):
    if trader_id >= len(traders):
        raise HTTPException(status_code=404, detail="Trader not found")
    return {"strategy_and_trade_info": "Strategy and Trade Info for trader {}".format(trader_id)}

@app.post("/set_tradeswitch/{trader_id}")
async def set_tradeswitch(trader_id: int, switch: bool):
    if trader_id >= len(traders):
        raise HTTPException(status_code=404, detail="Trader not found")
    traders[trader_id].set_tradeswitch(switch)
    return {"trader_id": trader_id, "tradeswitch": switch}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
