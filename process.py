#encoding:utf-8  
import sys
import re
import os
import shutil
import ConfigParser
import chardet
import time
from dbio import saveAllData
from dbio import saveDesData
from dbio import readData

reload(sys)
sys.setdefaultencoding('utf-8')

mySQLDict = {}
userDict = {}
scanDict = {}

def getconfig():
	global mySQLDict 

	try:
		config=ConfigParser.ConfigParser()
		config.read('config.ini')
		
		mySQLDict['host'] = config.get("mysqlconfig","MysqlIP")
		mySQLDict['user'] = config.get("mysqlconfig", "UserName")
		mySQLDict['passwd'] = config.get("mysqlconfig","UserPasswd")
		mySQLDict['port'] = config.getint("mysqlconfig","MysqlPort")
		mySQLDict['database'] = config.get('tableconfig',"DataBaseName")
		mySQLDict['mainDataTable'] = config.get('tableconfig',"MainTableName")
		mySQLDict['secondDataTable'] = config.get('tableconfig',"SecondTableName")
		mySQLDict['thirdDataTable'] = config.get('tableconfig',"ThirdTableName")
		mySQLDict['fourthDataTable'] = config.get('tableconfig',"FourthTableName")
		mySQLDict['fifthDataTable'] = config.get('tableconfig',"FifthTableName")
		mySQLDict['FilterTableName'] = config.get('tableconfig',"filterNameTable")
		userDict['userName'] = config.get('name_passwd_config',"username")
		userDict['passwd'] = config.get('name_passwd_config',"passwd")
	except Exception,e:
		print 'read config.ini error, error info:%s' % e
		sys.exit()
		
def getScanDict():
	global scanDict 
	try:
		with open('config.ini', 'r') as P:
			for line in P:
				if '@' in line:
					tmpList = re.split('@', line)
					scanDict[tmpList[0]] = tmpList[1]
	except Exception, e:
		print 'read config.ini error:%s' % e

def getNameList():
	nameList = []
	try:
		file = open('name.rule', )
		for line in file:
			name = re.sub(r'\s', '', line)
			name = name.decode('gbk')
			nameList.append(name)
	except Exception, e:
		print 'read name.rule error,%s' % e
		
	return nameList

def getFileName():
	fileList = []
	path = "G:\Python-exploition\Script\data-analyze\json-log-files\\"
	
	for filename in os.listdir(path):
		if '.json' in filename:
			fileList.append(filename)

	fileList.sort()
	print 'Loading file : ' + fileList[0]
	
	if fileList:
		return ['G:\Python-exploition\Script\data-analyze\json-log-files\\' + fileList[0]]
	else:
		return []
	
def getSrcAndDesIP(ipStr):
	srcIP = re.search(r'^\[(?:[0-9]{1,3}\.){3}[0-9]{1,3}\:[0-9]{2,5}\]', ipStr)
	if srcIP is not None:
		srcIP = srcIP.group()
		srcIP = re.sub(r'\[', '', srcIP)
		srcIP = re.sub(r'\]', '', srcIP)
		
	desIP = re.search(r'-- -- --> \[(?:[0-9]{1,3}\.){3}[0-9]{1,3}\:[0-9]{2,5}\]', ipStr)
	if desIP is not None:
		desIP = desIP.group()
		desIP = re.sub(r'-- -- --> \[', '', desIP)
		desIP = re.sub(r'\]', '', desIP)
		
	return srcIP, desIP
	
def getHeadAndUrl(dataStr):
	strList = re.split(r'(?<=\n)\s*?\n', dataStr, re.I|re.M|re.S)
	for tmpStr in strList:
		if re.match(r'(?:GET|POST).*?HTTP/', tmpStr, re.I|re.M|re.S):
			url = re.search(r'^(?:GET|POST).*?\n', tmpStr)
			submit = re.search(r'^(?:GET|POST)', tmpStr)
			submit = submit.group()
			url = re.sub(r'^(?:GET|POST) ', '', url.group())
			url = url.replace('HTTP/1.1', '')
			head = re.sub(r'^(?:GET|POST).*?\n', '', tmpStr)
			return head, url, submit
	
	return '', '', ''
	
def getSubmitValue(dataStr):
	getStr = re.search(r'GET /.*?\n', dataStr)
	if getStr:
		getStr = getStr.group()
		submitValue = re.search('\?.*?HTTP', getStr)
		if submitValue:
			submitValue = submitValue.group().replace('?', '')
			return submitValue.replace('HTTP', '')
		else:
			return ''
	else:
		getStr = re.search(r'POST /.*?\n', dataStr)
		if getStr:
			contentLen = re.search(r'Content-Length:.*?\d+', dataStr)
			if contentLen:
				contentLen = contentLen.group().replace('Content-Length:', '')
				if int(contentLen) > 0:
					strList = re.split(r'(?<=\n)\s*?\n', dataStr, re.I|re.M|re.S)
					i = 0
					for tmpStr in strList:
						if tmpStr:
							i += 1
							if i == 2:
								return tmpStr
				else:
					return ''
			
			else:
				return ''
	
