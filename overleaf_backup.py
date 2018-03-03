import json

try:
    import urllib2 as urlreq  # Python 2.x
except:
    import urllib.request as urlreq  # Python 3.x

import os
import sys
import requests as reqs
import logging
import time
import random

if __name__ == "__main__":
    sleep_range_ms = [500, 1000]
    # https://stackoverflow.com/questions/10588644/how-can-i-see-the-entire-http-request-thats-being-sent-by-my-python-application
    # These two lines enable debugging at httplib level (requests->urllib3->http.client)
    # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # The only thing missing will be the response.body which is not logged.
    try:
        import http.client as http_client
    except ImportError:
        # Python 2
        import httplib as http_client
    http_client.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    backup_dir = ""
    backup_git_dir = "git_backup/"

    if len(sys.argv) > 1:
        backup_dir = sys.argv[1]
    if not backup_dir.endswith("/"):
        backup_dir = backup_dir + "/"

    backup_git_dir = os.path.join(backup_dir, backup_git_dir)

    if len(sys.argv) > 2:
        username = sys.argv[2]
    else:
        username = os.environ['overleaf_user']

    if len(sys.argv) > 3:
        password = sys.argv[3]
    else:
        password = os.environ['overleaf_pass']

    URL_OVERLEAF_SIGNIN = "https://www.overleaf.com/users/sign_in"

    get_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
    r = reqs.get(URL_OVERLEAF_SIGNIN, headers=get_headers)
    html_doc = r.text

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_doc, 'html.parser')

    # utf8:✓
    # authenticity_token: E + t5snaBKzoP3z5aoQIFI + +o5XiAUJLgzj / yelPaEO8CsldTSo3LcVMQ + Ay2HM7GeMrdI + 3
    # RAfOI + c9LLlNqUw ==
    # user[email]: test @ gmail.com
    # user[password]: test
    # user[remember_me]: 0

    login_json = {"utf8":u"\u2713",
                  "authenticity_token":"",
                  "user[email]": username,
                  "user[password]": password,
                  "user[remember_me]": 0,
                  }

    for tag in soup.find_all("meta"):
        if tag.get("name", None) == "csrf-token":
            login_json["authenticity_token"] = tag.get("content", None)

    # login and get cookies

    print(login_json)

    post_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    }

    r = reqs.post(URL_OVERLEAF_SIGNIN, data=login_json, timeout=5, headers=post_headers, cookies=r.cookies)
    print(r)
    #print(r.text)
    login_cookies = None
    if r.status_code == 200:
        for cookie in r.cookies:
            print(cookie)

        login_cookies = r.cookies

    # get projects
    get_projects_url = "https://www.overleaf.com/dash/"

    projects_info_list = []
    page_projects_req = reqs.get(get_projects_url, headers=get_headers, cookies=login_cookies)
    if page_projects_req.status_code != 200:
        logging.error("Something went wrong! : %s" % str(page_projects_req.status_code))

    page = 1

    while(True):
        params = params={"is": "active",
                         "per": 50,
                         }
        if page > 1:
            params["page"] = page

        proj_json_req = reqs.get("https://www.overleaf.com/api/v0/current_user/docs/",
                                 params,
                                 headers=get_headers,
                                 cookies=login_cookies)

        proj_json = json.loads(proj_json_req.text)
        res_curr_page = proj_json["paging"]["current_page"]
        res_total_pages = proj_json["paging"]["total_pages"]

        projects_info_list.extend(proj_json["docs"])

        if res_curr_page == res_total_pages:
            break
        page += 1
        time.sleep(float(random.randrange(sleep_range_ms[0], sleep_range_ms[1]))/1000.0)  # reducing the chance of being caught by a simple api server crawler security

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    logging.info("Total projects:%s" % len(projects_info_list))


    projects_json_file = os.path.join(backup_dir, "projects.json")
    projects_info_list_old = None
    if os.path.isfile(projects_json_file):
        projects_info_list_old = json.loads(open(projects_json_file, mode="r"))

    for proj in projects_info_list:
        proj["url_git"] = "https://git.overleaf.com/%s" % proj["id"]
        proj["url"] = "https://www.overleaf.com/%s" % proj["id"]
        proj["local_path_git"] = os.path.join(backup_dir, proj["id"])




    print(projects_info_list[0].keys())




