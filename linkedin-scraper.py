import time
import cProfile
import pstats
import requests
import pandas as pd
from bs4 import BeautifulSoup

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}
counter = 0
"""
Original URL: 
    https://www.linkedin.com/jobs/search/?currentJobId=2906215008&f_JT=I&geoId=103644278&keywords=software%20engineer&location=United%20States&refresh=true    
    @7566 results

Request URL:
    https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=software%20engineer&location=United%20States&geoId=103644278&currentJobId=3485534331
"""
def options():
    # TODO: remove hardcoding, allowing user option
    keywords = "keywords=software%20engineer"
    location = "&location=United%20States"
    geo_id = "&geoID=103644278"
    job_id = "&currentJobID=3485534331"
    job_type = "&f_JT=I"    # internship
    opt = [keywords, location, geo_id, job_id, job_type]
    return opt


def grab_text(url, pg, print_debug):
    if print_debug:
        if not counter % 5:
            print(f"The URL is: {url.format(pg)}")
    resp = requests.get(url.format(pg), headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    return soup


def main():
    all_ID, all_job_info, curr_job_info = [], [], {}
    # https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?software%20engineer&United%20States&103644278&3485534331&f_JT=Istart={}
    target_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
    chosen_options = options()
    for filter in chosen_options:
        target_url += filter
    target_url += "&start={}"

    # TODO: fix rate limit, use something like scrapingdog
    page_num = 0
    while True:
        curr_page_jobs = grab_text(target_url, page_num, True).find_all("li")
        if not curr_page_jobs:
            break
        for x in range(len(curr_page_jobs)):
            job_id = curr_page_jobs[x].find("div", {"class":"base-card"})
            if job_id:
                id = job_id.get("data-entity-urn").split(":")[-1]
                all_ID.append(id)
        time.sleep(1)
        page_num += 1

    target_url = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}"
    all_ID = list(set(all_ID))

    for j in range(len(all_ID)):
        soup = grab_text(target_url, all_ID[j], False)
        link, location, company, title, level = None, None, None, None, None
        curr_job_info = {}
        try:
            link = soup.find("div", {"class":"top-card-layout__entity-info"}).find("a").get("href")
        except:
            pass
        try:
            location = soup.find("span", {"class":"topcard__flavor--bullet"}).contents[0].strip("\n").strip()
        except:
            pass
        try:
            company = soup.find("div", {"class":"top-card-layout__card"}).find("a").find("img").get('alt')
        except:
            pass
        try:
            title = soup.find("div", {"class":"top-card-layout__entity-info"}).find("a").text.strip()
        except:
            pass
        try:
            level = soup.find("ul", {"class":"description__job-criteria-list"}).find("li").text.replace("Seniority level", "").strip()
        except:
            pass
        if not link and not location and not company and not title and not level:
            continue
        curr_job_info = {"link":link, "location":location, "company":company, "job-title":title, "level":level}
        all_job_info.append(curr_job_info)

    df = pd.DataFrame(all_job_info)
    df.to_csv('linkedin-jobs.csv', index=False, encoding='utf-8')
    return


if __name__ == "__main__":
    cProfile.run('main()','linkedin-scraper-profile')
    p = pstats.Stats('linkedin-scraper-profile')
    p.strip_dirs().sort_stats('time').print_stats(0)

    # main()