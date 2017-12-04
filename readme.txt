pour faire release
Se mettre dans le directory (uat, hc ou cam)
git clone https://github.com/mmggbe/hc.git
adapter manuellement  le : hc@Horus:~/uat/hc/climax_web$ nano Hcsettings.py

updater :
class HcDB:
    __conf = {
        "host" :"localhost",
        "database" : "hcdbuat",
        "user" : "hcuat",
        "password": "hcdb1"
    }

Adapter le fichier settings.py avec les params de la DB
(uat) hc@Horus:~/uat/hc/climax_web/climax_web$ nano settings.py 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hcdbuat',
        'USER': 'hcuat',
        'PASSWORD' : 'hcdb1',
        'HOST' : 'localhost',
        'PORT' : '',  
    }
}

Create the DB
sudo mysql -u root -p
[sudo]HCMGGDV2
HCMGGDV1

CREATE DATABASE hcdbuat CHARACTER SET UTF8;
CREATE USER hcuat@localhost IDENTIFIED BY 'hcdb1';

GRANT ALL PRIVILEGES ON hcdbuat .* TO hcuat@localhost;

FLUSH PRIVILEGES;

exit;

create Django DB
python3 manage.py makemigrations
python3 manage.py migrate

Django super user
./manage.py createsuperuser
email = mage.gerin@gmail.com
Username (leave blank to use 'hc'): hc
password : hcdb1

changer le root dans 

server {
    listen 80;
    server_name uat.horus.ovh;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/hc/uat/hc/climax_web;
    }

    location / {
        include         uwsgi_params;
        uwsgi_pass      unix:/run/uwsgi/uat.sock;
    }
}
