import requests
import pandas as pd
from bs4 import BeautifulSoup

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}

def filter_jobs(states):
    drop_rows = []
    remote_rows = []
    remote_status = []
    status = ""
    df = pd.read_csv('linkedin-jobs.csv', sep=',')
    df.reset_index()
    for row in df.itertuples():
        location = row.location.split()
        title = row._4.split()
        if not(location[-1] not in states or (len(location) == 2 and location[0] == "United" and location[1] == "States") or title in ["Remote", "remote"]):
            drop_rows.append(row.Index)
        else:
            resp = requests.get(row.link, headers=headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            try:
                description = soup.find("script", {"type":"application/ld+json"}).contents[0].strip("\n").strip()
            except:
                continue
            if "remote" in description or "Remote" in description:
                if "hybrid" in description or "Hybrid" in description:
                    status = "Not fully remote"
                else:
                    if "office" in description or "Office" in description:
                        status = "Potentially not remote"
                    else:
                        status = "Remote"
                remote_rows.append(row.Index)
                remote_status.append(status)
    # new_df = df.copy().iloc[remote_rows, :] 
    # new_df.loc[:, ["remote"]] = remote_status
    # new_df.to_csv("remote-linkedin-jobs.csv", index=False, encoding='utf-8')

    # df_copy = df.copy()
    # for i in range(len(drop_rows) - 1, -1, -1):
    #     df_copy = df_copy.drop(drop_rows[i], axis=0, inplace=False)
    # df_copy.to_csv('linkedin-filtered-jobs.csv', index=False, encoding='utf-8')
    return

if __name__ == "__main__":
    states = ["United States"]
    filter_jobs(states)