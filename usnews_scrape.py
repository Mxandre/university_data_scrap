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


def get_college_urls(driver, url, sleep_time=5):
    try:
        driver.get(url)
        # time.sleep(sleep_time)
        target_count = 50

        # last_height = driver.execute_script("return document.body.scrollHeight")
        # Initialize the last height of the page
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.Card__CardContainer-sc-1ra20i5-0")
            )
        )

        # Initialize an empty list to store the elements
        collected_elements = []

        while True:
            try:

                # 使用 CSS Selector 定位按钮
                button = driver.find_element(
                    By.CSS_SELECTOR,
                    "button.button__ButtonStyled-sc-1vhaw8r-1.bGXiGV.pager__ButtonStyled-sc-1i8e93j-1.dypUdv.type-secondary.size-large",
                )

                # 点击按钮
                button.click()

                print("Button clicked successfully.")

            # 继续你的其他操作

            except Exception as e:
                print(f"An error occurred: {e}")
            elements = driver.find_elements(
                By.CSS_SELECTOR, "div.Card__CardContainer-sc-1ra20i5-0"
            )

            # Append newly found elements to the list
            collected_elements.extend(elements)

            # Remove duplicates by converting the list to a set and back to a list
            collected_elements = list(set(collected_elements))

            # Check if we have collected enough elements
            if len(collected_elements) >= target_count:
                break  # Exit the loop if the target count is reached

            # Scroll down to the bottom of the page
            # driver.execute_script("window.scrollBy(0, 500);")

            # Wait for new content to load
            time.sleep(random.uniform(5, 10))

            # Calculate new scroll height and compare with last scroll height
            # new_height = driver.execute_script("return document.body.scrollHeight")

            # Check if no new content is loaded
            # if new_height == last_height:
            #     break  # Exit the loop if no new elements are loaded

            # Update the last height
            # last_height = new_height

        # Now you have enough elements stored in collected_elements
        # You can process them as needed
        for element in collected_elements[
            :target_count
        ]:  # Ensure you only process the target number
            print(element.text)

        # Don't forget to close the WebDriver
        driver.quit()

    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        return None

    #     college_cards = driver.find_elements(
    #         By.CSS_SELECTOR, "div.Card__CardContainer-sc-1ra20i5-0"
    #     )
    #     top_10_schools = []
    #     for card in college_cards[:20]:  # 改变爬取数量
    #         try:
    #             name_element = card.find_element(
    #                 By.CSS_SELECTOR, "a.Card__StyledAnchor-sc-1ra20i5-10 h3"
    #             )
    #             name = name_element.text
    #             href_element = card.find_element(
    #                 By.CSS_SELECTOR, "a.Card__StyledAnchor-sc-1ra20i5-10"
    #             )
    #             href_url = href_element.get_attribute("href")
    #             top_10_schools.append((href_url))
    #         except Exception as e:
    #             print(f"Error extracting URL from card: {e}")
    #     return top_10_schools
    # except Exception as e:
    #     print(f"Error loading page or extracting college URLs: {e}")
    #     return []


