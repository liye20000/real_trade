# real trade ma strategy implemention
import pandas as pd
import pandas_ta as ta
from lb_para_handler import ParameterHandler
from lb_logger import log

class CoreDMAStrategy:
    def __init__(self,cfg_json):
        self.param_handler = ParameterHandler()
        self.cfg = cfg_json
        self.logger = log

    def _get_paramter(self):
        self.param_handler.load_from_json(self.cfg)
        self.fast_period = self.param_handler.get_param('fast_period', 5)
        self.slow_period = self.param_handler.get_param('slow_period', 20)
        self.volume_threshold = self.param_handler.get_param('volume_threshold', 1.5)
        self.volume_window = self.param_handler.get_param('volume_window', 5)


    def _calculate_indicators(self,df):

        df['sma_fast'] = ta.sma(df['close'], length=self.fast_period)
        df['sma_slow'] = ta.sma(df['close'], length=self.slow_period)
        df['volume_ma'] = ta.sma(df['volume'], length=self.volume_window)
        # Ensure the volume and volume_ma columns are of type float
        df['volume'] = df['volume'].astype(float)
        df['volume_ma'] =df['volume_ma'].astype(float)

        df['signal'] = df['sma_fast'] - df['sma_slow']
        return df

    def generate_signals(self,df):

        try:
            self._get_paramter()
            df = self._calculate_indicators(df)
            signals = []
            df['buy'] = None
            df['sell'] = None

            for i in range(1, len(df)):
                # volume_increasing = self.df['volume'][i] > self.volume_threshold * self.df['volume_ma'][i]
                volume_increasing = True # 为了后面读写信号测试用
                if df['signal'][i] > 0 and df['signal'][i - 1] <= 0 and volume_increasing:
                    df.loc[i,'buy'] = df['close'][i]
                    signals.append(('buy', df['timestamp'][i]))

                elif df['signal'][i] < 0 and df['signal'][i - 1] >= 0 and volume_increasing:
                    signals.append(('sell', df['timestamp'][i]))
                    df.loc[i,'sell'] = df['close'][i]
            # self.logger.info(signals)

        except Exception as e:
            self.logger.error(f"Error generate signals: {e}")
        return df


if __name__ == '__main__':

    # 测试代码
    from live_data_fetch import LiveDataFetcher
    test_para = {
        'fetcher_cfg': 'configure/data_cfg.json',
        'strager_cfg': 'configure/stra_dma_cfg.json'
    }
    bn_future_fetch = LiveDataFetcher(test_para['fetcher_cfg'])
    strategy = CoreDMAStrategy(test_para['strager_cfg'])
    
    df = bn_future_fetch.fetch_data()
    print(df)
    df = strategy.generate_signals(df)

    # 为了让df被打印不截断
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    print(df)




    


