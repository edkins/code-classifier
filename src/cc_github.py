from datetime import datetime, timedelta, timezone
from time import sleep
from tempfile import TemporaryDirectory, NamedTemporaryFile
import re
import requests
import subprocess
from cc_credentials import get_github_credentials

re_owner = re.compile(r'^[-_a-zA-Z]+$')
re_repo = re.compile(r'^[-_a-zA-Z]+$')

def _before_request(con, host):
    cur = con.cursor()
    rph = None
    fetch_date = None
    remaining = None
    for row in cur.execute("SELECT requests_per_hour, fetch_date, requests_remaining FROM host WHERE host=?", (host,)):
        rph, fetch_date, remaining = row
    if rph == None:
        if host == 'github-rest':
            rph = 5000
        elif host == 'github-git':
            rph = 60
        else:
            raise Exception(f'Unexpected github host {host}')
        cur.execute("INSERT INTO host(host, requests_per_hour) VALUES (?,?)", (host,rph))
        con.commit()

    if fetch_date == None:
        # If we haven't fetched before, we don't need to wait
        wait_seconds = 0
    else:
        if remaining == None:
            # If we're not told how many requests we have remaining, space them out to rph requests every hour
            delay_hours = 1 / rph
        else:
            # How many requests do we have remaining this hour? Space them out evenly
            # 1 request - wait one hour
            # 2 requests - wait half an hour
            # 5000 requests - wait 1/5000 hour
            delay_hours = 1 / max(1, remaining)

        fetch_datetime = datetime.strptime(fetch_date, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo = timezone.utc)
        wait_time = (fetch_datetime + timedelta(hours=delay_hours)) - datetime.now(timezone.utc)
        wait_seconds = max(0, wait_time.total_seconds())

    if wait_seconds > 0:
        print(f"Delay {wait_seconds} seconds")
        sleep(wait_seconds)

    username, access_token = get_github_credentials()
    if remaining != None and remaining > 0:
        remaining -= 1
    return username, access_token, remaining


def _after_request(con, requests_remaining, host):
    fetch_date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    cur = con.cursor()
    cur.execute("UPDATE host SET fetch_date = ?, requests_remaining = ? WHERE host = ?", (fetch_date, requests_remaining, host))
    con.commit()

def github_get_repo(con, owner, repo):
    username, access_token, requests_remaining = _before_request(con, 'github-rest')
    try:
        if not re_owner.match(owner):
            raise Exception(f"Invalid owner string {owner}")
        if not re_repo.match(repo):
            raise Exception(f"Invalid repo string {repo}")
        url = f'https://api.github.com/repos/{owner}/{repo}'
        headers = {'accept':'application/vnd.github.v3+json'}
        response = requests.get(url, auth=(username, access_token), headers=headers)
        requests_remaining = response.headers['x-ratelimit-remaining']
        print(f"{requests_remaining}/{response.headers['x-ratelimit-limit']} requests remaining. Status code = {response.status_code}")
        if response.status_code == 200:
            return response.json(), response.status_code
        else:
            return {}, response.status_code
    finally:
        _after_request(con, requests_remaining, 'github-rest')

def github_clone_repo(con, git_https_url, s3_bucket, s3_key):
    import boto3
    username, access_token, requests_remaining = _before_request(con, 'github-git')
    try:
        subprocess.run(['git','config','--global','credential.https://github.com.username', username])
        subprocess.run(['git','config','--global','credential.https://github.com.password', access_token])
        with TemporaryDirectory() as tempdir:
            print(f"Cloning {git_https_url}")
            subprocess.run(['git','clone','--depth','1','--no-checkout','--',git_https_url,tempdir])
            sha = subprocess.run(['git','-C',tempdir,'show-ref','--hash','HEAD'], capture_output=True).stdout.decode('utf-8').strip()
            print(f"sha = {sha}")
            with NamedTemporaryFile(suffix='.tar.gz') as tarfile:
                print(f"Tarring {tarfile.name}")
                subprocess.run(['tar','--create','--file',tarfile.name,'--gzip','-C',tempdir,'.git'])
                print(f"Writing to s3://{s3_bucket}/{s3_key}")
                s3 = boto3.client('s3')
                s3.upload_file(tarfile.name, s3_bucket, s3_key)
                return sha
    finally:
        _after_request(con, None, 'github-git')