def parse_page_content(urls, sleep_time=5):
    data = {
        "url": [],
        "name": [],
        "overview": [],
        "houses_and_dorms": [],
        "national_university_rank": [],
        "best_values_school_rank": [],
        "engineering_programs_doctorate": [],
        "four_year_graduation_rate": [],
        "student_faculty_ratio": [],
        "classes_with_fewer_students": [],
        "sat": [],
        "act": [],
        "gpa": [],
        "application_deadline": [],
        "acceptance_rate": [],
        "ethnic_diversity": [],
        "ten_popular_major": [],
    }

    # for url in urls[:3]:
    driver = initialize_driver()
    driver.get(urls)

    try:
        # Get college name
        name_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (
                    By.CSS_SELECTOR,
                    "div.Villain__TitleContainer-sc-1y12ps5-6.knjdTo",
                )
            )
        )
        # name_elements = driver.find_elements(
        #     By.CSS_SELECTOR, "div.Villain__TitleContainer-sc-1y12ps5-6.knjdTo"
        # )
        if name_elements:
            data["name"].append(" ".join([name.text for name in name_elements]))
        else:
            data["name"].append(None)

        # Get statistical data
        some_rates = driver.find_elements(
            By.CSS_SELECTOR, "p.AcademicSection__DataHeader-sc-1g5x16k-5.cKgZfy"
        )
        if len(some_rates) >= 3:
            data["four_year_graduation_rate"].append(some_rates[0].text)
            data["student_faculty_ratio"].append(some_rates[1].text)
            data["classes_with_fewer_students"].append(some_rates[2].text)
        else:
            data["four_year_graduation_rate"].append(None)
            data["student_faculty_ratio"].append(None)
            data["classes_with_fewer_students"].append(None)

        # Get dormitory info
        houses = driver.find_elements(
            By.CSS_SELECTOR,
            "li.CampusLifeSection__StyledListItem-x6yma0-2.bPrOzD",
        )
        data["houses_and_dorms"].append(",".join([house.text for house in houses]))

        # Get overview information
        overview_element = driver.find_elements(By.CSS_SELECTOR, "p.mt2.mb2")
        if overview_element:
            data["overview"].append(overview_element[0].text)
        else:
            data["overview"].append(None)

        # Get ranking information
        ranks = driver.find_elements(
            By.CSS_SELECTOR,
            "div.RankList__Rank-sc-2xewen-2.ieuiBj.ranked.has-badge",
        )
        if len(ranks) >= 3:
            data["national_university_rank"].append(ranks[0].text)
            data["best_values_school_rank"].append(ranks[1].text)
            data["engineering_programs_doctorate"].append(ranks[2].text)
        else:
            data["national_university_rank"].append(None)
            data["best_values_school_rank"].append(None)
            data["engineering_programs_doctorate"].append(None)

        # Get application deadline and acceptance rate
        applying_data = driver.find_elements(
            By.CSS_SELECTOR, "p.ApplyingSection__DataHeader-sc-2strss-7.hRHtQv"
        )
        if len(applying_data) >= 2:
            data["application_deadline"].append(applying_data[0].text)
            data["acceptance_rate"].append(applying_data[1].text)
        else:
            data["application_deadline"].append(None)
            data["acceptance_rate"].append(None)

        # Get admission requirements
        req = driver.find_elements(
            By.CSS_SELECTOR,
            "div.Box-w0dun1-0.DataRow__Row-sc-1udybh3-0.beItxn.fPkWrz.ApplyingSection__StyledDataRow-sc-2strss-5.iVBcfS",
        )
        if len(req) >= 3:
            data["sat"].append(
                req[0]
                .find_element(By.CSS_SELECTOR, "p.Paragraph-sc-1iyax29-0.kqzqfx")
                .text
            )
            data["act"].append(
                req[1]
                .find_element(By.CSS_SELECTOR, "p.Paragraph-sc-1iyax29-0.kqzqfx")
                .text
            )
            data["gpa"].append(
                req[2]
                .find_element(By.CSS_SELECTOR, "p.Paragraph-sc-1iyax29-0.kqzqfx")
                .text
            )
        else:
            data["sat"].append(None)
            data["act"].append(None)
            data["gpa"].append(None)

        # Get ethnic diversity
        ethnic_diversity_names = driver.find_elements(
            By.CSS_SELECTOR,
            "p.Paragraph-sc-1iyax29-0.Key__Title-sc-12afmmk-1.dDlwaN.hWVZdP",
        )
        ethnic_diversity_numbers = driver.find_elements(
            By.CSS_SELECTOR,
            "p.Paragraph-sc-1iyax29-0.Key__Data-sc-12afmmk-3.dDlwaN.eoKXJn",
        )
        ethnic_diversity = []
        for i in range(len(ethnic_diversity_names)):
            ethnic_diversity.append(
                ethnic_diversity_names[i].text + ":" + ethnic_diversity_numbers[i].text
            )
        data["ethnic_diversity"].append(
            ", ".join(ethnic_diversity) if ethnic_diversity else None
        )

        # Get popular majors
        try:
            major_url_parent = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div.AcademicSection__InteriorLink-sc-1g5x16k-10.koxmPs.left-align-link",
                    )
                )
            )
            major_url = major_url_parent.find_element(
                By.CSS_SELECTOR, "a.Anchor-byh49a-0.gSfjJc"
            ).get_attribute("href")

            driver.close()
            driver.quit()
            print("driver has been quitted")
            driver_majors = initialize_driver()
            driver_majors.get(major_url)
            time.sleep(sleep_time)
            major_table = driver_majors.find_element(
                By.CSS_SELECTOR,
                "ul.List__ListWrap-rhf5no-0.jqlIBi.TruncatedList__TopList-sc-1bpza2o-7.fRtWCB",
            )
            majors = major_table.find_elements(
                By.CSS_SELECTOR, "li.List__ListItem-rhf5no-1.jYdEtR"
            )
            popular_majors = [major.text for major in majors]
            data["ten_popular_major"].append(
                ", ".join(popular_majors) if popular_majors else None
            )
            # driver_majors.quit()
        except Exception as e:
            print(f"Error extracting popular majors: {e}")
            data["ten_popular_major"].append(None)
        finally:
            print("finishing the second page parse")
            # pid = driver_majors.service.process.pid
            # # 终止该进程
            # os.kill(pid, signal.SIGTERM)
            driver_majors.close()
            driver_majors.quit()

        data["url"].append(urls)
        print(f"finishing scraping in: {data['name'][-1]}")

    except Exception as e:
        print(f"Error occurred while processing {url}: {e}")
        for key in data.keys():
            if len(data[key]) < len(data["name"]):
                data[key].append(None)

    return data


def parse_pages_content(urls, sleep_time=5, max_workers=5):
    all_data = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(parse_page_content, url, sleep_time): url for url in urls
        }

        for future in as_completed(futures):
            try:
                result = future.result()
                all_data.append(result)
            except Exception as e:
                print(f"Error occurred during scraping: {e}")

    # 将所有数据合并为一个 DataFrame
    flattened_data = [
        dict(zip(result.keys(), item))
        for result in all_data
        for item in zip(*result.values())
    ]
    return pd.DataFrame(flattened_data)


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


# Example usage
if __name__ == "__main__":
    url = "https://www.usnews.com/best-colleges/rankings/national-universities"

    # driver = initialize_driver()
    # driver = webdriver.Chrome()

    if True:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "college_data.csv")

        # Load existing cache
        cached_data = load_cache(file_path)

        # Get new URLs to scrape
        # top_10_urls = get_college_urls(driver, url)
        urls_file_path = os.path.join(script_dir, "urls.csv")

        urls_data = load_cache(urls_file_path)

        if not cached_data.empty:  # 返回dataframe，可用empty的返回值来判断是否为空
            new_urls = [
                u for u in urls_data["_follow"] if u not in cached_data["url"].values
            ]
        else:
            new_urls = urls_data

        # Scrape new data
        new_data = parse_pages_content(new_urls)

        # Combine cached and new data
        combined_data = pd.concat([cached_data, new_data], ignore_index=True)

        # Save combined data back to cache
        save_cache(combined_data, file_path)

        print(f"Data saved to {file_path}")
        # driver.quit()
