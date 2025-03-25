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
        "link_selector": "a",
        "base_url": "https://techcrunch.com",
    },
    {
        "name": "MIT Tech Review",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/",
        "article_selector": ".story-item__title",
        "link_selector": "a",
        "base_url": "https://www.technologyreview.com",
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/",
        "article_selector": ".ArticleListing__title",
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
        if link_tag and "href" in link_tag.attrs:
            full_url = urljoin(source["base_url"], link_tag["href"])
            latest_news.append({"source": source["name"], "title": article.text.strip(), "url": full_url})
            print(f"✔ {source['name']} - {article.text.strip()} - {full_url}")

# 遍历所有新闻网站
for source in sources:
    scrape_website(source)

# 5. 保存到 JSON
def save_news_to_json(news):
    with open("news.json", "w", encoding="utf-8") as file:
        json.dump(news, file, indent=4, ensure_ascii=False)
    print("✅ 新闻数据已保存到 news.json")

save_news_to_json(latest_news)

# 6. Git 提交更新
def update_git_repo():
    os.system("git add news.json")
    os.system('git commit -m "更新新闻数据"')
    os.system("git push origin main")
    print("🚀 GitHub 已更新")

update_git_repo()

# 7. 关闭浏览器
driver.quit()
