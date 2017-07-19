#encoding:utf-8  
import sys
import os
import time

reload(sys)
sys.setdefaultencoding('utf-8')

def readStrategyTable(cur, tablename):
	sql = 'select * from '+ tablename
	cur.execute(sql)

	return cur.fetchall()
	
def readAlarmFrequencyStrategy(cur):
	rowList = []
	rows = readStrategyTable(cur, 'tb_alarm_frequency_strategy')
	
	for row in rows:
		dict = {}
		dict['id'] = row[0]
		dict['label'] = row[1]
		dict['level'] = row[2]
		dict['title'] = row[3]
		dict['url'] = row[4]
		dict['is_use'] = row[5]
		dict['frequence'] = row[6]
		dict['minutes'] = row[7]
		dict['create_data'] = row[8]
		dict['last_time'] = row[9]
		rowList.append(dict)
		
	return rowList
	
def readAlarmLoginStrategy(cur):
	rowList = []
	rows = readStrategyTable(cur, 'tb_alarm_login_strategy')
	
	for row in rows:
		dict = {}
		dict['id'] = row[0]
		dict['label'] = row[1]
		dict['level'] = row[2]
		dict['is_use'] = row[3]
		dict['minutes'] = row[4]
		dict['ip_counts'] = row[5]
		dict['create_data'] = row[6]
		dict['last_time'] = row[7]
		rowList.append(dict)
		
	return rowList
	
def readJsonLog(cur):
	rowList = []
	rows = readStrategyTable(cur, 'json_log')           #####################################
	for row in rows:
		dict = {}
		dict['src_ip'] = row[1]
		dict['url'] = row[3]
		dict['session_id'] = row[4]
		dict['date'] = row[7]
		rowList.append(dict)
		
	return rowList
	
def readUserMg(cur):
	rowList = []
	rows = readStrategyTable(cur, 'user_mg')
	for row in rows:
		dict = {}
		dict['src_ip'] = row[1]
		dict['session_id'] = row[4]
		dict['date'] = row[5]
		dict['username'] = row[6]
		rowList.append(dict)
		
	return rowList
	
def readAlarmTimeStrategy(cur):
	rowList = []
	rows = readStrategyTable(cur, 'tb_alarm_time_strategy')
	
	for row in rows:
		dict = {}
		dict['id'] = row[0]
		dict['label'] = row[1]
		dict['level'] = row[2]
		dict['is_use'] = row[4]
		dict['start_time'] = row[5]
		dict['end_time'] = row[6]
		dict['create_data'] = row[7]
		dict['last_time'] = row[8]
		rowList.append(dict)
		
	return rowList

	
def readAlarmUserStrategy(cur):
	rowList = []
	rows = readStrategyTable(cur, 'tb_alarm_user_strategy')

	for row in rows:
		dict = {}
		dict['id'] = row[0]
		dict['label'] = row[1]
		dict['level'] = row[2]
		dict['is_use'] = row[3]
		dict['unuse_days'] = row[4]
		dict['create_date'] = row[5]
		dict['last_time'] = row[6]
		rowList.append(dict)
	
	return rowList


def readUserCollection(cur):
	rowList = []
	rows = readStrategyTable(cur, 'user_collection')

	for row in rows:
		dict = {}
		dict['id'] = row[0]
		dict['date'] = row[5]
		dict['username'] = row[6]
		rowList.append(dict)
	
	return rowList
	
def readUserCollectionByUserName(cur, username):
	sql = 'select * from user_collection where username = \'%s\'' % (username)
	cur.execute(sql)
	
	rows = cur.fetchall()

	for row in rows:
		return row[4]
	
	return ''
	

def readAlarmUltraViresStrategy(cur):
	rowList = []
	rows = readStrategyTable(cur, 'tb_alarm_ultra_vires_strategy')

	for row in rows:
		dict = {}
		dict['id'] = row[0]
		dict['label'] = row[1]
		dict['level'] = row[2]
		dict['URL'] = row[3]
		dict['Key_Value'] = row[4]
		dict['Account'] = row[5]
		dict['is_use'] = row[6]
		dict['create_date'] = row[7]
		dict['last_time'] = row[8]
		rowList.append(dict)
		
	return rowList

def readJsonLogBySessionAndUrl(cur, url, sessionID):
	rowList = []
	sql = 'select * from json_log where URL like \'%%%s%%\' and SessionID = \'%s\'' % (url, sessionID)                ############################
	#print sql
	cur.execute(sql)

	rows = cur.fetchall()

	for row in rows:
		dict = {}
		dict['date'] = row[7]
		dict['submitValue'] = row[11]
		rowList.append(dict)
	
	return rowList

	