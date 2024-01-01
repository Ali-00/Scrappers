from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from geotext import GeoText
import dateparser
import psycopg2
import requests
import os
import chromedriver_autoinstaller
from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv
import numpy as np
from sqlalchemy import create_engine
import uuid
import pycountry
import re
import random
import datetime
import time
import random

load_dotenv()

def get_option():
    user_agent_list = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 OPR/90.0.4480.54",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37",
    ]

    # chromedriver_autoinstaller.install()
    # chrome_options = Options()
    chrome_options = uc.ChromeOptions()
    # chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--ignore-certificate-error")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # chrome_options.add_experimental_option("useAutomationExtension", False)
    # user_agent = random.choice(user_agent_list)
    # chrome_options.add_argument(f"user-agent={user_agent}")
    version_main = int(chromedriver_autoinstaller.get_chrome_version().split(".")[0])
    # version_main = 113
    return chrome_options,version_main
# driver = uc.Chrome(chrome_options=chrome_options,version_main=version_main)

# chrome_options,version_main = get_option()
# driver = uc.Chrome(chrome_options=chrome_options,version_main=version_main)

# def date_conversion(df):
#     dates_converted = []
#     for i in df["job_posted"]:
#         try:
#             if re.findall(r"[0-9]", i):
#                 b = "".join(re.findall(r"[0-9]", i))
#                 g = (
#                     (datetime.datetime.today() - datetime.timedelta(int(b)))
#                     .date()
#                     .strftime("%m-%d-%Y")
#                 )
#                 dates_converted.append(g)

#             else:
#                 dates_converted.append(
#                     datetime.datetime.today().date().strftime("%m-%d-%Y")
#                 )
#         except Exception as e:
#             dates_converted.append(np.nan)
#             print(e)
#     df["job_posted"] = dates_converted
#     return df

def convert_string_to_date(text):
    date = dateparser.parse(text)
    if date:
        return date.strftime("%Y-%m-%d")
    return np.nan

def get_country_name(location):
    try:
        country = pycountry.countries.search_fuzzy(location)
        if country:
            return country[0].name
    except LookupError:
        pass
    return ""


def extract_city_names(text):
    places = GeoText(text)
    return places.cities


def get_page_count():
    next_page_available = True
    pages = 1
    while next_page_available:
        # driver = uc.Chrome(options=chrome_options,version_main=version_main)
        # chrome_options,version_main = get_option()
        # driver = uc.Chrome(chrome_options=chrome_options,version_main=version_main)
        locations = ""
        driver.get(
            "https://indeed.com/jobs?q={}&l={}&sort=date&radius=25&start={}".format(
                search_term, "&".join(locations), pages * 10
            )
        )
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        total = soup.find("a")
        print(len(total))
        next_button = soup.find("a", {"data-testid": "pagination-page-next"})

        if next_button is None:
            next_page_available = False
            print("This is the last page. No more pages available.")
        else:
            pages += 1
            print("Page: ", pages)
            print("There are more pages available.")
    return pages

def is_iterable(value):
    try:
        iter(value)
        return True
    except TypeError:
        return False

