#encoding:utf-8
import re
import multiprocessing
import MySQLdb
from DataOperate.loadData import *
from DataOperate.saveData import *

reload(sys)
sys.setdefaultencoding('utf-8')

def connectDB():
	conn=MySQLdb.connect(host='localhost', user='root', passwd='4869', charset='utf8', port=3306) 
	conn.select_db('obs') 
	cur=conn.cursor() 
	return conn, cur
	
def commitDataTable(conn, cur):
	cur.close()
	conn.commit() 
	conn.close()

def processAlarmFrequency():
	conn, cur = connectDB()
	dictList = readAlarmFrequencyStrategy(cur)
	jsonDataList = readJsonLog(cur)
	
	for dict in dictList:
		if dict['is_use'] != 1:
			continue
			
		if not dict['last_time']:
			dict['last_time'] = '2000-01-01 00:00:00'
		
		lastTimeArray = time.strptime(str(dict['last_time']), "%Y-%m-%d %H:%M:%S")
		lastTime = int(time.mktime(lastTimeArray))
		creatTimeArray = time.strptime(str(dict['create_data']), "%Y-%m-%d %H:%M:%S")
		creatTime = int(time.mktime(creatTimeArray))

		beginTime = lastTime if lastTime > creatTime else creatTime
		
		dictUserCount = {}
		dictUserStartTime = {}
		dictUserEndTime = {}
		for jsonDict in jsonDataList:
			if jsonDict['date'] == '504':
				continue
			
			timeArray = time.strptime(str(jsonDict['date']), "%Y-%m-%d %H:%M:%S")
			date = int(time.mktime(timeArray))
			if date > beginTime and jsonDict['url'] == dict['url']:
				srcIP = re.split(':', jsonDict['src_ip'])[0]
				key = (srcIP, jsonDict['session_id'])
				if key in dictUserCount:
					if (date - dictUserStartTime[key]) >= (dict['minutes'] * 60):
						if dictUserCount[key] >= dict['frequence']:
							saveAlarmFrequency(cur,key,dict['label'],dict['level'],dictUserStartTime[key],dictUserEndTime[key],dictUserCount[key])

						dictUserCount[key] = 1
						dictUserStartTime[key] = date
						dictUserEndTime[key] = date
					else:
						dictUserCount[key] += 1
						dictUserEndTime[key] = date
				else:
					dictUserCount[key] = 1
					dictUserStartTime[key] = date
		else:
			for key in dictUserCount:
				if dictUserEndTime[key] - dictUserStartTime[key] <= (dict['minutes'] * 60) and dictUserCount[key] >= dict['frequence']:
					saveAlarmFrequency(cur,key,dict['label'],dict['level'],dictUserStartTime[key],dictUserEndTime[key],dictUserCount[key])
			
			updateStrategyLastTime(cur, dict['id'], date, 'tb_alarm_frequency_strategy')
	
	commitDataTable(conn, cur)
	
def initUserInfo(srcIP, key, dictUserInfo, dictUserStartTime, dictUserEndTime, date, UserMgDict):
	ipDict = {}
	ipValue = []
	ipValue.append(date)
	ipValue.append(UserMgDict['session_id'])
	ipDict[srcIP] = ipValue
	dictUserInfo[key] = ipDict
	dictUserStartTime[key] = date
	dictUserEndTime[key] = date
	
