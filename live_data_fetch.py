from binance.um_futures import UMFutures
import pandas as pd
from lb_para_handler import ParameterHandler
from lb_logger import log
# from rt_ma_db_handle import db_strategy

class LiveDataFetcher:
    def __init__(self): 
        self.fech_handler = UMFutures()
    
    def _get_paramter(self, param_handler):
        #后续可以考虑加上参数： 交易所， 交易类型：现货，币本位，U本位合约等
        self.symbol = param_handler.get_param('symbol','BTCUSDT')
        self.timeframe = param_handler.get_param('timeframe','1h')
        self.limit = param_handler.get_param('limit', 200)
        self.tocsv = param_handler.get_param('tocsv', None)
 
    def fetch_data(self,param_handler):
        try:
            self._get_paramter(param_handler)
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
            log.info(df.tail(1))
            # 保存数据到CSV文件
            if self.tocsv:
                df.to_csv(self.tocsv, index=False)
            
            # TODO: 在测试函数里面去掉这个代码，存储单独的类来处理
            # db_strategy.insert_or_update_data(df) 
        except Exception as e:
            log.error(f"Error fetch data: {e}")
        
        return df

if __name__ == '__main__':
    params = {
        'symbol':'BTCUSDT',
        'timeframe': '1h',
        'limit': 200
    }

    param_handler = ParameterHandler()
    param_handler.load_from_json('configure/data_cfg.json')
    bn_future_fetch = LiveDataFetcher()
    df = bn_future_fetch.fetch_data(param_handler)
    log.info(df)
    # db_strategy.insert_or_update_data(df)

