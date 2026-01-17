
import urllib.request
import json
import subprocess
from dataclasses import dataclass
import os
import argparse



# curl -L \
#   -H "Accept: application/vnd.github+json" \
#   -H "Authorization: Bearer <YOUR-TOKEN>" \
#   -H "X-GitHub-Api-Version: 2022-11-28" \
#   https://api.github.com/orgs/ORG/repos


@dataclass
class Repository:
    name: str
    git_url: str
    git_wiki_url: str|None
    

ROOT_REPO_NAME = "root"

# Set to True to only print commands without executing them
TEST = False


def get_repos(token : str):
    url = "https://api.github.com/orgs/modular-server-manager/repos"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    req = urllib.request.Request(url, headers=headers)
    repos : list[Repository] = []
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        for repo in data:
            if repo['archived'] or repo['name'] == ROOT_REPO_NAME:
                continue
            repository = Repository(
                name=repo['name'],
                git_url=repo['ssh_url'],
                git_wiki_url=repo['ssh_url'].replace('.git', '.wiki.git') if repo['has_wiki'] else None
            )
            repos.append(repository)
    return repos


def run(command: list[str]):
    if TEST:
        print("\033[30m"+" ".join(command)+"\033[0m")
        return
    subprocess.run(command)


def clone_repo(repo : Repository):    
    dest_folder = repo.name
    if os.path.exists(dest_folder):
        print(f"Folder {dest_folder} already exists, skipping clone.")
        return
    print(f"Cloning {repo.name}...")
    run(["git", "clone", repo.git_url])

def clone_repo_wiki(repo : Repository):
    if repo.git_wiki_url:
        dest_folder = f"{repo.name}.wiki"
        if os.path.exists(dest_folder):
            print(f"Folder {dest_folder} already exists, skipping wiki clone.")
            return
        print(f"Cloning wiki for {repo.name}...")
        run(["git", "clone", repo.git_wiki_url])
        
        
if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Clone all Modular Server Manager repositories.")
    argparser.add_argument('--test', action='store_true', help='Print commands without executing them.')
    argparser.add_argument('token', type=str, help='GitHub token for authentication.')
    args = argparser.parse_args()
    TEST = args.test
    
    repositories = get_repos(args.token)
    print(f"Found {len(repositories)} repositories.")
    for repo in repositories:
        clone_repo(repo)
        clone_repo_wiki(repo)
    print("Done.")