def processAlarmLogin():
	conn, cur = connectDB()
	dictList = readAlarmLoginStrategy(cur)
	UserMgList = readUserMg(cur)
	
	for dict in dictList:
		if dict['is_use'] != 1:
			continue
			
		if not dict['last_time']:
			dict['last_time'] = '2000-01-01 00:00:00'
		
		lastTimeArray = time.strptime(str(dict['last_time']), "%Y-%m-%d %H:%M:%S")
		lastTime = int(time.mktime(lastTimeArray))
		creatTimeArray = time.strptime(str(dict['create_data']), "%Y-%m-%d %H:%M:%S")
		creatTime = int(time.mktime(creatTimeArray))

		beginTime = lastTime if lastTime > creatTime else creatTime
		
		dictUserInfo = {}
		dictUserStartTime = {}
		dictUserEndTime = {}

		for UserMgDict in UserMgList:
			if UserMgDict['date'] == '504':
				continue
				
			timeArray = time.strptime(str(UserMgDict['date']), "%Y-%m-%d %H:%M:%S")
			date = int(time.mktime(timeArray))
			if date > beginTime:
				srcIP = re.split(':', UserMgDict['src_ip'])[0]
				key = UserMgDict['username']
				if key in dictUserInfo:
					ipValue = []
					ipValue.append(date)
					ipValue.append(UserMgDict['session_id'])
					dictUserInfo[key][srcIP] = ipValue
					
					if len(dictUserInfo[key]) >= dict['ip_counts']:
						if (date - dictUserStartTime[key]) <= (dict['minutes'] * 60):
							saveAlarmLogin(cur,key,dict['label'],dict['level'],dictUserInfo[key])
						initUserInfo(srcIP, key, dictUserInfo, dictUserStartTime, dictUserEndTime, date, UserMgDict)
					else:
						ipValue = []
						ipValue.append(date)
						ipValue.append(UserMgDict['session_id'])
						dictUserInfo[key][srcIP] = ipValue
						dictUserEndTime[key] = date
				else:
					initUserInfo(srcIP, key, dictUserInfo, dictUserStartTime, dictUserEndTime, date, UserMgDict)
		else:
			for key in dictUserInfo:
				if len(dictUserInfo[key]) >= dict['ip_counts'] and dictUserEndTime[key] - dictUserStartTime[key] <= (dict['minutes'] * 60):
					saveAlarmLogin(cur,key,dict['label'],dict['level'],dictUserInfo[key])
					
			updateStrategyLastTime(cur, dict['id'], date, 'tb_alarm_login_strategy')
				
	commitDataTable(conn, cur)

def calcBeginDateAndEndDate(dict, lastTime, creatTime, beginTime):
	startDateStr = str(dict['last_time']) if lastTime > creatTime else str(dict['create_data'])
	beginDateStr = startDateStr[0:10] + ' ' + str(dict['start_time'])
	beginDateArray = time.strptime(beginDateStr, "%Y-%m-%d %H:%M:%S")
	beginDate = int(time.mktime(beginDateArray))
	
	if int(dict['end_time'][0:2]) < int(dict['start_time'][0:2]):
		tmpTime = beginTime + 24*3600
		clock = time.localtime(tmpTime)
		formatClock = time.strftime("%Y-%m-%d %H:%M:%S",clock)
		endDateStr = formatClock[0:10] + ' ' + str(dict['end_time'])
	else:
		endDateStr = startDateStr[0:10] + ' ' + str(dict['end_time'])
		
	endDateArray = time.strptime(endDateStr, "%Y-%m-%d %H:%M:%S")
	endinDate = int(time.mktime(endDateArray))
	
	return beginDate, endinDate
	

def processAlarmTime():
	conn, cur = connectDB()
	dictList = readAlarmTimeStrategy(cur)
	jsonDataList = readJsonLog(cur)
	
	for dict in dictList:
		if dict['is_use'] != 1:
			continue
			
		if not dict['last_time']:
			dict['last_time'] = '2000-01-01 00:00:00'
		
		lastTimeArray = time.strptime(str(dict['last_time']), "%Y-%m-%d %H:%M:%S")
		lastTime = int(time.mktime(lastTimeArray))
		creatTimeArray = time.strptime(str(dict['create_data']), "%Y-%m-%d %H:%M:%S")
		creatTime = int(time.mktime(creatTimeArray))

		beginTime = lastTime if lastTime > creatTime else creatTime
		
		beginDate, endDate = calcBeginDateAndEndDate(dict, lastTime, creatTime, beginTime)
		
		initBeginDate = beginDate
		
		if beginTime > endDate:
			beginDate = beginDate + 24*3600
			endDate = endDate + 24*3600
		elif beginDate < beginTime:
			beginDate = beginTime
		
		dictIPInfo = {}
		
		firstChangeTimeFlag = 1
		
		for jsonDict in jsonDataList:
			if jsonDict['date'] == '504':
				continue
			
			timeArray = time.strptime(str(jsonDict['date']), "%Y-%m-%d %H:%M:%S")
			date = int(time.mktime(timeArray))
			if date > beginTime and jsonDict['session_id'] != 'NULL':
				key = jsonDict['session_id']
				if key in dictIPInfo and date <= endDate:
					dictIPInfo[key]['end_time'] = date
				elif key not in dictIPInfo and date >= beginDate:
					valueDict = {}
					valueDict['start_time'] = date
					valueDict['src_ip'] = jsonDict['src_ip']
					dictIPInfo[key] = valueDict
					
				if date >= endDate:
					saveAlarmTime(cur,dictIPInfo,dict['label'],dict['level'])
					dictIPInfo = {}
					if firstChangeTimeFlag == 1 and beginDate == beginTime:
						beginDate = initBeginDate + 24*3600
						firstChangeTimeFlag = 0
					else:
						beginDate = beginDate + 24*3600
					
					endDate = endDate + 24*3600
		else:
			saveAlarmTime(cur,dictIPInfo,dict['label'],dict['level'])
	
		updateStrategyLastTime(cur, dict['id'], date, 'tb_alarm_time_strategy')
				
	commitDataTable(conn, cur)
	
	
