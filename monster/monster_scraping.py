from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re
import datetime
import all_functions as func
from data_cleaning_pandas import data_cleaning, get_all_jobs_from_df


def get_job_list(search_term, location):
    chrome_options = Options()
    chrome_options.add_argument(f"user-agent={func.get_user_agent()}")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome("chromedriver", options=chrome_options)
    location
    url = f"https://www.monster.com/jobs/search?q={search_term.replace(' ', '+')}&where={location.replace(' ', '+')}&page=1&so=m.h.s"
    print(url)
    driver.get(url)
    print("Waiting for 5 seconds...")
    time.sleep(5)

    try:
        for i in range(4):
            driver.execute_script(
                """const container = document.getElementById('card-scroll-container');
                const scrollHeight = container.scrollHeight;
                const duration = 500; // Adjust the duration (in milliseconds) as needed

                const start = container.scrollTop;
                const startTime = 'now' in window.performance ? performance.now() : new Date().getTime();

                const scrollStep = () => {
                const currentTime = 'now' in window.performance ? performance.now() : new Date().getTime();
                const elapsedTime = currentTime - startTime;

                container.scrollTop = easeInOutCubic(elapsedTime, start, scrollHeight - start, duration);

                if (elapsedTime < duration) {
                    requestAnimationFrame(scrollStep);
                }
                };

                const easeInOutCubic = (t, b, c, d) => {
                t /= d / 2;
                if (t < 1) return c / 2 * t * t * t + b;
                t -= 2;
                return c / 2 * (t * t * t + 2) + b;
                };

                scrollStep();
                """
            )

            time.sleep(2)
            print(f"Scrolled for {i} time")
    except Exception as e:
        print(f"Exception on index: {i}\nError: {e}")

    page_source = driver.page_source
    soup = func.get_soup(page_source)
    driver.close()
    driver.quit()

    job_list = []

    job_cards = soup.find_all("article")

    for card in job_cards:
        h3 = card.find("h3")
        if h3:
            if search_term not in h3.find("a").text.lower():
                continue

            job_dict = {"title": h3.find("a").text}
            job_dict["link"] = h3.find("a")["href"]

            job_dict["company_name"] = h3.find("span").text

            loc = card.find("span", {"data-testid": "jobDetailLocation"})
            if loc:
                loc = loc.text
            job_dict["city"] = loc
            job_dict["country"] = location

            date_posted = card.find("span", {"data-testid": "jobDetailDateRecency"})
            if date_posted:
                date_posted = func.convert_string_to_date(date_posted.text)
            job_dict["job_posted"] = date_posted

            current_datetime = datetime.datetime.now()
            job_dict["created_at"] = current_datetime
            job_dict["updated_at"] = current_datetime

            job_dict["platform"] = "Monster"

            job_list.append(job_dict)

    return job_list


def get_job_description(job):
    url = job["link"].strip("/")
    if not url.startswith("http"):
        url = f"https://{url}"
    resp = func.web_scrape(url)

    soup = func.get_soup(resp)

    # Iterate over the <h2> tags
    for h2 in soup.find_all("h2"):
        # Check if the <h2> tag contains the text "Description"
        if "Description" in h2.text:
            # Find the parent tag of the <h2> tag
            description = h2.parent

            # Convert the section to a stringcle
            description_html = str(description)

            # Replace newlines with <br> tags
            formatted_description = description_html.replace("<br/>", "\n")

            description = func.get_soup(formatted_description).text

            return description.strip("Description")


def process_job_description(job):
    description = get_job_description(job)

    if description:
        job["description"] = description

        # Extract salary information
        pattern = r"([£€$CAD])?([\d,]+) (?:-|to) ([£€$CAD])?([\d,]+)"
        matches1 = re.findall(pattern, job["description"])
        if len(matches1) > 0:
            salary_min = matches1[0][0].replace(",", "")
            salary_max = matches1[0][1].replace(",", "")
            job["salary"] = "{}-{}".format(salary_min, salary_max)
            print("Salary range from sentence1:", salary_min, "-", salary_max)
        else:
            job["salary"] = None

        # Extract job type
        pattern = r"(?i)(Permanent|Full[-\s]?time|Contract)"
        matches = re.findall(pattern, job["description"])
        if len(matches) > 0:
            job_type = matches[0]
            job["job_type"] = job_type
            print("Job type:", job_type)
        else:
            job["job_type"] = None
            print("No job type found.")

        time.sleep(1)
        return True

    return False


if __name__ == "__main__":
    # Define search terms and locations
    search_terms = [
        "data scientist",
        "data engineer",
        "software engineer",
        "data analyst",
        "python",
    ]

    locations = [
        "Germany",
        "United States",
        "United Kingdom",
        "Canada",
    ]

    # Get all jobs from DataFrame
    df = get_all_jobs_from_df()

    # Iterate over search terms and locations
    for search_term in search_terms:
        for location in locations:
            job_list = get_job_list(search_term, location)

            print(f"Length of jobs: {len(job_list)}")

        for job in job_list:
            job["description"] = get_job_description(job)
            # pattern = r"([£€$CAD])?([\d,]+) (?:-|to) ([£€$CAD])?([\d,]+)"
            pattern = r"(?!-)([£€$CAD])([\d,]+) (?:-|to) ([£€$CAD])([\d,]+)"
            matches1 = re.findall(pattern, job["description"])
            if len(matches1) > 0:
                salary_min = re.sub(r"[,()\-]", "", matches1[0][0])
                salary_max = re.sub(r"[,()\-]", "", matches1[0][1])
                if salary_min is not None and salary_max is not None and not all(char in "$£€CAD" for char in salary_min) and not all(char in "$£€CAD" for char in salary_max):
                    job["salary"] = "{}-{}".format(salary_min, salary_max)
                elif all(char in "$£€CAD" for char in salary_min):
                    job["salary"] = "{} {}".format(salary_min, salary_max)
                elif all(char in "$£€CAD" for char in salary_max):
                    job["salary"] = job["salary"] = "{} {}".format(salary_min, salary_max)
                else:
                    job["salary"] = None
            else:
                job["salary"] = None

            if len(job_list) > 0:
                new_jobs = []
                for job in job_list:
                    if not any(df["link"].isin([job["link"]])):
                        if process_job_description(job):
                            job_type_keywords = ["permanent", "full-time", "fulltime", "full time", "contract", "permanent"]
                            if job["job_type"] and any(keyword in job["job_type"].lower() for keyword in job_type_keywords):
                                new_jobs.append(job)

                data_cleaning(new_jobs)
                print(
                    "Uploaded Jobs Successfully for " + search_term + " in " + location
                )
