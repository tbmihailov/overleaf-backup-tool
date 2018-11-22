import os
import git
import sys
import logging
import time
from git import Repo

RETRY = 5

class GitStorage():
    def create_or_update(self, git_url, repo_dir):
        for i in range(1, RETRY + 1):
            try:
                if os.path.isdir(repo_dir):
                     # pull
                     g = git.cmd.Git(repo_dir)
                     g.pull()
                else:
                     # clone
                     Repo.clone_from(git_url, repo_dir)
            except git.GitCommandError as ex:
                logging.info("error:{0}: retry:{1}/{2}".format(ex, i, RETRY))
                time.sleep(10 * i)
                logging.info("retrying")
            else:
                return True
        logging.exception("max retry count reached")
        raise


if __name__ == "__main__":
    storage = GitStorage()

    git_url = sys.argv[1]
    repo_dir = sys.argv[2]

    storage.create_or_update(git_url, repo_dir)

    assert(os.path.exists(repo_dir))
