#encoding:utf-8  
import sys
import re
import hashlib
import MySQLdb

reload(sys)
sys.setdefaultencoding('utf-8')

def md5(str):
	m = hashlib.md5()   
	m.update(str)
	return m.hexdigest()

def getDesDataTableHandle(mySQLDict):
	conn=MySQLdb.connect(host=mySQLDict['host'], user=mySQLDict['user'], passwd=mySQLDict['passwd'], charset='utf8', port=mySQLDict['port']) 
	conn.select_db(mySQLDict['database']) 
	cur1=conn.cursor()
	cur2=conn.cursor() 
	cur3=conn.cursor()
	cur4=conn.cursor()
	cur5=conn.cursor()
	cur6=conn.cursor()
	
	sql1 = 'create table if not exists ' + mySQLDict['secondDataTable'] +"(ID int auto_increment, DES_IP VARCHAR(32),TITLE text charset utf8, URL text charset utf8, DATE VARCHAR(32), HTML_BODY mediumtext charset utf8, DATA_TYPE VARCHAR(255) charset utf8, SENS_GRADE VARCHAR(8) charset utf8, NAME VARCHAR(2048) charset utf8, IDCARD VARCHAR(2048) charset utf8, TELPHONE VARCHAR(2048) charset utf8, EMAIL VARCHAR(2048) charset utf8, ADDRESS VARCHAR(2048) charset utf8, Sign int NOT NULL DEFAULT 0, Remark text charset utf8, primary key(ID))"
	cur1.execute(sql1)
	
	sql2 = 'create table if not exists ' + mySQLDict['thirdDataTable'] +"(ID int auto_increment, DES_IP VARCHAR(32),TITLE text charset utf8, URL text charset utf8, DATE VARCHAR(32), HTML_BODY mediumtext charset utf8, Sign int NOT NULL DEFAULT 0, Remark text charset utf8, primary key(ID))"
	cur2.execute(sql2)
	
	sql3 = 'create table if not exists ' + mySQLDict['fourthDataTable'] +"(ID int auto_increment, SRC_IP VARCHAR(32), DES_IP VARCHAR(32), URL text charset utf8, SessionID VARCHAR(255), DATE VARCHAR(32), userName VARCHAR(64) charset utf8, passWord VARCHAR(128), primary key(ID))"
	cur3.execute(sql3)
	
	sql4 = 'create table if not exists ' + mySQLDict['fifthDataTable'] +"(ID int auto_increment, SRC_IP VARCHAR(32), DES_IP VARCHAR(32), TITLE text charset utf8, URL text charset utf8, SessionID VARCHAR(255), DATE VARCHAR(32), TYPE VARCHAR(32), HEAD mediumtext charset utf8, Response mediumtext charset utf8, level varchar(32) NOT NULL DEFAULT 'high', Remark text charset utf8, primary key(ID))"
	cur4.execute(sql4)

	sql5 = 'create table if not exists user_collection(ID int auto_increment, SRC_IP VARCHAR(32), DES_IP VARCHAR(32), URL text charset utf8, SessionID VARCHAR(255), DATE VARCHAR(32), userName VARCHAR(64) charset utf8, passWord VARCHAR(128), primary key(ID),UNIQUE KEY (userName))'
	cur5.execute(sql5)

	sql6 = 'create table if not exists data_batch(ID int auto_increment, SRC_IP VARCHAR(32), DES_IP VARCHAR(32), SessionID VARCHAR(255), TITLE text charset utf8, URL text charset utf8, DATE VARCHAR(32), HTML_BODY mediumtext charset utf8, DATA_TYPE VARCHAR(255) charset utf8, NAME VARCHAR(2048) charset utf8, IDCARD VARCHAR(2048) charset utf8, TELPHONE VARCHAR(2048) charset utf8, EMAIL VARCHAR(2048) charset utf8, ADDRESS VARCHAR(2048) charset utf8, Sign int NOT NULL DEFAULT 0, SUM VARCHAR(64), primary key(ID))'
	cur6.execute(sql6)
	return conn, cur1, cur2, cur3, cur4, cur5, cur6
	


telpattern1 = re.compile(r'\d{3,4}-\d{6,10}')
telpattern2 = re.compile(r'\(\d{3,4}\)\d{6,10}')
telpattern3 = re.compile(r'[86]{0,2}1[3458]\d{9}')

emailPattern = re.compile(r'(\w[-\w.+]*@[A-Za-z0-9][-A-Za-z0-9]+\.+[A-Za-z]{2,14})')
#emailPattern = re.compile(r'([\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?')
#emailPattern2 = re.compile(r'\<[[:alnum:]_\-]+\.?[[:alnum:]]+@([[:alnum:]_\-]+\.)+(com|cn|edu|org|net|gov)\.?\>')
idCardPattern = re.compile(r'\d{17}(?:\d|x)')

