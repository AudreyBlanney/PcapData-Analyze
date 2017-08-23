#! /usr/bin/bash
/usr/share/tomcat/bin/startup.sh
cd /root/assets
gunicorn -k gevent -t 6000 -b 0.0.0.0:5000 run:app &
