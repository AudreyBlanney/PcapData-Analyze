#!/bin/bash
#####################################
#                           		#
#						   			#
#      Run Program          		#
# 									#
#	__Author__ = Audrey丶Blanney	    #
#									#
#####################################

DATE=`date`

cd /home/audrey/data-analyze/warning/
python Alarm.py > /home/audrey/logs/alarm/alarm.tmp 2>&1

Info=`cat /home/audrey/logs/process/alarm.tmp` 
echo -e "$DATE \n $Info" >> /home/audrey/logs/alarm/alarm.logs