#!/bin/bash
set -e;

mkdir -p storage

sudo chgrp www-data storage \
                   .htpasswd \
                   nginx.conf

sudo chmod 770 storage
sudo chmod g+s storage

sudo chmod 640 .htpasswd nginx.conf

sudo ln -sf $PWD/nginx.conf /etc/nginx/sites-enabled/notes-app.conf

sudo nginx -t
sudo service nginx reload
