import requests
import time
import hmac
import hashlib
import pandas as pd


API_KEY = "nGXPRad8iBKt2h83U3JOitYPBinu4un7pp5gsBnKSzWACUkvu51UOzNMeNkaDQIN"
SECRET_KEY= "g7EIyuylKe2N28I6SAgK7XFUcBtQDeZYSIGEgojnGHAaJzoitGHMJz3dCaH0Lkpt"
BASE_URL = 'https://fapi.binance.com'

def get_server_time():
    response = requests.get(f'{BASE_URL}/fapi/v1/time')
    return response.json()['serverTime']

def get_account_info(version='v3'):
    endpoint = f'/fapi/{version}/account'
    timestamp = get_server_time()
    recv_window = 5000
    query_string = f'recvWindow={recv_window}&timestamp={timestamp}'
    signature = hmac.new(SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    url = f'{BASE_URL}{endpoint}?{query_string}&signature={signature}'
    
    headers = {
        'X-MBX-APIKEY': API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果请求不成功会引发HTTPError异常
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
    return None

def filter_non_zero_positions(account_info):
    if account_info is None:
        return None
    
    filtered_positions = [position for position in account_info['positions'] if float(position['positionAmt']) != 0]
    filtered_assets = [asset for asset in account_info['assets'] if float(asset['walletBalance']) != 0]
    
    account_info['positions'] = filtered_positions
    account_info['assets'] = filtered_assets
    
    return account_info

def convert_to_dataframe(account_info):
    if account_info is None:
        return None, None, None
    
    assets_df = pd.DataFrame(account_info['assets'])
    positions_df = pd.DataFrame(account_info['positions'])
    general_info = {k: v for k, v in account_info.items() if k not in ['assets', 'positions']}
    general_info_df = pd.DataFrame([general_info])
    
    return general_info_df, assets_df, positions_df

def print_account_info(general_info_df, assets_df, positions_df):
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

if __name__ == '__main__':
    account_info = get_account_info(version='v3')
    if account_info != None:
        filtered_account_info = filter_non_zero_positions(account_info)
        general_info_df, assets_df, positions_df = convert_to_dataframe(filtered_account_info)
        print(general_info_df)
        print(assets_df)
        print(positions_df)
        print_account_info(general_info_df, assets_df, positions_df)