def dump_data(df):
    df["id"] = [uuid.uuid4() for _ in range(len(df))]
    df["id"] = df["id"].astype(str)
    df["platform"] = "Indeed"
    current_datetime = datetime.datetime.now()
    df["created_at"] = current_datetime
    df["updated_at"] = current_datetime
    # df["ir_35_status"] = np.nan
    ir35_keywords = ["ir35", "inside ir35", "outside ir35"]
    # Check if description mentions IR35 status
    df["ir_35_status"] = df["description"].apply(lambda x: any(keyword in x for keyword in ir35_keywords) if is_iterable(x) else np.nan)
    df.replace("", np.nan, inplace=False)
    df = df.dropna(subset=["title", "company_name", "job_posted"])
    column_name = "id"
    cols = list(df.columns)
    cols.insert(0, cols.pop(cols.index(column_name)))
    df = df[cols]
    print(df.head())
    l = [
        "id",
        "company_name",
        "title",
        "description",
        "platform",
        "job_posted",
        "salary",
        "link",
        "created_at",
        "updated_at",
        "job_type",
        "ir_35_status",
        "is_remote_job",
        "city",
        "country",
    ]
    df = df[l]

    # conn = psycopg2.connect(
    #     dbname=os.getenv("DATABASE_NAME"),
    #     user=os.getenv("DATABASE_USER"),
    #     password=os.getenv("DATABASE_PASS"),
    #     host=os.getenv("DATABASE_HOST"),
    #     port=5433,
    # )
    # cursor = conn.cursor()
    # query_post = "INSERT INTO core_job (id, company_name, title, description, platform, job_posted, salary, link, created_at,updated_at,job_type,ir_35_status,is_remote_job,city,country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;"
    # values_posts = [
    #     (
    #         row["id"],
    #         row["company_name"],
    #         row["title"],
    #         row["description"],
    #         row["platform"],
    #         row["job_posted"],
    #         row["salary"],
    #         row["link"],
    #         row["created_at"],
    #         row["updated_at"],
    #         row["job_type"],
    #         row["ir_35_status"],
    #         row["is_remote_job"],
    #         row["city"],
    #         row["country"],
    #     )
    #     for _, row in df.iterrows()
    # ]
    # cursor.executemany(query_post, values_posts)
    # conn.commit()
    # conn.close()
    return df


