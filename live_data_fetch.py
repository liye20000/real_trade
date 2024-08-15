from binance.um_futures import UMFutures
import pandas as pd
from lb_para_handler import ParameterHandler
from lb_logger import log
# from zoneinfo import ZoneInfo
from datetime import datetime

class LiveDataFetcher:
    def __init__(self,cfg_json): 
        self.fech_handler = UMFutures()
        self.param_handler = ParameterHandler()
        self.cfg = cfg_json
        self.logger = log
    
    def _get_paramter(self):
        #后续可以考虑加上参数： 交易所， 交易类型：现货，币本位，U本位合约等
        self.param_handler.load_from_json(self.cfg)
        self.symbol = self.param_handler.get_param('symbol','BTCUSDT')
        self.timeframe = self.param_handler.get_param('timeframe','1h')
        self.limit = self.param_handler.get_param('limit', 200)
 
    def fetch_data(self):
        try:
            self._get_paramter()
            klines = self.fech_handler.klines(self.symbol, self.timeframe, limit = self.limit)
            # 将数据转换成Pandas DataFrame
            df = pd.DataFrame(klines, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                         ])
    
            # 删除不需要的列
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            # 获得系统时区
            local_tz = datetime.now().astimezone().tzinfo
            # 将时间戳转换成可读时间,并转换为系统时区
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert(local_tz).dt.strftime('%Y-%m-%d %H:%M:%S')


        except Exception as e:
            self.logger.error(f"Error fetch data: {e}")
        return df

if __name__ == '__main__':
    test_para = {
        'fetcher_cfg': 'configure/data_cfg.json'
    } 
    bn_future_fetch = LiveDataFetcher(test_para['fetcher_cfg'])
    df = bn_future_fetch.fetch_data()
    print(df)
    now = datetime.now()
    execution_time= now.strftime('%Y-%m-%d %H:%M:%S')
    local_tz = datetime.now().astimezone().tzinfo
    print(execution_time)
    # db_strategy.insert_or_update_data(df)

