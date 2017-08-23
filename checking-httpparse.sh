#!/bin/bash
#####################################
#                           		#
#						   			#
#      checking httpparse           #
# 									#
#	__Author__ = Audrey丶Blanney	#
#									#
#####################################

DATE=`date`

ps -ef | grep httpparse_main.py | grep -v grep > /home/audrey/logs/httpparse/checking.tmp
grep -i "httpparse_main.py" /home/audrey/logs/httpparse/checking.tmp
if [[ $? = '0' ]]; then
	echo "$DATE  It's working !!!!" >> /home/audrey/logs/httpparse/checking.logs
	exit 0
else
	cd /home/audrey/httpparse/
	python httpparse_main.py
	echo "$DATE Restart Success!!!" >> /home/audrey/logs/httpparse/checking.logs
	exit 0
fi
 
#rm -f /home/audrey/logs/httpparse/checking.tmp
