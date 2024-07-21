# real trade ma strategy implemention
import pandas as pd
import pandas_ta as ta
from lb_para_handler import ParameterHandler
from live_data_fetch import LiveDataFetcher

class CoreDMAStrategy:
    def __init__(self, df, param_handler):
        self.df = df
        self.fast_period = param_handler.get_param('fast_period', 5)
        self.slow_period = param_handler.get_param('slow_period', 15)
        self.volume_threshold = param_handler.get_param('volume_threshold', 1.5)
        self.volume_window = param_handler.get_param('volume_window', 5)

        self._calculate_indicators()
        print(f'p fast {self.fast_period}')
        print(f'p slow {self.slow_period}')

    def _calculate_indicators(self):
        self.df['sma_fast'] = ta.sma(self.df['close'], length=self.fast_period)
        self.df['sma_slow'] = ta.sma(self.df['close'], length=self.slow_period)
        self.df['volume_ma'] = ta.sma(self.df['volume'], length=self.volume_window)
        # Ensure the volume and volume_ma columns are of type float
        self.df['volume'] = self.df['volume'].astype(float)
        self.df['volume_ma'] = self.df['volume_ma'].astype(float)

        self.df['signal'] = self.df['sma_fast'] - self.df['sma_slow']

    def generate_signals(self):
        signals = []
        for i in range(1, len(self.df)):
            volume_increasing = self.df['volume'][i] > self.volume_threshold * self.df['volume_ma'][i]
            if self.df['signal'][i] > 0 and self.df['signal'][i - 1] <= 0 and volume_increasing:
                signals.append(('buy', self.df['timestamp'][i]))
            elif self.df['signal'][i] < 0 and self.df['signal'][i - 1] >= 0 and volume_increasing:
                signals.append(('sell', self.df['timestamp'][i]))
        print(signals)
        return signals


if __name__ == '__main__':
    # 示例参数字典
    params = {
    'fast_period': 11,
    'slow_period': 21,
    'volume_threshold': 1.5,
    'volume_window': 5
    }
    param_handler = ParameterHandler(params)
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
    data_params = {
        'symbol':'BTCUSDT',
        'timeframe': '1h',
        'limit': 200
    }
    data_param_handler = ParameterHandler(data_params)
    bn_future_fetch = LiveDataFetcher(data_param_handler)
    data = bn_future_fetch.fetch_data()

    strategy = CoreDMAStrategy(data, param_handler)
    signals = strategy.generate_signals()
    print(signals)

