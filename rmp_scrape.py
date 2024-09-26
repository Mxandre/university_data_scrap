import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors
    options.add_argument("--ignore-ssl-errors")
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


def read_names_from_csv(file_path):
    df = pd.read_csv(file_path)
    print(f"DataFrame dimensions: {df.shape}")  # Show the dimensions of the DataFrame
    print(df)  # Print the entire DataFrame
    if "name" in df.columns:
        return df["name"].tolist()
    else:
        raise KeyError("The CSV file does not contain a column named 'name'.")


def find_names(university_names, cache_file):
    names = []
    if os.path.exists(cache_file):
        cache = pd.read_csv(cache_file)
        for university_name in university_names:
            cached_result = cache[
                cache["name"].str.lower() == str(university_name).lower()
            ]
            if not cached_result.empty:
                print(f"Found {university_name} in cache")
                continue
            else:
                names.append(university_name)
    else:
        names = university_names  # 如果没有缓存文件，将所有大学名称返回
    return names


def search_university(university_name):
    # Check cache first
    # if os.path.exists(cache_file):
    #     cache = pd.read_csv(cache_file)
    #     cached_result = cache[cache['name'].str.lower() == university_name.lower()]
    #     if not cached_result.empty:
    #         print(f"Found {university_name} in cache")
    #         return cached_result.iloc[0]['url']

    # If not in cache, perform search
    driver = initialize_driver()
    if not driver:
        return None

    driver.get("https://www.ratemyprofessors.com/")
    university_url = None

    try:
        # Wait until the search box is present
        wait = WebDriverWait(driver, 10)
        search_box = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[placeholder="Your school"]')
            )
        )
        search_box.send_keys(university_name)
        search_box.send_keys(Keys.RETURN)

        # Wait for the new page to load
        time.sleep(5)

        # Get the first search result name and compare
        first_result_name = wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    ".SchoolCard__StyledSchoolCard-sc-130cnkk-0.bJboOI .SchoolCardHeader__StyledSchoolCardHeader-sc-1gq3qdv-0",
                )
            )
        )
        first_result_name_text = first_result_name.text

        if first_result_name_text.lower() == university_name.lower():
            # Get the URL of the university
            university_link = wait.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        ".SchoolCard__StyledSchoolCard-sc-130cnkk-0.bJboOI",
                    )
                )
            )
            university_url = university_link.get_attribute("href")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()
    print(f"university {university_name} has been scraped,result is :{university_url}")

    # Update cache
    # if university_url:
    #     new_entry = pd.DataFrame([[university_name, university_url]], columns=['name', 'url'])
    #     if os.path.exists(cache_file):
    #         cache = pd.read_csv(cache_file)
    #         cache = pd.concat([cache, new_entry], ignore_index=True)
    #     else:
    #         cache = new_entry
    #     cache.to_csv(cache_file, index=False)

    return {"name": university_name, "url": university_url}


def scrape_urls_content(names, sleep_time=5, max_workers=5):
    all_data = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(search_university, name): name for name in names}

        for future in as_completed(futures):
            try:
                result = future.result()
                all_data.append(result)
            except Exception as e:
                print(f"Error occurred during scraping: {e}")

    # 将所有数据合并为一个 DataFrame
    # flattened_data = [dict(zip(result.keys(), item)) for item in zip(*result.values())]
    return pd.DataFrame(all_data)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "college_data.csv")
    cache_file = os.path.join(script_dir, "caches.csv")

    try:
        university_names = read_names_from_csv(file_path)
        # print(university_names)
        names = find_names(university_names, cache_file)
        names_urls = scrape_urls_content(names)
        cache_data = pd.read_csv(cache_file)
        #  Update cache
        if not names_urls.empty:
            # new_entry = pd.DataFrame([[cache_data ,names_urls]], columns=['name', 'url'])
            if os.path.exists(cache_file):
                cache = pd.read_csv(cache_file)
                cache = pd.concat([cache, names_urls], ignore_index=True)
            else:
                print("error occurs when reading cache_file")
            cache.to_csv(cache_file, index=False)
            print(f"file has been saved to {cache_file}")

        # for university_name in university_names:
        #     print(f"Searching for {university_name}...")
        #     url = search_university(university_name, cache_file)
        #     if url:
        #         print(f"Found URL: {url}")
        #     else:
        #         print(f"URL not found for {university_name}")
    except KeyError as e:
        print(e)


if __name__ == "__main__":
    main()
