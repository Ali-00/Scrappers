import pandas as pd
import uuid
import psycopg2
import numpy as np
from all_functions import *


def data_cleaning(data):
    df = pd.DataFrame(data)
    if "job_posted" not in df.columns:
        return
    df.replace("", np.nan, inplace=True)
    df.replace(np.nan, None, inplace=True)
    df.dropna(subset=["job_posted"], inplace=True)
    df.dropna(subset=["country"], inplace=True)

    df = df.fillna(np.nan).replace([np.nan], [None])

    df["id"] = [uuid.uuid4() for _ in range(len(df))]
    df["id"] = df["id"].astype(str)

    # List of remote-related keywords
    remote_keywords = [
        "remote work",
        "work from home",
        "telecommute",
        "virtual",
        "distributed team",
        "remote position",
    ]

    # Check if description contains remote keywords
    df["is_remote_job"] = df["description"].apply(
        lambda x: any(keyword in x.lower() for keyword in remote_keywords)
    )

    # List of IR35-related keywords
    ir35_keywords = ["ir35", "inside ir35", "outside ir35"]

    # Check if description mentions IR35 status
    df["ir_35_status"] = df["description"].apply(
        lambda x: any(keyword in x.lower() for keyword in ir35_keywords)
    )
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

    print(df.head())

    # df.to_csv("jobs.csv",index=False)
    conn = psycopg2.connect(
        user="muhammad_mutahhar",
        password="abc@123",
        host="127.0.0.1",
        port="5433",
        database="jobs_dashboard_db",
    )
    cursor = conn.cursor()
    query_post = "INSERT INTO core_job (id, company_name, title, description, platform, job_posted, salary, link, created_at, updated_at, job_type, ir_35_status, is_remote_job, city, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;"
    values_posts = [
        (
            row["id"],
            row["company_name"],
            row["title"],
            row["description"],
            row["platform"],
            row["job_posted"],
            row["salary"],
            row["link"],
            row["created_at"],
            row["updated_at"],
            row["job_type"],
            row["ir_35_status"],
            row["is_remote_job"],
            row["city"],
            row["country"],
        )
        for _, row in df.iterrows()
    ]

    cursor.executemany(query_post, values_posts)
    conn.commit()
    conn.close()


def get_all_jobs_from_df():
    url = "https://jobs-dashboard-backend-dot-work-projects-389011.uc.r.appspot.com/core/show_data?platform=Monster"
    resp = web_scrape(url, format="json")
    return pd.DataFrame(resp)
