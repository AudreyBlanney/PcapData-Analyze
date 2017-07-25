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
	sql = 'create table if not exists ' + mySQLDict['mainDataTable'] +"(id int auto_increment, src_ip VARCHAR(32), des_ip VARCHAR(32), url text charset utf8, sessionid VARCHAR(255), title text charset utf8, head mediumtext charset utf8, date VARCHAR(32), response mediumtext charset utf8, html_body mediumtext charset utf8,submit VARCHAR(8),submit_value mediumtext charset utf8, primary key(id))"

	cur.execute(sql)
	return conn, cur
	
def saveDatatoMainDB(mySQLDict, dataDict, cur):
	dataDict['head'] = MySQLdb.escape_string(dataDict['head'])
	dataDict['htmlBody'] = MySQLdb.escape_string(dataDict['htmlBody'])
	dataDict['response'] = MySQLdb.escape_string(dataDict['response'])
	
	try: 
		sql = 'insert into '+ mySQLDict['mainDataTable'] + '(src_ip, des_ip, url, sessionid, title, head, date, response, html_body,submit,submit_value) values(\'%s\', \'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\', \'%s\',\'%s\', \'%s\')' % (dataDict['srcIP'], dataDict['desIP'], dataDict['url'],dataDict['sessionID'],dataDict['title'], dataDict['head'], dataDict['date'], dataDict['response'], dataDict['htmlBody'], dataDict['submit'], dataDict['submitValue'])
		cur.execute(sql)
	except MySQLdb.Error,e: 
		print 'saveAllDate, operation Table Json_Log error! info:%s' % e
		print sql
	
def commitMainDataTable(conn, cur):
	conn.commit() 
	cur.close() 
	conn.close()
