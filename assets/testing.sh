#!/bin/bash

DATE=`date`

ps -ef |grep run.py | grep -v grep >/home/bai/assets/log/service.tmp
grep -i run.py /home/bai/assets/log/service.logs

if test -s /home/bai/assets/log/service.tmp; then
        echo "$DATE  It's working !!!!" >> /home/bai/assets/log/service.logs
        exit 0
else
        cd /home/bai/assets/
        python run.py &
        echo "$DATE Restart Success!!!" >> /home/bai/assets/log/service.logs
        exit 0
fi
