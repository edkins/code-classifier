import os
import subprocess
import sys

def main():
    if sys.argv[1:] == ['init']:
        os.makedirs('.code-classifier', exist_ok=True)
        subprocess.run(['python3','-m','pip','install','-r','requirements.txt'])
    elif sys.argv[1:] == ['db','migrate']:
        subprocess.run(['./.local/bin/alembic', 'upgrade', 'head'])
    else:
        raise Exception('Unrecognized subcommand')

if __name__ == '__main__':
    main()
