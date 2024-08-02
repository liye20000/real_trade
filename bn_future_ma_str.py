# TODO：一个交易类应由一下元素构成
# storer 数据存储对象，支撑计算数据和存储
# fetcher 数据获取对象
# strager 策略执行对象
# trader  交易执行对象,包含账号信息,交易存储，IM执行等操作
# shower  显示对象，用来对交易情况做图形显示
# Processer 后台策略执行函数

from lb_logger import log
from rt_ma_db_handle import db_strategy
from rt_ma_strategy import CoreDMAStrategy
from live_data_fetch import LiveDataFetcher
from lb_para_handler import ParameterHandler
from bn_um_future import Bn_um_future
class bn_future_ma_trader:
    def __init__(self):
        self.fetcher = LiveDataFetcher()
        self.strager = CoreDMAStrategy()
        self.storer = db_strategy
        self.param_handler = ParameterHandler()
        self.param_handler.load_from_json('configure/user_cfg.json')
        self.trader = Bn_um_future(param_handler=self.param_handler)
        self.tradeswitch = True
        self.logger = log
    
    def set_tradeswitch(self, switch):
        self.tradeswitch = switch
        return self.tradeswitch

    def process_stragy(self):
        try:
            if self.tradeswitch==True :
                #获取数据
                self.param_handler.load_from_json('configure/data_cfg.json')
                df = self.fetcher.fetch_data(self.param_handler)
                self.storer.insert_or_update_data(df)
                # self.storer.print_data()
                
                #策略处理，数据更新
                df = self.storer.fetch_data()
                self.param_handler.load_from_json('configure/stra_dma_cfg.json')
                self.strager.generate_signals(self.param_handler,df)
                self.storer.insert_or_update_data(df)
                # self.storer.print_data()

                #交易处理
                df = self.storer.fetch_data()
                self.trader.process_trade(df)
                
        except Exception as e:            
            self.logger.error(f"unexpected error occured: {e}")
        return None

    def process_chart(self):
        return

    def show_traderinfo(self):
        return
    
    def show_strategyinfo(self):
        return

if __name__ == "__main__":
    
    test_trader = bn_future_ma_trader()

    test_trader.process_stragy()
    


