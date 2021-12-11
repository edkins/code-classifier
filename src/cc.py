import argparse
import os
import subprocess
import sys

def init(args):
    os.makedirs('.code-classifier', exist_ok=True)
    subprocess.run(['python3','-m','pip','install','-r','requirements.txt'])

def db_migrate(args):
    subprocess.run(['./.local/bin/alembic', 'upgrade', 'head'])

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_init = subparsers.add_parser('init')
    parser_init.set_defaults(func=init)

    parser_db = subparsers.add_parser('db')
    subparsers_db = parser_db.add_subparsers()
    parser_db_migrate = subparsers_db.add_parser('migrate')
    parser_db_migrate.set_defaults(func=db_migrate)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
