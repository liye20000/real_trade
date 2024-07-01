import pandas as pd
from binance.client import Client

# 设置API Key和Secret
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_SECRET'

# 创建币安客户端
client = Client(api_key, api_secret)

# 获取K线数据
symbol = 'BTCUSDT'
interval = Client.KLINE_INTERVAL_1MINUTE  # 时间周期，可以选择 '1m', '5m', '15m', '1h', '1d', 等
limit = 100  # 获取最近100条数据

# 获取K线数据
klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)

# 将数据转换成Pandas DataFrame
df = pd.DataFrame(klines, columns=[
    'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
    'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
])

# 删除不需要的列
df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

# 将时间戳转换成可读时间
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# 打印DataFrame
print(df.head())

# 保存数据到CSV文件
df.to_csv('btc_usdt_futures_ohlcv.csv', index=False)
