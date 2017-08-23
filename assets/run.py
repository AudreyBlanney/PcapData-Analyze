# coding=utf-8


from flask import Flask, request, make_response
from functools import wraps

from gevent import monkey
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from lib.Social import Social, search_soc
from lib.search_email import search
from lib.get_ip_list import get_ip_list
from lib.get_domain.wydomain import get_domain_api
from lib.port_scan import Nmap
from lib.get_title_requests import get_titles
from lib.Blast import Blast
from lib.Cron import Crons
from configs import Clint

import os
import json
import shutil
import time
import re
import string, random
import threading
import log

monkey.patch_all()
app = Flask(__name__)
app.config.update(
    DEBUG=True
)

#返回值为受影响的行数和结果集
def select_db(table, columns, columns_name1, wheres1, columns_name2, wheres2):
	db = Clint()
	cursor = db.cursor()
	sql = 'select %s from %s where %s = "%s" and %s = "%s"' % (columns, table, columns_name1, wheres1, columns_name2, wheres2)
	# print (sql)
	try :
		result = cursor.execute(sql)
		results = cursor.fetchall()
	except Exception as e :
		print (e)
		db.close()
		return False
	db.close()
	return result,results

def create_db_soc(table):
	db = Clint()
	cursor = db.cursor()
	try:
		cursor.execute('''CREATE TABLE IF NOT EXISTS %s (
			id INT NOT NULL AUTO_INCREMENT,
			root_domain VARCHAR(100) DEFAULT '' COMMENT '',
			root_domain_email VARCHAR(100) DEFAULT '' COMMENT '***@root_domain.*** email', 
			social_name VARCHAR(100) DEFAULT '' COMMENT 'Domain name of the registrant',
			social_mail VARCHAR(100) DEFAULT '' COMMENT 'Domain name registration mailbox',
			social_pwd VARCHAR(100) DEFAULT '' COMMENT 'Domain name registrar mailbox password',
			social_source VARCHAR(100) DEFAULT '' COMMENT 'Domain Name Registrant Email Source',
			scan_time VARCHAR(19) DEFAULT '' NOT NULL COMMENT 'Scan time',
			PRIMARY KEY ( id )
		) ENGINE=InnoDB DEFAULT CHARSET=utf8;
			''' % table)
		db.commit()
	except Exception as e :
		db.rollback()
		db.close()
		return False
	db.close()
	return True


def create_db(table):
	db = Clint()
	cursor = db.cursor()
	try:
		cursor.execute('''CREATE TABLE IF NOT EXISTS %s (
			id INT NOT NULL AUTO_INCREMENT, 
			root_domain VARCHAR(50) DEFAULT '' COMMENT 'The root domain name',
			domain VARCHAR(50) DEFAULT '' COMMENT 'secondary domain', 
			title VARCHAR(100) DEFAULT '' NOT NULL COMMENT 'domain name corresponding to the business', 
			ip VARCHAR(50) DEFAULT '' NOT NULL COMMENT 'Have the ip', 
			port VARCHAR(50) DEFAULT '' NOT NULL COMMENT 'Open ports', 
			service VARCHAR(50) DEFAULT '' NOT NULL COMMENT 'Port corresponding to the service',
			service_info VARCHAR(50) DEFAULT '' NOT NULL COMMENT 'fu wu xie xi',
			scan_time varchar(19) DEFAULT '' NOT NULL  COMMENT 'Scan time',
			is_confirm_port TINYINT(1)  NOT NULL DEFAULT '0' COMMENT 'Whether the port is open',
			is_confirm TINYINT(1)  NOT NULL DEFAULT '0' COMMENT 'Whether the db is open',
			domain_header VARCHAR(100) DEFAULT '' COMMENT 'domain fuzeren',
			domain_remark VARCHAR(100) DEFAULT '' COMMENT 'domains beizhu',
			root_domain_header VARCHAR(100) DEFAULT '' COMMENT 'root domains fuzeren',
			root_domain_remark VARCHAR(100) DEFAULT '' COMMENT 'root domains beizhu',
			ip_header VARCHAR(100) DEFAULT '' COMMENT 'ip fuzeren',
			ip_remark VARCHAR(100) DEFAULT '' COMMENT 'ip beizhu',
			port_remark VARCHAR(100) DEFAULT '' ,
			PRIMARY KEY ( id )
		) ENGINE=InnoDB DEFAULT CHARSET=utf8;
			''' % table)
		db.commit()
	except Exception as e :
		db.rollback()
		db.close()
		return False
	db.close()
	return True

