#!/bin/bash
##################################
#   Author = Audrey_Blanney	 #
##################################

# ps -ef | grep httpparse_main.py | grep -v grep | cut -c 9-15 | xargs kill -9

PID=`ps -ef | grep httpparse_main.py | grep -v grep | cut -c 9-15`
DATE=`date`

ps -ef | grep httpparse_main.py | grep -v grep
if [[ $? = '0' ]]; then
	kill -9 $PID
	cd /home/audrey/httpparse/
	python httpparse_main.py
	echo "$DATE Httpparse Restart Success!" >> /home/audrey/logs/httpparse/normal.logs
	exit 0
else
	echo "$DATE Httpparse Start Failed!" >> /home/audrey/logs/httpparse/error.logs
fi
