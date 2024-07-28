# 测试数据库代码
# 构建交易记录表
# 完成表创建
# 完成表写入 新的买入数据
# 完成表更新 更新卖出数据
# 完成表擦出 擦出指定数据， 擦出所有数据
# 完成表数据打印
import sqlite3
import pandas as pd
import os

class TradeDatabase:
    def __init__(self, db_name='data/trading.db'):
        self.db_name = db_name
        self.create_trade_table()

    def create_trade_table(self):
        if not os.path.exists(os.path.dirname(self.db_name)):
            os.makedirs(os.path.dirname(self.db_name))
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            side TEXT,
            position_side TEXT,
            trade_volume REAL,
            trade_price REAL,
            order_id TEXT,
            execution_time TEXT
        )
        ''')
        conn.commit()
        conn.close()

    def insert_trade(self, symbol, side, position_side, trade_volume, trade_price, order_id, execution_time):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO trades (symbol, side, position_side, trade_volume, trade_price, order_id, execution_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, side, position_side, trade_volume, trade_price, order_id, execution_time))
        conn.commit()
        conn.close()

    def update_trade(self, trade_id, **kwargs):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        set_clause = ', '.join([f"{key} = ?" for key in kwargs])
        values = list(kwargs.values())
        values.append(trade_id)

        cursor.execute(f'''
        UPDATE trades
        SET {set_clause}
        WHERE trade_id = ?
        ''', values)
        conn.commit()
        conn.close()

    def delete_trade(self, trade_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
        DELETE FROM trades
        WHERE trade_id = ?
        ''', (trade_id,))
        conn.commit()
        conn.close()

    def delete_all_trades(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
        DELETE FROM trades
        ''')
        conn.commit()
        conn.close()

    def fetch_trades(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM trades
        ''')
        trades = cursor.fetchall()
        conn.close()
        return trades

    def fetch_trade_by_order_id(self, order_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM trades
        WHERE order_id = ?
        ''', (order_id,))
        trade = cursor.fetchone()
        conn.close()
        return trade

    def fetch_trades_as_dataframe(self):
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql('SELECT * FROM trades', conn)
        conn.close()
        return df

    def print_trades(self):
        trades = self.fetch_trades()
        for trade in trades:
            print(trade)

    def print_trades_as_dataframe(self):
        df = self.fetch_trades_as_dataframe()
        print(df)

    def add_column_to_table(self, table_name, column_name, column_type):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f'''
        ALTER TABLE {table_name}
        ADD COLUMN {column_name} {column_type}
        ''')
        conn.commit()
        conn.close()

    def drop_column_from_table(self, table_name, column_name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(f'PRAGMA table_info({table_name})')
        columns = [col[1] for col in cursor.fetchall() if col[1] != column_name]

        cursor.execute(f'''
        CREATE TABLE {table_name}_new AS SELECT {', '.join(columns)} FROM {table_name}
        ''')

        cursor.execute(f'DROP TABLE {table_name}')

        cursor.execute(f'ALTER TABLE {table_name}_new RENAME TO {table_name}')

        conn.commit()
        conn.close()

if __name__ == '__main__':
    db = TradeDatabase(db_name='data/trading.db')

    # 插入一条新的交易记录
    db.insert_trade(symbol='BTCUSDT', side='BUY', position_side='LONG', trade_volume=1.2, trade_price=30000.5, order_id='123456', execution_time='2024-07-27 12:00:00')

    # 更新交易记录
    db.update_trade(trade_id=1, trade_price=30500.5, trade_volume=1.5)

    # 通过订单ID查询交易记录
    trade = db.fetch_trade_by_order_id(order_id='123456')
    print(trade)

    # 打印所有交易记录
    db.print_trades()

    # 打印交易记录为 DataFrame
    db.print_trades_as_dataframe()

    # 增加一个新的列
    db.add_column_to_table(table_name='trades', column_name='trade_notes', column_type='TEXT')

    # 删除一个列
    db.drop_column_from_table(table_name='trades', column_name='trade_notes')

    # 删除一条交易记录
    db.delete_trade(trade_id=1)

    # 删除所有交易记录
    db.delete_all_trades()
