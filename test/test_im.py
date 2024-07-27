import requests

TELEGRAM_TOKEN = '7084027203:AAGiH_B1nknbN5oxrZJcI4Rq4_TBklXhBuA'
CHAT_ID = '6726085444'


def send_telegram_message(message, parse_mode=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
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

def send_markdown_message(text):
    markdown_message = f"**{text}**"
    # https://core.telegram.org/bots/api#markdownv2-style
    return send_telegram_message(markdown_message, parse_mode="MarkdownV2")

def send_html_message(text):
    html_message = f"""
    <b>{text}</b>
    """
    # https://core.telegram.org/bots/api#html-style
    
    return send_telegram_message(html_message, parse_mode="HTML")

if __name__ == "__main__":
    markdown_reply = send_markdown_message("Hello word, It's a test with Markdown")
    print(markdown_reply)

    html_reply = send_html_message("Hello word, It's a test with HTML")
    print(html_reply)

