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
from newspaper import Article  # 引入 newspaper3k 库

# 1. 设置 Chrome 配置，启用无头模式
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 2. 启动 Chrome 浏览器
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 3. 定义要抓取的新闻网站及其解析逻辑
sources = [
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/category/artificial-intelligence/",
        "article_selector": "h3",
        "summary_selector": "p",
        "date_selector": "time",
        "link_selector": "a",
        "base_url": "https://techcrunch.com",
    },
    {
        "name": "MIT Tech Review",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/",
        "article_selector": ".story-item__title",
        "summary_selector": ".story-item__dek",
        "date_selector": ".story-item__timestamp",
        "link_selector": "a",
        "base_url": "https://www.technologyreview.com",
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/",
        "article_selector": ".ArticleListing__title",
        "summary_selector": ".ArticleListing__excerpt",
        "date_selector": ".ArticleListing__timestamp",
        "link_selector": "a",
        "base_url": "https://venturebeat.com",
    },
]

latest_news = []

# 4. 爬取多个网站
def scrape_website(source):
    driver.get(source["url"])
    time.sleep(5)  # 等待页面加载
    soup = BeautifulSoup(driver.page_source, "html.parser")

    articles = soup.select(source["article_selector"])

    if not articles:
        print(f"❌ {source['name']} 未找到新闻")
        return

    for article in articles[:10]:  # 每个站点最多抓取 10 条
        link_tag = article.select_one(source["link_selector"])
        summary_tag = article.select_one(source["summary_selector"])
        date_tag = article.select_one(source["date_selector"])

        if link_tag and "href" in link_tag.attrs:
            full_url = urljoin(source["base_url"], link_tag["href"])
            title = article.text.strip()
            summary = summary_tag.text.strip() if summary_tag else (title[:50] + "...")
            date = date_tag.text.strip() if date_tag else datetime.today().strftime("%Y-%m-%d")

            # 使用 newspaper3k 提取文章内容
