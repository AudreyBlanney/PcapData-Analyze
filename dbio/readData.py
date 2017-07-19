#encoding:utf-8  
import sys
import MySQLdb

reload(sys)
sys.setdefaultencoding('utf-8')

def saveTableTest():
	conn=MySQLdb.connect(host='localhost', user='root', passwd='4869', charset='utf8', port=3306) 
	cur=conn.cursor() 
	sql = 'create database if not exists obs default charset utf8'
	cur.execute(sql)
	conn.select_db('obs') 
	
	sql = 'create table if not exists shield_reg' + "(ID int auto_increment, Shield_reg_value VARCHAR(255), Type VARCHAR(64) charset utf8, Description VARCHAR(64), primary key(ID))"
	cur.execute(sql)
	
	filterName1 = u'关闭|高端贷|高架桥|房融贷|乐购贷|乐驾贷|经营贷|乐居贷|车融贷|经营贷|宋体'
	filterName2 = u'高兴|关门|房东|关闭|全选|全不选|保存|终审|查询|全球|无妨|无房|国有|国营|年收入'
	filterName3 = u'广东|方案|计算|支持|相关的|包含|时间|时使用|金融|金盾|无效|万元|申请|司机'
	try: 
		sql1 = 'insert into shield_reg(Shield_reg_value) values(\"' + filterName1 + '\")'
		cur.execute(sql1)
		sql2 = 'insert into shield_reg(Shield_reg_value) values(\"' + filterName2 + '\")'
		cur.execute(sql2)
		sql3 = 'insert into shield_reg(Shield_reg_value) values(\"' + filterName3 + '\")'
		cur.execute(sql3)
	except MySQLdb.Error,e: 
		print 'operation MySql error! info:%s' % e
		
	conn.commit() 
	cur.close() 
	conn.close()
	

def readFilterTable(database, tablename, mySQLDict):
	nameList = []

	try: 
		conn=MySQLdb.connect(host=mySQLDict['host'],user=mySQLDict['user'],passwd=mySQLDict['passwd'],charset='utf8', port=mySQLDict['port'])
		#conn=MySQLdb.connect(host='localhost', user='root', passwd='root', charset='utf8', port=3306) 

		cur=conn.cursor() 
		conn.select_db(database) 
				
		sql = 'select * from '+ tablename
		cur.execute(sql)
		
		rows = cur.fetchall()
			
		cur.close()
		conn.commit()
		conn.close() 
		
		for row in rows:
			#print row[1]
			nameList.append(row[1])
	except Exception,e:
		print 'waring: read shield_reg error! %s' % e
		
	return nameList
		
		
if __name__ == '__main__':  
	#saveTableTest()
	readFilterTable('obs', 'shield_reg', 'll')
