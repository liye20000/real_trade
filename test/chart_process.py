import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 示例数据
data = {
    'timestamp': ['2024-06-21', '2024-06-22', '2024-06-23', '2024-06-24', '2024-06-25', '2024-06-26', '2024-06-27', '2024-06-28', '2024-06-29', '2024-06-30'],
    'open': [65000.00, 64500.00, 64000.00, 63500.00, 63000.00, 62500.00, 62000.00, 61500.00, 61000.00, 60500.00],
    'high': [65100.00, 64600.00, 64100.00, 63600.00, 63100.00, 62600.00, 62100.00, 61600.00, 61100.00, 60600.00],
    'low': [64900.00, 64400.00, 63900.00, 63400.00, 62900.00, 62400.00, 61900.00, 61400.00, 60900.00, 60400.00],
    'close': [64854.00, 64124.10, 64240.10, 63194.90, 60273.50, 61000.00, 62000.00, 63000.00, 64000.00, 65000.00],
    'volume': [210109.601, 53855.862, 72052.293, 445903.184, 264647.317, 180123.123, 192834.456, 210123.789, 221234.567, 230987.654]
}

# 创建 Pandas DataFrame
df = pd.DataFrame(data)

# 将 'timestamp' 列转换为 datetime 类型并设置为索引
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

# 计算短期和长期简单均线
short_window = 3
long_window = 6

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
fig.savefig('kline_with_sma_signals_high_res.png', dpi=300)

# 关闭绘图以释放内存
plt.close()
