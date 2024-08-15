import sqlite3
import pandas as pd
import os
from lb_logger import log

class StrategyDatabase:
    def __init__(self, db_name='data/ma_strategy.db'):
        self.db_name = db_name
        self.logger = log
        self._create_strategy_table()
    

    def _create_strategy_table(self):
        if not os.path.exists(os.path.dirname(self.db_name)):
            os.makedirs(os.path.dirname(self.db_name))
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_data (
                timestamp TEXT PRIMARY KEY,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                sma_fast REAL,
                sma_slow REAL,
                volume_ma REAL,
                signal TEXT,
                buy REAL,
                sell REAL,
                processed INTEGER DEFAULT 0
            )
            ''')
            conn.commit()
            conn.close()
            self.logger.info("Table 'strategy_data' created successfully.")
        except Exception as e:
            self.logger.error(f"Error creating table: {e}")

    def insert_or_update_data(self, df):
        try:
            # Ensure all required columns are present in the DataFrame
            required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                'sma_fast', 'sma_slow', 'volume_ma', 'signal', 'buy', 'sell','processed']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None

            # Convert timestamp column to string
            df['timestamp'] = df['timestamp'].astype(str)
            # df['processed'] = df['processed'].astype(int)  # 将processed列转换为整数类型
        
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            for index, row in df.iterrows():
                cursor.execute('''
                INSERT INTO strategy_data (timestamp, open, high, low, close, volume, sma_fast, sma_slow, volume_ma, signal, buy, sell, processed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(timestamp) DO UPDATE SET
                    open=excluded.open,
                    high=excluded.high,
                    low=excluded.low,
                    close=excluded.close,
                    volume=excluded.volume,
                    sma_fast=excluded.sma_fast,
                    sma_slow=excluded.sma_slow,
                    volume_ma=excluded.volume_ma,
                    signal=excluded.signal,
                    buy=excluded.buy,
                    sell=excluded.sell,
                    processed=COALESCE(strategy_data.processed, excluded.processed) 
                ''', (row['timestamp'], row['open'], row['high'], row['low'], row['close'], row['volume'], row['sma_fast'], row['sma_slow'], row['volume_ma'], row['signal'], row['buy'], row['sell'], row['processed']))
            conn.commit()
            conn.close()
            self.logger.info("Data inserted/updated successfully.")
        except Exception as e:
            self.logger.error(f"Error inserting/updating data: {e}")

    def query_data(self, limit=None, start_time=None, end_time=None, offset = 0):
        try:
            conn = sqlite3.connect(self.db_name)
            query = "SELECT * FROM strategy_data"
            conditions = []
            if start_time:
                conditions.append(f"timestamp >= '{start_time}'")
            if end_time:
                conditions.append(f"timestamp <= '{end_time}'")
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY timestamp"
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            return pd.DataFrame()
    def delete_data(self, start_time=None, end_time=None, limit=None):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            if start_time or end_time:
                query = "DELETE FROM strategy_data WHERE "
                conditions = []
                if start_time:
                    conditions.append(f"timestamp >= '{start_time}'")
                if end_time:
                    conditions.append(f"timestamp <= '{end_time}'")
                query += " AND ".join(conditions)
            elif limit:
                query = f"DELETE FROM strategy_data WHERE timestamp IN (SELECT timestamp FROM strategy_data ORDER BY timestamp LIMIT {limit})"
            else:
                query = "DELETE FROM strategy_data"
            cursor.execute(query)
            conn.commit()
            conn.close()
            self.logger.info("Data deleted successfully.")
        except Exception as e:
            self.logger.error(f"Error deleting data: {e}")

def db_process_test_func():
    db_strategy = StrategyDatabase(db_name='test/ma_strategy.db')

    def print_db(number = None):
        data = db_strategy.query_data(limit=number)
        print(data)
    
    # 测试数据
    initial_data = {
        'timestamp': ['2024-07-27 12:00:00', '2024-07-27 12:05:00', '2024-07-27 12:10:00'],
        'open': [100, 110, 120],
        'high': [105, 115, 125],
        'low': [95, 105, 115],
        'close': [104, 114, 124],
        'volume': [1000, 1500, 2000]
    }

    strategy_data = {
        'timestamp': ['2024-07-27 12:00:00', '2024-07-27 12:05:00', '2024-07-27 12:10:00'],
        'open': [100, 110, 120],
        'high': [105, 115, 125],
        'low': [95, 105, 115],
        'close': [104, 114, 124],
        'volume': [1000, 1500, 2000],
        'sma_fast': [102, 112, 122],
        'sma_slow': [101, 111, 121],
        'volume_ma': [1200, 1300, 1400],
        'signal': ['buy', 'sell', 'hold'],
        'buy': [104, None, None],
        'sell': [None, 114, None]
    }

    processed_strategy_data = {
        'timestamp': ['2024-07-27 12:00:00', '2024-07-27 12:05:00', '2024-07-27 12:10:00'],
        'open': [100, 110, 120],
        'high': [105, 115, 125],
        'low': [95, 105, 115],
        'close': [104, 114, 124],
        'volume': [1000, 1500, 2000],
        'sma_fast': [102, 112, 122],
        'sma_slow': [101, 111, 121],
        'volume_ma': [1200, 1300, 1400],
        'signal': ['buy', 'sell', 'hold'],
        'buy': [104, None, None],
        'sell': [None, 114, None],
        'processed':[False,False,True]
    }


    initial_df = pd.DataFrame(initial_data)
    strategy_df = pd.DataFrame(strategy_data)
    processed_strategy_df = pd.DataFrame(processed_strategy_data)

    # 插入基础数据
    db_strategy.insert_or_update_data(initial_df)
    print_db()

    # 插入策略数据
    db_strategy.insert_or_update_data(strategy_df)
    print_db()
    
    # 插入处理过的策略数据
    db_strategy.insert_or_update_data(processed_strategy_df)
    print_db()

    # 插入基础数据
    db_strategy.insert_or_update_data(strategy_df)
    print_db()
 
    # # 读取部分数据（2条）
    # data = db_strategy.query_data(limit=2)
    # print(data)

    # # 根据时间读取数据（某时间点后的数据）
    # data = db_strategy.query_data(start_time='2024-07-27 12:05:00')
    # print(data)

    # # 擦除数据（某时间点前的数据）
    # db_strategy.delete_data(end_time='2024-07-27 12:05:00')
    # print_db()

    # # 擦除数据（最早的1条数据）
    # db_strategy.delete_data(limit=1)
    # # 打印所有数据
    # print_db()
    
    # db_strategy.insert_or_update_data(strategy_df)
    # print_db()
    # db_strategy.delete_data()
    # print_db()
# 全局变量

def fetch_caculate_and_store_test():
    # 测试代码
    from live_data_fetch import LiveDataFetcher
    from rt_ma_strategy import CoreDMAStrategy
    test_para = {
        'fetcher_cfg': 'configure/data_cfg.json',
        'strager_cfg': 'configure/stra_dma_cfg.json',
        'strager_db':  'test/ma_strategy.db'
    }
    bn_future_fetch = LiveDataFetcher(test_para['fetcher_cfg'])
    strategy = CoreDMAStrategy(test_para['strager_cfg'])
    db_strategy = StrategyDatabase(test_para['strager_db'])
    
    
    df = bn_future_fetch.fetch_data()
    db_strategy.insert_or_update_data(df)

    df = db_strategy.query_data()
    df = strategy.generate_signals(df)
    db_strategy.insert_or_update_data(df)

    df =db_strategy.query_data()

    # 为了让df被打印不截断:
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    print(df)
if __name__ == '__main__':
#    fetch_caculate_and_store_test()
    db_process_test_func()