def getSSIONID(headStr):
	ssionIDStr = 'NULL'
	ssionID = re.search(r'JSESSIONID.*?\;', headStr, re.I|re.M|re.S)
	
	if ssionID is not None:
		ssionList = re.split(r'=', ssionID.group())
		ssionIDStr = re.sub(r'\;', '', ssionList[1], re.I|re.M|re.S)
		#print ssionIDStr
	return ssionIDStr

def getResponse(dataStr):
	strList = re.split(r'(?<=\n)\s*?\n', dataStr, re.I|re.M|re.S)
	for tmpStr in strList:
		if re.match(r'HTTP/', tmpStr, re.I|re.M|re.S):
			return tmpStr
	
	return ''
	
def getHtmlBody(dataStr):
	bodyStr = re.search(r'<html.*>(.*?)</html>', dataStr, re.I|re.M|re.S)
	if bodyStr is not None:
		return bodyStr.group()
	else:
		return ''
		
def getTitle(bodyStr):
	if bodyStr:
		title = re.search(r'<title>.*?</title>', bodyStr, re.I|re.M|re.S)
		if title is not None:
			title = re.sub(r'<title>', '', title.group())
			title = re.sub(r'</title>', '', title)
			return title
	
	return ''
	
def getNameAndPasswdPattern():
	nameList = re.split(r'\|', userDict['userName'])
	passwdList = re.split(r'\|', userDict['passwd'])
	
	nameStr = ''
	count = 0
	for name in nameList:
		if count == 0:
			nameStr += name
		else:
			nameStr = nameStr + '|' + name
		count += 1
		
	passwdStr = ''
	count = 0
	for passwd in passwdList:
		if count == 0:
			passwdStr += passwd
		else:
			passwdStr = passwdStr + '|' + passwd
		count += 1
		
	return '(?:' + nameStr + ')' + '=.*?&{1,3}' + '(?:' + passwdStr + ')' + '=.*?&{1,3}'
	#return '(?:' + nameStr + ')' + '=.*?&{1,3}' + '(?:' + passwdStr + ')' + '=.*?&{1,3}code='
	
def getNameAndPasswd(dataStr, userInfoPattern):		
	userInfo = re.search(userInfoPattern, dataStr, re.I|re.M|re.S)
	if userInfo is not None:
		userInfoList = re.split(r'=', userInfo.group())
		username = userInfoList[1]
		passwd = userInfoList[2]
		
		username = re.sub(r'&.*', '', username)
		passwd = re.sub(r'&.*', '', passwd)
		
		return username, passwd
			
	return '', ''
	

def decodeData(dataStr):
	codeList = ['gbk', 'ascii', 'utf-8']
	try:
		chardit1 = chardet.detect(dataStr)
		if chardit1['encoding'] not in codeList:
			chardit1['encoding'] = 'gbk'
		dataStr = dataStr.decode(chardit1['encoding'])
	except Exception,e:
		print 'unicode mode:%s' % chardit1['encoding']
		print 'decode error:%s' % e
	return dataStr
	
def getDate(reponseStr):
	monDict = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
	dateStr = re.search(r'Date: .*?\n', reponseStr, re.I|re.M|re.S)
	format_clock = '504'
	if dateStr is not None:
		dateStr = dateStr.group()
		tmpList = re.split(r',', dateStr)
		dateList = re.split(r'\s', tmpList[1])
		
		day = int(dateList[1])
		mon = monDict[dateList[2]]
		year = int(dateList[3])
	
		timeList = re.split(r':', dateList[4])
		hour = int(timeList[0])
		min = int(timeList[1])
		sec = int(timeList[2])

		t = (year, mon, day, hour, min, sec, 0, 0, 0)
		secs = time.mktime(t)
		if 'GMT' in dateStr:
			secs += 28800
		clock = time.localtime(secs)
		format_clock = time.strftime("%Y-%m-%d %H:%M:%S",clock)
		
	return format_clock
	
def getType(dataDict):
	for key in scanDict:
		tmpList = re.split(':', scanDict[key])
		targetStr = tmpList[1].replace('\n', '')
		searchAreaList = re.split(',', tmpList[0])
		for searchArea in searchAreaList:
			if searchArea.upper() == 'HEAD':
				tar = re.search(targetStr, dataDict['head'], re.I|re.M|re.S)
				if tar is not None:
					return key
			elif searchArea.upper() == 'URL':
				tar = re.search(targetStr, dataDict['url'], re.I|re.M|re.S)
				if tar is not None:
					return key
			elif searchArea.upper() == 'USER-AGENT':
				userAgent = re.search('User-Agent.*', dataDict['head'], re.I|re.M|re.S)
				if userAgent is not None:
					tar = re.search(targetStr, userAgent.group(), re.I|re.M|re.S)
					if tar is not None:
						return key
			else:
				return ''
				
	return ''
	
