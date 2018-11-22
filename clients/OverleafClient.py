import json
import logging
import random

import time

import requests as reqs
import sys
from bs4 import BeautifulSoup

from utils.debug import is_debug, enable_http_client_debug

sleep_range_ms = [500, 1000]
def random_sleep():
    time.sleep(float(random.randrange(sleep_range_ms[0], sleep_range_ms[
        1])) / 1000.0)  # reducing the chance of being caught by a simple api server crawler security

OVERLEAF_PROJECTS_STATUS_TYPES = ["active", "starred", "archived", "trash"]

class OverleafClient(object):
    def __init__(self, ):

        self._url_signin = "https://www.overleaf.com/login"
        self._dashboard_url = "https://www.overleaf.com/dash/"

        self._login_cookies = None
        self._login_request_get = None
        self._login_request_post = None

    def get_projects(self, status="all"):
        if not status in OVERLEAF_PROJECTS_STATUS_TYPES+["all"]:
            raise ValueError("status {0} is not in allowed types list: {1}".format(status, ", ".join(OVERLEAF_PROJECTS_STATUS_TYPES)))

        if status == "all":
            status_list = ["active", "archived"]
        else:
            status_list = [status]

        login_cookies = self._login_cookies
        all_projects = []
        for st in status_list:
            status_projects = self.get_projects_by_status(st, login_cookies)
            all_projects.extend(status_projects)

        return all_projects



    def get_projects_by_status(self, status, login_cookies=None):
        """
        Gets the projects json by status
        :param status: Status type: active, archived, trash
        :param login_cookies: The cookie container. If None, it is retrieved from the current object
        :return: Projects list
        """

        if not status in OVERLEAF_PROJECTS_STATUS_TYPES:
            raise ValueError("status {0} is not in allowed types list: {1}".format(status, ", ".join(OVERLEAF_PROJECTS_STATUS_TYPES)))

        if login_cookies is None:
            login_cookies = self._login_cookies

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

        # try to load the dashboard page
        dashboard_url = self._dashboard_url
        page_projects_req = reqs.get(dashboard_url, headers=headers, cookies=login_cookies)
        if page_projects_req.status_code != 200:
            logging.error("Something went wrong! : %s" % str(page_projects_req.status_code))

        # load the projects via the json api
        projects_list = []

        page = 1
        while (True):
            params = {"is": status,
                      "per": 50,
                      }

            if page > 1:
                params["page"] = page

            proj_json_req = reqs.get("https://www.overleaf.com/api/v0/current_user/docs/",
                                     params,
                                     headers=headers,
                                     cookies=login_cookies)

            # parse json
            proj_json = json.loads(proj_json_req.text)
            projects_list.extend(proj_json["docs"])

            # check if this is the last page
            res_curr_page = proj_json["paging"]["current_page"]
            res_total_pages = proj_json["paging"]["total_pages"]
            if res_curr_page == res_total_pages:
                break

            page += 1

            random_sleep()

        return projects_list

    def login_with_user_and_pass(self, username, password):
        """
        Try to signin and sets the login cookie if successfull.
        :param username: Overleaf username (e-mail)
        :param password: Overleaf password
        :return:
        """

        is_successfull = False
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

        # get sign_in page html and get authenticity token - this is required to make the login request
        r_signing_get = reqs.get(self._url_signin, headers=headers)
        if r_signing_get.status_code != 200:
            err_msg = "Status code {0} when loading {1}. Can not continue...".format(r_signing_get.status_code, self._url_signin)

            raise Exception(err_msg)

        html_doc = r_signing_get.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        authenticity_token = ""
        for tag in soup.find_all("input"):
            if tag.get("name", None) == "_csrf":
                authenticity_token = tag.get("value", None)
                break

        if len(authenticity_token) == 0:
            err_msg = "authenticity_token is empty! Can not continue..."

            raise Exception(err_msg)

        # form login data object
        login_json = {"_csrf": authenticity_token,
                      "email": username,
                      "password": password,
                      }

        r_signing_post = reqs.post(self._url_signin, data=login_json, timeout=5, headers=headers, cookies=r_signing_get.cookies)

        if not r_signing_post.status_code == 200:
            err_msg = 'Status code {} when signing in {1} with user [{2}].'
            msg = err_msg.format(r_signing_post.status_code, self.url_signin, email)
            raise Exception(err_msg)

        try:
            response = json.loads(r_signing_post.text)
            if response['message']['type'] == 'error':
                msg = 'Login failed: {}'
                msg = msg.format(response['message']['text'])
                raise ValueError(msg)
        except json.JSONDecodeError:
            # This happens when the login is successful because a HTML document
            # is returned instead of some JSON.
            pass
        login_cookies = r_signing_post.cookies
        is_successfull = True

        self._login_request_get = r_signing_get
        self._login_request_post = r_signing_post
        self._login_cookies = login_cookies

        return is_successfull


if __name__ == "__main__":

    if is_debug():
        enable_http_client_debug()  # log http requests

    username = sys.argv[1]
    password = sys.argv[2]

    overleaf_client = OverleafClient()

    overleaf_client.login_with_user_and_pass(username, password)

    projects = overleaf_client.get_projects_by_status('active')
    projects_all = overleaf_client.get_projects('all')


    logging.info("Projects loaded:%s" % len(projects))

