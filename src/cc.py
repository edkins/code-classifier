import subprocess
import sys

def main():
    if sys.argv[1:] == ['install']:
        subprocess.run(['python3','-m','pip','install','-r','requirements.txt'])
    else:
        raise Exception('Unrecognized subcommand')

if __name__ == '__main__':
    main()
