import feedparser
import requests
import json
import os

# ==========配置区 博主binancezh，更换新镜像==========
USERNAME = "binancezh"
DING_WEBHOOK = os.getenv("DING_WEBHOOK")
RECORD_FILE = "last_id.json"
# 新镜像
RSS_URL = f"https://nitter.privacydev.net/{USERNAME}/rss"
# ======================================================

def get_newest_tweet():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        return None, None, None
    latest = feed.entries[0]
    tweet_id = latest.id
    tweet_text = latest.summary
    link = latest.link
    return tweet_id, tweet_text, link

def send_ding(tweet_content, tweet_link):
    msg = {
        "msgtype": "markdown",
        "markdown": {
            "title": "🔥binancezh 新推文",
            "text": f"**推文内容：**\n{tweet_content}\n\n🔗链接：{tweet_link}"
        }
    }
    res = requests.post(DING_WEBHOOK, json=msg)
    print("钉钉返回信息：", res.text)

def main():
    try:
        with open(RECORD_FILE, "r", encoding="utf-8") as f:
            last_data = json.load(f)
    except Exception:
        last_data = {"last_tweet_id": ""}

    tweet_id, tweet_content, link = get_newest_tweet()
    if tweet_id is None:
        print("RSS读取失败或暂无推文")
        return

    if tweet_id != last_data["last_tweet_id"]:
        send_ding(tweet_content, link)
        last_data["last_tweet_id"] = tweet_id
        with open(RECORD_FILE, "w", encoding="utf-8") as f:
            json.dump(last_data, f)
        print("✅检测到新推文，已经推送钉钉")
    else:
        print("暂无新推文")

if __name__ == "__main__":
    main()
