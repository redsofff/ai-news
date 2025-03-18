from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# 1. 启动 Chrome 浏览器
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 无界面模式
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 2. 访问 TechCrunch AI 页面
url = "https://techcrunch.com/category/artificial-intelligence/"
driver.get(url)

# 3. 等待页面加载
time.sleep(10)

# 4. 获取 HTML 并解析
soup = BeautifulSoup(driver.page_source, "html.parser")
print(driver.page_source[:1000])  # 打印前 1000 个字符

# 5. 查找新闻标题（你需要手动查看 HTML 结构）
articles = soup.find_all("h3")  # 可能需要调整


# 遍历并排除特定标题
if articles:
    for i, article in enumerate(articles[:23]):
        # 排除包含 "Topics" 或 "More from TechCrunch" 或具有特定类名的元素
        if article.text.strip() == "Topics" or article.text.strip() == "More from TechCrunch" or "wp-block-query-title" in article.get("class", []):
            continue  # 跳过不需要的标题
        print(f"{i+1}. {article.text.strip()}")
else:
    print("❌ 未找到任何新闻！")
# 6. 关闭浏览器
driver.quit()

#以下代码到save_news..是虫应该在抓取到最新的新闻数据后，将这些数据保存到 news.json 文件中
import json

# 假设这是你爬虫抓取到的数据
latest_news = [
    {"title": "AI Breakthrough in 2025", "url": "https://example.com/ai-news-1"},
    {"title": "New AI Model Released", "url": "https://example.com/ai-news-2"},
    # 更多新闻项
]

# 将新闻保存到 news.json 文件
def save_news_to_json(news):
    with open("news.json", "w", encoding="utf-8") as file:
        json.dump(news, file, indent=4, ensure_ascii=False)
    print("新闻数据已保存到 news.json")

# 调用保存函数
save_news_to_json(latest_news)

#以下代码到 是能够将更新的 news.json 文件提交到 GitHub提交和推送
import os

# Git 提交和推送
def update_git_repo():
    os.system("git add news.json")  # 添加 news.json 到 git
    os.system('git commit -m "更新新闻数据"')  # 提交更改
    os.system("git push origin main")  # 推送到远程仓库（确保你是推送到正确的分支）
    print("GitHub 已更新")

# 调用 Git 更新函数
update_git_repo()