# execute sql
def execute_db(sql):
	db = Clint()
	cursor = db.cursor()
	try:
		cursor.execute(sql)
		db.commit()
	except Exception as e :
		db.rollback()
		db.close()
		return False
	db.close()
	return True

def getRootDoamin(domain):
	res = re.search(r'([a-zA-Z0-9-]+?)\.(com\.cn|edu\.cn|gov\.cn|org\.cn|net\.cn|gq|hk|im|info|la|mobi|so|tech|biz|co|tv|me|cc|org|net|cn|com)$', domain)
	if res == None:
		return False
	return res.group(0)


def allow_cross_domain(fun):
	@wraps(fun)
	def wrapper_fun(*args, **kwargs):
		rst = make_response(fun(*args, **kwargs))
		rst.headers['Access-Control-Allow-Origin'] = '*'
		rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
		allow_headers = "Referer,Accept,Origin,userid-Agent"
		rst.headers['Access-Control-Allow-Headers'] = allow_headers
		return rst
	return wrapper_fun

def remove_dir(rootdir):
	filelist=[]
	filelist=os.listdir(rootdir)
	for f in filelist:
		filepath = os.path.join( rootdir, f )
		if os.path.isfile(filepath):
			os.remove(filepath)
		elif os.path.isdir(filepath):
			shutil.rmtree(filepath,True)

def random_md5():
	try:
		md5 = ''
		strs = string.ascii_letters + string.digits
		for _ in range(32) :
			md5 = md5 + random.choice(strs)
	except Exception as e:
		log.logger.error(e)
	return md5

def get_domains(domain,userid,openid):
	path = './results/%s/root_domain.json' % domain
	if os.path.exists(path):
		try:
			root_domain = json.loads(open(path, 'r').read(),encoding = 'utf-8')

			# the domain find
			domains = get_domain_api(root_domain)
			if not domains:
				jsons = {'error':True,  'msgs':'Access to the secondary domain name error!', "trse":True}
				return json.dumps(jsons)

			#  write doamins to json file
			with open('./results/%s/domains.json' % domain, 'w') as f:
				f.write(json.dumps(domains))

			jsons = {'error':False, 'msgs':50}
			return json.dumps(jsons)
		except Exception as e:
			log.logger.error(e)
	else :
		jsons = {'error':True,  'msgs':'Wrong domain/ip !', "trse":False}
		return json.dumps(jsons)

def get_port(domain,userid,openid,lict):
	if lict == 'list' :
		try:
			path = './results/%s/ip_list.json' % domain
			if os.path.exists(path):
				domains = json.loads(open(path, 'r').read(), encoding = 'utf-8')
				ip_list = domains
			else:
				jsons = {'error':True,  'msgs':'Wrong IP Path!', "trse":False}
				return json.dumps(jsons)
		except Exception as e:
			log.logger.error(e)

	elif lict == 'dict' :
		try:
			path = './results/%s/domains.json' % domain
			if os.path.exists(path):
				domains = json.loads(open(path, 'r').read(), encoding = 'utf-8')
				ip_list = []
				for root_domain in domains:
					for domain_ in domains[root_domain]:
						ip_list.extend(domains[root_domain][domain_])
				ip_list = list(set(ip_list))
			else :
				jsons = {'error':True,  'msgs':'Wrong domains Path!', "trse":False}
				return json.dumps(jsons)
		except Exception as e:
			log.logger.error(e)
	else :
		jsons = {'error':True,  'msgs':'Wrong domain/ip ! ', "trse":False}
		return json.dumps(jsons)

	ports = Nmap(ip_list)

	if not ports:
		jsons = {'error':True,  'msgs':'Error getting port info!', "trse":True}
		return json.dumps(jsons)

	# write port to json file
	json_path = './results/%s/ports.json' % domain
	with open(json_path, 'w') as f:
		f.write(json.dumps(ports))

	jsons = {'error':False, 'msgs':75}
	return json.dumps(jsons)

