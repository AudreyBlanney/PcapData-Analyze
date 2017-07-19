#encoding:utf-8  
import sys
import os
import time

reload(sys)
sys.setdefaultencoding('utf-8')


def saveAlarmFrequency(cur,tuple,label,level,startTime, endTime, count):
	startClock = time.localtime(startTime)
	formatStartClock = time.strftime("%Y-%m-%d %H:%M:%S",startClock)
	endClock = time.localtime(endTime)
	formatEndClock = time.strftime("%Y-%m-%d %H:%M:%S",endClock)
	try:
		sql = 'create table if not exists tb_alarm_frequency(id int primary key auto_increment, SRC_IP varchar(32) not null, SessionID varchar(64) not null, label varchar(100) not null, level varchar(16) not null, start_time timestamp not null, end_time timestamp not null, match_times varchar(12) not null, Remark text charset utf8)'
		cur.execute(sql)
		
		sql = 'insert into tb_alarm_frequency(SRC_IP, SessionID, label, level, start_time, end_time, match_times) values(\'%s\', \'%s\',\'%s\',\'%s\',\'%s\', \'%s\', \'%d\')' % (tuple[0],tuple[1],label,level,formatStartClock, formatEndClock, count)
		cur.execute(sql)
	except Exception, e:
		print 'insert tb_alarm_frequency error:%s' % e
		
def updateStrategyLastTime(cur,id,last_time,tableName):
	lastTime = time.localtime(last_time)
	formatLastClock = time.strftime("%Y-%m-%d %H:%M:%S",lastTime)
	try:
		sql = 'update '+ tableName +' set last_time=\'%s\' where id=\'%d\'' % (formatLastClock, id)
		#sql = 'update tb_alarm_frequency_strategy set last_time=\'%s\' where id=\'%d\'' % (formatLastClock, id)
		cur.execute(sql)
	except Exception, e:
		print 'update %s error:%s' % (tableName, e)

def saveAlarmLogin(cur, username, label, level, srcIPInfo):
	#以src_ip为键的
	sql = 'create table if not exists tb_alarm_login(id int primary key auto_increment, label varchar(100) not null, level varchar(16) not null, SRC_IP varchar(64) not null, time timestamp not null, SessionID varchar(120) not null, userName varchar(24) not null, Remark text charset utf8)'
	cur.execute(sql)
	
	for key in srcIPInfo:
		tmpTime = srcIPInfo[key][0]
		sessionID = srcIPInfo[key][1]
		clock = time.localtime(tmpTime)
		formatClock = time.strftime("%Y-%m-%d %H:%M:%S",clock)
		try:
			sql = 'insert into tb_alarm_login(label, level, SRC_IP, time, SessionID, userName) values(\'%s\', \'%s\',\'%s\',\'%s\',\'%s\', \'%s\')' % (label,level,key, formatClock, sessionID,username)
			cur.execute(sql)
		except Exception, e:
			print 'insert tb_alarm_login error:%s' % e
			
			
def saveAlarmTime(cur,dictIPInfo,label,level):
	#以src_ip为键的
	sql = 'create table if not exists tb_alarm_time(id int primary key auto_increment, SRC_IP varchar(32) not null, SessionID varchar(64) not null, label varchar(100) not null, level varchar(16) not null, start_time timestamp not null, end_time timestamp not null, Remark text charset utf8)'
	cur.execute(sql)
	
	for key in dictIPInfo:
		if 'start_time' in dictIPInfo[key] and 'end_time' in dictIPInfo[key]:
			startTime = dictIPInfo[key]['start_time']
			endTime = dictIPInfo[key]['end_time']
			src_ip = dictIPInfo[key]['src_ip']
			startClock = time.localtime(startTime)
			formatStartClock = time.strftime("%Y-%m-%d %H:%M:%S",startClock)
			endClock = time.localtime(endTime)
			formatEndClock = time.strftime("%Y-%m-%d %H:%M:%S",endClock)
			
			try:
				sql = 'insert into tb_alarm_time(SRC_IP, SessionID, label, level, start_time, end_time) values(\'%s\', \'%s\',\'%s\',\'%s\',\'%s\', \'%s\')' % (src_ip,key,label,level,formatStartClock, formatEndClock)
				cur.execute(sql)
			except Exception, e:
				print 'insert tb_alarm_time error:%s' % e
				
				
def saveUserTime(cur,label,level,appearTime, findTime, username):
	#以src_ip为键的
	sql = 'create table if not exists tb_alarm_user(id int primary key auto_increment, label varchar(100) not null, level varchar(16) not null, appear_time timestamp not null, find_time timestamp not null, days int not null, userName varchar(24) not null, Remark text charset utf8)'
	cur.execute(sql)
	
	appearClock = time.localtime(appearTime)
	formatAppearClock = time.strftime("%Y-%m-%d %H:%M:%S",appearClock)
	findClock = time.localtime(findTime)
	formatFindClock = time.strftime("%Y-%m-%d %H:%M:%S",findClock)
	
	days = int((findTime - appearTime)/86400.0)
	
	try:
		sql = 'insert into tb_alarm_user(label, level, appear_time, find_time, days, userName) values(\'%s\', \'%s\',\'%s\',\'%s\',\'%d\', \'%s\')' % (label,level,formatAppearClock, formatFindClock, days, username)
		cur.execute(sql)
	except Exception, e:
		print 'insert tb_alarm_user error:%s' % e
		
		
def saveAlarmUltraVires(cur,label,level,url, keyValue, change, account, sessionID, date):
	sql = 'create table if not exists tb_alarm_ultra_vires(ID int primary key auto_increment, Label varchar(100) not null, Level varchar(16) not null, URL text charset utf8, Key_Value varchar(64), change_value varchar(32), Account varchar(32), SessionID varchar(64), Date timestamp not null, Remark text charset utf8)'
	cur.execute(sql)
	
	clock = time.localtime(date)
	formatClock = time.strftime("%Y-%m-%d %H:%M:%S",clock)
	
	try:
		sql = 'insert into tb_alarm_ultra_vires(Label, Level, URL, Key_Value, change_value, Account, SessionID, Date) values(\'%s\', \'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\', \'%s\')' % (label,level,url, keyValue, change, account,sessionID,formatClock)
		cur.execute(sql)
		print sql
	except Exception, e:
		print 'insert tb_alarm_ultra_vires error:%s' % e

	
	
	














