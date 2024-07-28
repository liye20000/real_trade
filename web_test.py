from fastapi import FastAPI, BackgroundTasks, Request
import pandas as pd
from datetime import datetime, timedelta
import time
import asyncio
import plotly.graph_objects as go
import pandas_ta as ta

# 假设这两个类已经定义好了
from rt_ma_strategy import CoreDMAStrategy
from live_data_fetch import LiveDataFetcher
from lb_para_handler import ParameterHandler
from fastapi.responses import HTMLResponse
from plotly.subplots import make_subplots
from lb_logger import log
from rt_ma_db_handle import db_strategy

app = FastAPI()
def create_candlestick_chart():
    # fig = go.Figure(data=[go.Candlestick(x=df['timestamp'],
    #                                      open=df['open'],
    #                                      high=df['high'],
    #                                      low=df['low'],
    #                                      close=df['close'])])
    
    # fig.update_layout(title='Candlestick Chart', xaxis_title='Date', yaxis_title='Price')

    # df = pd.read_csv('data/db_btcusdt.csv')
    df = db_strategy.fetch_data(limit = 50)
    # df['sma_fast'] = ta.sma(df['close'], length=11)
    # df['sma_slow'] = ta.sma(df['close'], length=21)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                        row_heights=[0.7, 0.3])

    # K 线图
    fig.add_trace(go.Candlestick(x=df['timestamp'],
                                 open=df['open'],
                                 high=df['high'],
                                 low=df['low'],
                                 close=df['close'],
                                 name='Candlesticks'), row=1, col=1)

    # 交易量
    fig.add_trace(go.Bar(x=df['timestamp'], y=df['volume'], name='Volume', marker=dict(color='blue', opacity=0.5)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['volume_ma'], mode='lines', name='Volume SMA'), row=2, col=1)
    
    # 双均线
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['sma_fast'], mode='lines', name='Fast SMA'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['sma_slow'], mode='lines', name='Slow SMA'), row=1, col=1)

    

    # 买卖信号测试用
    # for signal in signals:
    #     action, timestamp, volume, price = signal
    #     color = 'red' if action == 'buy' else 'green'
    #     label = f"{action.capitalize()}<br>Time: {timestamp}<br>Volume: {volume}<br>Price: {price}"
    #     fig.add_trace(go.Scatter(x=[timestamp], y=[price], mode='markers+text', marker=dict(color=color, size=10),
    #                              text=label, textposition='top center', name=action.capitalize()), row=1, col=1)

    # action, timestamp, volume, price = signal
    # timestamp = '2024-07-19 08:00:00'
    # color = 'red'
    # volume = '100'
    # price = 65300
    # action = 'buy'
    # label = f"{action.capitalize()}<br>Time: {timestamp}<br>Volume: {volume}<br>Price: {price}"
    # fig.add_trace(go.Scatter(x=[timestamp], y=[price], mode='markers+text', marker=dict(color=color, size=20),
    #                              text=label, textposition='top center', name=action.capitalize()), row=1, col=1) 
    
    
    # 遍历数据框，添加买入和卖出信号
    for i, row in df.iterrows():
        if row['buy']:
            label = f"Buy<br>Time: {row['timestamp']}<br>Price: {row['buy']}"
            fig.add_trace(go.Scatter(
                x=[row['timestamp']],
                y=[row['buy']],
                mode='markers+text',
                marker=dict(color='red', size=10),
                text=label,
                textposition='top center',
                name='Buy',
                legendgroup='Buy',  # 分组
                showlegend=i == 0  # 只在第一次出现时显示图例
            ), row=1, col=1)

        if row['sell']:
            label = f"Sell<br>Time: {row['timestamp']}<br>Price: {row['sell']}"
            fig.add_trace(go.Scatter(
                x=[row['timestamp']],
                y=[row['sell']],
                mode='markers+text',
                marker=dict(color='green', size=10),
                text=label,
                textposition='top center',
                name='Sell',
                legendgroup='Sell',  # 分组
                showlegend=i == 0  # 只在第一次出现时显示图例
            ), row=1, col=1)


    # fig.update_layout(title='Candlestick Chart with Volume and Trading Signals',
    #                   xaxis_title='Date',
    #                   yaxis_title='Price')
    fig.update_layout(title='Candlestick Chart with Volume and Trading Signals',
                      xaxis_title='Date',
                      yaxis_title='Price',
                      template='plotly_dark',  # 使用Plotly自带的深色模板
                      plot_bgcolor='black',  # 图表背景颜色
                      paper_bgcolor='black',  # 纸张背景颜色
                      font=dict(color='white'))  # 字体颜色

    return fig 
class DataProcessor:
    def __init__(self):
        self.data_param_handler = ParameterHandler()
        self.fetcher = LiveDataFetcher()
        self.strategy = CoreDMAStrategy()
        self.last_run = datetime.now() #- timedelta(seconds=10)

    
    async def fetch_and_process_data(self):
        # 检查是否到了新的时间段
        while True:
            current_time = datetime.now()
            if current_time - self.last_run >= timedelta(seconds=10):
                
                # 获取数据
                self.data_param_handler.load_from_json('configure/data_cfg.json')
                self.fetcher.fetch_data(self.data_param_handler)

                # 策略计算 
                self.data_param_handler.load_from_json('configure/stra_dma_cfg.json')
                signals = self.strategy.generate_signals(self.data_param_handler)

                # TODO 执行买卖操作

                # # 打印相关信息
                # print(signals)
                log.info(f'{current_time}It is just test sending')
                self.last_run = current_time
            await asyncio.sleep(5)  # 每分钟检查一次

data_processor = DataProcessor()

@app.on_event("startup")
async def startup_event():
    # 启动数据处理任务
    asyncio.create_task(data_processor.fetch_and_process_data())

@app.get("/")
def read_root():
    return {"message": "FastAPI server is running"}

@app.get("/strategy_results")
def get_strategy_results():
    # return {"results": data_processor.strategy.results}
    return {"results": "Test get result"}

@app.get("/chart/", response_class=HTMLResponse)
def get_chart():
    # fetcher = LiveDataFetcher()
    # df = fetcher.fetch_data()
    fig = create_candlestick_chart()
    # return fig.to_html(full_html=False)
    chart_html = fig.to_html(full_html=False)
    html_content = f"""
                    <html>
                    <head>
                        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                    </head>
                    <body>
                        {chart_html}
                    </body>
                    </html>
                    """
    return HTMLResponse(content=html_content)

@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down FastAPI server...")
    # 在这里可以添加清理资源的代码，比如关闭数据库连接等

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

if __name__ == "__main__":
    import uvicorn
    from signal import SIGINT, SIGTERM
    # uvicorn.run(app, host="0.0.0.0", port=8090)
    def run():
        loop = asyncio.get_event_loop()
        server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=8000))

        async def main():
            loop.add_signal_handler(SIGINT, lambda: asyncio.create_task(server.shutdown()))
            loop.add_signal_handler(SIGTERM, lambda: asyncio.create_task(server.shutdown()))
            await server.serve()

        loop.run_until_complete(main())

    run()