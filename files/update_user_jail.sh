#!/bin/bash
if [ -z "$1" ]; then
  echo "Error: Argument 1 is missing." >&2 # Send error to stderr
  exit 1 # Exit with a non-zero status code to indicate failure
fi

PAM_USER=$1

# Create user
/usr/sbin/useradd ${PAM_USER} -g sharelatex -k /etc/skel -m -d /downloads/${PAM_USER}
chown -R ${PAM_USER}:sharelatex /downloads/${PAM_USER}
chmod -R 0755 /downloads/${PAM_USER}

cp -rfa /master_jail/* /downloads/${PAM_USER}
chown -R ${PAM_USER}:sharelatex /downloads/${PAM_USER}
chmod 0755 /downloads/${PAM_USER}
cat /etc/passwd | grep ${PAM_USER} > /downloads/${PAM_USER}/etc/passwd

# Make devs for the jail
mkdir -p /downloads/${PAM_USER}/dev
mknod -m 666 /downloads/${PAM_USER}/dev/null c 1 3
mknod -m 666 /downloads/${PAM_USER}/dev/zero c 1 5
mknod -m 666 /downloads/${PAM_USER}/dev/random c 1 8
mknod -m 666 /downloads/${PAM_USER}/dev/urandom c 1 9
mknod -m 666 /downloads/${PAM_USER}/dev/tty c 5 0

# Make new ssh key
mkdir -p /downloads/${PAM_USER}/.ssh
chmod 700 /downloads/${PAM_USER}/.ssh
ssh-keygen -t ed25519 -f /downloads/${PAM_USER}/.ssh/sharelatex -N ""
cat /downloads/${PAM_USER}/.ssh/sharelatex.pub > /downloads/${PAM_USER}/.ssh/authorized_keys 
chmod 600 /downloads/${PAM_USER}/.ssh/sharelatex 
chmod 700 /downloads/${PAM_USER}/.ssh 
chmod 600 /downloads/${PAM_USER}/.ssh/authorized_keys 
chown -R ${PAM_USER}:sharelatex /downloads/${PAM_USER}/.ssh 

chmod 777 /downloads/${PAM_USER} 
sudo -u ${PAM_USER} /usr/bin/git config --global user.email ${PAM_USER} 
sudo -u ${PAM_USER} /usr/bin/git config --global user.name ${PAM_USER} 

mkdir -p /downloads/${PAM_USER}/sshkey.git 
cp /downloads/${PAM_USER}/.ssh/sharelatex.pub /downloads/${PAM_USER}/sshkey.git 
cp /downloads/${PAM_USER}/.ssh/sharelatex /downloads/${PAM_USER}/sshkey.git 
chown -R ${PAM_USER}:sharelatex /downloads/${PAM_USER}/sshkey.git

cd /downloads/${PAM_USER}/sshkey.git && sudo -u ${PAM_USER} /usr/bin/git init -q 
cd /downloads/${PAM_USER}/sshkey.git && sudo -u ${PAM_USER} /usr/bin/git add --all 
cd /downloads/${PAM_USER}/sshkey.git && sudo -u ${PAM_USER} /usr/bin/git commit -m 'by sharelatex' 
chown -R ${PAM_USER}:sharelatex /downloads/${PAM_USER}/sshkey.git 
chmod -R 0755 /downloads/${PAM_USER}/sshkey.git 

mkdir -p /downloads/${PAM_USER}/projects.git 
echo "" > /downloads/${PAM_USER}/projects.git/projects.txt
chown -R ${PAM_USER}:sharelatex /downloads/${PAM_USER}/projects.git

cd /downloads/${PAM_USER}/projects.git && sudo -u ${PAM_USER} /usr/bin/git init -q 
cd /downloads/${PAM_USER}/projects.git && sudo -u ${PAM_USER} /usr/bin/git add --all 
cd /downloads/${PAM_USER}/projects.git && sudo -u ${PAM_USER} /usr/bin/git commit -m 'by sharelatex' 
chown -R ${PAM_USER}:sharelatex /downloads/${PAM_USER}/projects.git 
chmod -R 0755 /downloads/${PAM_USER}/projects.git 


chmod 755 /downloads/${PAM_USER} 

