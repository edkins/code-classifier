from datetime import datetime
from getpass import getpass
import json
import os.path

credentials_filename = '.code-classifier/credentials.json'

def enter_credentials():
    if os.path.exists(credentials_filename):
        with open(credentials_filename) as f:
            credentials = json.load(f)
    else:
        credentials = {}

    github_username = input(f"Github username ({credentials.get('github_username')}): ")
    if github_username != '':
        credentials['github_username'] = github_username

    github_access_token = getpass(f"Github personal access token ({'***' if 'github_access_token' in credentials else None}): ")
    if github_access_token != '':
        credentials['github_access_token'] = github_access_token

    github_expiry = input(f"Github personal access token expiry date yyyy-mm-dd ({credentials.get('github_expiry')}): ")
    if github_expiry != '':
        datetime.strptime(github_expiry, '%Y-%m-%d')
        credentials['github_expiry'] = github_expiry

    with open(credentials_filename, 'w') as f:
        json.dump(credentials, f, indent=4)
        print(f"Written {credentials_filename}")

def get_github_credentials():
    with open(credentials_filename) as f:
        credentials = json.load(f)
        if datetime.strptime(credentials['github_expiry'], '%Y-%m-%d') <= datetime.now():
            raise Exception('github credentials have expired')
        return credentials['github_username'], credentials['github_access_token']
