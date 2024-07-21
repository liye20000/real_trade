from binance.um_futures import UMFutures
import pandas as pd
from lb_para_handler import ParameterHandler

class LiveDataFetcher:
    def __init__(self, para_handler):
        self.symbol = para_handler.get_param('symbol','BTCUSDT')
        self.timeframe = para_handler.get_param('timeframe','1h')
        self.limit = para_handler.get_param('limit', 200)
        
        #后续可以考虑加上参数： 交易所， 交易类型：现货，币本位，U本位合约等

        self.fech_handler = UMFutures()

    def fetch_data(self):
        klines = self.fech_handler.klines(self.symbol, self.timeframe, limit = self.limit)
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
        print(df)

        # 保存数据到CSV文件
        # df.to_csv('data/btc_usdt_test.csv', index=False)
       
        return df
def get_bndata_via_API():
    um_futures_client = UMFutures()

    # logging.info(um_futures_client.klines("BTCUSDT", "1d"))
    klines = um_futures_client.klines("BTCUSDT", "1h", limit = 550)
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
    # df.to_csv('data/btc_usdt_test.csv', index=False)
    return df


if __name__ == '__main__':
    print("test")
    # get_bndata_via_API()
    params = {
        'symbol':'BTCUSDT',
        'timeframe': '1h',
        'limit': 200
    }

    param_handler = ParameterHandler(params)
    bn_future_fetch = LiveDataFetcher(param_handler)
    bn_future_fetch.fetch_data()
