import pymysql
def Clint():
	try:
		db = pymysql.connect(host = "localhost", user = "root", passwd = "4869", db = "obs", charset = 'utf8' )
	except Exception:
		db = pymysql.connect(host = "localhost", user = "assets", passwd = "assets", db = "db_assets", charset = 'utf8' )
	
	return db

