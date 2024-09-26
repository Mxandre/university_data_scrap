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
from selenium.webdriver.common.action_chains import ActionChains
from typing import List, Dict, Any


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


def scrape_data(url):
    data = {
        "url": "",
        "name": "",
        "type": "",
        "description": "",
        "location": "",
        "address": "",
        "web": "",
        # "rankings": "",
        # "professional_ranking": "",
        "students": "",
        "campus_location": "",
        "geographical_location": "",
        "campus_size": "",
        "campus_size_description": "",
        "on_campus_mandatory": "",
        "percentage_of_commuter_students": "",
        "dormitory_conditions:": "",
        "types_of_dormitories": "",
        "athletic_programs": "",
        "crime": "",
        "history": "",
        "fun_fact": "",
        "alumni": "",
        "key_information_apply": "",
        "undergraduate_application_request": "",
        "number_of_admitted_students_undergraduated": "",
        "grade_distribution": "",
        "overall_rating": "",
        "teaching_quality": "",
        "extracurricular_activities": "",
        "campus_activities": "",
        "features_review ": "",
    }

    driver = initialize_driver()
    try:
        driver.get(url)
        data["url"] = url
        try:
            # 名字
            name = driver.find_element(
                By.XPATH,
                '//*[@id="content"]/div[1]/div/div[2]/div/div/div/div[2]/div[2]',
            )
            data["name"] = name.text

            # 类型
            type = driver.find_element(
                By.XPATH, '//*[@id="Basic_Info"]/div[2]/div[1]/div[1]/div[2]'
            )
            data["type"] = type.text

            # location
            location = driver.find_element(
                By.XPATH, '//*[@id="Basic_Info"]/div[2]/div[1]/div[2]/div[2]'
            )
            data["location"] = location.text

            # address
            address = driver.find_element(
                By.XPATH, '//*[@id="Basic_Info"]/div[2]/div[1]/div[3]/div[2]'
            )
            data["address"] = address.text

            # website
            web = driver.find_element(
                By.XPATH, '//*[@id="Basic_Info"]/div[2]/div[1]/div[4]/div[2]/a'
            )
            data["web"] = web.text

        except NoSuchElementException:
            print("basic_info cannot be located")
            # data["basic_info"] = " "

        try:
            # 获取院校总览的href
            overview_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="content"]/div[2]/div/a[2]')
                )
            )
            overview_button.click()
        except NoSuchElementException:
            print("not a overview button")

        try:
            # 获取各类排名
            ranking_block = driver.find_element(
                By.CSS_SELECTOR, "div.f10s67gx.f1nzr65k"
            )
            ranking_block = ranking_block.find_elements(By.CSS_SELECTOR, "div.f14m5di9")
            for block in ranking_block:
                category = block.find_element(By.CSS_SELECTOR, "span.f1crdn7n").text
                rank = block.find_element(By.CSS_SELECTOR, "span.f1912lu2").text
                key = f"ranking{category}"
                data[key] = rank
            # rankings = driver.find_element(By.XPATH, "//*[@id='Ranking']/div[2]/div[3]")
            # data["rankings"] = "\n".join(
            #     rank.text for rank in rankings.find_elements(By.XPATH, ".//*")
            # )
        except NoSuchElementException:
            print("ranking cannot be located")
            # data["rankings"] = ""

        try:
            # 使用xpath定位展示更多按键
            div_element = driver.find_element(
                By.XPATH, '//*[@id="Ranking"]/div[3]/div[4]/div[1]/div'
            )
            actions = ActionChains(driver)
            actions.move_to_element(div_element).click().perform()
            time.sleep(3)
            profession_rank_block = driver.find_element(
                By.XPATH, '//*[@id="Ranking"]/div[3]/div[2]'
            )
            profession_ranks = profession_rank_block.find_elements(
                By.CSS_SELECTOR, "div.fxrkxhc"
            )
            for profession in profession_ranks:
                prfession_name = profession.find_element(
                    By.CSS_SELECTOR, "div.f19f5d37"
                )
                profession_rank = profession.find_elements(
                    By.XPATH, ".//span[not(ancestor::span)]"
                )
                profession_rank_text = "".join([span.text for span in profession_rank])
                key = prfession_name.text
                data[f"{key}"] = profession_rank_text

            # data["professional_ranking"] = "\n".join(
            #     pro.text for pro in profession_ranks
            # )
        except NoSuchElementException:
            print("professional rankings cannot be located")
            # data["professional_ranking"] = ""

        try:
            # scrape description
            description = driver.find_element(
                By.XPATH, '//*[@id="Description"]/div[2]/div[1]'
            )
            data["description"] = description.text
        except NoSuchElementException:
            print("description not found")
            data["description"] = ""

        try:
            # 学生组成
            students = driver.find_elements(By.CSS_SELECTOR, "div.f2eq7vv")
            data["students"] = "\n".join(stu.text for stu in students)
        except NoSuchElementException:
            print("cannot locate student element")
            data["students"] = ""

        try:
            # 校园位置
            campus_location = driver.find_element(
                By.XPATH, '//*[@id="Campus"]/div[2]/div[1]/div[2]'
            )
            data["campus_location"] = campus_location.text
            geographical_location = driver.find_element(
                By.XPATH, '//*[@id="Campus"]/div[2]/div[2]/div[2]/div[1]'
            )
            data["geographical_location"] = geographical_location.text
        except NoSuchElementException:
            print("cannot find location")
            data["campus_location"] = ""
            data["geographical_location"] = ""

        try:
            # 校园面积
            campus_size = driver.find_element(
                By.XPATH, '//*[@id="Campus"]/div[3]/div[1]/div[2]'
            )
            data["campus_size"] = campus_size.text
            campus_size_description = driver.find_element(
                By.XPATH, '//*[@id="Campus"]/div[3]/div[2]/div[2]/div[1]'
            )
            data["campus_size_description"] = campus_size_description.text
        except NoSuchElementException:
            print("cannot find campus")
            data["campus_size"] = ""
            data["campus_size_description"] = ""

        try:
            # 住宿条件
            mandatory = driver.find_element(
                By.XPATH, '//*[@id="Campus"]/div[4]/div[1]/div[2]'
            )
            data["on_campus_mandatory"] = mandatory.text
            percentage = driver.find_element(
                By.XPATH, '//*[@id="Campus"]/div[4]/div[2]/div[2]'
            )
            data["percentage_of_commuter_students"] = percentage.text
            type = driver.find_element(
                By.XPATH, '//*[@id="Campus"]/div[4]/div[3]/div[2]'
            )
            data["types_of_dormitories"] = type.text
            conditon = driver.find_element(
                By.XPATH, '//*[@id="Campus"]/div[4]/div[4]/div[2]/div[1]'
            )
            data["dormitory_conditions:"] = conditon.text
        except NoSuchElementException:
            print("cannot find dormitory")
            data["on_campus_mandatory"] = ""
            data["percentage_of_commuter_students"] = ""
            data["types_of_dormitories"] = ""
            data["dormitory_conditions:"] = ""

        try:
            # 体育培养
            Sport = driver.find_element(
                By.XPATH, '//*[@id="Campus"]/div[5]/div/div[2]/div[1]'
            )
            data["athletic_programs"] = Sport.text
        except NoSuchElementException:
            print("cannot find Sport")
            data["athletic_programs"] = ""

        try:
            # 犯罪率
            crime = driver.find_element(By.XPATH, '//*[@id="Campus"]/div[6]')
            data["crime"] = crime.text
        except NoSuchElementException:
            print("cannot find crime")
            data["crime"] = ""

        try:
            # 历史
            history = driver.find_element(
                By.XPATH,
                '//*[@id="Culture_History"]/div[1]/div[2]/div[1]/div[2]/div[1]',
            )
            data["history"] = history.text
        except NoSuchElementException:
            print("cannot find history")
            data["history"] = ""

        try:
            # 有趣事实
            culture_history = driver.find_element(
                By.XPATH, '//*[@id="Culture_History"]/div[1]/div[2]/div[2]/div[2]'
            )
            data["fun_fact"] = culture_history.text
        except NoSuchElementException:
            print("cannot find fun_fact")
            data["fun_fact"] = ""

        try:
            # 校友
            alumna = driver.find_element(
                By.XPATH, '//*[@id="Culture_History"]/div[2]/div[3]/div/div[2]/div[1]'
            )
            data["alumni"] = alumna.text
        except NoSuchElementException:
            print("cannot find alumna")
            data["alumni"] = ""

        try:
            # 升学通道按键定位
            admission_channel_button = driver.find_element(
                By.XPATH,
                '//*[@id="content"]/div[1]/div/div[3]/div/div/div/div/div/a[2]',
            )  # a标签
            admission_channel_button.click()
            # 申请重要数据
            key_information_apply_block = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.fkkenzk"))
            )
            key_information_apply = key_information_apply_block.find_elements(
                By.CSS_SELECTOR, "div.f1c2r9sn"
            )
            data["key_information_apply"] = "\n".join(
                key.text for key in key_information_apply
            )
        except NoSuchElementException:
            print("key_information cannot be located")
            data["key_information_apply"] = " "

        try:
            # 定位本科申请要求
            undergraduate_block = driver.find_element(
                By.XPATH, '//*[@id="Undergraduate_Application_Request"]/div[2]'
            )
            undergraduate_request = driver.find_elements(By.CSS_SELECTOR, "div.fkyhmxm")
            data["undergraduate_application_request"] = "\n".join(
                request.text for request in undergraduate_request
            )
        except NoSuchElementException:
            print("undergraduate_block cannot be located")
            data["undergraduate_application_request"] = " "

        try:
            # 定位录取情况
            admissioin_number = driver.find_element(
                By.XPATH, '//*[@id="Undergraduate_Admission"]/div[1]/div[2]/div/div[1]'
            )
            data["number_of_admitted_students_undergraduated"] = admissioin_number.text
            # 定位学生成绩分布
            grade_block = driver.find_element(
                By.XPATH,
                '//*[@id="Undergraduate_Admission"]/div[2]/div[2]',  # //*[@id="Undergraduate_Admission"]/div[2]/div[2]
            )
            grades = grade_block.find_elements(By.XPATH, ".//*")
            data["grade_distribution"] = "\n".join(grade.text for grade in grades)
        except NoSuchElementException:
            print("grade cannot be located")
            data["number_of_admitted_students_undergraduated"] = " "
            data["grade_distribution"] = ""

        try:
            # 定位点评
            comment_button = driver.find_element(
                By.XPATH,
                '//*[@id="content"]/div[1]/div/div[3]/div/div/div/div/div/a[5]',
            )
            comment_button.click()
            overall_comment = driver.find_element(
                By.XPATH,
                '//*[@id="content"]/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/div[2]',
            )
            data["overall_rating"] = overall_comment.text
            teaching_quality = driver.find_element(
                By.XPATH,
                '//*[@id="content"]/div[2]/div/div[1]/div[1]/div[1]/div/div[3]/div[1]',
            )
            data["teaching_quality"] = teaching_quality.text
            extracurricular_activities = driver.find_element(
                By.XPATH,
                '//*[@id="content"]/div[2]/div/div[1]/div[1]/div[1]/div/div[3]/div[1]',
            )
            data["extracurricular_activities"] = extracurricular_activities.text
            campus_life = driver.find_element(
                By.XPATH,
                '//*[@id="content"]/div[2]/div/div[1]/div[1]/div[1]/div/div[3]/div[3]',
            )
            data["campus_activities"] = campus_life.text
        except NoSuchElementException:
            print("cannot located rating area")
            data["overall_rating"] = " "
            data["extracurricular_activities"] = " "
            data["teaching_quality"] = " "
            data["campus_activities"] = " "

        try:
            # cibler featured reviews
            featured_reviews = driver.find_elements(By.CSS_SELECTOR, "div.fz5kw9q")
            data["features_review "] = "\n".join(
                review.text for review in featured_reviews
            )
        except NoSuchElementException:
            print("connot located reviews")
            data["features_review "] = " "

    except NoSuchElementException:
        print(f"{url} cannot be connected")

    finally:
        print(f"finishing scraping {url}")
        driver.close()
        driver.quit()

    return data


