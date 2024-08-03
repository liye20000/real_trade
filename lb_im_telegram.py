import requests

TELEGRAM_TOKEN = '7084027203:AAGiH_B1nknbN5oxrZJcI4Rq4_TBklXhBuA'
CHAT_ID = '6726085444'

from datetime import datetime

class TelegramNotifier:
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.chat_id = CHAT_ID

    def send_message(self, message, parse_mode=None):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()  # 检查HTTP请求是否成功
            result = response.json()
            if not result.get("ok"):
                raise ValueError(f"Error from Telegram API: {result}")
            return result
        except requests.RequestException as e:
            print(f"HTTP error occurred: {e}")
        except ValueError as e:
            print(f"Error response from Telegram API: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        return None

    # https://core.telegram.org/bots/api#markdownv2-style
    def send_markdown_message(self, text):
        markdown_message = self.escape_markdown(text)
        return self.send_message(markdown_message, parse_mode="MarkdownV2")

    def escape_markdown(self, text):
        # Telegram MarkdownV2 requires the following characters to be escaped
        escape_chars = r'_*\[\]()~`>#+-=|{}.!'
        return ''.join(['\\' + char if char in escape_chars else char for char in text])
    
    # https://core.telegram.org/bots/api#html-style
    def send_html_message(self, text):
        html_message = f"<b>{text}</b>"
        return self.send_message(html_message, parse_mode="HTML")

    def send_trade_info(self, symbol, side, position_side, trade_volume, trade_price, execution_time, **kwargs):
        markdown_message = f"交易信息\n" \
                           f"交易对: {symbol}\n" \
                           f"买卖方向: {side}\n" \
                           f"持仓方向: {position_side}\n" \
                           f"持仓量: {trade_volume}\n" \
                           f"持仓价格: {trade_price}\n" \
                           f"执行时间: {execution_time}\n"
        
        # 添加额外的参数
        for key, value in kwargs.items():
            key_formatted = key.replace('_', ' ').capitalize()
            markdown_message += f"{key_formatted}: {value}\n"
        
        # return self.send_markdown_message(markdown_message)
        return self.send_html_message(markdown_message)

if __name__ == "__main__":
    # 示例TOKEN和CHAT_ID，实际使用时替换为真实的TOKEN和CHAT_ID
    
    notifier = TelegramNotifier()

    # 发送Markdown消息测试
    # markdown_reply = notifier.send_markdown_message("Hello world, It's a test with Markdown")
    # print(markdown_reply)

    # 发送HTML消息测试
    # html_reply = notifier.send_html_message("Hello world, It's a test with HTML")
    # print(html_reply)

    # 发送交易信息测试
    symbol = "BTCUSDT"
    side = "BUY"
    position_side = "LONG"
    trade_volume = 0.1
    trade_price = 30000
    execution_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 发送带有额外信息的交易信息
    trade_info_reply = notifier.send_trade_info(symbol, side, position_side, trade_volume, trade_price, execution_time, leverage=10, order_id=123456)
    print(trade_info_reply)
