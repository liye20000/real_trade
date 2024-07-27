from binance.um_futures import UMFutures
import requests
import logging
from lb_logger import log as loguru_logger
import pandas as pd
import json
from lb_para_handler import ParameterHandler

class OrderResponse:
    def __init__(self, data):
        self.client_order_id = data.get("clientOrderId")
        self.cum_qty = data.get("cumQty")
        self.cum_quote = data.get("cumQuote")
        self.executed_qty = data.get("executedQty")
        self.order_id = data.get("orderId")
        self.avg_price = data.get("avgPrice")
        self.orig_qty = data.get("origQty")
        self.price = data.get("price")
        self.reduce_only = data.get("reduceOnly")
        self.side = data.get("side")
        self.position_side = data.get("positionSide")
        self.status = data.get("status")
        self.stop_price = data.get("stopPrice")
        self.close_position = data.get("closePosition")
        self.symbol = data.get("symbol")
        self.time_in_force = data.get("timeInForce")
        self.order_type = data.get("type")
        self.orig_type = data.get("origType")
        self.activate_price = data.get("activatePrice")
        self.price_rate = data.get("priceRate")
        self.update_time = data.get("updateTime")
        self.working_type = data.get("workingType")
        self.price_protect = data.get("priceProtect")
        self.price_match = data.get("priceMatch")
        self.self_trade_prevention_mode = data.get("selfTradePreventionMode")
        self.good_till_date = data.get("goodTillDate")

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

class Bn_um_future(UMFutures):
    def __init__(self, key, secret, use_loguru=False):
        super().__init__(key, secret)
        self.api_key = key
        self.secret_key = secret
        self.use_loguru = use_loguru

        if not self.use_loguru:
            self.logger = logging.getLogger(__name__)
            logging.basicConfig(level=logging.INFO)
        else:
            self.logger = loguru_logger

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

    def filter_non_zero_positions(self,account_info):
        if account_info is None:
            return None
        
        filtered_positions = [position for position in account_info['positions'] if float(position['positionAmt']) != 0]
        filtered_assets = [asset for asset in account_info['assets'] if float(asset['walletBalance']) != 0]
        
        account_info['positions'] = filtered_positions
        account_info['assets'] = filtered_assets
        
        return account_info

    def convert_to_dataframe(self,account_info):
        if account_info is None:
            return None, None, None
        
        assets_df = pd.DataFrame(account_info['assets'])
        positions_df = pd.DataFrame(account_info['positions'])
        general_info = {k: v for k, v in account_info.items() if k not in ['assets', 'positions']}
        general_info_df = pd.DataFrame([general_info])
        
        return general_info_df, assets_df, positions_df

    def print_account_info(self,general_info_df, assets_df, positions_df):
        if general_info_df is None or assets_df is None or positions_df is None:
            print("No account information to display.")
            return

        general_info_columns = {
            'feeTier': '手续费等级',
            'canTrade': '是否可以交易',
            'canDeposit': '是否可以入金',
            'canWithdraw': '是否可以出金',
            'feeBurn': '手续费抵扣',
            'tradeGroupId': '交易组ID',
            'updateTime': '更新时间',
            'multiAssetsMargin': '多资产保证金',
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
            'maxWithdrawAmount': '最大可转出余额',
            'crossWalletBalance': '全仓账户余额',
            'crossUnPnl': '全仓未实现盈亏',
            'availableBalance': '可用余额',
            'marginAvailable': '是否可用作联合保证金',
            'updateTime': '更新时间'
        }

        positions_columns = {
            'symbol': '交易对',
            'initialMargin': '起始保证金',
            'maintMargin': '维持保证金',
            'unrealizedProfit': '未实现盈亏',
            'positionInitialMargin': '持仓起始保证金',
            'openOrderInitialMargin': '挂单起始保证金',
            'leverage': '杠杆倍率',
            'isolated': '是否是逐仓模式',
            'entryPrice': '持仓成本价',
            'breakEvenPrice': '持仓成本价',
            'maxNotional': '最大名义价值',
            'bidNotional': '买单净值',
            'askNotional': '买单净值',
            'positionSide': '持仓方向',
            'positionAmt': '持仓数量',
            'updateTime': '更新时间'
        }

        # Translate column names
        general_info_df.rename(columns=general_info_columns, inplace=True)
        assets_df.rename(columns=assets_columns, inplace=True)
        positions_df.rename(columns=positions_columns, inplace=True)
        
        print("一般信息:")
        print(general_info_df)
        print("\n资产:")
        print(assets_df)
        print("\n头寸:")
        print(positions_df)

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

# Example usage
if __name__ == '__main__':
    param_handler = ParameterHandler()
    param_handler.load_from_json('configure/user_cfg.json')
    secret = param_handler.get_param('secret')
    key = param_handler.get_param('key')

    # Use loguru logger
    account = Bn_um_future(key, secret, use_loguru=True)

    # Get v3 account info
    account_info = account.v3_account(recvWindow = 6000)
    if account_info != None:
        print(account_info)
        filtered_account_info = account.filter_non_zero_positions(account_info)
        general_info_df, assets_df, positions_df = account.convert_to_dataframe(filtered_account_info)
        print(general_info_df)
        print(assets_df)
        print(positions_df)
        account.print_account_info(general_info_df, assets_df, positions_df)

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