def get_title(domain,userid,openid,lict):
	if lict == 'list' :
		try:
			path = './results/%s/ip_list.json' % domain
			if os.path.exists(path):
				domains = json.loads(open(path, 'r').read(), encoding = 'utf-8')
				host = domains
				# get title
				titles = get_titles(host)

				if not titles:
					jsons = {'error':True,  'msgs':'Error getting business info!', "trse":True}
					return json.dumps(jsons)

				#  write title to json file
				json_path = './results/%s/titles.json' % domain
				with open(json_path, 'w') as f:
					f.write(json.dumps(titles))

				jsons = {'error':False, 'msgs':95}
				return json.dumps(jsons)
			else:
				jsons = {'error':True,  'msgs':'Wrong IP Path !', "trse":False}
				return json.dumps(jsons)
		except Exception as e:
			log.logger.error(e)

	elif lict == 'dict' :
		try:
			path = './results/%s/domains.json' % domain
			if os.path.exists(path) :
				domains = json.loads(open(path, 'r').read(),encoding = 'utf-8')
				host = []
				for root_domain in domains:
					for domain_ in domains[root_domain]:
						host.append(domain_)

				# get title
				titles = get_titles(host)

				if not titles:
					jsons = {'error':True,  'msgs':'Error getting business info!', "trse":True}
					return json.dumps(jsons)

				# write title to json file
				json_path = './results/%s/titles.json' % domain
				with open(json_path, 'w') as f:
					f.write(json.dumps(titles))

				jsons = {'error':False, 'msgs':95}
				return json.dumps(jsons)

			else:
				jsons = {'error':True,  'msgs':'Wrong Domain Path!', "trse":False}
				return json.dumps(jsons)
		except Exception as e:
			log.logger.error(e)
	else :
		jsons = {'error':True,  'msgs':'Wrong domain/ip ! ', "trse":False}
		return json.dumps(jsons)

def database(domain,userid,openid,lict):
	scan_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	if lict == 'list' :
		try:
			# create table
			name = domain.replace('.', '_')
			table_name = name.replace('-', '_')

			if not create_db( table_name):
				jsons = {'error':True,  'msgs':'Failed to create table!', "trse":False}
				return json.dumps(jsons)

			#  get ip，port，service，title
			ports = json.loads(open('./results/%s/ports.json' % domain, 'r').read(),encoding = 'utf-8')
			titles = json.loads(open('./results/%s/titles.json' % domain, 'r').read(),encoding = 'utf-8')

			print ('start to inster db ')
			# inster
			for ip in ports :
				for port in ports[ip]:
					if not port[0] :
						continue

					sql = '''INSERT INTO %s (title, ip, port,  service, service_info, scan_time)
											VALUES
											("%s", "%s", "%s", "%s", "%s", "%s")
											''' % (
					table_name, titles[ip], ip, port[0], port[1], port[2], scan_time)
					execute_db(sql)
			jsons = {'error':False, 'msgs':100, 'task':table_name}
			return json.dumps(jsons)
		except Exception as e:
			log.logger.error(e)
	elif lict == 'dict' :
		try:
			# get table name
			name = domain.replace('.', '_')
			table_name = name.replace('-', '_')
			table_name_social = table_name + '_social'

			# create table
			if not create_db( table_name):
				jsons = {'error':True,  'msgs':'Failed to create table!', "trse":False}
				return json.dumps(jsons)
			if not create_db_soc(table_name_social):
				jsons = {'error':True,  'msgs':'Failed to create table_social!', "trse":False}
				return json.dumps(jsons)
			# get root_domain, domain, title, ip, port, service
			root_domains = json.loads(open('./results/%s/root_domain.json' % domain, 'r').read(),encoding = 'utf-8')
			domains = json.loads(open('./results/%s/domains.json' % domain, 'r').read(),encoding = 'utf-8')
			ports = json.loads(open('./results/%s/ports.json' % domain, 'r').read(),encoding = 'utf-8')
			titles = json.loads(open('./results/%s/titles.json' % domain, 'r').read(),encoding = 'utf-8')
			soc = json.loads(open('./results/%s/social.json' % domain, 'r').read(),encoding = 'utf-8')
			emails = json.loads(open('./results/%s/email.json' % domain, 'r').read(),encoding = 'utf-8')
			print ('start to inster db ')
			# inster
			for root_domain in emails :
				for email in emails[root_domain] :
					for social in soc[root_domain] :
						if len(social) == 1 :
							continue
						elif len(social) == 2 :
							social_name = ''
							social_mail = social[0]
							social_pwd = social[1]
							social_source = ''
						elif len(social) == 3 :
							social_name = social[0]
							social_mail = social[2]
							social_pwd = social[1]
							social_source = ''
						elif len(social) == 4 :
							social_name = social[0]
							social_mail = social[1]
							social_pwd = social[2]
							social_source = social[3]

						sql = '''INSERT INTO %s (root_domain, root_domain_email, social_name, social_mail, social_pwd, social_source, scan_time)
								VALUES
								("%s", "%s", "%s", "%s", "%s", "%s", "%s")
								''' % (table_name_social, root_domain, email, social_name, social_mail, social_pwd, social_source, scan_time)
						# print (sql)
						execute_db(sql)

			for root_domain in root_domains :
				for domain in domains[root_domain] :
					for ip in domains[root_domain][domain] :
						for port in ports[ip] :
							sql = '''INSERT INTO %s (root_domain, domain, title, ip, port, service, service_info, scan_time) 
							VALUES
							("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")
							''' % (table_name, root_domain, domain, titles[domain], ip, port[0], port[1], port[2], scan_time)
							execute_db(sql)

			jsons = {'error':False, 'msgs':100, 'task':table_name}
			return json.dumps(jsons)
		except Exception as e:
			log.logger.error(e)
	else :
		jsons = {'error':True,  'msgs':'Wrong database parameters!', "trse":False}
		return json.dumps(jsons)

