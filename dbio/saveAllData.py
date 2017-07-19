#encoding:utf-8  
import sys
import MySQLdb
#import base64

reload(sys)
sys.setdefaultencoding('utf-8')

def getMainDataTableHandle(mySQLDict):
	conn=MySQLdb.connect(host=mySQLDict['host'], user=mySQLDict['user'], passwd=mySQLDict['passwd'], charset='utf8', port=mySQLDict['port']) 
	cur=conn.cursor() 
	sql = 'create database if not exists ' + mySQLDict['database'] +' default charset utf8'
	cur.execute(sql)
	conn.select_db(mySQLDict['database']) 
	sql = 'create table if not exists ' + mySQLDict['mainDataTable'] +"(ID int auto_increment, SRC_IP VARCHAR(32), DES_IP VARCHAR(32), URL text charset utf8, SessionID VARCHAR(255), TITLE text charset utf8, HEAD mediumtext charset utf8, DATE VARCHAR(32), Response mediumtext charset utf8, HTML_BODY mediumtext charset utf8, Submit VARCHAR(8), Submit_value mediumtext charset utf8, primary key(ID))"

	cur.execute(sql)
	return conn, cur
	
def saveDatatoMainDB(mySQLDict, dataDict, cur):
	dataDict['head'] = MySQLdb.escape_string(dataDict['head'])
	dataDict['htmlBody'] = MySQLdb.escape_string(dataDict['htmlBody'])
	dataDict['response'] = MySQLdb.escape_string(dataDict['response'])
	
	try: 
		sql = 'insert into '+ mySQLDict['mainDataTable'] + '(SRC_IP, DES_IP, URL, SessionID, TITLE, HEAD, DATE, Response, HTML_BODY, Submit, Submit_value) values(\'%s\', \'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\', \'%s\',\'%s\', \'%s\')' % (dataDict['srcIP'], dataDict['desIP'], dataDict['url'],dataDict['sessionID'],dataDict['title'], dataDict['head'], dataDict['date'], dataDict['response'], dataDict['htmlBody'], dataDict['submit'], dataDict['submitValue'])
		cur.execute(sql)
	except MySQLdb.Error,e: 
		print 'saveAllDate, operation Table Json_Log error! info:%s' % e
		print sql
	
def commitMainDataTable(conn, cur):
	conn.commit() 
	cur.close() 
	conn.close()
