import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt

import logging
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging


def setup_logging():
    # 创建logger
    logger = logging.getLogger('BNLOG')
    logger.setLevel(logging.DEBUG)  # 设置最低日志级别

    # 创建控制台handler并设置级别为DEBUG
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # 创建文件handler并设置级别为WARNING
    file_handler = logging.FileHandler('debug/BNLOG.log',mode='w') # mode='w' 'a'
    file_handler.setLevel(logging.WARNING)
 
    # 创建formatter并添加到handlers
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 将handlers添加到logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# config_logging(logging, logging.DEBUG)

def get_bndata_via_API():
    um_futures_client = UMFutures()

    # logging.info(um_futures_client.klines("BTCUSDT", "1d"))
    klines = um_futures_client.klines("BTCUSDT", "1d", limit = 100)
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
    # print(df.head())

    # 保存数据到CSV文件
    df.to_csv('data/btc_usdt_test.csv', index=False)
    return df

def process_strategy(df:pd.DataFrame):
    df.set_index('timestamp', inplace=True)
    # 确保所有数据列都是浮点数类型
    df = df.astype(float)
    # 计算短期和长期简单均线
    short_window = 10
    long_window = 30

    df['SMA_short'] = df['close'].rolling(window=short_window).mean()
    df['SMA_long'] = df['close'].rolling(window=long_window).mean()

    # 构建信号：短期均线超过长期均线时买入，短期均线低于长期均线时卖出
    df['Signal'] = 0.0
    df['Signal'][short_window:] = np.where(df['SMA_short'][short_window:] > df['SMA_long'][short_window:], 1.0, 0.0)

    # 生成交易订单
    df['Position'] = df['Signal'].diff()

    # 打印买卖信号
    buy_signals = df[df['Position'] == 1].index
    sell_signals = df[df['Position'] == -1].index

    print("Buy Signals:", buy_signals)
    print("Sell Signals:", sell_signals)

    # 创建一个与 df 大小一致的列，并用 np.nan 填充
    df['buy'] = np.nan
    df['sell'] = np.nan

    # 将买卖信号对应的 close 价格填充到新的列中
    df.loc[buy_signals, 'buy'] = df['close']
    df.loc[sell_signals, 'sell'] = df['close']

    df.to_csv('data/finish_stra_btc_usdt.csv',index = False)

    return df

def process_pic(df:pd.DataFrame):
    # 创建买入卖出信号的添加参数
    apdict = [
        mpf.make_addplot(df['SMA_short'], color='blue', width=1.0),
        mpf.make_addplot(df['SMA_long'], color='orange', width=1.0)
    ]

    # 仅当买入和卖出信号非空时添加相应的 addplot
    if not df['buy'].isnull().all():
        apdict.append(mpf.make_addplot(df['buy'], type='scatter', markersize=100, marker='^', color='green'))
    if not df['sell'].isnull().all():
        apdict.append(mpf.make_addplot(df['sell'], type='scatter', markersize=100, marker='v', color='red'))

    # 创建高分辨率图像
    fig, ax = mpf.plot(df, type='candle', style='charles', addplot=apdict, returnfig=True)

    # 设置中文字体和标题
    # 找到系统中的中文字体
    # font_path = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'  # 根据实际安装路径调整
    # prop = fm.FontProperties(fname=font_path)

    # plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置字体为黑体
    # plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

    # ax[0].set_title('K line and buy and sell sigla chart', fontsize=20, fontproperties=prop)
    ax[0].set_title('K line and buy and sell sigla chart', fontsize=20)


    # 调整 x 轴上的日期显示
    ax[0].xaxis.set_major_locator(plt.MaxNLocator(10))  # 显示更多的日期

    # 保存高分辨率图片
    fig.savefig('debug/kline_with_sma_signals_high_res.png', dpi=300)

    # 关闭绘图以释放内存
    plt.close()
    
if __name__ == '__main__':
    bn_df = get_bndata_via_API()
    # print(bn_df)
    bn_strategy = process_strategy(bn_df)

    process_pic(bn_strategy)
    print('Hello word')