def blast(domain,userid,openid):
	path = './results/%s/ports.json' % domain
	name = domain.replace('.', '_')
	table = name.replace('-', '_') + '_blast'
	db = Clint()
	cursor = db.cursor()
	try:
		cursor.execute('''CREATE TABLE IF NOT EXISTS %s
			(id INT NOT NULL AUTO_INCREMENT, 
			ip VARCHAR(50) DEFAULT '' NOT NULL COMMENT 'Scan the ip',
			port VARCHAR(50) DEFAULT '' NOT NULL COMMENT 'Scanned port', 
			user VARCHAR(50) DEFAULT '' NOT NULL COMMENT 'The corresponding user name', 
			pwd VARCHAR(100) DEFAULT '' NOT NULL COMMENT 'The corresponding password', 
			`level` VARCHAR (16) DEFAULT 'high' COMMENT 'level',
			scan_time VARCHAR(19) DEFAULT ''NOT NULL COMMENT 'Scan time',
			PRIMARY KEY ( id )) ENGINE=InnoDB DEFAULT CHARSET=utf8;
			''' % table)
		db.commit()
	except Exception as e :
		print (e)
		db.rollback()
		jsons = {'error':True,  'msgs':'Can`t create table Blast !', "trse":False}
		return json.dumps(jsons)
	if os.path.exists(path):
		ports = json.loads(open(path, 'r').read(), encoding = 'utf-8')
		# Blast(ports,  table)
		t = threading.Thread(target = Blast, args = (ports, db, table,))
		t.start()
		t.join()
		jsons = {'error':False,  'msgs':'ok'}
		return json.dumps(jsons)
	else :
		jsons = {'error':True,  'msgs':'Wrong ports file path!', "trse":False}
		return json.dumps(jsons)

#添加定时任务
def add_cron(domain,crontab,taskid,userid,openid,cron_tpye,lict):
	try:
		con = Crons()
		result = con.add_job(str(taskid), str(crontab), domain, str(userid), str(openid),cron_tpye,lict)
		if not result :
			jsons = {taskid:False}
		else :
			jsons = {taskid:True}
	except Exception as e:
		log.logger.error(e)
	return json.dumps(jsons)

#删除定时任务
@app.route('/del_cron', methods = ['GET', 'POST'])
@allow_cross_domain
def del_cron():
	try:
		taskid = request.args.get('taskid')
		userid = request.args.get('userid')
		openid = request.args.get('openid')
		select_result = select_db( 'tb_userinfo', 'openid', 'id', userid, 'openid', openid)
		if select_result[0] == 0 or not openid :
			jsons = {'error':True, 'msgs':'Authentication failed!', "trse":False}
			return json.dumps(jsons)

		con = Crons()
		result = con.del_job(str(taskid))
		if not result :
			jsons = {taskid:True}
		else :
			jsons = {taskid:False}
	except Exception as e:
		log.logger.error(e)
	return json.dumps(jsons)

