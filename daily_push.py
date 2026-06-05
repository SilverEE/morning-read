#!/usr/bin/env python3
"""
晨间轻读 - 每日推送脚本
功能：获取天气+热点+名言+歌曲，通过Server酱推送到微信（支持多个接收人）
"""

import json
import random
import re
import os
import sys
from datetime import datetime

try:
    import requests
except ImportError:
    print("缺少 requests 库，请运行: pip install requests")
    sys.exit(1)

try:
    import feedparser
except ImportError:
    print("缺少 feedparser 库，请运行: pip install feedparser")
    sys.exit(1)


# ============ 配置读取 ============

def load_config():
    """读取配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        return {
            "enabled": True,
            "location": "福州",
            "push_time": "07:00",
            "receivers": []
        }


def get_receivers(config):
    """获取所有接收人列表，优先从环境变量读取（逗号分隔）"""
    env_keys = os.environ.get("SCT_KEYS", "").strip()
    if env_keys:
        # 环境变量格式: key1:name1,key2:name2 或 key1,key2
        receivers = []
        for item in env_keys.split(","):
            item = item.strip()
            if ":" in item:
                key, name = item.split(":", 1)
                receivers.append({"sct_key": key.strip(), "name": name.strip()})
            else:
                receivers.append({"sct_key": item, "name": "接收人"})
        return receivers

    # 从配置文件读取
    return config.get("receivers", [])


# ============ 天气获取 ============

WEATHER_CODE_MAP = {
    0: "晴", 1: "大部晴", 2: "多云", 3: "阴天",
    45: "雾", 48: "雾凇",
    51: "小毛毛雨", 53: "毛毛雨", 55: "大毛毛雨",
    56: "冻毛毛雨", 57: "大冻毛毛雨",
    61: "小雨", 63: "中雨", 65: "大雨",
    66: "冻雨", 67: "大冻雨",
    71: "小雪", 73: "中雪", 75: "大雪",
    77: "雪粒",
    80: "小阵雨", 81: "中阵雨", 82: "大阵雨",
    85: "小阵雪", 86: "大阵雪",
    95: "雷暴", 96: "雷暴伴冰雹", 99: "强雷暴伴冰雹"
}

WEATHER_ICON_MAP = {
    0: "☀️", 1: "🌤", 2: "⛅", 3: "☁️",
    45: "🌫", 48: "🌫",
    51: "🌦", 53: "🌦", 55: "🌧",
    56: "🌧", 57: "🌧",
    61: "🌧", 63: "🌧", 65: "🌧",
    66: "🌧", 67: "🌧",
    71: "🌨", 73: "🌨", 75: "❄️",
    77: "🌨",
    80: "🌦", 81: "🌧", 82: "⛈",
    85: "🌨", 86: "❄️",
    95: "⛈", 96: "⛈", 99: "⛈"
}


def get_location_coords(location):
    """通过地名获取经纬度"""
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": location, "count": 1, "language": "zh"}
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("results"):
            r = data["results"][0]
            return r["latitude"], r["longitude"], r.get("name", location)
    except Exception as e:
        print(f"地理编码失败: {e}")
    return None, None, location


def get_weather(location):
    """获取天气数据"""
    lat, lon, city_name = get_location_coords(location)
    if lat is None or lon is None:
        return None, city_name

    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode",
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code",
            "timezone": "Asia/Shanghai"
        }
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        weather_code = current.get("weather_code", 0)
        weather_desc = WEATHER_CODE_MAP.get(weather_code, "未知")
        weather_icon = WEATHER_ICON_MAP.get(weather_code, "🌤")

        result = {
            "icon": weather_icon,
            "desc": weather_desc,
            "city": city_name,
            "current_temp": current.get("temperature_2m", "--"),
            "apparent_temp": current.get("apparent_temperature", "--"),
            "humidity": current.get("relative_humidity_2m", "--"),
            "temp_min": daily.get("temperature_2m_min", ["--"])[0],
            "temp_max": daily.get("temperature_2m_max", ["--"])[0],
            "precip_prob": daily.get("precipitation_probability_max", ["--"])[0],
        }
        return result, city_name
    except Exception as e:
        print(f"天气获取失败: {e}")
        return None, city_name


def format_weather_markdown(weather, city_name):
    """格式化天气为 Markdown"""
    if weather is None:
        return f"🌤 天气 · {city_name}\n天气数据暂不可用"

    return (
        f"{weather['icon']} 天气 · {weather['city']}\n"
        f"{weather['desc']} | 当前 {weather['current_temp']}°C | 体感 {weather['apparent_temp']}°C\n"
        f"🌡 {weather['temp_min']}°C ~ {weather['temp_max']}°C | "
        f"💧 湿度 {weather['humidity']}% | "
        f"🌧 降雨概率 {weather['precip_prob']}%"
    )


# ============ 新闻获取 ============

RSS_FEEDS = [
    {"name": "36氪", "url": "https://36kr.com/feed"},
    {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss"},
    {"name": "Hacker News", "url": "https://hnrss.org/frontpage"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
]


def clean_html(text):
    """清理 HTML 标签"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def truncate(text, max_len=200):
    """截取文本"""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def is_foreign_text(text):
    """检测文本是否主要是外语（英文等）"""
    if not text:
        return False
    # 统计英文字符占比
    english_chars = sum(1 for c in text if c.isascii() and c.isalpha())
    total_chars = sum(1 for c in text if c.isalpha())
    if total_chars == 0:
        return False
    return english_chars / total_chars > 0.6


