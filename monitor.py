import requests
import json
import os
from xml.etree import ElementTree

# ==========配置信息，你的账号algo1145==========
USERNAME = "algo1145"
DING_WEBHOOK = os.getenv("DING_WEBHOOK")
RECORD_FILE = "last_id.json"
# RSSHub公开实例，获取X账号RSS
RSS_URL = f"https://rsshub.app/twitter/user/{USERNAME}"

def get_newest_tweet():
    try:
        print(f"正在请求RSS地址: {RSS_URL}")
        resp = requests.get(RSS_URL, timeout=20)
        print(f"http状态码: {resp.status_code}")
        if resp.status_code != 200:
            print("RSS请求失败")
            return None, None, None
        #解析xml
        root = ElementTree.fromstring(resp.content)
        #xml命名空间
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items = root.findall(".//atom:entry", ns)
        if len(items) ==0:
            print("没有抓到推文条目")
            return None, None, None
        latest_item = items[0]
        tweet_id = latest_item.find("./atom:id", ns).text
        tweet_text = latest_item.find("./atom:title", ns).text
        tweet_link = latest_item.find("./atom:link", ns).attrib["href"]
        return tweet_id, tweet_text, tweet_link
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
