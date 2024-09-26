# 开发时间:2024/8/9 15:36
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import re


def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--headless")
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


def scrape_scores(url, driver):
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

    try:
        overall_score_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div.columns.small-12.large-6.xxxlarge-3.end.linklist",
                )
            )
        )
    except Exception as e:
        print(f"Error scraping overall score: {e}")
        overall_score = None

    data = {}
    majors = driver.find_elements(By.CLASS_NAME, "accordion-title")

    pattern = re.compile(r"\s*\(.*?\)")

    majors_blocks = driver.find_elements(
        By.CLASS_NAME, "accordion-content.row.small-12"
    )
    # for major_block[0] in majors_blocks:
    i = 0
    degree_lists = majors_blocks[0].find_elements(By.CLASS_NAME, "extlink-nobreak")
    degree_blocks = majors_blocks[0].find_elements(
        By.CLASS_NAME, "columns.small-12.large-6.xxxlarge-3.end.linklist"
    )
    degree_lists = degree_blocks.find_elements(By.CLASS_NAME, "ext")
    for degree in degree_lists:
        if re.match(r"^Graduate", degree.text) or re.match(r"^Ph", degree.text):
            continue  # 待补充，不同元素名称

        try:
            degree_link = degree_blocks.get_attribute("href")
            degree_name = degree.text
            degree_name = re.sub(pattern, "", degree_name).strip()
            print(f"now is major{majors[i].text} with degree{degree_name}")

            data.update({"major": majors[i].text, "degree": degree_lists})
            driver.get(degree_link)
            anchors = driver.find_elements(By.CLASS_NAME, "jump-link-anchor")
            fields = driver.find_elements(
                By.CLASS_NAME, r".*field--type-text-long.field--label-above$"
            )
            for field in fields:
                label = field.find_elements(By.CLASS_NAME, "field__label")
                item = field.find_elements(By.CLASS_NAME, "field__item")
                data.update({label: item})
            faculty = driver.find_elements(By.CLASS_NAME, "fos-faculty-list")
            courses = driver.find_elements(
                By.CLASS_NAME, "fos-detail-main-courses-list"
            )
            overview = driver.find_elements(
                By.CLASS_NAME,
                "clearfix.text-formatted.field.field--name-field-ua-dar-prog-desc.field--type-text-long.field--label-hidden.field__item",
            )
            data.update(
                {"faculty": faculty, "course": courses, "program offerings": overview}
            )
            i = i + 1
        except Exception as e:
            print(f"Error scraping overall score: {e}")
            driver.quit()

    return data


# jump-link-anchor,field__item


def read_cache(file_path):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df
    else:
        raise FileNotFoundError(f"The cache file at {file_path} does not exist.")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_file = os.path.join(script_dir, "Princeton.csv")

    try:
        # cache_data = read_cache(cache_file)
        driver = initialize_driver()
        if not driver:
            return
        data = scrape_scores(
            "https://www.princeton.edu/academics/areas-of-study", driver
        )
        princeton = pd.DataFrame(data)
        # princeton_file="D:\\vsco\python\\Princeton.csv"
        princeton.to_csv(cache_file, index=False)
        driver.quit()

        # results_df.to_csv(results_file, index=False)
        # print(f"Scraped data saved to {results_file}")
        # csv_file = "D:\\vsco\python\\scraped_scores.csv"  # 替换为你的 Excel 文件路径
        # # sheet_name = 'Sheet1'  # 替换为你的工作表名称
        # df_existing = pd.read_csv(csv_file)
        # scores_and_comments=pd.DataFrame(result)

        # df_combined = pd.merge(df_existing, scores_and_comments, on='university_name',how='left')
        # df_combined.to_csv(results_file,index=False)

    except FileNotFoundError as e:
        print(e)


if __name__ == "__main__":
    main()