cityList = [u'北京市',u'广东省',u'山东省',u'江苏省',u'河南省',u'上海市',u'河北省',u'浙江省',u'香港',u'陕西省',u'湖南省',u'重庆市',u'福建省',u'天津市',
u'云南省',u'四川省',u'广西',u'安徽省',u'海南省',u'江西省',u'湖北省',u'山西省',u'辽宁省',u'台湾省',u'黑龙江',u'内蒙古',u'澳门',u'贵州省',u'甘肃省',
u'青海省',u'新疆',u'西藏',u'吉林省',u'宁夏']


def calcSenseGrade(bodyStr, nameList, filterNameList):
	sensDict = {'name':0, 'telphone':0, 'email':0, 'idCard':0, 'adress':0}
	listDict = {'name':[], 'telphone':[], 'email':[], 'idCard':[], 'adress':[]}
	
	if bodyStr:
		#匹配名字
		for name in nameList:
			nameRule =  ur'[^\u4e00-\u9fa5]' + name + ur"[\u4e00-\u9fa5]{1,2}[^\u4e00-\u9fa5]"
			pattern = re.compile(nameRule)
			realNameList = pattern.findall(bodyStr, re.I|re.M|re.S)
			if realNameList:
				for realName in realNameList:
					flag = 0
					tmp = re.match(ur'[\u4e00-\u9fa5]{2,3}[a-zA-Z]', realName)
					if not tmp:
						realName = realName[1:-1]
						for filterName in filterNameList:
							if filterName.find(realName) > 0:
								flag = 1
								break
						if flag == 0:
							#print realName
							sensDict['name'] += 1
							listDict['name'].append(realName)
		
		#匹配电话
		telPatternList = [telpattern1, telpattern2, telpattern3]
		for telPattern in telPatternList:
			telphoneList = telPattern.findall(bodyStr, re.I|re.M|re.S)
			if telphoneList:
				for telphone in telphoneList:
					sensDict['telphone'] += 1
					listDict['telphone'].append(telphone)
		
		#匹配邮箱
		emailList = emailPattern.findall(bodyStr, re.I|re.M|re.S)
		if emailList:
			for email in emailList:
				print email
				sensDict['email'] += 1
				listDict['email'].append(email)
				
		#匹配地址
		for city in cityList:
			cityRule =  city.decode('utf-8') + ur".*?[^\u4e00-\u9fa5]"
			cityPattern = re.compile(cityRule)
			realCityList = cityPattern.findall(bodyStr, re.I|re.M|re.S)
			if realCityList:
				for realCity in realCityList:
					realCity = realCity[:-1]
					sensDict['adress'] += 1
					listDict['adress'].append(realCity)
				

		#匹配身份证
		idCardList = idCardPattern.findall(bodyStr, re.I|re.M|re.S)
		if idCardList:
			for idCard in idCardList:
				sensDict['idCard'] += 1
				listDict['idCard'].append(idCard)
		
	return sensDict, listDict
	

gradeDict = {'name':u'姓名 ', 'telphone':u'电话 ', 'email':u'邮箱 ', 'idCard':u'身份证号码 ', 'adress':u'地址 '}

