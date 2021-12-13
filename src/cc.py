import argparse
import os
import sqlite3
import subprocess
import sys

db_name = '.code-classifier/sqlite.db'

def init(args):
    os.makedirs('.code-classifier', exist_ok=True)
    subprocess.run(['sudo','apt-get','install','-y','curl','python3-pip'])
    subprocess.run(['curl','-LO','https://github.com/jgm/pandoc/releases/download/2.16.2/pandoc-2.16.2-1-arm64.deb'])
    subprocess.run(['sudo','dpkg','-i','pandoc-2.16.2-1-arm64.deb'])
    subprocess.run(['python3','-m','pip','install','-r','requirements.txt'])

def db_migrate(args):
    subprocess.run(['./.local/bin/alembic', 'upgrade', 'head'])

def listing_ls(args):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    count = 0
    print('Listings:')
    for row in cur.execute("select name,url from listing order by name asc"):
        name, url = row
        print(f'   {name:20} {url}')
        count += 1
    print(f'{count} results.')
    con.close()

def listing_add(args):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute("insert into listing(name,url) values (?,?)", (args.name, args.url))
    con.commit()
    con.close()
    print(f'1 listing added')
    pass

def listing_rm(args):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    rowcount = cur.execute("delete from listing where name=?", (args.name,)).rowcount
    print(f'{rowcount} listing(s) removed')
    con.commit()
    con.close()

def listing_scrape(args):
    from cc_scrape import scrape_listing_url
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    listing_id = None
    url = None
    for row in cur.execute("select id,url from listing where name=?", (args.name,)):
        listing_id, url = row
    if listing_id == None or url == None:
        raise Exception('No such listing')
    names_and_urls = scrape_listing_url(url)
    id_name_urls = [(listing_id,name,url) for name,url in names_and_urls]
    print(f'Inserting {len(id_name_urls)} items')
    cur.execute("delete from listing_elem where listing_id=?", (listing_id,))
    cur.executemany("insert into listing_elem(listing_id,name,url) values (?,?,?)", id_name_urls)
    con.commit()
    con.close()

def listing_fetch(args):
    from cc_project import get_project_host, fetch_project
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    listing_id = None
    for row in cur.execute("select id from listing where name=?", (args.name,)):
        listing_id, = row
    if listing_id == None:
        raise Exception('No such listing')

    seen = 0
    fetched = 0
    for row in cur.execute("SELECT url FROM listing_elem WHERE listing_id = ?", (listing_id,)):
        code_url, = row
        host = get_project_host(code_url)
        seen += 1
        if host == None:
            print(f'Skipping: No code host known for {code_url}')
        else:
            fetch_project(con, host, code_url, False)
            fetched += 1
    print(f'{seen} seen. {fetched} fetched. {seen-fetched} skipped.')

def listing_get(args):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    listing_id = None
    url = None
    for row in cur.execute("select id,url from listing where name=?", (args.name,)):
        listing_id, url = row
    if listing_id == None or url == None:
        raise Exception('No such listing')
    print(f'id = {listing_id}')
    print(f'name = {args.name}')
    print(f'url = {url}')
    print('Listing:')
    count = 0
    for row in cur.execute("select name,url from listing_elem where listing_id=? order by name asc", (listing_id,)):
        name,url = row
        print(f'    {name:30} {url}')
        count ++ 1
    print(f'{count} results.')
    con.close()

def project_ls(args):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    count = 0
    if args.priority:
        for row in cur.execute("""
SELECT name, update_date, size, code_url
FROM project
WHERE
    metadata_status = 200
    AND public = true
    AND is_fork = false
    AND fetch_date is null
ORDER BY update_date DESC, size ASC"""):
            name, update_date, size, code_url = row
            print(f'{str(name):20} {str(update_date):25} {size:15} {code_url}')
            count += 1
    else:
        for row in cur.execute("SELECT name, metadata_status, metadata_date, fetch_date, code_url FROM project ORDER BY name ASC, code_url ASC"):
            name, metadata_status, metadata_date, fetch_date, code_url = row
            print(f'{str(name):20} {str(metadata_status):4} {str(metadata_date):25} {str(fetch_date):25} {code_url}')
            count += 1
    print(f'{count} results.')

