import sqlite3
import pandas as pd
import os
from lb_logger import log

class StrategyDatabase:
    def __init__(self, db_name='data/ma_strategy.db'):
        self.db_name = db_name
        self.create_strategy_table()

    def create_strategy_table(self):
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
                sell REAL
            )
            ''')
            conn.commit()
            conn.close()
            log.info("Table 'strategy_data' created successfully.")
        except Exception as e:
            log.error(f"Error creating table: {e}")

    def insert_or_update_data(self, df):
        try:
            # Ensure all required columns are present in the DataFrame
            required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                'sma_fast', 'sma_slow', 'volume_ma', 'signal', 'buy', 'sell']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None

            # Convert timestamp column to string
            df['timestamp'] = df['timestamp'].astype(str)
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            for index, row in df.iterrows():
                cursor.execute('''
                INSERT INTO strategy_data (timestamp, open, high, low, close, volume, sma_fast, sma_slow, volume_ma, signal, buy, sell)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    sell=excluded.sell
                ''', (row['timestamp'], row['open'], row['high'], row['low'], row['close'], row['volume'], row['sma_fast'], row['sma_slow'], row['volume_ma'], row['signal'], row['buy'], row['sell']))
            conn.commit()
            conn.close()
            log.info("Data inserted/updated successfully.")
        except Exception as e:
            log.error(f"Error inserting/updating data: {e}")

    def fetch_data(self, limit=None, start_time=None, end_time=None):
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
                query += f" LIMIT {limit}"
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            log.error(f"Error fetching data: {e}")
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
            log.info("Data deleted successfully.")
        except Exception as e:
            log.error(f"Error deleting data: {e}")

    def print_data(self):
        df = self.fetch_data()
        print(df)

# 全局变量
db_strategy = StrategyDatabase(db_name='data/ma_strategy.db')

if __name__ == '__main__':
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

    initial_df = pd.DataFrame(initial_data)
    strategy_df = pd.DataFrame(strategy_data)

    # 插入基础数据
    db_strategy.insert_or_update_data(initial_df)
    db_strategy.print_data()

    # 插入策略数据
    db_strategy.insert_or_update_data(strategy_df)
    db_strategy.print_data()

    # 读取数据
    data = db_strategy.fetch_data()
    print(data)

    # 读取部分数据（最新2条）
    data = db_strategy.fetch_data(limit=2)
    print(data)

    # 根据时间读取数据（某时间点后的数据）
    data = db_strategy.fetch_data(start_time='2024-07-27 12:05:00')
    print(data)

    # 擦除数据（某时间点前的数据）
    db_strategy.delete_data(end_time='2024-07-27 12:05:00')

    # 擦除数据（最早的1条数据）
    db_strategy.delete_data(limit=1)

    # 打印所有数据
    db_strategy.print_data()

    db_strategy.delete_data()
    db_strategy.print_data()