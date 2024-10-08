from binance.um_futures import UMFutures
import requests
import logging
from lb_logger import log
import pandas as pd
import json
from lb_para_handler import ParameterHandler
from datetime import datetime, timedelta, timezone
from lb_trading_db import TradeDatabase
from lb_im_telegram import TelegramNotifier



class Bn_um_future(UMFutures):
    def __init__(self, cfg_json, db_name):

        self.param_handler = ParameterHandler()
        self.param_handler.load_from_json(cfg_json)

        secret = self.param_handler.get_param('secret',None)
        key = self.param_handler.get_param('key',None)
        super().__init__(key, secret)

        self.symbol = self.param_handler.get_param('symbol','BTCUSDT')
        self.positionside = self.param_handler.get_param('positionSide','BOTH')
        self.USDTquantity = self.param_handler.get_param('USDTquantity',200)
        self.leverage = self.param_handler.get_param('leverage',100)

        self.trading_db = TradeDatabase(db_name)
        self.im_notifier = TelegramNotifier()

        self.logger = log

        print(f'symbol:{self.symbol}')
        print(f'positionside:{self.positionside}')
        print(f'USDTquantity:{self.USDTquantity}')
        print(f'leverage:{self.leverage}')
 

    def v3_account(self, **kwargs):
        url_path = "/fapi/v3/account"
        try:
            response = self.sign_request("GET", url_path, {**kwargs})
            if 'code' in response and response['code'] != 200:
                self.logger.error(f"API error occurred: {response}")
                return None
            return response
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
        return None 

    def place_order(self, symbol, side, order_type, **kwargs):
        # 订单类型参数
        # MARKET 市价单
        # LIMIT 限价单
        # STOP 止损单
        # TAKE_PROFIT 止盈单
        # LIQUIDATION 强平单
        try:
            order = super().new_order(
                symbol=symbol,
                side=side,
                type=order_type,
                **kwargs
            )
            if 'code' in order and order['code'] != 200:
                self.logger.error(f"API error occurred while placing order: {order}")
                return None
            return order
        except requests.exceptions.HTTPError as err:
            self.logger.error(f"HTTP error occurred while placing order: {err}")
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Error occurred while placing order: {err}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred while placing order: {e}")
        return None

    def _filter_non_zero_info(self,account_info):
        if account_info is None:
            return None
        
        filtered_positions = [position for position in account_info['positions'] if float(position['positionAmt']) != 0]
        filtered_assets = [asset for asset in account_info['assets'] if float(asset['walletBalance']) != 0]
        
        account_info['positions'] = filtered_positions
        account_info['assets'] = filtered_assets
        
        return account_info

    def convert_account_info(self, account_data, langCn = True):
        if not account_data:
            self.logger.info("No account information to display.")
            return None, None, None
        account_data = self._filter_non_zero_info(account_data)
        # General account information
        general_info = {
            'totalInitialMargin': account_data.get('totalInitialMargin', ''),
            'totalMaintMargin': account_data.get('totalMaintMargin', ''),
            'totalWalletBalance': account_data.get('totalWalletBalance', ''),
            'totalUnrealizedProfit': account_data.get('totalUnrealizedProfit', ''),
            'totalMarginBalance': account_data.get('totalMarginBalance', ''),
            'totalPositionInitialMargin': account_data.get('totalPositionInitialMargin', ''),
            'totalOpenOrderInitialMargin': account_data.get('totalOpenOrderInitialMargin', ''),
            'totalCrossWalletBalance': account_data.get('totalCrossWalletBalance', ''),
            'totalCrossUnPnl': account_data.get('totalCrossUnPnl', ''),
            'availableBalance': account_data.get('availableBalance', ''),
            'maxWithdrawAmount': account_data.get('maxWithdrawAmount', '')
        }
        general_info_df = pd.DataFrame([general_info])

        # Asset information
        assets_data = account_data.get('assets', [])
        assets_df = pd.DataFrame(assets_data)

        # Position information
        positions_data = account_data.get('positions', [])
        positions_df = pd.DataFrame(positions_data)

        if langCn == True:
            # Translate column names
            general_info_columns = {
                'totalInitialMargin': '总起始保证金',
                'totalMaintMargin': '总维持保证金',
                'totalWalletBalance': '总账户余额',
                'totalUnrealizedProfit': '总未实现盈亏',
                'totalMarginBalance': '总保证金余额',
                'totalPositionInitialMargin': '总持仓起始保证金',
                'totalOpenOrderInitialMargin': '总挂单起始保证金',
                'totalCrossWalletBalance': '全仓账户余额',
                'totalCrossUnPnl': '全仓未实现盈亏',
                'availableBalance': '可用余额',
                'maxWithdrawAmount': '最大可转出余额'
            }
            
            assets_columns = {
                'asset': '资产',
                'walletBalance': '余额',
                'unrealizedProfit': '未实现盈亏',
                'marginBalance': '保证金余额',
                'maintMargin': '维持保证金',
                'initialMargin': '起始保证金',
                'positionInitialMargin': '持仓起始保证金',
                'openOrderInitialMargin': '挂单起始保证金',
                'crossWalletBalance': '全仓账户余额',
                'crossUnPnl': '全仓未实现盈亏',
                'availableBalance': '可用余额',
                'maxWithdrawAmount': '最大可转出余额',
                'updateTime': '更新时间'
            }

            positions_columns = {
                'symbol': '交易对',
                'positionSide': '持仓方向',
                'positionAmt': '持仓数量',
                'unrealizedProfit': '持仓未实现盈亏',
                'initialMargin': '持仓起始保证金',
                'maintMargin': '维持保证金',
                'updateTime': '更新时间'
            }

            general_info_df.rename(columns=general_info_columns, inplace=True)
            assets_df.rename(columns=assets_columns, inplace=True)
            positions_df.rename(columns=positions_columns, inplace=True)
        
        print("一般信息:")
        print(general_info_df)
        print("\n资产:")
        print(assets_df)
        print("\n头寸:")
        print(positions_df)

        return general_info_df, assets_df, positions_df

    def get_position_by_symbol(self,account_data, symbol):
        positions_data = account_data.get('positions', [])
        positions_df = pd.DataFrame(positions_data)

        if positions_df.empty:
            return None

        position = positions_df[positions_df['symbol'] == symbol]
        
        if position.empty:
            return None

        return position

    def get_position_by_symbolAndpositionside(self, account_data, symbol, position_side):
        positions_data = account_data.get('positions', [])
        positions_df = pd.DataFrame(positions_data)

        if positions_df.empty:
            return None

        # 过滤符合symbol和position_side的头寸
        position = positions_df[(positions_df['symbol'] == symbol) & (positions_df['positionSide'] == position_side)]
        
        if position.empty:
            return None

        # 返回头寸持仓数量
        position_amt = position['positionAmt'].iloc[0]
        return float(position_amt)


    def get_order(self, symbol, order_id):
        # 订单状态 (status):
        # NEW 新建订单
        # PARTIALLY_FILLED 部分成交
        # FILLED 全部成交
        # CANCELED 已撤销
        # REJECTED 订单被拒绝
        # EXPIRED 订单过期(根据timeInForce参数规则)
        # EXPIRED_IN_MATCH 订单被STP过期
        try:
            order = super().query_order(symbol=symbol, orderId=order_id)
            if 'code' in order and order['code'] != 200:
                self.logger.error(f"API error occurred while placing order: {order}")
                return None
            return order
        except requests.exceptions.HTTPError as err:
            self.logger.error(f"HTTP error occurred while retrieving order: {err}")
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Error occurred while retrieving order: {err}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred while retrieving order: {e}")
        return None

    def cancel_order(self, symbol, order_id):
        try:
            order = super().cancel_order(symbol=symbol, orderId=order_id)
            if 'code' in order and order['code'] != 200:
                self.logger.error(f"API error occurred while placing order: {order}")
                return None
            return result
        except requests.exceptions.HTTPError as err:
            self.logger.error(f"HTTP error occurred while cancelling order: {err}")
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Error occurred while cancelling order: {err}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred while cancelling order: {e}")
        return None
    def _convert_timestamp_to_datetime(self,timestamp):
        # TODO: 修改为带时区的时间
        # 转换时间戳（毫秒）为秒
        timestamp_in_seconds = timestamp / 1000
        # 使用datetime.fromtimestamp()方法转换为datetime对象
        dt_object = datetime.fromtimestamp(timestamp_in_seconds)
        # 格式化日期时间对象为字符串
        formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_time
    
    def _perform_tradingorder(self,trade_side,trade_price):
        # 获取账户信息信息
        account_info = self.v3_account(recvWindow = 6000)
        if account_info is not  None:
            # 获取当前头寸信息
            # Positions = account.get_position_by_symbol(account_info, self.symbol)
            Positions = self.get_position_by_symbolAndpositionside(account_data=account_info,symbol=self.symbol,position_side=self.positionside)
            # 无symbol的long头寸且执行BUY操作
            # 有symbol的long头寸且执行SELL操作
            if (Positions is None and trade_side == 'BUY') or (Positions is not None and trade_side == 'SELL'):
                print("Action!!")

                # # 获取当前的quantity信息和计划投资信息，计算期待交易量
                if trade_side == 'BUY':
                    trade_quantity = round(self.USDTquantity*self.leverage/trade_price, 3)
                elif trade_side == 'SELL':
                    trade_quantity = Positions
                print(f'trade_quantity:{trade_quantity}')
                # 执行交易操作(json获取symbol，获取quantity，获取position side？，执行side)        
                order = self.place_order(symbol=self.symbol, 
                                            side=trade_side,   
                                            order_type='MARKET', 
                                            positionSide = self.positionside,
                                            quantity=trade_quantity)
                
                if order is not None:
                    # order_dict = json.loads(order)
                    if isinstance(order, dict):
                        order_dict = order
                    else:
                        order_dict = json.loads(order)
                    # 提取 orderId 信息
                    trade_order_id = order_dict.get("orderId")
                    print(f'orderid:{trade_order_id}')
                    confirm_order = self.get_order(symbol=self.symbol,order_id=trade_order_id)
                    # 根据返回订单号查询交易执行情况，如成功
                    if confirm_order is not None:
                        # confirm_order_dict = json.loads(confirm_order)
                        confirm_order_dict = confirm_order
                        # 获得订单信息
                        # 记录交易到数据库
                        trade_execute_status = confirm_order_dict['status']  #交易状态
                        trade_execute_time=self._convert_timestamp_to_datetime(confirm_order_dict['time']) #交易时间
                        trade_execute_volume= confirm_order_dict['executedQty'] #交易量
                        trade_execute_price= confirm_order_dict['avgPrice']  #交易价

                        print(f'trade_execute_status:{trade_execute_status}')
                        print(f'trade_execute_time:{trade_execute_time}')
                        print(f'trade_execute_volume:{trade_execute_volume}')
                        print(f'trade_execute_price:{trade_execute_price}')

                        self.trading_db.insert_trade(symbol = self.symbol,
                                                     side = trade_side,
                                                     position_side=self.positionside,
                                                     trade_volume=trade_execute_volume, 
                                                     trade_price= trade_execute_price, 
                                                     order_id= trade_order_id, 
                                                     execution_time=trade_execute_time)
                        self.trading_db.print_trades_as_dataframe()
                        self.im_notifier.send_trade_info(symbol=self.symbol,
                                                        side = trade_side,
                                                        position_side=self.positionside,
                                                        trade_volume=trade_execute_volume,
                                                        trade_price=trade_execute_price,
                                                        leverage = self.leverage,
                                                        order_id = trade_order_id,
                                                        execution_time= trade_execute_time)
                        return True
        return False
    def _test_perform_order(self, trade_side, trade_price):
        # ---------------------------------------------------
        # 下面是测试代码，在实战交易前模拟使用
        now = datetime.now()
        trade_quantity = 0.05
        self.trading_db.insert_trade(symbol = self.symbol,
                                             side = trade_side,
                                             position_side=self.positionside,
                                             trade_volume= trade_quantity, 
                                             trade_price= trade_price, 
                                             order_id= '123456',
                                             execution_time= now.strftime('%Y-%m-%d %H:%M:%S') )
        # self.trading_db.print_trades_as_dataframe()
        # 发送IM消息 
        self.im_notifier.send_trade_info(symbol=self.symbol,
                                         side = trade_side,
                                         position_side=self.positionside,
                                         trade_volume=trade_quantity,
                                         trade_price=trade_price,
                                         leverage = self.leverage,
                                         order_id = '123456',
                                         execution_time= now.strftime('%Y-%m-%d %H:%M:%S'))
        return
    
    def process_trade(self, df, current_time=None):
        # self.logger.info("Start Process trade")
        try:
            # 获取当前本地时间
            if current_time is None:
                current_time = datetime.now()

            # 计算窗口期基数：获取 df 中最近两条记录的时间间隔
            if len(df) >= 2:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values(by='timestamp', ascending=False)
                window_base = (df['timestamp'].iloc[0] - df['timestamp'].iloc[1]).total_seconds()
            else:
                window_base = 60  # 默认窗口基数为60秒

            # 确定时间窗口
            time_window_start = current_time - timedelta(seconds=window_base + 120)  # 后向时间段
            time_window_end = current_time + timedelta(minutes=2)  # 前向时间段

            self.logger.info(f'Current time is {current_time} {time_window_start} {time_window_end}')
            # print(df)
            # 筛选满足条件的条目
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['processed'] = df['processed'].fillna(False)
            mask = (
                (df['timestamp'] >= time_window_start) &
                (df['timestamp'] <= time_window_end) &
                (df['processed'] == False) &
                (df[['buy', 'sell']].notnull().any(axis=1))
            )
            df_filtered = df[mask].sort_values(by='timestamp', ascending=False)
            print('It is a test')
            print(df_filtered)

            # 处理找到的第一个信号
            if not df_filtered.empty:
                row = df_filtered.iloc[0]
                if pd.notnull(row['buy']):
                    self._test_perform_order(trade_side='BUY', trade_price=row['buy'])
                elif pd.notnull(row['sell']):
                    self._test_perform_order(trade_side='SELL', trade_price=row['sell'])

                df.at[row.name, 'processed'] = True  # 标记为已处理

                # 将返回的 df_filtered 转换为字符串格式
                df_filtered['timestamp'] = df_filtered['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
                # print(df.loc[row.name])
                return df.loc[[row.name]]

        except Exception as e:
            self.logger.error(f"An error occurred during trade processing: {e}")

        return None 
# Example usage
def test_process_function():
    data = {
    'timestamp': [
        '2024-08-14 15:00:00',
        '2024-08-14 15:05:00',
        '2024-08-14 15:10:00',
        '2024-08-14 15:15:00',
        '2024-08-14 15:20:00'
    ],
    'open': [100, 102, 104, 106, 108],
    'high': [101, 103, 105, 107, 109],
    'low': [99, 101, 103, 105, 107],
    'close': [100.5, 102.5, 104.5, 106.5, 108.5],
    'volume': [1000, 1500, 2000, 2500, 3000],
    'sma_fast': [101, 103, 105, 107, 109],
    'sma_slow': [100, 102, 104, 106, 108],
    'volume_ma': [1200, 1600, 1800, 2200, 2600],
    'signal': [None, 'buy', None, 'sell', None],
    'buy': [None, 102.5, None, None, 113.5],
    'sell': [None, None, None, 106.5, None],
    'processed': [True, None, None, None, False]
    }
    # 创建 DataFrame
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])  # 转换为 datetime 类型
    print(df)

    test_para = {
            'trader_cfg': 'configure/user_cfg.json',
            'trader_db':  'test/trader_test.db'
    }
    account = Bn_um_future(test_para['trader_cfg'], test_para['trader_db'])

    test_time = datetime(2024, 8, 14 ,15, 23)  # 例如2024-08-12 13:08:00
    account.process_trade(df,test_time)
    return

