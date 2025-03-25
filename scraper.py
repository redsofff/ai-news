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

# 4. 使用 newspaper3k 提取文章内容和摘要
def extract_summary(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text[:200]  # 取文章前200个字符作为摘要

# 5. 爬取多个网站
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

            # 使用 newspaper3k 提取文章摘要
            summary = extract_summary(full_url)

            # 如果没有摘要字段，默认使用标题的前200个字符作为摘要
            if not summary:
                summary = title[:200] + "..." if len(title) > 200 else title

            date = date_tag.text.strip() if date_tag else datetime.today().strftime("%Y-%m-%d")

            latest_news.append({
                "title": title,
                "summary": summary,
                "source": source["name"],
                "date": date,
                "url": full_url
            })
            print(f"✔ {source['name']} - {title} - {full_url}")

# 遍历所有新闻网站
for source in sources:
    scrape_website(source)

# 6. 只保留最新 20 条新闻
latest_news = sorted(latest_news, key=lambda x: x["date"], reverse=True)[:20]

# 7. 保存到 JSON
def save_news_to_json(news):
    with open("news.json", "w", encoding="utf-8") as file:
        json.dump(news, file, indent=4, ensure_ascii=False)
    print("✅ 新闻数据已保存到 news.json")

save_news_to_json(latest_news)

# 8. Git 提交更新
def update_git_repo():
    os.system("git add news.json")
    os.system('git commit -m "更新新闻数据"')
    os.system("git push origin main")
    print("🚀 GitHub 已更新")

update_git_repo()

# 9. 关闭浏览器
driver.quit()
