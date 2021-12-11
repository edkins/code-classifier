import argparse
import os
import sqlite3
import subprocess
import sys

db_name = '.code-classifier/sqlite.db'

def init(args):
    os.makedirs('.code-classifier', exist_ok=True)
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

def main():
    parser = argparse.ArgumentParser()
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
    parser_listing_add.add_argument('--name', required=True)
    parser_listing_add.add_argument('--url', required=True)
    parser_listing_rm = subparsers_listing.add_parser('rm')
    parser_listing_rm.set_defaults(func=listing_rm)
    parser_listing_rm.add_argument('--name', required=True)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
