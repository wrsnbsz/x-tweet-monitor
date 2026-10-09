import requests
import json
import os

# ==========配置区==========
USERNAME = "binancezh"
DING_WEBHOOK = os.getenv("DING_WEBHOOK")
RECORD_FILE = "last_id.json"
API_URL = f"https://api.fxtwitter.com/{USERNAME}"
# ======================================================

def get_newest_tweet():
    try:
        print(f"正在请求地址: {API_URL}")
        resp = requests.get(API_URL, timeout=15)
        print(f"http状态码: {resp.status_code}")
        data = resp.json()
        print(f"接口返回原始数据：{data}")
        if data and data.get("tweets") and len(data["tweets"]) > 0:
            latest = data["tweets"][0]
            tweet_id = latest["id"]
            tweet_text = latest["text"]
            link = latest["url"]
            return tweet_id, tweet_text, link
        else:
            print("接口返回数据里没有tweets数组")
            return None, None, None
    except Exception as e:
        print(f"请求出错详细信息：{e}")
        return None, None, None


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
        print("读取失败或暂无推文")
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
