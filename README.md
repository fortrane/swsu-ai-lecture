
## Install

Requirements:
* Ubuntu 20.04 or 22.04

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
. source venv/bin/activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

Add URL and Auth token for Gigachat in .env:

```bash
ENV_GIGACHAT_URL = https://ngw.devices.sberbank.ru:9443/api/v2/oauth
ENV_GIGACHAT_TOKEN = ZDlmNDAxYmYtZ.......hlMQ==
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

Start project manually:

```bash
hypercorn main:app --bind 0.0.0.0:8000
```

**Go to your ip and, ohhh, god bless, all working!!**
