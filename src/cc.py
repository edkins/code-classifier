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

def subcommand_required(args):
    raise Exception('Subcommand required')

def main():
    try:
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

        args = parser.parse_args()
        args.func(args)
    except KeyboardInterrupt as e:
        print('aagagh')
        sys.stdout.flush()
        raise e

if __name__ == '__main__':
    main()
