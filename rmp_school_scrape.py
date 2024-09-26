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
from concurrent.futures import ThreadPoolExecutor, as_completed


def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--headless")
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


def read_cache(file_path):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df
    else:
        raise FileNotFoundError(f"The cache file at {file_path} does not exist.")


def scrape_scores(url):
    driver = initialize_driver()
    driver.get(url)
    time.sleep(3)  # Wait for the page to load
    print("hello")

    # try:
    #     overall_score_element = WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located(
    #             (By.CSS_SELECTOR, "div.OverallRating__Number-y66epv-3")
    #         )
    #     )
    #     overall_score = overall_score_element.text
    # except Exception as e:
    #     print(f"Error scraping overall score: {e}")
    #     overall_score = None

    # detailed_scores = {}
    # scores_and_comments = ""
    # try:
    #     categories = driver.find_elements(
    #         By.CSS_SELECTOR, "div.CategoryGrade__CategoryGradeContainer-sc-17vzv7e-0"
    #     )
    #     for category in categories:
    #         category_title_element = category.find_element(
    #             By.CSS_SELECTOR, "div.CategoryGrade__CategoryTitle-sc-17vzv7e-1"
    #         )
    #         category_score_element = category.find_element(
    #             By.CSS_SELECTOR, "div.GradeSquare__ColoredSquare-sc-6d97x2-0"
    #         )
    #         category_title = category_title_element.text
    #         category_score = category_score_element.text
    #         detailed_scores[category_title] = category_score
    try:
        comment_scores_blocks = driver.find_elements(
            By.CSS_SELECTOR, "div.SchoolRating__SchoolRatingBody-sb9dsm-1"
        )
        # comment and score
        for score_block in comment_scores_blocks:
            score_element = score_block.find_element(
                By.CSS_SELECTOR, "div.SchoolRating__OverallRatingContainer-sb9dsm-2"
            )
            score = re.findall(r"\d+\.\d*", score_element.text)
            score = "".join(score)
            comment_element = score_block.find_element(
                By.CSS_SELECTOR, "div.SchoolRating__RatingComment-sb9dsm-6"
            )
            comment = comment_element.text
            scores_and_comments += "".join(score) + ": " + comment + "\n"

    except Exception as e:
        print(f"Error scraping detailed scores: {e}")
        overall_score, detailed_scores, scores_and_comments = None, {}, ""
    finally:
        driver.quit()

    # return overall_score, detailed_scores, scores_and_comments
    return scores_and_comments


def process_url(url, name):
    overall_score, detailed_scores, scores_and_comments = scrape_scores(url)
    result = {"url": url, "university_name": name, "overall_score": overall_score}
    result.update(detailed_scores)
    result["scores_and_comments"] = scores_and_comments
    return result


def scrape_many_scores(urls, names, max_workers=5):
    all_data = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_url, url, name): url
            for url, name in zip(urls, names)
        }

        for future in as_completed(futures):
            try:
                result = future.result()
                all_data.append(result)
            except Exception as e:
                print(f"Error occurred during scraping: {e}")

    return pd.DataFrame(all_data)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_file = os.path.join(script_dir, "caches.csv")
    rmp_file = os.path.join(script_dir, "scraped_scores.csv")

    try:
        cache_data = read_cache(cache_file)
        rmp_cache_data = read_cache(rmp_file)
        # get the last gotten university
        start_num = rmp_cache_data.shape[0]
        last_num = start_num + 50
        names = cache_data.iloc[start_num:last_num]["name"]
        urls = cache_data.iloc[start_num:last_num]["url"].dropna()
        results = scrape_many_scores(urls.tolist(), names.tolist())

        # results = []
        # result={
        #         'university_name':[],
        #         'scores_and_comments':[]
        #     }

        # for index, row in cache_data[ start_num : last_num ].iterrows():
        #     university_name = row['name']
        #     url = row['url']
        #     print(f"Visiting {university_name} at {url}...")

        #     overall_score, detailed_scores,scores_and_comments = scrape_scores(url, driver)
        #     # scores_and_comments=scrape_scores(url,driver)
        #     result = {
        #         'university_name': university_name,
        #         'url': url,
        #         'overall_score': overall_score
        #     }
        #     result.update(detailed_scores)
        #     result.update(scores_and_comments)
        #     # results.append(result)

        # driver.quit()

        # results_df = pd.DataFrame(results)
        results_file = os.path.join(script_dir, "scraped_scores.csv")

        # results_df.to_csv(results_file, index=False)
        csv_file = "D:\\vsco\python\\scraped_scores.csv"  # 替换为你的 Excel 文件路径
        # sheet_name = 'Sheet1'  # 替换为你的工作表名称
        df_existing = pd.read_csv(csv_file)
        df_result = pd.concat([df_existing, results], ignore_index=True)
        # scores_and_comments=pd.DataFrame(result)

        # df_combined = pd.merge(df_existing, scores_and_comments, on='university_name',how='left')
        df_result.to_csv(results_file, index=False)
        print(f"Scraped data saved to {results_file}")

    except FileNotFoundError as e:
        print(e)


if __name__ == "__main__":
    main()