def translate_text(text, source_lang="en", target_lang="zh"):
    """翻译文本（使用 MyMemory 免费翻译 API）"""
    if not text or not is_foreign_text(text):
        return None
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": text[:500],  # API 限制单次 500 字符
            "langpair": f"{source_lang}|{target_lang}"
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("responseStatus") == 200:
            translated = data.get("responseData", {}).get("translatedText", "")
            # 翻译质量检查：如果返回的和原文一样说明没翻译成功
            if translated and translated.lower() != text.lower():
                return translated
        return None
    except Exception as e:
        print(f"翻译失败: {e}")
        return None


def fetch_news():
    """获取新闻"""
    news_list = []
    for feed_info in RSS_FEEDS:
        try:
            resp = requests.get(feed_info["url"], timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (compatible; MorningRead/1.0)"
            })
            feed = feedparser.parse(resp.content)
            count = 0
            for entry in feed.entries:
                if count >= 3:
                    break
                title = entry.get("title", "")
                summary = clean_html(entry.get("summary", entry.get("description", "")))
                if not title:
                    continue
                is_foreign = is_foreign_text(title)
                item = {
                    "source": feed_info["name"],
                    "title": title,
                    "summary": truncate(summary),
                    "link": entry.get("link", ""),
                    "is_foreign": is_foreign
                }
                # 外语新闻自动翻译标题
                if is_foreign:
                    title_zh = translate_text(title)
                    if title_zh:
                        item["title_zh"] = title_zh
                    # 摘要也翻译
                    if summary:
                        summary_zh = translate_text(summary[:300])
                        if summary_zh:
                            item["summary_zh"] = summary_zh
                news_list.append(item)
                count += 1
        except Exception as e:
            print(f"获取 {feed_info['name']} 失败: {e}")
            continue

    # 取前8条
    return news_list[:8]


def format_news_markdown(news_list):
    """格式化新闻为 Markdown（标题可点击，外语有翻译）"""
    if not news_list:
        return "📰 今日热点\n暂无新闻数据"

    lines = ["📰 今日热点\n"]
    for i, item in enumerate(news_list, 1):
        # 标题做成可点击链接
        title = item['title']
        if item['is_foreign'] and item.get('title_zh'):
            # 外语新闻：显示中文翻译，原标题保留
            title_display = f"{item['title_zh']}"
            lines.append(f"{i}. [{item['source']}] [{title_display}]({item['link']})")
            lines.append(f"   🌐 原文：{title}")
        else:
            lines.append(f"{i}. [{item['source']}] [{title}]({item['link']})")
        # 摘要
        if item['is_foreign'] and item.get('summary_zh'):
            lines.append(f"   > {item['summary_zh']}")
        elif item.get('summary'):
            lines.append(f"   > {item['summary']}")
    return "\n".join(lines)


