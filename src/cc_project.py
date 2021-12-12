from datetime import datetime, timezone
import re

re_github = re.compile(r'https:\/\/github.com\/([-_a-zA-Z]+)\/([-_a-zA-Z]+)')

def now_as_string():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def get_project_host(code_url):
    if re_github.match(code_url):
        return 'github'
    else:
        return None

def fetch_project(con, host, code_url):
    project_id = create_or_get_project_id(con, code_url)

    if host == 'github':
        m = re_github.match(code_url)
        if m == None:
            raise Exception('url does not match github')
        owner = m.group(1)
        repo = m.group(2)
        fetch_project_github(con, project_id, code_url, owner, repo)
    else:
        raise Exception(f'Unknown code host {host}')

def create_or_get_project_id(con, code_url):
    cur = con.cursor()
    project_id = None
    for row in cur.execute("SELECT id FROM project WHERE code_url = ?", (code_url,)):
        project_id, = row
    if project_id == None:
        cur.execute("INSERT INTO project(code_url) VALUES (?)", (code_url,))
        for row in cur.execute("SELECT id FROM project WHERE code_url = ?", (code_url,)):
            project_id, = row
        if project_id == None:
            raise Exception("Don't know why insert didn't work")
        print(f"Created project with id={project_id}, code_url={code_url}")
        con.commit()
    return project_id

def fetch_project_github(con, project_id, code_url, owner, repo):
    from cc_github import github_get_repo
    response = github_get_repo(con, owner, repo)

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
    metadata_date = ?
WHERE
    id = ?
    AND code_url = ?
""", 
        (
            'github',
            response['name'],
            None if response['homepage'] == code_url else response['homepage'],
            None,
            not response['private'],
            response['fork'],
            response['git_url'],
            code_url,
            response['language'],
            response['size'],
            response['forks_count'],
            response['stargazers_count'],
            response['default_branch'],
            response['created_at'],
            response['pushed_at'],
            now_as_string(),

            project_id,
            code_url
        )
    ).rowcount
    print(f'{rowcount} project metadata updated')
    con.commit()
    return rowcount
