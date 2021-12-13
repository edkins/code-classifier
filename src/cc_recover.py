import boto3
import os
import re
import shutil
import subprocess

re_s3 = re.compile(r'^s3:\/\/([-.a-z]+)\/(.+)$')

def recover_repo(s3_bucket, s3_url, tempdir, keep_git):
    m = re_s3.match(s3_url)
    if m == None:
        raise Exception(f"Could not parse s3 url {s3_url}")
    elif m.group(1) != s3_bucket:
        raise Exception("Wrong s3 bucket")
    s3_key = m.group(2)
    s3 = boto3.client('s3')
    print(f"Downloading from {s3_url}")
    s3.download_file(s3_bucket, s3_key, f'{tempdir}/tmp.tar.gz')
    print("Untarring")
    subprocess.run(['tar','zxf','tmp.tar.gz'], cwd=tempdir)
    print("Removing tar file")
    os.remove(f'{tempdir}/tmp.tar.gz')
    print("Checking out HEAD")
    subprocess.run(['git','checkout','HEAD'], cwd=tempdir)
    if not keep_git:
        print("Removing .git dir")
        shutil.rmtree(f'{tempdir}/.git')
