from datetime import datetime, timezone
import re

re_github = re.compile(r'^https:\/\/github.com\/([-_a-zA-Z]+)\/([-_a-zA-Z]+)$')

def now_as_string():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def get_project_host(code_url):
    if re_github.match(code_url):
        return 'github'
    else:
        return None

def fetch_project(con, host, code_url, refetch):
    project_id = create_or_get_project_id(con, code_url, refetch)
    if project_id == None:
        pass
    elif host == 'github':
        m = re_github.match(code_url)
        if m == None:
            raise Exception('url does not match github')
        owner = m.group(1)
        repo = m.group(2)
        fetch_project_github(con, project_id, code_url, owner, repo)
    else:
        raise Exception(f'Unknown code host {host}')

def create_or_get_project_id(con, code_url, refetch):
    cur = con.cursor()
    project_id = None
    metadata_date = None
    for row in cur.execute("SELECT id, metadata_date FROM project WHERE code_url = ?", (code_url,)):
        project_id,metadata_date = row
    if project_id == None:
        cur.execute("INSERT INTO project(code_url) VALUES (?)", (code_url,))
        for row in cur.execute("SELECT id FROM project WHERE code_url = ?", (code_url,)):
            project_id, = row
        if project_id == None:
            raise Exception("Don't know why insert didn't work")
        print(f"Created project with id={project_id}, code_url={code_url}")
        con.commit()
    elif metadata_date != None and not refetch:
        print(f'Skipping: already have metadata for {code_url}')
        return None
    return project_id

def fetch_project_github(con, project_id, code_url, owner, repo):
    from cc_github import github_get_repo
    response, status_code = github_get_repo(con, owner, repo)

    cur = con.cursor()
    rowcount = cur.execute("""
UPDATE project
SET
    host = ?,
    name = ?,
    project_url = ?,
    doc_url = ?,
    public = ?,
    is_fork = ?,
    git_ssh = ?,
    git_https = ?,
    language = ?,
    size = ?,
    forks_count = ?,
    stars_count = ?,
    main_branch = ?,
    create_date = ?,
    update_date = ?,
    metadata_date = ?,
    metadata_status = ?
WHERE
    id = ?
    AND code_url = ?
""", 
        (
            'github',
            response.get('name'),
            None if response.get('homepage') == code_url else response.get('homepage'),
            None,
            not response.get('private',True),
            response.get('fork'),
            response.get('git_url'),
            code_url if status_code == 200 else None,
            response.get('language'),
            response.get('size'),
            response.get('forks_count'),
            response.get('stargazers_count'),
            response.get('default_branch'),
            response.get('created_at'),
            response.get('pushed_at'),
            now_as_string(),
            status_code,

            project_id,
            code_url
        )
    ).rowcount
    print(f'{rowcount} project metadata updated')
    con.commit()

def clone_project(con, project_id, host, git_https_url):
    from cc_credentials import get_s3_bucket
    from cc_github import github_clone_repo
    date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    s3_bucket = get_s3_bucket()
    if host == 'github':
        m = re_github.match(git_https_url)
        if m == None:
            raise Exception("Could not recognize github url {git_https_url}")
        owner = m.group(1)
        repo = m.group(2)
        s3_key = f'repos/{date}.github.{owner}.{repo}.tar.gz'
        sha = github_clone_repo(con, git_https_url, s3_bucket, s3_key)
    date = now_as_string()
    return date, sha, f's3://{s3_bucket}/{s3_key}'