if __name__ == '__main__':
    test_process_function()
    # param_handler = ParameterHandler()
    # param_handler.load_from_json('configure/user_cfg.json')

    # test_para = {
    #         'trader_cfg': 'configure/user_cfg.json',
    #         'trader_db':  'test/trader_test.db'
    # }
    # account = Bn_um_future(test_para['trader_cfg'], test_para['trader_db'])
    # # account._perform_tradingorder('SELL', 64254.03)
    # # account._test_perform_order('BUY', 64254.03)
    # account_info  = account.v3_account()
    # account.convert_account_info(account_info)

    # # Get v3 account info
    # account_info = account.v3_account(recvWindow = 6000)
    # if account_info is not  None:
    #     # account.convert_account_info(account_info)
    #     Positions = account.get_position_by_symbol(account_info, account.symbol)
    #     if Positions is None:
    #         print("No positions")
    #     else:
    #         print(Positions)

    # 买入LONG单试例
    # order = account.place_order(
                    # symbol='DOGEUSDT', 
                    # side='BUY',   
                    # order_type='MARKET', 
                    # positionSide = "LONG",
                    # quantity=40)
    # 平掉LONG单试例
    # order = account.place_order(
    #                 symbol='DOGEUSDT', 
    #                 side='SELL', 
    #                 order_type='MARKET',
    #                 positionSide = "LONG",
    #                 quantity=40)

    # if order != None:
    #     # print(order)
    #     order_response = OrderResponse(order)
    #     print(order_response.status)
    #     # 访问订单ID
    #     print(f"订单ID: {order_response.order_id}")
    #     # 访问买卖方向
    #     print(f"买卖方向: {order_response.side}")
    #     # 访问订单状态
    #     print(f"订单状态: {order_response.status}")

    # 查询订单试例，确认订单是否完成
    # if order:
    #     order_info = account.get_order(symbol='DOGEUSDT', order_id=order_response.order_id)
    #     print(order_info['status'])



