import os
import git
import sys
from git import Repo


class GitStorage():
    def create_or_update(self, git_url, repo_dir):
        if os.path.isdir(repo_dir):
            # pull
            g = git.cmd.Git(repo_dir)
            g.pull()
        else:
            # clone
            Repo.clone_from(git_url, repo_dir)


if __name__ == "__main__":
    storage = GitStorage()

    git_url = sys.argv[1]
    repo_dir = sys.argv[2]

    storage.create_or_update(git_url, repo_dir)

    assert(os.path.exists(repo_dir))
