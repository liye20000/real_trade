# real trade ma strategy implemention
import pandas as pd
import pandas_ta as ta
from lb_para_handler import ParameterHandler
from live_data_fetch import LiveDataFetcher
from lb_logger import log
import numpy as np
from rt_ma_db_handle import db_strategy

class CoreDMAStrategy:
    def __init__(self):
        pass

    def _get_paramter(self,param_handler):
        self.fast_period = param_handler.get_param('fast_period', 5)
        self.slow_period = param_handler.get_param('slow_period', 15)
        self.volume_threshold = param_handler.get_param('volume_threshold', 1.5)
        self.volume_window = param_handler.get_param('volume_window', 5)
        self.fromcsv = param_handler.get_param('fromcsv',None)
        self.tocsv = param_handler.get_param('tocsv',None)


    def _calculate_indicators(self):
        # self.df = pd.read_csv(self.fromcsv)
        self.df = db_strategy.fetch_data()

        self.df['sma_fast'] = ta.sma(self.df['close'], length=self.fast_period)
        self.df['sma_slow'] = ta.sma(self.df['close'], length=self.slow_period)
        self.df['volume_ma'] = ta.sma(self.df['volume'], length=self.volume_window)
        # Ensure the volume and volume_ma columns are of type float
        self.df['volume'] = self.df['volume'].astype(float)
        self.df['volume_ma'] = self.df['volume_ma'].astype(float)

        self.df['signal'] = self.df['sma_fast'] - self.df['sma_slow']

    def generate_signals(self,param_handler):

        try:
            self._get_paramter(param_handler)
            self._calculate_indicators()
            signals = []
            self.df['buy'] = None
            self.df['sell'] = None

            for i in range(1, len(self.df)):
                # volume_increasing = self.df['volume'][i] > self.volume_threshold * self.df['volume_ma'][i]
                volume_increasing = True # 为了后面读写信号测试用
                if self.df['signal'][i] > 0 and self.df['signal'][i - 1] <= 0 and volume_increasing:
                    self.df.loc[i,'buy'] = self.df['close'][i]
                    signals.append(('buy', self.df['timestamp'][i]))

                elif self.df['signal'][i] < 0 and self.df['signal'][i - 1] >= 0 and volume_increasing:
                    signals.append(('sell', self.df['timestamp'][i]))
                    self.df.loc[i,'sell'] = self.df['close'][i]
            log.info(signals)


            if self.tocsv:
                # self.df.to_csv(self.tocsv,index=False)
                db_strategy.insert_or_update_data(self.df)
        except Exception as e:
            log.error(f"Error generate signals: {e}")
        return signals


if __name__ == '__main__':
    # 示例参数字典
    # params = {
    # 'fast_period': 11,
    # 'slow_period': 21,
    # 'volume_threshold': 1.5,
    # 'volume_window': 5
    # }
    # param_handler = ParameterHandler(params)
    param_handler = ParameterHandler()
    # fast_period  = param_handler.get_param('fast_period',20)
    # print(f'fast_period:{fast_period}')
    # 示例数据
    # data = pd.DataFrame({
    #     'close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    #     'volume': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    # })

    # test
    # data = pd.read_csv('data/btc_usdt_test.csv')
    # print(data)
    # data_params = {
    #     'symbol':'BTCUSDT',
    #     'timeframe': '1h',
    #     'limit': 200
    # }
    data_param_handler = ParameterHandler()
    data_param_handler.load_from_json('configure/data_cfg.json')
    bn_future_fetch = LiveDataFetcher()
    data = bn_future_fetch.fetch_data(data_param_handler)

    # stra_param_handler = ParameterHandler()
    data_param_handler.load_from_json('configure/stra_dma_cfg.json')
    strategy = CoreDMAStrategy()
    signals = strategy.generate_signals(data_param_handler)

    db_strategy.print_data()

