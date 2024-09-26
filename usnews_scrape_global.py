from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.common.exceptions import NoSuchElementException


def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    # options.add_argument("--headless")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.binary_location = (
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    )
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        return driver
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        return None


def parse_page_content(urls, sleep_time=5):
    data = {
        "url": [],
        "name": [],
        "overview": [],
        "university_rank": [],
        "subject_rank": [],
        "indicator_ranking": [],
    }

    driver = initialize_driver()

    try:
        driver.get(urls)

        # 获取大学名称
        try:
            name_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.Villain__TitleContainer-sc-1y12ps5-6.knjdTo")
                )
            )
            data["name"].append(name_element.text if name_element else None)
        except NoSuchElementException:
            print("Name element not found")
            data["name"].append(None)

        # 获取概述信息
        try:
            overview_element = driver.find_element(
                By.CSS_SELECTOR,
                "p.Paragraph-sc-1iyax29-0.SummarySection__SummaryParagraph-sc-1i2pwhh-1.kbzWiQ.dXkSkj.cms-blurb",
            )
            data["overview"].append(overview_element.text if overview_element else None)
        except NoSuchElementException:
            print("Overview element not found")
            data["overview"].append(None)

        # 获取大学排名
        try:
            university_rank_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.mb5"))
            )
            university_ranks = university_rank_element.find_elements(
                By.CSS_SELECTOR, "a.RankList__RankLink-sc-2xewen-3.gdBSCm.has-badge"
            )
            data["university_rank"].append(
                "\n".join([rank.text for rank in university_ranks])
                if university_ranks
                else "No university ranks found"
            )
        except NoSuchElementException:
            print("University rank element not found")
            data["university_rank"].append(None)

        # 获取学科排名
        try:
            subject_rank_element = driver.find_element(
                By.CSS_SELECTOR, "div.subject-rankings"
            )
            subject_ranks = subject_rank_element.find_elements(
                By.CSS_SELECTOR, "a.RankList__RankLink-sc-2xewen-3.gdBSCm.has-badge"
            )
            data["subject_rank"].append(
                "\n".join([rank.text for rank in subject_ranks])
                if subject_ranks
                else None
            )
        except NoSuchElementException:
            print("Subject ranking element not found")
            data["subject_rank"].append(None)

        # 获取指标排名
        try:
            indicator_rank_element = driver.find_element(
                By.CSS_SELECTOR, "div.Bellow__Content-sc-1wt7bw1-3.kGennU"
            )
            indicator_rank_global = indicator_rank_element.find_element(
                By.CSS_SELECTOR,
                "div.RankList__Rank-sc-2xewen-2.hjRmgV.ranked.has-badge",
            )
            if indicator_rank_global:
                data["indicator_ranking"].append(indicator_rank_global.text + "\n")

            indicator_ranks = indicator_rank_element.find_elements(
                By.CSS_SELECTOR, "div.Box-w0dun1-0.DataRow__Row-sc-1udybh3-0.egPJfu"
            )
            if indicator_ranks:
                data["indicator_ranking"].append(
                    "\n".join([rank.text for rank in indicator_ranks])
                )
        except NoSuchElementException:
            print("Indicator ranking element not found")
            data["indicator_ranking"].append(None)

        data["url"].append(urls)

    finally:
        driver.close()
        driver.quit()

    return data


def clean_data_for_csv(data):
    """清理数据，去除多余的 [] 符号并正确处理换行符."""
    for key in data:
        if isinstance(data[key], list):
            # 将列表转换为字符串，并移除 []
            data[key] = "\n".join(
                [
                    str(item).strip("[]").replace("'", "").replace("\\n", "\n")
                    for item in data[key]
                ]
            )
        else:
            data[key] = str(data[key]).strip("[]").replace("'", "").replace("\\n", "\n")
    return data


def parse_pages_content(urls, sleep_time=5, max_workers=5):
    all_data = []

    def parse_page_wrapper(url):
        try:
            # 通过调用 `parse_page_content` 来获取页面数据
            return parse_page_content(url, sleep_time)
        except Exception as e:
            print(f"Error occurred while processing {url}: {e}")
            return {}  # 返回空字典，以便在合并数据时处理异常情况

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(parse_page_wrapper, url): url for url in urls}

        for future in as_completed(futures):
            try:
                result = future.result()
                if result:  # 确保结果非空
                    cleaned_result = clean_data_for_csv(result)  # 清理数据
                    all_data.append(cleaned_result)
            except Exception as e:
                print(f"Error occurred during scraping: {e}")

    # 将所有数据合并为一个 DataFrame
    if all_data:
        # 确保所有数据具有相同的结构
        keys = set()
        for item in all_data:
            keys.update(item.keys())

        # 填充缺失的键
        for item in all_data:
            for key in keys:
                if key not in item:
                    item[key] = None

        # 将数据合并为 DataFrame
        flattened_data = []
        for data_dict in all_data:
            flattened_data.append(data_dict)

        return pd.DataFrame(flattened_data)
    else:
        # 如果没有数据，返回一个空的 DataFrame
        return pd.DataFrame()


def load_cache(file_path):
    if os.path.exists(file_path):
        cached_data = pd.read_csv(file_path)
        if "url" not in cached_data.columns:  # Ensure 'url' column exists
            cached_data["url"] = None
        return cached_data
    else:
        # 如果文件不存在，返回一个空的 DataFrame，并指定列名为 'url'
        return pd.DataFrame(columns=["url"])


def save_cache(df, file_path):
    df.to_csv(file_path, index=False)


if __name__ == "__main__":

    if True:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "global_college_data.csv")

        # Load existing cache
        cached_data = load_cache(file_path)

        # Get new URLs to scrape
        # top_10_urls = get_college_urls(driver, url)
        urls_file_path = os.path.join(script_dir, "urls_global.csv")

        urls_data = load_cache(urls_file_path)
        cached_urls_list = cached_data["url"].tolist()

        if not cached_data.empty:  # 返回dataframe，可用empty的返回值来判断是否为空
            new_urls = [u for u in urls_data["url"] if u not in cached_urls_list]
        else:
            new_urls = urls_data["url"]

        # Scrape new data
        new_data = parse_pages_content(new_urls)
        new_data = pd.DataFrame(new_data)

        # Combine cached and new data
        combined_data = pd.concat([cached_data, new_data], ignore_index=True)

        # Save combined data back to cache
        save_cache(combined_data, file_path)

        print(f"Data saved to {file_path}")
        # driver.quit()
