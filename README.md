Setup
=====

AWS setup

- Create an S3 bucket
- Create an EC2 instance IAM role with read/write access to that bucket
- Create an EC2 keypair and download the pem
- Create a t4g.micro EC2 instance running Ubuntu with 20GB EBS
- Create an elastic IP address and attach it to the EC2 instance
- Attach the IAM role to the EC2 instance

SSH setup
- Create an entry in your `~/.ssh/config` as follows, substituting the IP address and PEM location:

```
Host cc
    HostName 1.2.3.4
    IdentityFile blah.pem
    User ubuntu
    IdentitiesOnly yes
```

EC2 instance setup
- `ssh cc`, accepting the prompt to add it to your known hosts
- Make sure the software on it is up to date:
  - `sudo apt update`
  - `sudo apt upgrade`
  - `sudo reboot`
- exit your ssh shell

Github setup
- Go to your settings and create a Personal Access Token, making a note of the token secret and the expiry date.

Code classifier setup
- `./cc init` on your local machine
  - you will be prompted for the name of the ssh profile. Enter `cc`
- `./cc db migrate`
- `./cc credentials`, entering the info you are prompted for

Import some data!
- `./cc listing add -n awesome-pipeline --url https://raw.githubusercontent.com/pditommaso/awesome-pipeline/master/README`
- `./cc listing scrape -n awesome-pipeline`
- `./cc listing fetch -n awesome-pipeline`

