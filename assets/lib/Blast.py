#! coding=utf-8

import threading

from ftplib import FTP
import telnetlib
# import paramiko
import re
import socket
import requests
import binascii
import hashlib
import struct
import time
try:
	from queue import Queue
except Exception as e:
	from Queue import Queue

# ssh_client = paramiko.SSHClient()
# ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

lock = threading.Lock()

que_ftp = Queue()
# que_ssh = Queue()
que_telnet = Queue()
que_mysql = Queue()
que_mssql = Queue()
que_mongodb = Queue()
que_redis = Queue()
que_postgresql = Queue()
que_memcached = Queue()
que_elasticsearch = Queue()
que_tomcat = Queue()

que_result = Queue()


def open_dict(path_user, path_pwd):
	user_dict = []
	pwd_dict = []

	for user in open(path_user, 'r') :
		user_dict.append(user.strip())
	for pwd in open(path_pwd, 'r') :
		pwd_dict.append(pwd.strip())

	return user_dict, pwd_dict


class MyThread(threading.Thread):

	def __init__(self, user_list, pwd_list):
		super(MyThread, self).__init__()
		self.user_list = user_list
		self.pwd_list = pwd_list

	def run(self):

		# print('redis is start !')
		while not que_redis.empty():
			host = que_redis.get()
			self.__redis(host)

		# print('mongodb is start !')
		while not que_mongodb.empty():
			host = que_mongodb.get()
			self.__mongodb(host)


		# print('memcached is start !')
		while not que_memcached.empty() :
			host = que_memcached.get()
			self.__memcached(host)

		# print ('elasticsearch is start !')
		while  not que_elasticsearch.empty() :
			host = que_elasticsearch.get()
			self.__elasticsearch(host)

		# print( 'postgresql is start !')
		while not que_postgresql.empty() :
			host = que_postgresql.get()
			self.__postgresql(host)

		# print ('ftp is start !')
		while not que_ftp.empty() :
			host = que_ftp.get()
			self.__ftp(host)

		# print('mssql is start !')
		while not que_mssql.empty() :
			host = que_mssql.get()
			self.__mssql(host)

		# print('telent is start !')
		while not que_telnet.empty() :
			host = que_telnet.get()
			self.__telnet(host)

		# print ('ssh is start !')
		# while not que_ssh.empty() :
		# 	host = que_ssh.get()
		# 	self.__ssh(host)

		# print('mysql is start !')
		while not que_mysql.empty() :
			host = que_mysql.get()
			self.__mysql(host)

		while not que_tomcat.empty() :
			host = que_tomcat.get()
			self.__tomcat(host)

	def __telnet(self, host):
		try:
			tn = telnetlib.Telnet(host, 23, timeout = 2)
			time.sleep(0.5)
			os = tn.read_some()
		except Exception as e:
			# print('telnet:',e)
			return 
		user_match="(?i)(login|user|username)"
		pass_match='(?i)(password|pass)'
		login_match='#|\$|>'
		if re.search(user_match,os):
			for user in self.user_list :
				for pwd in self.pwd_list :
					try:
						tn.write(str(user)+'\r\n')
						tn.read_until(pass_match, timeout = 2)
						tn.write(str(pwd)+'\r\n')
						login_info = tn.read_until(login_match, timeout = 3)
						tn.close()
						if re.search(login_match, login_info):
							lock.acquire()
							que_telnet.put(('telnet', host, '23', user, pwd))
							lock.release()
							return
					except Exception as e:
						# print('telnet:',e)
						pass
		else:
			try:
				info=tn.read_until(user_match, timeout=2)
			except Exception as e:
				# print('telnet:',e)
				return
			if re.search(user_match,info):
				for user in self.user_list :
					for pwd in self.pwd_list :
						try:
							tn.write(str(user) + '\r\n')
							tn.read_until(pass_match, timeout = 2)
							tn.write(str(pwd) + '\r\n')
							login_info = tn.read_until(login_match, timeout = 3)
							tn.close()
							if re.search(login_match,login_info):
								lock.acquire()
								que_telnet.put(('telnet', host, '23', user, pwd))
								lock.release()
								return
						except Exception as e:
							# print ('telnet:',e)
							return 
			elif re.search(pass_match,info):
				for pwd in self.pwd_list :
					tn.read_until(pass_match, timeout = 2)
					tn.write(str(pwd) + '\r\n')
					login_info = tn.read_until(login_match, timeout = 3)
					tn.close()
					if re.search(login_match, login_info):
						lock.acquire()
						que_telnet.put(('telnet', host, '23', '', pwd))
						lock.release()
						return
		
	def __ftp(self, host):
		for user in self.user_list :
			for pwd in self.pwd_list :
				try:
					ftp = FTP(host, timeout = 2)
					if ftp.login() :
						lock.acquire()
						# print ('ftp:\n    host: %-15s 可以匿名登陆！' % host)
						que_result.put(('ftp', host, '21', '', ''))
						ftp.close()
						lock.release()
						return
					elif ftp.login(user, pwd) :
						lock.acquire()
						# print ('ftp:\n    host: %-15suser: %-10spwd: %-20s' % (host, user, pwd))
						que_result.put(('ftp', host, '21', user, pwd))
						ftp.close()
						lock.release()
						return
				except Exception as e:
					# print('ftp:',e)
					pass

	def __ssh(self, host):
		
		for user in self.user_list :
			for pwd in self.pwd_list :
				try:
					ssh = ssh_client.connect(host, user, pwd, timeout = 2)
					lock.acquire()
					# print ('ssh:\n    host: %-15suser: %-10spwd: %-20s' % (host, user, pwd))
					que_result.put(('ssh', host, '22', user, pwd))
					ssh.close()
					lock.release()
					return 
				except Exception as e:
					# print('ssh:',e)
					pass



	def __postgresql(self, host):
		for user in self.user_list :
			for pwd in self.pwd_list :
				try:
					sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
					sock.connect((host, 5431))
					packet_length = len(user) + 7 + len("\x03user  database postgres application_name psql client_encoding UTF8  ")
					p = "%c%c%c%c%c\x03%c%cuser%c%s%cdatabase%cpostgres%capplication_name%cpsql%cclient_encoding%cUTF8%c%c" % ( 0,0,0,packet_length,0,0,0,0,user,0,0,0,0,0,0,0,0)
					sock.send(p)
					packet = sock.recv(1024)
					psql_salt = []
					if packet[0] == 'R':
						a = str([packet[4]])
						b = int(a[4:6],16)
						authentication_type = str([packet[8]])
						c = int(authentication_type[4:6],16)
						if c == 5: psql_salt = packet[9:]
					else : 
						return 
					buf = []
					salt = psql_salt
					lmd5= self._make_response(buf, user, pwd, salt)
					packet_length1 = len(lmd5) + 5 + len('p')
					pp = 'p%c%c%c%c%s%c' % (0,0,0,packet_length1 - 1,lmd5,0)
					sock.send(pp)
					packet1 = sock.recv(1024)
					if packet1[0] == "R":
						lock.acquire()
						que_result.put(('postgresql', host, '5431', user, pwd))
						lock.release()
						return
				except Exception as e:
					# print('postgresql:',e)
					pass

	def __mysql(self, host):
		for user in self.user_list :
			for pwd in self.pwd_list :
				try:
					# print (host,user,pwd)
					sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
					sock.connect((host, 3306))
					packet = sock.recv(254)
					plugin,scramble = self._get_scramble(packet)
					if not scramble: return 
					auth_data = self._get_auth_data(user, pwd, scramble, plugin)
					sock.send(auth_data)
					result = sock.recv(1024)
					if result == "\x07\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00":
						lock.acquire()
						que_result.put(('mysql', host, '3306', user, pwd))
						lock.release()
						return
				except Exception as e:
					# print('mysql:',e)
					pass


	def __mssql(self, host):
		for user in self.user_list :
			for pwd in self.pwd_list :
				try:
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.connect((host, 1433))
					hh=binascii.b2a_hex(host)
					husername=binascii.b2a_hex(user)
					lusername=len(user)
					lpassword=len(pwd)
					ladd=len(host)+len(str(1433))+1
					hladd=hex(ladd).replace('0x','')
					hpwd=binascii.b2a_hex(pwd)
					pp=binascii.b2a_hex(str(1433))
					address=hh+'3a'+pp
					hhost= binascii.b2a_hex(host)
					data="0200020000000000123456789000000000000000000000000000000000000000000000000000ZZ5440000000000000000000000000000000000000000000000000000000000X3360000000000000000000000000000000000000000000000000000000000Y373933340000000000000000000000000000000000000000000000000000040301060a09010000000002000000000070796d7373716c000000000000000000000000000000000000000000000007123456789000000000000000000000000000000000000000000000000000ZZ3360000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000Y0402000044422d4c6962726172790a00000000000d1175735f656e676c69736800000000000000000000000000000201004c000000000000000000000a000000000000000000000000000069736f5f31000000000000000000000000000000000000000000000000000501353132000000030000000000000000"
					data1=data.replace(data[16:16+len(address)],address)
					data2=data1.replace(data1[78:78+len(husername)],husername)
					data3=data2.replace(data2[140:140+len(hpwd)],hpwd)
					if lusername>=16:
						data4=data3.replace('0X',str(hex(lusername)).replace('0x',''))
					else:
						data4=data3.replace('X',str(hex(lusername)).replace('0x',''))
					if lpassword>=16:
						data5=data4.replace('0Y',str(hex(lpassword)).replace('0x',''))
					else:
						data5=data4.replace('Y',str(hex(lpassword)).replace('0x',''))
					hladd = hex(ladd).replace('0x', '')
					data6=data5.replace('ZZ',str(hladd))
					data7=binascii.a2b_hex(data6)
					sock.send(data7)
					packet=sock.recv(1024)
					if 'master' in packet:
						lock.acquire()
						que_result.put(('mssql', host, '1433', user, pwd))
						lock.release()
						return
				except Exception as e:
					# print ('mssql:',e)
					pass
	def __tomcat(self, host):
		try:
			url = 'http://%s:8080/manager/html' % host
			r = requests.get(url, timeout = 2)
			if not re.search(r'Coyote', r.headers['server']) :
				return 
			data = r.text
		except Exception as e:
			return 
		for user in self.user_list :
			for pwd in self.pwd_list :
				try:
					r = requests.get(url, timeout = 2, auth=(user, pwd))
					if r.status_code == '200' :
						lock.acquire()
						que_result.put(('tomcat', host, '8080', user, pwd))
						lock.release()
						return
				except Exception as e:
					return 
				


	def __redis(self, host):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((host, 6379))
			s.send("INFO\r\n")
			result = s.recv(1024)
			if "redis_version" in result:
				que_result.put(('redis', host, '6379', '', ''))
				return 
			elif "Authentication" in result:
				for pwd in self.pwd_list :
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s.connect((host, 6379))
					s.send("AUTH %s\r\n" % (pwd))
					result = s.recv(1024)
					if '+OK' in result:
						lock.acquire()
						que_result.put(('redis', host, '6379', '', ''))
						lock.release()
						return 
		except Exception as e:
			# print('redis:',e)
			return
   
	def __mongodb(self, host):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((host, 27017))
			data = binascii.a2b_hex("3a000000a741000000000000d40700000000000061646d696e2e24636d640000000000ffffffff130000001069736d6173746572000100000000")
			s.send(data)
			result = s.recv(1024)
			if "ismaster" in result:
				getlog_data = binascii.a2b_hex("480000000200000000000000d40700000000000061646d696e2e24636d6400000000000100000021000000026765744c6f670010000000737461727475705761726e696e67730000")
				s.send(getlog_data)
				result = s.recv(1024)
				if "totalLinesWritten" in result:
					lock.acquire()
					que_result.put(('mongodb', host, '27017', '', ''))
					lock.release()
					return 
				else:return 
		except Exception as e:
			# print('mongodb:',e)
			return

	def __memcached(self, host):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((host, 11211))
			s.send("stats\r\n")
			result = s.recv(1024)
			if "version" in result:
				lock.acquire()
				que_result.put(('memcached', host, '11211', '', ''))
				lock.release()
				return 
		except Exception as e:
			# print('memcached:',e)
			return

	def __elasticsearch(self, host):
		try:
			url = "http://" + host + ":" + str(9200) + "/_cat"
			data = requests.get(url).text
			if '/_cat/master' in data:
				lock.acquire()
				que_result.put(('elasticsearch', host, '9200', '', ''))
				lock.release()
				return 
			else:
				return 
		except Exception as e:
			# print('elasticsearch:',e)
			return

	def _get_hash(self, password, scramble):
		hash_stage1 = hashlib.sha1(password).digest()
		hash_stage2 = hashlib.sha1(hash_stage1).digest()
		to = hashlib.sha1(scramble+hash_stage2).digest()
		reply = [ord(h1) ^ ord(h3) for (h1, h3) in zip(hash_stage1, to)]
		hashs = struct.pack('20B', *reply)
		return hashs
	def _get_scramble(self, packet):
		scramble,plugin = '',''
		try:
			tmp = packet[15:]
			m = re.findall("\x00?([\x01-\x7F]{7,})\x00", tmp)
			if len(m)>3:del m[0]
			scramble = m[0] + m[1]
		except:
			return '',''
		try:
			plugin = m[2]
		except:
			pass
		return plugin, scramble
	def _get_auth_data(self, user, password, scramble, plugin):
		user_hex = binascii.b2a_hex(user)
		pass_hex = binascii.b2a_hex(self._get_hash(password,scramble))
		data = "85a23f0000000040080000000000000000000000000000000000000000000000" + user_hex + "0014" + pass_hex
		if plugin: data += binascii.b2a_hex(plugin) + "0055035f6f73076f737831302e380c5f636c69656e745f6e616d65086c69626d7973716c045f7069640539323330360f5f636c69656e745f76657273696f6e06352e362e3231095f706c6174666f726d067838365f3634"
		len_hex = hex(len(data)/2).replace("0x","")
		auth_data = len_hex + "000001" + data
		return binascii.a2b_hex(auth_data)
	def _make_response(self, buf, username, password, salt):
		pu = hashlib.md5(password + username).hexdigest()
		buf = hashlib.md5(pu + salt).hexdigest()
		return 'md5' + buf