# ============ 名言获取 ============

def get_random_quote():
    """随机获取一条名言"""
    try:
        quotes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quotes.json")
        with open(quotes_path, "r", encoding="utf-8") as f:
            quotes = json.load(f)
        return random.choice(quotes)
    except Exception as e:
        print(f"读取名言失败: {e}")
        return {"text": "新的一天，新的开始。", "author": "晨间轻读"}


def format_quote_markdown(quote):
    """格式化名言为 Markdown"""
    return f"💡 每日一言\n\n> {quote['text']}\n> —— {quote['author']}"


# ============ 歌曲获取 ============

def get_random_song():
    """随机获取一首歌"""
    try:
        songs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "songs.json")
        with open(songs_path, "r", encoding="utf-8") as f:
            songs = json.load(f)
        return random.choice(songs)
    except Exception as e:
        print(f"读取歌曲失败: {e}")
        return {"name": "清晨", "artist": "未知"}


def generate_music_link(song):
    """生成音乐搜索链接（网易云音乐）"""
    from urllib.parse import quote
    keyword = f"{song['name']} {song['artist']}"
    return f"https://music.163.com/#/search/m/?s={quote(keyword)}"


def format_song_markdown(song):
    """格式化歌曲为 Markdown（标题可点击跳转网易云）"""
    music_link = generate_music_link(song)
    return (
        f"🎵 今日推荐\n\n"
        f"[《{song['name']}》 - {song['artist']}]({music_link})\n\n"
        f"👆 点击即可搜索播放"
    )


# ============ 推送 ============

def send_push(sct_key, title, content):
    """通过 Server酱 发送推送"""
    try:
        url = f"https://sctapi.ftqq.com/{sct_key}.send"
        data = {"title": title, "desp": content}
        resp = requests.post(url, data=data, timeout=15)
        result = resp.json()
        if result.get("code") == 0:
            print("推送成功！")
            return True
        else:
            print(f"推送失败: {result}")
            return False
    except Exception as e:
        print(f"推送请求失败: {e}")
        return False


# ============ 主流程 ============

def main():
    print(f"===== 晨间轻读 推送开始 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====")

    # 1. 读取配置
    config = load_config()

    # 2. 检查是否启用
    if not config.get("enabled", True):
        print("推送已关闭，退出。")
        return

    # 3. 获取所有接收人
    receivers = get_receivers(config)
    if not receivers:
        print("未配置任何接收人，无法推送。")
        return

    location = config.get("location", "福州")

    # 4. 获取天气
    print(f"正在获取 {location} 天气...")
    weather, city_name = get_weather(location)
    weather_md = format_weather_markdown(weather, city_name)

    # 5. 获取新闻
    print("正在获取新闻...")
    news_list = fetch_news()
    news_md = format_news_markdown(news_list)

    # 6. 获取名言
    quote = get_random_quote()
    quote_md = format_quote_markdown(quote)

    # 7. 获取歌曲
    song = get_random_song()
    song_md = format_song_markdown(song)

    # 8. 组装推送内容
    today = datetime.now().strftime('%Y年%m月%d日')
    # 标题带上天气概况，聊天列表扫一眼就能看到
    if weather:
        title = f"{weather['icon']} 晨间轻读 | {weather['city']} {weather['current_temp']}°C {weather['desc']} | {today}"
    else:
        title = f"晨间轻读 | {today}"
    content = f"{weather_md}\n\n---\n\n{news_md}\n\n---\n\n{quote_md}\n\n---\n\n{song_md}"

    print("推送内容组装完成，正在发送...")

    # 9. 逐个推送给所有接收人
    success_count = 0
    fail_count = 0
    for receiver in receivers:
        name = receiver.get("name", "未命名")
        sct_key = receiver.get("sct_key", "").strip()
        if not sct_key:
            print(f"跳过 {name}：SCT Key 为空")
            continue
        print(f"推送给 {name}...")
        if send_push(sct_key, title, content):
            success_count += 1
        else:
            fail_count += 1

    print(f"===== 推送完成：成功 {success_count} 人，失败 {fail_count} 人 =====")


if __name__ == "__main__":
    main()
