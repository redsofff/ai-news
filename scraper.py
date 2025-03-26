from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
import os
from urllib.parse import urljoin
from datetime import datetime
from newspaper import Article

# 设置 Chrome 配置，启用无头模式
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--remote-debugging-port=9222")

# 启动 Chrome 浏览器
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 定义要抓取的新闻网站及其解析逻辑
sources = [
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/category/artificial-intelligence/",
        "article_selector": "h3.loop-card__title a",
        "summary_selector": "",
        "date_selector": "time",
        "link_selector": "h3.loop-card__title a",
        "base_url": "https://techcrunch.com",
    },
    {
        "name": "MIT Tech Review",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/",
        "article_selector": "a[data-event-label='topic-story'] h3",
        "summary_selector": "div.homepageStoryCard__dek--7c9e3c85841df43b5fb2385cdf2b46e3 p",
        "date_selector": "div[data-immersive-translate-walked] time",
        "link_selector": "a[data-event-label='topic-story']",
        "base_url": "https://www.technologyreview.com",
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/",
        "article_selector": ".ArticleListing__title a",
        "summary_selector": ".ArticleListing__excerpt",
        "date_selector": ".ArticleListing__timestamp",
        "link_selector": ".ArticleListing__title a",
        "base_url": "https://venturebeat.com",
    },
]

latest_news = []

def scrape_website(source):
    driver.get(source["url"])
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    articles = soup.select(source["article_selector"])

    if not articles:
        print(f"❌ {source['name']} 未找到新闻")
        return

    for article in articles[:10]:
        link_tag = article.find_parent("a") if article.name == "h3" else article
        if link_tag:
            summary_tag = link_tag.find_next(source["summary_selector"]) if source["summary_selector"] else None
            date_tag = link_tag.find_next(source["date_selector"]) if source["date_selector"] else None

            if "href" in link_tag.attrs:
                full_url = urljoin(source["base_url"], link_tag["href"])
                title = article.get_text(strip=True)

                summary = ""
                if summary_tag:
                    summary = summary_tag.get_text(strip=True)
                else:
                    try:
                        article_obj = Article(full_url)
                        article_obj.download()
                        article_obj.parse()
                        summary = article_obj.text[:200]
                    except Exception as e:
                        print(f"Error processing article {full_url}: {e}")
                        summary = title[:200]

                date = ""
                if date_tag:
                    date = date_tag["datetime"] if date_tag.has_attr("datetime") else date_tag.get_text(strip=True)
                if not date:
                    date = datetime.today().strftime("%Y-%m-%d")

                news_item = {
                    "title": title,
                    "summary": summary,
                    "url": full_url,
                    "date": date,
                    "source": source["name"],
                }
                latest_news.append(news_item)

for source in sources:
    scrape_website(source)

driver.quit()

output_file = "/Users/apple/ai-news/news.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(latest_news, f, ensure_ascii=False, indent=4)

print("✅ 新闻数据已保存到 news.json")
