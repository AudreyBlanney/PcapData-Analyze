#!/bin/bash
#####################################
#                           		#
#						   			#
#      Run Program          		#
# 									#
#	__Author__ = Audrey丶Blanney	#
#									#
#####################################
DATE=`date`

cd /home/audrey/data-analyze/
python process.py > /home/audrey/logs/process/process.tmp 2>&1

Info=`cat /home/audrey/logs/process/process.tmp` 
echo -e "$DATE \n $Info" >> /home/audrey/logs/process/process.logs