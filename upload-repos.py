import argparse
import github
import os
import subprocess

parser = argparse.ArgumentParser(description='Batch-upload git repos to the demoscene-source-archive org')
parser.add_argument('token', help='GitHub access token')
parser.add_argument('repos', help='Directory containing repos to upload')
args = parser.parse_args()

g = github.Github(args.token)
org = g.get_organization('demoscene-source-archive')

# name = 'test'
# description = 'foo'
# repo = org.create_repo(name, description, private=False, has_issues=False, has_wiki=False, has_downloads=False, has_projects=False)
# print(repo.clone_url)

cwd = os.getcwd()
try:
    for f in os.scandir(args.repos):
        if f.is_dir():
            print(f.path)
            os.chdir(f.path)
            name = f.name
            description = None
            with open('.git/description', 'r') as file:
                description = file.read()
            print('{0} : "{1}"'.format(f.name, description))
            repo = org.create_repo(f.name, description, private=False, has_issues=False, has_wiki=False, has_downloads=False, has_projects=False)
            print(repo.clone_url)
            subprocess.run(['git', 'remote', 'add', 'origin', repo.clone_url])
            subprocess.run(['git', 'push', '-u', 'origin', 'master'])
            os.chdir(cwd)
finally:
    os.chdir(cwd)