def scrape_all(urls: List[str]) -> List[Dict[str, Any]]:
    all_data = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(scrape_data, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
                print(data)
                all_data.append(data)
            except Exception as exc:
                print(f"{url} generated an exception: {exc}")
    return all_data


def load_cache(file_path):
    if os.path.exists(file_path):
        cached_data = pd.read_csv(file_path)
        if "url" not in cached_data.columns:  # Ensure 'url' column exists
            cached_data["url"] = None
        return cached_data
    else:
        # 如果文件不存在，返回一个空的 DataFrame，并指定列名为 'url'
        df = pd.DataFrame(columns=["url"])
        save_cache(df, file_path)
        return df


def save_cache(df, file_path):
    if isinstance(df, pd.DataFrame):
        df.to_csv(
            file_path, index=False, encoding="utf-8-sig"
        )  # 'utf-8-sig' 编码可以确保在 Excel 中正确显示中文字符

    else:
        raise TypeError("Expected data to be a pandas DataFrame")


if __name__ == "__main__":

    if True:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "global_college_datasets.csv")

        # Load existing cache
        cached_data = load_cache(file_path)

        # Get new URLs to scrape
        # top_10_urls = get_college_urls(driver, url)
        urls_file_path = os.path.join(script_dir, "apply_school_url.csv")

        urls_data = load_cache(urls_file_path)
        cached_urls_list = cached_data["url"].tolist()

        if not cached_data.empty:  # 返回dataframe，可用empty的返回值来判断是否为空
            new_urls = [u for u in urls_data["url"] if u not in cached_urls_list]
        else:
            new_urls = urls_data["url"]

        # print(new_urls)

        # Scrape new data
        new_data = scrape_all(new_urls)
        # print(new_data)
        # 获取所有可能的键
        all_key = set()
        for data in new_data:
            all_key.update(data.keys())

        # 补充没有的键，设置为None
        uniform_data = []
        for data in new_data:
            uniform_data.append({key: data.get(key, None) for key in all_key})

        new_data = pd.DataFrame(uniform_data)

        # 将已有数据与新爬取数据进行整合
        # 获取所有的列名
        all_columns = set(cached_data.columns) | set(new_data.columns)
        # print(f"all_columns:{all_columns}")

        # 确保现有数据包含所有可能的列
        existing_data_df = cached_data.reindex(columns=all_columns)

        # 确保新数据包含所有可能的列
        new_data_df = new_data.reindex(columns=all_columns)  # 某列缺失，则变为None
        # print(new_data_df)

        # Combine cached and new data
        combined_data = pd.concat([existing_data_df, new_data_df], ignore_index=True)

        # Save combined data back to cache
        save_cache(combined_data, file_path)

        print(f"Data saved to {file_path}")
        # driver.quit()
