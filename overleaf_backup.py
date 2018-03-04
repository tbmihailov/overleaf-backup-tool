import json

from clients.OverleafClient import OverleafClient
from storage.GitStorage import GitStorage
from utils.debug import enable_http_client_debug, is_debug

try:
    import urllib2 as urlreq  # Python 2.x
except:
    import urllib.request as urlreq  # Python 3.x

import os
import sys
import logging

if __name__ == "__main__":

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    if is_debug():
        logging.getLogger().setLevel(logging.DEBUG)
        enable_http_client_debug()  # log http requests

    # read input params
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

    # login
    overleaf_client = OverleafClient()
    overleaf_client.login_with_user_and_pass(username, password)

    projects_info_list = overleaf_client.get_projects(status="all")

    logging.info("Total projects:%s" % len(projects_info_list))

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    projects_json_file = os.path.join(backup_dir, "projects.json")

    projects_old_id_to_info = {}
    if os.path.isfile(projects_json_file):
        projects_info_list_old = json.load(open(projects_json_file, mode="r"))
        for item in projects_info_list_old:
            projects_old_id_to_info[item["id"]] = item


    # backup projects
    storage = GitStorage()
    logging.info("Backing up projects..")
    for i, proj in enumerate(projects_info_list):
        proj["url_git"] = "https://git.overleaf.com/%s" % proj["id"]
        proj_id = proj["id"]
        proj_git_url = proj["url_git"]

        proj_backup_path = os.path.join(backup_git_dir, proj_id)

        # check if needs backup
        backup = True
        if proj["id"] in projects_old_id_to_info\
                and (projects_old_id_to_info[proj["id"]]["updated_at"] >= proj["updated_at"])\
                and ("backup_up_to_date" in projects_old_id_to_info[proj["id"]] and projects_old_id_to_info[proj["id"]]["backup_up_to_date"]):
            proj["backup_up_to_date"] = True
            backup = False
        else:
            proj["backup_up_to_date"] = False

        if not backup:
            logging.info("{0}/{1} Project {2} with url {3} has not changes since last backup! Skip..."
                         .format(i + 1, len(projects_info_list), proj_id, proj_git_url, proj_backup_path))
            continue

        logging.info("{0}/{1} Backing up project {2} with url {3} to {4}"
                     .format(i+1, len(projects_info_list), proj_id, proj_git_url, proj_backup_path))

        try:
            storage.create_or_update(proj_git_url, proj_backup_path)
            logging.info("Backup successful!")
            proj["backup_up_to_date"] = True
        except Exception as ex:
            logging.exception("Something went wrong!")

    json.dump(projects_info_list, open(projects_json_file, "w"))
    logging.info("Info for {0} projects saved to {1}!".format(len(projects_info_list), projects_json_file))






