
## Install

Install linux requirements:

```bash
apt update && apt upgrade -y
apt install software-properties-common -y
add-apt-repository ppa:deadsnakes/ppa
apt update
apt install python3.12
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12 
apt install python3.12-venv
```

Check version:

```bash
pip3.12 -V
python3.12 --version
```

Change default version

```bash
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 2
sudo update-alternatives --config python3
```

Then, select 3.12 by default version

Install nodejs and nginx:

```bash
sudo apt install nodejs
sudo apt install npm
sudo apt-get -y install nginx
```

Check version:

```bash
node -v
```

Create directory:

```bash
mkdir swsu_ai_api
cd swsu_ai_api
```

Init venv:

```bash
python3 -m venv venv
```

Clone repo:

```bash
git clone https://github.com/fortrane/swsu-ai-lecture.git
mv swsu-ai-lecture/* ./
rm -Rfv swsu-ai-lecture/
```

Activate venv (not for now):

```bash
. venv/bin/activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

Add Auth token for Gigachat:

```bash
vim api_getter.py
Click "i"
Go to TOKEN_HERE, delete it
Press "Shift+Insert"
Press "Esc"
Write ":wq"
```

Install pm2:

```bash
sudo npm install -g pm2
```

Start gunicorn:
```bash
pm2 start "gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app" --name swsu_ai_api
```

Make cUrl request:
```bash
curl localhost:8000
```

We can see:
_"{"detail":"Not Found"}"_

Ouuu, yeah 😎

So, next, nginx configuration:

```bash
cd /etc/nginx/conf.d/
nano default.conf
```

Paste config:

```bash
server {
       listen 80;

       server_name IP_ADDRESS_HERE example.com;

       location / {
         proxy_pass http://localhost:8000;
       }
}
```

Replace "IP_ADDRESS_HERE", exit and save.

Restart nginx service:

```bash
sudo service nginx restart
```

**Go to your ip and, ohhh, god bless, all working!!**