def Scraper(search_term, location):
    print("location-------------: ", location)
    indeed_posts = []
    pages = 1
    # chrome_options,version_main = get_option()
    # driver = uc.Chrome(chrome_options=chrome_options,version_main=version_main)
    for page in range(pages):
        time.sleep(random.uniform(0, 5))
        chrome_options,version_main = get_option()
        driver = uc.Chrome(chrome_options=chrome_options,version_main=version_main)
        try:
        # driver = uc.Chrome(options=chrome_options,version_main=version_main)
            if (location == "United States") or (location == "Canada"):
                print("LINK: https://indeed.com/jobs?q={}&l={}&sort=date&radius=25&start={}".format(
                        search_term, location, page * 10))
                driver.get(
                    "https://indeed.com/jobs?q={}&l={}&sort=date&radius=25&start={}".format(
                        search_term, location, page * 10
                    )
                )
                link1 = "https://indeed.com"
            elif location == "United Kingdom":
                driver.get(
                    "https://uk.indeed.com/jobs?q={}&sort=date&radius=25&start={}".format(
                        search_term, page * 10
                    )
                )
                link1 = "https://uk.indeed.com"
            elif location == "Germany":
                driver.get(
                    "https://de.indeed.com/jobs?q={}&sort=date&radius=25&start={}".format(
                        search_term, page * 10
                    )
                )
                link1 = "https://de.indeed.com"
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            outer_most_point = soup.find("div", attrs={"id": "mosaic-provider-jobcards"})

            
            for i in outer_most_point.find(
                "ul", attrs={"class": "jobsearch-ResultsList"}
            ):
                job_title = i.find("h2")
                if job_title != None:
                    try:
                        jobs = job_title.find("span").text
                    except Exception as e:
                        jobs = ""
                        print("Error: ", e)
                else:
                    jobs = np.nan

                if i.find("span", {"class": "companyName"}) != None:
                    company = i.find("span", {"class": "companyName"}).text
                    if "remote" in company.lower():
                        IsRemoteJob = True
                    else:
                        IsRemoteJob = False
                else:
                    IsRemoteJob = False

                # Company Name:
                if i.find("span", {"class": "companyName"}) != None:
                    company = i.find("span", {"class": "companyName"}).text
                else:
                    company = np.nan

                if i.find("div", {"class": "companyLocation"}) != None:
                    city_location = i.find("div", {"class": "companyLocation"}).text
                    city_names = extract_city_names(city_location)
                    if len(city_names) >= 1:
                        city = city_names[0]
                    else:
                        city = ""
                else:
                    city = ""

                country_name = location
                # Links:
                if i.find("a") != None:
                    try:
                        link = i.find("a", {"class": "jcs-JobTitle"})["href"]
                        # link = 'https://indeed.com'+link
                        link = link1 + link
                    except Exception as e:
                        link = np.nan
                        print("Error: ", e)
                else:
                    link = np.nan

                # Salary if available:
                if (
                    i.select_one(
                        ".metadataContainer.salaryOnly .metadata.salary-snippet-container .attribute_snippet"
                    )
                    != None
                ):
                    try:
                        salary = i.select_one(
                            ".metadataContainer.salaryOnly .metadata.salary-snippet-container .attribute_snippet"
                        ).text
                    except Exception as e:
                        salary = ""
                        print("Error: ", e)
                else:
                    salary = ""

                # Job_type if available:
                if (
                    i.select_one(
                        ".metadataContainer.salaryOnly .metadata:not(.salary-snippet-container) .attribute_snippet"
                    )
                    != None
                ):
                    try:
                        job_type = i.select_one(
                            ".metadataContainer.salaryOnly .metadata:not(.salary-snippet-container) .attribute_snippet"
                        ).text
                    except Exception as e:
                        job_type = ""
                        print("Error: ", e)
                else:
                    job_type = ""

                # Job Post Date:
                if i.find("span", attrs={"class": "date"}) != None:
                    try:
                        post_date = i.find("span", attrs={"class": "date"}).text
                        # post_date = convert_string_to_date(post_date)
                        date = dateparser.parse(post_date)
                        if date:
                            post_date = date.strftime("%Y-%m-%d")
                        else:
                            post_date = np.nan
                    except Exception as e:
                        post_date = np.nan
                        print("Error: ", e)
                else:
                    post_date = np.nan
                description = np.nan
                indeed_posts.append(
                    [
                        company,
                        country_name,
                        city,
                        jobs,
                        job_type,
                        description,
                        link,
                        salary,
                        IsRemoteJob,
                        post_date,
                    ]
                )
                driver.back()
        except Exception as e:
            print(e)
    driver.close()
    driver.quit()
    indeed_spec = [
        "company_name",
        "country",
        "city",
        "title",
        "job_type",
        "description",
        "link",
        "salary",
        "is_remote_job",
        "job_posted",
    ]
    df = pd.DataFrame(indeed_posts, columns=indeed_spec)
    
    return df


def get_description(df):
    for index, row in df.iterrows():
        link = row["link"]
        if pd.notna(link):
            time.sleep(random.uniform(0, 5))
            chrome_options,version_main = get_option()
            driver = uc.Chrome(chrome_options=chrome_options,version_main=version_main)
            # driver = uc.Chrome(options=chrome_options,version_main=version_main)
            driver.get(link)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            desc = soup.find("div", attrs={"id": "jobDescriptionText"})
            if desc:
                df.loc[index, "description"] = str(desc.text.strip()).replace(
                    "<br/>", "\n"
                )
            else:
                df.loc[index, "description"] = np.nan
            driver.quit()
        else:
            df.loc[index, "description"] = np.nan

    # driver.close()
    return df


if __name__ == "__main__":
    search_terms = [
        "python",
        "data scientist",
        "data engineer",
        "software engineer",
        "data analyst",
    ]
    # locations = ["United States", "Canada", "United Kingdom", "Germany"]
    locations = ["United States"]
    for search_term in search_terms:
        for location in locations:
            df = Scraper(search_term, location)
            # df = date_conversion(df)
            df = get_description(df)
            df = dump_data(df)
            print(df.head(2))
            df.to_csv("{}.csv".format(search_term),index=False)
