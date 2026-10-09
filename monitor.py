import requests
import json
import os

# ==========你的X账号 algo1145 ==========
USERNAME = "algo1145"
DING_WEBHOOK = os.getenv("DING_WEBHOOK")
RECORD_FILE = "last_id.json"
# 正确接口：获取用户推文列表
API_URL = f"https://api.fxtwitter.com/user/{USERNAME}/tweets"
# ======================================================

def get_newest_tweet():
    try:
        print(f"正在请求地址: {API_URL}")
        resp = requests.get(API_URL, timeout=20)
        print(f"http状态码: {resp.status_code}")
        data = resp.json()
        print(f"接口返回原始数据：{data}")
        # 推文在data数组里面
        if data and "data" in data and len(data["data"]) > 0:
            latest = data["data"][0]
            tweet_id = latest["id"]
            tweet_text = latest["text"]
            tweet_link = f"https://x.com/{USERNAME}/status/{tweet_id}"
            return tweet_id, tweet_text, tweet_link
        else:
            print("接口没有抓到推文data数组")
            return None, None, None
    except Exception as e:
        print(f"请求出错详细信息：{e}")
        return None, None, None


def send_ding(tweet_content, tweet_link):
    msg = {
        "msgtype": "markdown",
        "markdown": {
            "title": "🔥algo1145 新推文",
            "text": f"**新推文：**\n{tweet_content}\n\n🔗链接：{tweet_link}"
        }
    }
    res = requests.post(DING_WEBHOOK, json=msg)
    print("钉钉返回信息：", res.text)


def main():
    # 读取上次记录的推文id
    try:
        with open(RECORD_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
    except Exception:
        saved = {"last_tweet_id": ""}

    tweet_id, tweet_text, tweet_link = get_newest_tweet()
    if tweet_id is None:
        print("读取失败或暂无推文")
        return

    # 判断是否是新推文
    if str(tweet_id) != saved["last_tweet_id"]:
        print("✅检测到全新推文，推送钉钉")
        send_ding(tweet_text, tweet_link)
        saved["last_tweet_id"] = str(tweet_id)
        # 保存最新id
        with open(RECORD_FILE, "w", encoding="utf-8") as f:
            json.dump(saved, f)
    else:
        print("暂无新推文")


if __name__ == "__main__":
    main()
