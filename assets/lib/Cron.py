#! /usr/bin/python
#coding=utf-8

import os
from crontab import CronTab
import datetime,time
# from cron_run import *

PATH = os.getcwd()
# print (PATH)


class Crons():
	def __init__(self):
		self.cron = CronTab(user = 'root')

	def select_job(self, taskid):
		result = {}
		jobs = self.cron.find_comment(taskid)
		for job in jobs:
			if job :
				result[taskid] = job.command
				return result
			else :
				return False

	def add_job(self, taskid, crontab, domain, userid, openid,cron_tpye,lict) :
		result = self.select_job(taskid)
		if result:
			return False
		command = 'python %s%slib%scron_run.py %s %s %s %s' % (PATH, os.path.sep, os.path.sep, domain, userid, openid,lict)
		job = self.cron.new(command = command, comment = taskid)

		if cron_tpye == '0':
			date_time = time.strptime(str(crontab), "%Y-%m-%d %H:%M")
			y, m, d, h, M = date_time[0:5]
			times = '%s %s %s %s %s' % (M, h, d, m, y)
			job.setall(times)
		elif cron_tpye == '1':
			week_time = time.strptime(str(crontab), "%w-%H:%M:%S")
			y, m, d, h, M, s, w = week_time[0:7]
			times = '%s %s * * %s'%(M,h,w+1)
			job.setall(times)
		self.cron.write()
		if job.is_valid() == True:
			return True
		else:
			return False

	def del_job(self, taskid):
		self.cron.remove_all(comment = taskid)
		self.cron.write()
		result = self.select_job(taskid)
		return result

if __name__ == '__main__':
	con = Crons()	
	# print (con.select_job('3'))
	print (con.del_job('2'))
