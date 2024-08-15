# TODO：一个交易类应由一下元素构成
# storer 数据存储对象，支撑计算数据和存储
# fetcher 数据获取对象
# strager 策略执行对象
# trader  交易执行对象,包含账号信息,交易存储，IM执行等操作
# shower  显示对象，用来对交易情况做图形显示
# Processer 后台策略执行函数

from lb_logger import log
from rt_ma_db_handle import StrategyDatabase
from rt_ma_strategy import CoreDMAStrategy
from live_data_fetch import LiveDataFetcher
from bn_um_future import Bn_um_future
class bn_future_ma_trader:

    def __init__(self,name=None):
        params = {
                'fetcher_cfg':  'configure/data_cfg.json',
                'strager_cfg':  'configure/stra_dma_cfg.json',
                'strager_db':   'data/ma_stragy.db',
                'trader_cfg':   'configure/user_cfg.json',
                'trader_db':    'data/trading.db'
                 }
        self.name = name
        self.fetcher = LiveDataFetcher(params['fetcher_cfg'])
        self.strager = CoreDMAStrategy(params['strager_cfg'])
        self.storer = StrategyDatabase(params['strager_db'])
        self.trader = Bn_um_future( cfg_json=params['trader_cfg'], 
                                    db_name=params['trader_db'])
        
        self.tradeswitch = True
        self.logger = log
    
    def set_tradeswitch(self, switch):
        self.tradeswitch = switch
        self.logger.info(f"set swiitch {switch}")
        return self.tradeswitch
    
    def get_traderswitch(self):
        return self.tradeswitch

    def process_stategy(self):
        try:
            if self.tradeswitch==True :
                #获取数据
                df = self.fetcher.fetch_data()
                self.storer.insert_or_update_data(df)

                # # test
                # df = self.storer.query_data()
                # print(df)
                
                #策略处理，数据更新
                df = self.storer.query_data()
                df = self.strager.generate_signals(df)
                self.storer.insert_or_update_data(df)

                # # test
                # df = self.storer.query_data()
                # print(df)

                #交易处理
                df = self.storer.query_data()
                df = self.trader.process_trade(df)
                # print(df)
                if df is not None and not df.empty:
                    self.storer.insert_or_update_data(df)
                
                # test
                # df = self.storer.query_data()
                # print(df)
                
        except Exception as e:            
            self.logger.error(f"unexpected error occured: {e}")
        return None

    def process_chart(self):
        return

    def show_traderinfo(self):
        return
    
    def show_strategyinfo(self):
        return
    
    def show_strategydata(self):
        df = self.storer.query_data()
        df = df.fillna(0)  # 将 NaN 值替换为 0，或根据需要替换为其他值
        df = df.replace([float('inf'), float('-inf')], 0)  # 将无穷大替换为 0，或根据需要替换为其他值
        return df.to_dict(orient='records')

    def show_tradingdata(self):
        df = self.trader.trading_db.fetch_trades_as_dataframe()
        df = df.fillna(0)  # 将 NaN 值替换为 0，或根据需要替换为其他值
        df = df.replace([float('inf'), float('-inf')], 0)  # 将无穷大替换为 0，或根据需要替换为其他值
        return df.to_dict(orient='records')

if __name__ == "__main__":
    
    test_trader = bn_future_ma_trader()

    test_trader.process_stategy()

    # test_trader.process_stategy()

    # dict = test_trader.show_strategydata()
    # print(dict)

    # test_trader.sho
     