# 新建/修改保存添加定时扫描
@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@allow_cross_domain
def index():
	ip = request.args.get('ip')
	domain = request.args.get('domain')
	userid = request.args.get('userid')
	openid = request.args.get('openid')

	select_result = select_db('tb_userinfo', 'openid', 'id', userid, 'openid', openid)
	if select_result[0] == 0 or not openid:
		jsons = {'error': True, 'msgs': 'Authentication failed!', "trse": False}
		return json.dumps(jsons)

	if domain and not ip :
		try:
			# the root_domain is true or false
			domain = getRootDoamin(domain)
			if not domain:
				jsons = {'error':True, 'msgs':'Enter the domain name is wrong!', "trse":True}
				return json.dumps(jsons)

			if not os.path.exists('./results/%s' % domain):
				os.mkdir('./results/%s' % domain)

			lict = 'dict'
			# 查看数据库是否有这个域名
			select_result = select_db('tb_message', 'cron_type', 'userid', userid, 'domainip', domain)
			if select_result[0] == 0:
				jsons = {'error': True, 'msgs': 'Failed to create domain!', "trse": False}
				return json.dumps(jsons)
			cron_type = select_result[1][0][0]

			# #查找定时时间并添加定时任务
			if cron_type == 0:
				#查找一次扫描时间
				select_time = select_db('tb_message', 'date_time', 'userid', userid, 'domainip', domain)
				if select_time[0] == 0:
					jsons = {'error': True, 'msgs': 'Failed to create datetime!', "trse": False}
					return json.dumps(jsons)
				#查找taskid
				select_taskid = select_db('tb_message', 'taskid', 'userid', userid, 'domainip', domain)
				if select_taskid[0] == 0:
					jsons = {'error': True, 'msgs': 'Failed to create domainip!', "trse": False}
					return json.dumps(jsons)

				taskid = select_taskid[1][0][0]
				crontab = select_time[1][0][0]
				con = Crons()
				cron_delete = con.del_job(str(taskid))
				if not cron_delete:
					cron = add_cron(domain,str(crontab),str(taskid),userid,openid,str(cron_type),lict)
					if json.loads(cron)[taskid] == True:
						sql = 'UPDATE tb_message SET scan_status = 0 WHERE userid = "%s" and domainip = "%s"' % (userid, domain)
						execute_db(sql)
						jsons = {'error':False,'msgs':'Added timed task success'}
						return json.dumps(jsons)
			elif cron_type == 1:
				#查找周期扫描
				select_time = select_db('tb_message', 'week_time', 'userid', userid, 'domainip', domain)
				if select_time[0] == 0:
					jsons = {'error': True, 'msgs': 'Failed to create weektime!', "trse": False}
					return json.dumps(jsons)

				#查找taskid
				select_taskid = select_db('tb_message', 'taskid', 'userid', userid, 'domainip', domain)
				if select_taskid[0] == 0:
					jsons = {'error': True, 'msgs': 'Failed to create domainip!', "trse": False}
					return json.dumps(jsons)

				taskid = select_taskid[1][0][0]
				crontab = select_time[1][0][0]
				con = Crons()
				cron_delete = con.del_job(str(taskid))
				if not cron_delete:
					cron = add_cron(domain, str(crontab), str(taskid), userid, openid, str(cron_type), lict)
					if json.loads(cron)[taskid] == True:
						sql = 'UPDATE tb_message SET scan_status = 0 WHERE userid = "%s" and domainip = "%s"' % (userid, domain)
						execute_db(sql)
						jsons = {'error': False, 'msgs': 'Added timed task success'}
						return json.dumps(jsons)
			else:
				jsons = {'error': True, 'msgs': 'Failed to create task!', "trse": False}
				return json.dumps(jsons)
		except Exception as e:
			log.logger.error(e)

	elif ip and not domain:
		try:
			ip_list = get_ip_list(ip)
			if not ip_list:
				jsons = {'error':True, 'msgs':'Input ip wrong!', "trse":True}
				return json.dumps(jsons)

			if not os.path.exists('./results/%s' % ip):
				os.mkdir('./results/%s' % ip)

			# # write ips to json file
			with open('./results/%s/ip_list.json' % ip, 'w') as f:
				f.write(json.dumps(ip_list))
			lict = 'list'

			#查看数据库是否有ｉｐ段
			select_result = select_db('tb_message', 'cron_type', 'userid', userid, 'domainip',ip)
			if select_result[0] == 0:
				jsons = {'error': True, 'msgs': 'Failed to create ip!', "trse": False}
				return json.dumps(jsons)
			cron_type = select_result[1][0][0]

			# # 查找定时时间并添加定时任务
			if cron_type == 0:
				# 查找一次扫描时间
				select_time = select_db('tb_message', 'date_time', 'userid', userid, 'domainip',ip)
				if select_time[0] == 0:
					jsons = {'error': True, 'msgs': 'Failed to create datetime!', "trse": False}
					return json.dumps(jsons)

				# 查找taskid
				select_taskid = select_db('tb_message', 'taskid', 'userid', userid, 'domainip', ip)
				if select_taskid[0] == 0:
					jsons = {'error': True, 'msgs': 'Failed to create domainip!', "trse": False}
					return json.dumps(jsons)

				taskid = select_taskid[1][0][0]
				crontab = select_time[1][0][0]
				con = Crons()
				cron_delete = con.del_job(str(taskid))
				if not cron_delete:
					cron = add_cron(ip, str(crontab), str(taskid), userid, openid, str(cron_type), lict)
					if json.loads(cron)[taskid] == True:
						sql = 'UPDATE tb_message SET scan_status = 0 WHERE userid = "%s" and domainip = "%s"' % (userid, ip)
						execute_db(sql)
						jsons = {'error': False, 'msgs': 'Added timed task success'}
						return json.dumps(jsons)
			elif cron_type == 1:
				# 查找周期扫描
				select_time = select_db('tb_message', 'week_time', 'userid', userid, 'domainip', ip)
				if select_time[0] == 0:
					jsons = {'error': True, 'msgs': 'Failed to create weektime!', "trse": False}
					return json.dumps(jsons)
				# 查找taskid
				select_taskid = select_db('tb_message', 'taskid', 'userid', userid, 'domainip', ip)
				if select_taskid[0] == 0:
					jsons = {'error': True, 'msgs': 'Failed to create domainip!', "trse": False}
					return json.dumps(jsons)

				taskid = select_taskid[1][0][0]
				crontab = select_time[1][0][0]
				con = Crons()
				cron_delete = con.del_job(str(taskid))
				if not cron_delete:
					cron = add_cron(ip, str(crontab), str(taskid), userid, openid, str(cron_type), lict)
					if json.loads(cron)[taskid] == True:
						sql = 'UPDATE tb_message SET scan_status = 0 WHERE userid = "%s" and domainip = "%s"' % (userid, ip)
						execute_db(sql)
						jsons = {'error': False, 'msgs': 'Added timed task success'}
						return json.dumps(jsons)
			else:
				jsons = {'error': True, 'msgs': 'Failed to create task!', "trse": False}
				return json.dumps(jsons)
		except Exception as e:
			log.logger.error(e)
	else :
		jsons = {'error':True,  'msgs':'Submitted data error!', "trse":False}
		return json.dumps(jsons)

