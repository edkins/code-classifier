from datetime import datetime, timedelta, timezone
from time import sleep
import re
import requests
from cc_credentials import get_github_credentials

re_owner = re.compile(r'[-_a-zA-Z]+')
re_repo = re.compile(r'[-_a-zA-Z]+')

def _before_request(con):
    cur = con.cursor()
    rph = None
    fetch_date = None
    remaining = None
    host = 'github'
    for row in cur.execute("SELECT requests_per_hour, fetch_date, requests_remaining FROM host WHERE host=?", (host,)):
        rph, fetch_date, remaining = row
    if rph == None:
        rph = 5000
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

        wait_time = (datetime.fromisoformat(fetch_date) + timedelta(hours=delay_hours)) - datetime.now(timezone.utc)
        wait_seconds = max(0, wait_time.total_seconds())

    if wait_seconds > 0:
        print(f"Delay {wait_seconds} seconds")
        sleep(wait_seconds)

    return get_github_credentials()


def _after_request(con, requests_remaining):
    fetch_date = datetime.now(timezone.utc).isoformat()
    cur = con.cursor()
    cur.execute("UPDATE host SET fetch_date = ?, requests_remaining = ?", (fetch_date, requests_remaining))
    con.commit()

def github_get_repo(con, owner, repo):
    username, access_token = _before_request(con)
    if not re_owner.match(owner):
        raise Exception(f"Invalid owner string {owner}")
    if not re_repo.match(repo):
        raise Exception(f"Invalid repo string {repo}")
    url = f'https://api.github.com/repos/{owner}/{repo}'
    headers = {'accept':'application/vnd.github.v3+json'}
    response = requests.get(url, auth=(username, access_token), headers=headers)
    requests_remaining = response.headers['x-ratelimit-remaining']
    print(f"{requests_remaining}/{response.headers['x-ratelimit-limit']} requests remaining. Status code = {response.status_code}")
    _after_request(con, requests_remaining)
    response.raise_for_status()
    return response.json()