def processAlarmUser():
	conn, cur = connectDB()
	dictList = readAlarmUserStrategy(cur)
	userCollectList = readUserCollection(cur)
	
	for dict in dictList:
		if dict['is_use'] != 1:
			continue
			
		if not dict['last_time']:
			dict['last_time'] = '2000-01-01 00:00:00'
		
		lastTimeArray = time.strptime(str(dict['last_time']), "%Y-%m-%d %H:%M:%S")
		lastTime = int(time.mktime(lastTimeArray))
		creatTimeArray = time.strptime(str(dict['create_date']), "%Y-%m-%d %H:%M:%S")
		creatTime = int(time.mktime(creatTimeArray))

		beginTime = lastTime if lastTime > creatTime else creatTime

		for userDict in userCollectList:
			if userDict['date'] == '504':
				continue

			timeArray = time.strptime(str(userDict['date']), "%Y-%m-%d %H:%M:%S")
			date = int(time.mktime(timeArray))
			if date > beginTime:
		
				nowTime = int(time.time())
				if (nowTime - date) > dict['unuse_days']*24*3600:
					saveUserTime(cur,dict['label'],dict['level'], date, nowTime, userDict['username'])
		
		updateStrategyLastTime(cur, dict['id'], date, 'tb_alarm_user_strategy')
			
	commitDataTable(conn, cur)
	

def processAlarmUltraVires():
	conn, cur = connectDB()
	dictList = readAlarmUltraViresStrategy(cur)
	
	for dict in dictList:
		if dict['is_use'] != 1:
			continue
			
		if not dict['last_time']:
			dict['last_time'] = '2000-01-01 00:00:00'
		
		lastTimeArray = time.strptime(str(dict['last_time']), "%Y-%m-%d %H:%M:%S")
		lastTime = int(time.mktime(lastTimeArray))
		creatTimeArray = time.strptime(str(dict['create_date']), "%Y-%m-%d %H:%M:%S")
		creatTime = int(time.mktime(creatTimeArray))

		beginTime = lastTime if lastTime > creatTime else creatTime
		
		SessionID = readUserCollectionByUserName(cur, dict['Account'])

		if not SessionID:
			continue
		
		jsonDataList = readJsonLogBySessionAndUrl(cur, dict['URL'], SessionID)

		date = 0
		for jsonDict in jsonDataList:
			if jsonDict['date'] == '504':
				continue
				
			timeArray = time.strptime(str(jsonDict['date']), "%Y-%m-%d %H:%M:%S")
			date = int(time.mktime(timeArray))
			if date > beginTime:
				if dict['Key_Value'] not in jsonDict['submitValue']:
					saveAlarmUltraVires(cur,dict['label'],dict['level'],dict['URL'], dict['Key_Value'], jsonDict['submitValue'][0:30], dict['Account'], SessionID, date)
		
		if date > 0:
			updateStrategyLastTime(cur, dict['id'], date, 'tb_alarm_ultra_vires_strategy')
		
	commitDataTable(conn, cur)

def mainFunc():
	processList = []
	processList.append(multiprocessing.Process(target=processAlarmFrequency, args=()))
	processList.append(multiprocessing.Process(target=processAlarmLogin, args=()))
	processList.append(multiprocessing.Process(target=processAlarmTime, args=()))
	processList.append(multiprocessing.Process(target=processAlarmUser, args=()))
	processList.append(multiprocessing.Process(target=processAlarmUltraVires, args=()))
	
	
	for p in processList:
		p.start()	
	
if __name__ == '__main__':
	mainFunc()
	#raw_input('Press Enter to exit...')