#更新（临时扫描:域名／用户ｉｄ／openid）
@app.route('/update', methods = ['GET', 'POST'])
@allow_cross_domain
def assets_update():
	domainip = request.args.get('domainip')
	userid = request.args.get('userid')
	openid = request.args.get('openid')
	lict = request.args.get('lict')
	try:

		select_result = select_db('tb_message', 'cron_type', 'userid', userid, 'domainip', domainip)
		#判断域名或ｉｐ是否入库
		if select_result[0] == 0:
			jsons = {'error': True, 'msgs': 'Failed to create domainip!', "trse": False}
			return json.dumps(jsons)
		else:
			sql = 'UPDATE tb_message SET scan_status = 1 WHERE userid = "%s" and domainip = "%s"' % (userid,domainip)
			execute_db(sql)
	except Exception as e:
		log.logger.error(e)

	if lict == 'dict':
		try:
			from lib.get_root_domain_api import get_root_domain
			root_domain = get_root_domain(domainip)
			if not root_domain:
				jsons = {'error':True, 'msgs':'Get root domain error!', "trse":True}
				return json.dumps(jsons)

			soc = Social(root_domain)#对比社工库

			emil_result = search(root_domain)#查找员工邮箱

			for root_domains in emil_result	:
				for email in emil_result[root_domains] :
					if root_domains not in soc :
						soc[root_domains] = search_soc(email)
					else :
						soc[root_domains].extend(search_soc(email))

			# write root_domain to json file
			with open('./results/%s/root_domain.json' % domainip, 'w') as f:
				f.write(json.dumps(root_domain))

			with open('./results/%s/social.json' % domainip, 'w') as f:
				f.write(json.dumps(soc))

			with open('./results/%s/email.json' % domainip, 'w') as f:
				f.write(json.dumps(emil_result))

			domains_result = get_domains(domainip,userid, openid)
			if json.loads(domains_result)['error'] == True:
				sql = 'UPDATE tb_message SET scan_status = 3,WHERE userid = "%s"and domainip = "%s"' % (userid, domainip)
				execute_db(sql)
				return domains_result

			port_result = get_port(domainip,userid, openid,lict)
			if json.loads(port_result)['error'] == True:
				sql = 'UPDATE tb_message SET scan_status = 3,WHERE userid = "%s"and domainip = "%s"' % (userid, domainip)
				execute_db(sql)
				return port_result

			title_result = get_title(domainip,userid, openid,lict)
			if json.loads(title_result)['error'] == True:
				sql = 'UPDATE tb_message SET scan_status = 3,WHERE userid = "%s"and domainip = "%s"' % (userid, domainip)
				execute_db(sql)
				return title_result

			database_result = database(domainip,userid, openid,lict)
			if json.loads(database_result)['error'] == True:
				sql = 'UPDATE tb_message SET scan_status = 3,WHERE userid = "%s"and domainip = "%s"' % (userid, domainip)
				execute_db(sql)
				return database_result

			#更新扫描状态
			update_time= time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
			name = domainip.replace('.', '_')
			table_name = name.replace('-', '_')
			sql = 'UPDATE tb_message SET scan_status = 2,update_time = "%s",map_table="%s" WHERE userid = "%s" and domainip = "%s"' % (update_time,table_name,userid,domainip)
			execute_db(sql)

			jsons = {'error': False, 'msgs': 'Scan success!'}
			return json.dumps(jsons)
		except Exception as e:
			log.logger.error(e)
	elif lict == 'list':
		try:
			title_result = get_title(domainip, userid, openid, lict)
			if json.loads(title_result)['error'] == True:
				sql = 'UPDATE tb_message SET scan_status = 3,WHERE userid = "%s"and domainip = "%s"' % (userid, domainip)
				execute_db(sql)
				return title_result

			port_result = get_port(domainip, userid, openid, lict)
			if json.loads(port_result)['error'] == True:
				sql = 'UPDATE tb_message SET scan_status = 3,WHERE userid = "%s"and domainip = "%s"' % (userid, domainip)
				execute_db(sql)
				return port_result

			database_result = database(domainip, userid, openid, lict)
			if json.loads(database_result)['error'] == True:
				sql = 'UPDATE tb_message SET scan_status = 3,WHERE userid = "%s"and domainip = "%s"' % (userid, domainip)
				execute_db(sql)
				return database_result

			blast_result = blast(domainip, userid, openid)
			if json.loads(blast_result)['error'] == True:
				sql = 'UPDATE tb_message SET scan_status = 3,WHERE userid = "%s"and domainip = "%s"' % (userid, domainip)
				execute_db(sql)
				return blast_result

			#更新扫描状态
			update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
			name = domainip.replace('.', '_')
			table_name = name.replace('-', '_')
			sql = 'UPDATE tb_message SET scan_status = 2,update_time = "%s",map_table = "%s" WHERE userid = "%s"and domainip = "%s"'%(update_time,table_name,userid,domainip)
			execute_db(sql)

			jsons = {'error':False, 'msgs': 'Scan success!'}
			return json.dumps(jsons)
		except Exception as e:
			log.logger.error(e)
	else :
		jsons = {'error':False,  'msgs':'Wrong domainip information!', "trse":False}
		return json.dumps(jsons)

if __name__ == '__main__':
	# remove_dir('./results')
	#app.run(host = '0.0.0.0', threaded = True)
	http_server = WSGIServer(('0.0.0.0',5000), app, handler_class=WebSocketHandler)
    	http_server.serve_forever()