def project_fetch(args):
    from cc_project import get_project_host, fetch_project
    code_url = args.url
    host = get_project_host(code_url)
    if host == None:
        raise Exception(f"Cannot identify code host for url {code_url}")
    con = sqlite3.connect(db_name)
    fetch_project(con, host, code_url, refetch=True)
    con.close()

def project_clone(args):
    from cc_project import clone_project
    project_id = None
    host = None
    git_https_url = None
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    for row in cur.execute("SELECT id, host, git_https FROM project WHERE name = ?", (args.name,)):
        if project_id != None:
            raise Exception(f"Multiple projects with name {name}")
        project_id, host, git_https_url = row
    if project_id == None or host == None or git_https_url == None:
        raise Exception(f"Could not find info on project {name}")
    date, sha, location = clone_project(con, project_id, host, git_https_url)
    cur.execute("""
UPDATE project
SET fetch_date = ?,
    fetch_sha = ?,
    fetch_location = ?
WHERE id = ?
""", (date, sha, location, project_id))
    con.commit()
    con.close()

def subcommand_required(args):
    raise Exception('Subcommand required')

def credentials(args):
    from cc_credentials import enter_credentials
    enter_credentials()

def main():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=subcommand_required)
    subparsers = parser.add_subparsers()

    parser_init = subparsers.add_parser('init')
    parser_init.set_defaults(func=init)

    parser_db = subparsers.add_parser('db')
    subparsers_db = parser_db.add_subparsers()
    parser_db_migrate = subparsers_db.add_parser('migrate')
    parser_db_migrate.set_defaults(func=db_migrate)

    parser_listing = subparsers.add_parser('listing')
    subparsers_listing = parser_listing.add_subparsers()
    parser_listing_ls = subparsers_listing.add_parser('ls')
    parser_listing_ls.set_defaults(func=listing_ls)
    parser_listing_add = subparsers_listing.add_parser('add')
    parser_listing_add.set_defaults(func=listing_add)
    parser_listing_add.add_argument('--name', '-n', required=True)
    parser_listing_add.add_argument('--url', required=True)
    parser_listing_rm = subparsers_listing.add_parser('rm')
    parser_listing_rm.set_defaults(func=listing_rm)
    parser_listing_rm.add_argument('--name', '-n', required=True)
    parser_listing_scrape = subparsers_listing.add_parser('scrape')
    parser_listing_scrape.set_defaults(func=listing_scrape)
    parser_listing_scrape.add_argument('--name', '-n', required=True)
    parser_listing_get = subparsers_listing.add_parser('get')
    parser_listing_get.set_defaults(func=listing_get)
    parser_listing_get.add_argument('--name', '-n', required=True)
    parser_listing_fetch = subparsers_listing.add_parser('fetch')
    parser_listing_fetch.set_defaults(func=listing_fetch)
    parser_listing_fetch.add_argument('--name', '-n', required=True)

    parser_project = subparsers.add_parser('project')
    subparsers_project = parser_project.add_subparsers()
    parser_project_ls = subparsers_project.add_parser('ls')
    parser_project_ls.set_defaults(func=project_ls)
    parser_project_ls.add_argument('--priority', action='store_true')
    parser_project_fetch = subparsers_project.add_parser('fetch')
    parser_project_fetch.set_defaults(func=project_fetch)
    parser_project_fetch.add_argument('--url', required=True)
    parser_project_clone = subparsers_project.add_parser('clone')
    parser_project_clone.set_defaults(func=project_clone)
    parser_project_clone.add_argument('--name','-n', required=True)

    parser_credentials = subparsers.add_parser('credentials')
    parser_credentials.set_defaults(func=credentials)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