def saveDatatoDesDB(mySQLDict, dataDict, sensDict, listDict, cur1, cur2, cur3, cur4, cur5, cur6):
	dataDict['htmlBody'] = MySQLdb.escape_string(dataDict['htmlBody'])
	dataDict['head'] = MySQLdb.escape_string(dataDict['head'])
	dataDict['response'] = MySQLdb.escape_string(dataDict['response'])
	
	if not dataDict['url']:
		return
	
	nameStr = ''
	idCardStr = ''
	emailStr = ''
	adressStr = ''
	telphoneStr = ''
	countname = 0
	countidCard = 0
	countemail = 0
	countadress = 0
	counttelphone = 0
	SUM = 0
	
	count = 0
	dataType = ''
	senseGrade = ''
	for key in sensDict:
		if sensDict[key] > 0:
			count += 1
			dataType += gradeDict[key].decode('utf-8')
			if key == 'name':
				for name in listDict[key]:
					nameStr += name
					nameStr += ' '
				nameStr = nameStr + '[' + str(sensDict[key]) + ']'
				countname = sensDict[key]
			elif key == 'telphone':
				for telphone in listDict[key]:
					telphoneStr += telphone
					telphoneStr += ' '
				telphoneStr = telphoneStr + '[' + str(sensDict[key]) + ']'
				counttelphone = sensDict[key]
			elif key == 'email':
				for email in listDict[key]:
					emailStr += email
					emailStr += ' '
				emailStr = emailStr + '[' + str(sensDict[key]) + ']'
				countemail = sensDict[key]
			elif key == 'adress':
				for adress in listDict[key]:
					adressStr += adress
					adressStr += ' '
				adressStr = adressStr + '[' + str(sensDict[key]) + ']'
				countadress = sensDict[key]
			elif key == 'idCard':
				for idCard in listDict[key]:
					idCardStr += idCard
					idCardStr += ' '
				idCardStr = idCardStr + '[' + str(sensDict[key]) + ']'
				countidCard = sensDict[key]

			SUM = countname + counttelphone + countemail + countadress + countidCard
			#print SUM

	if count == 1:
		senseGrade = u'低'.decode('utf-8')
	elif count == 2:
		senseGrade = u'中'.decode('utf-8')
	elif count > 2:
		senseGrade = u'高'.decode('utf-8')
	
	if count > 0:
		try:
			sql = 'insert into '+mySQLDict['secondDataTable']+'(TITLE, DES_IP, URL, DATE, HTML_BODY, DATA_TYPE, SENS_GRADE, NAME, IDCARD, TELPHONE, EMAIL, ADDRESS) select \'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\', \'%s\' from dual where not exists(select URL from ' % (dataDict['title'], dataDict['desIP'], dataDict['url'], dataDict['date'], dataDict['htmlBody'], dataType, senseGrade,nameStr,idCardStr,telphoneStr,emailStr,adressStr) +mySQLDict['secondDataTable']+' where URL = \'%s\')' % dataDict['url']
			cur1.execute(sql)
			sq6 = 'insert into data_batch(SRC_IP, DES_IP, SessionID, TITLE, URL, DATE, HTML_BODY, DATA_TYPE, NAME, IDCARD, TELPHONE, EMAIL, ADDRESS, SUM) values(\'%s\', \'%s\', \'%s\', \'%s\', \'%s\',\'%s\',\'%s\',\'%s\', \'%s\', \'%s\', \'%s\', \'%s\',\'%s\',\'%s\')' % (dataDict['srcIP'], dataDict['desIP'], dataDict['sessionID'], dataDict['title'], dataDict['url'], dataDict['date'], dataDict['htmlBody'], dataType,nameStr,idCardStr,telphoneStr,emailStr,adressStr,SUM)
			cur6.execute(sq6)
			#print sq6
		except Exception, e:
			print 'operation Table New_mg or Data_Batch error! info:%s' % e
			#print 'telphone:%s' % telphoneStr
	else:
		try:
			sq2 = 'insert into '+ mySQLDict['thirdDataTable'] + '(TITLE, DES_IP, URL, DATE, HTML_BODY) select \'%s\',\'%s\',\'%s\',\'%s\',\'%s\' from dual where not exists(select URL from ' % (dataDict['title'], dataDict['desIP'], dataDict['url'], dataDict['date'], dataDict['htmlBody']) +mySQLDict['thirdDataTable']+' where URL = \'%s\')' % dataDict['url']
			cur2.execute(sq2)
		except Exception, e:
			print 'operation Table New_dd error! info:%s' % e
			
	if dataDict['userName']:
		try:
			sq3 = 'insert into '+ mySQLDict['fourthDataTable'] + '(SRC_IP, DES_IP, URL, SessionID, DATE, userName, passWord) values(\'%s\', \'%s\', \'%s\', \'%s\', \'%s\',\'%s\', \'%s\')' % (dataDict['srcIP'], dataDict['desIP'], dataDict['url'], dataDict['sessionID'], dataDict['date'], dataDict['userName'], md5(dataDict['passwd']))
			cur3.execute(sq3)
			sq5 = 'replace into user_collection(SRC_IP, DES_IP, URL, SessionID, DATE, userName, passWord) values(\'%s\', \'%s\', \'%s\', \'%s\', \'%s\',\'%s\',\'%s\')' % (dataDict['srcIP'], dataDict['desIP'], dataDict['url'], dataDict['sessionID'], dataDict['date'], dataDict['userName'], dataDict['passwd'])
			cur5.execute(sq5)
		except Exception, e:
			print 'operation Table User_mg or User_Collection error! info:%s' % e
	
	if dataDict['type']:
		try:
			sq4 = 'insert into '+ mySQLDict['fifthDataTable'] + '(SRC_IP, DES_IP, TITLE, URL, SessionID, DATE, TYPE, HEAD, Response) values(\'%s\', \'%s\', \'%s\', \'%s\', \'%s\',\'%s\', \'%s\', \'%s\', \'%s\')' % (dataDict['srcIP'], dataDict['desIP'], dataDict['title'], dataDict['url'], dataDict['sessionID'], dataDict['date'], dataDict['type'], dataDict['head'], dataDict['response'])
			cur4.execute(sq4)
		except Exception, e:
			print 'operation Table Scan_Warning error! info:%s' % e
	
def commitDesDataTable(conn, cur1, cur2, cur3, cur4, cur5, cur6):
	conn.commit()
	cur1.close() 
	cur2.close()
	cur3.close()
	cur4.close()
	cur5.close()
	cur6.close()
	conn.close()

	
	
	
	
	
	
	
	
	
	