'''def getPostValues(dataStr):
	postValue = re.search(r'Content-Length.*?')'''
		
	
def fillDataDict(dataDict, dataStr, userInfoPattern):
	dataStr = decodeData(dataStr)

	dataDict['head'], dataDict['url'], dataDict['submit'] = getHeadAndUrl(dataStr)
	dataDict['response'] = getResponse(dataStr)
	dataDict['date'] = getDate(dataDict['response'])
	dataDict['title'] = getTitle(dataStr)
	dataDict['htmlBody'] = getHtmlBody(dataStr)
	dataDict['sessionID'] = getSSIONID(dataDict['head'])
	dataDict['userName'], dataDict['passwd'] = getNameAndPasswd(dataStr, userInfoPattern)
	dataDict['type'] = getType(dataDict)
	dataDict['submitValue'] = getSubmitValue(dataStr)
	
def main():
	if not os.path.exists('oldData'):
		os.makedirs('oldData')
	nameList = getNameList()
	
	fileNameList = getFileName()
	userInfoPattern = getNameAndPasswdPattern()
	
	filterNameList = readData.readFilterTable(mySQLDict['database'], mySQLDict['FilterTableName'], mySQLDict)
	
	for fileName in fileNameList:	
		connMain, curMain = saveAllData.getMainDataTableHandle(mySQLDict)
		conn, cur1, cur2, cur3, cur4, cur5, cur6 = saveDesData.getDesDataTableHandle(mySQLDict)

		dataDict = {}
		dataStr = ''
		
		fileP = open(fileName, 'r')
		pattern = re.compile(r'^\[(?:[0-9]{1,3}\.){3}[0-9]{1,3}\:[0-9]{2,5}\] -- -- --> \[(?:[0-9]{1,3}\.){3}[0-9]{1,3}\:[0-9]{2,5}\]')

		for line in fileP:
			if pattern.match(line):
				if dataStr and dataDict:
					fillDataDict(dataDict, dataStr, userInfoPattern)
					sensDict,listDict = saveDesData.calcSenseGrade(dataDict['htmlBody'], nameList, filterNameList)
					saveAllData.saveDatatoMainDB(mySQLDict, dataDict, curMain)
					saveDesData.saveDatatoDesDB(mySQLDict, dataDict, sensDict, listDict, cur1, cur2, cur3, cur4, cur5, cur6)
				dataDict = {}
				dataStr = ''
				dataDict['srcIP'], dataDict['desIP'] = getSrcAndDesIP(line)
			else:
				dataStr += line
		
		fillDataDict(dataDict, dataStr, userInfoPattern)
		sensDict,listDict = saveDesData.calcSenseGrade(dataDict['htmlBody'], nameList, filterNameList)
		saveAllData.saveDatatoMainDB(mySQLDict, dataDict, curMain)
		saveDesData.saveDatatoDesDB(mySQLDict, dataDict, sensDict, listDict, cur1, cur2, cur3, cur4, cur5, cur6)
		
		saveAllData.commitMainDataTable(connMain, curMain)
		saveDesData.commitDesDataTable(conn, cur1, cur2, cur3, cur4, cur5, cur6)
		
		fileP.close()
		
		try:
			shutil.move(fileName, 'oldData')   
		except Exception, e:
			print 'move file err:%s' % e
		
	print 'complete success!'
	
def check_if_proc_is_running(proc, para):
	if os.name == 'nt':
		cur_caption = proc + '.exe'
		cmd = 'wmic process where caption="'+cur_caption+'" get caption,commandline | find /i "'+para+'"'
		exclude_str=' wmic process '
	else:
		cmd = 'ps -ef | grep -v grep | grep "'+proc+'" | grep "'+para+'"'
		exclude_str = 'grep '
	
	is_running = 0
	count = 0
	
	with os.popen(cmd) as p:
		for line in p.readlines():
			line = re.sub(r'\s+$', '', line)
			if line.find(para) >=0 and line.find(exclude_str)<0:
				count += 1
	
	if count > 1:
		print 'waring:' + line + ' is already in running!'
		is_running = 1
		
	return is_running
	
def check_is_process_is_running():
	is_running = check_if_proc_is_running('python', 'process.py')
	if is_running == 1:
		sys.exit()
				
if __name__ == '__main__':
	check_is_process_is_running()
	getconfig()
	getScanDict()
	main()
	#raw_input('Press Enter to exit...')