def insert_db(db, table_name, host, port, user, pwd):
	scan_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	cursor = db.cursor()
	try:
		sql = '''INSERT INTO %s
		(ip, port, user, pwd, scan_time)
		VALUES
		("%s", "%s", "%s", "%s", "%s");
		''' % (table_name, host, port, user, pwd, scan_time )
		cursor.execute(sql)
		db.commit()
	except Exception as e :
		db.rollback()
		return False
	return True


def Blast(Blast_list, db, table_name):
	try :
		user_list, pwd_list = open_dict('./dict/username', './dict/password')
	except Exception as e :
		user_list, pwd_list = open_dict('username', 'password')
	for ip in Blast_list :
		for port in Blast_list[ip] :
			if port[0] == 21 :
				que_ftp.put(ip)
			# elif port[0] == 22 :
			# 	que_ssh.put(ip)
			elif port[0] == 23 :
				que_telnet.put(ip)
			elif port[0] == 3306 :
				que_mysql.put(ip)
			elif port[0] == 6379 :
				que_redis.put(ip)
			elif port[0] == 27017 :
				que_mongodb.put(ip)
			elif port[0] == 11211 :
				que_memcached.put(ip)
			elif port[0] == 9200 :
				que_elasticsearch.put(ip)
			elif port[0] == 1433 :
				que_mssql.put(ip)
			elif port[0] == 5431 :
				que_postgresql.put(ip)
			elif port[0] == 8080 :
				que_tomcat.put(ip)

	threads = []

	for _ in range(100) :
		t = MyThread(user_list, pwd_list)
		threads.append(t)
		t.setDaemon(True)
		t.start()
	from tqdm import tqdm
	for t in tqdm(threads) :
		t.join()

	while not que_result.empty() :
		result = que_result.get()
		if result[0] == 'ftp' :
			print ('ftp:\n    host: %-15sport:%-8suser: %-10spwd: %-20s' % (result[1], result[2], result[3], result[4]))
			insert_db(db, table_name, result[1], result[2], result[3], result[4])
		# elif result[0] == 'ssh' :
		# 	print ('ssh:\n    host: %-15sport:%-8suser: %-10spwd: %-20s' % (result[1], result[2], result[3], result[4]))
		# 	insert_db(db, table_name, result[1], result[2], result[3], result[4])
		elif result[0] == 'mysql' :
			print ('mysql:\n    host: %-15sport:%-8suser: %-10spwd: %-20s' % (result[1], result[2], result[3], result[4]))
			insert_db(db, table_name, result[1], result[2], result[3], result[4])
		elif result[0] == 'tomcat' :
			print ('tomcat:\n    host: %-15sport:%-8suser: %-10spwd: %-20s' % (result[1], result[2], result[3], result[4]))
			insert_db(db, table_name, result[1], result[2], result[3], result[4])
		elif result[0] == 'telnet' :
			print ('telnet:\n    host: %-15sport:%-8suser: %-10spwd: %-20s' % (result[1], result[2], result[3], result[4]))
			insert_db(db, table_name, result[1], result[2], result[3], result[4])
		elif result[0] == 'mssql' :
			print ('mssql:\n    host: %-15sport:%-8suser: %-10spwd: %-20s' % (result[1], result[2], result[3], result[4]))
			insert_db(db, table_name, result[1], result[2], result[3], result[4])
		elif result[0] == 'postgresql' :
			print ('postgresql:\n    host: %-15sport:%-8suser: %-10spwd: %-20s' % (result[1], result[2], result[3], result[4]))
			insert_db(db, table_name, result[1], result[2], result[3], result[4])
		elif result[0] == 'mongodb' :
			print ('mongodb:\n    host: %-15s' % result[1])
			insert_db(db, table_name, result[1], result[2], result[3], result[4])
		elif result[0] == 'memcached' :
			print ('memcached:\n    host: %-15s' % result[1])
			insert_db(db, table_name, result[1], result[2], result[3], result[4])
		elif result[0] == 'elasticsearch' :
			print ('elasticsearch:\n    host: %-15s' % result[1])
			insert_db(db, table_name, result[1], result[2], result[3], result[4])
		elif result[0] == 'redis' :
			print ('redis:\n    host: %-15s' % result[1])
			insert_db(db, table_name, result[1], result[2], result[3], result[4])


if __name__ == '__main__':
	import json, time
	import pymysql
	db  = pymysql.connect(host = "localhost", user = "root", passwd = "4869", db = "obs", charset = 'utf8' )
	stat_time = time.time()
	Blast_list = json.loads(open('../dict/ports.json', 'r').read(),encoding = 'utf-8')
	Blast({'127.0.0.1':[[3306,'mysql','mariadb'],],'192.168.199.227':[[3306,'mysql','mariadb'],]}, db, '123')
	end_time = time.time()
	print ('time: %s' % (end_time-stat_time))



'''

ftp
ssh
telnet
mysql
mssql
mongodb
redis
postgresql
memcached
elasticsearch


port 21 22 23 1433 3306 5431 27017 6379 11211 9200

ip port

{
	'22':[ip]
	'3306':[ip]
}

lock.acquire()
lock.release()
'''
