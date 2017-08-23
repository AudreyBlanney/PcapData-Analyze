#! /usr/bin/python
# coding=utf-8

'''
    进行根域名发现，使用爱站、站长之家、alexa、links的api，输入一个厂商的一个根域名，获取所有的根域名。
'''
import re
import requests

# get请求函数
def request_get(url, cookies = {}):
	try:
		r = requests.get(url, cookies = cookies, timeout = 2)
		r.encoding = r.apparent_encoding
	except Exception as e:
		print ('can`t link the url: %s' % url)
		print (e)
		return False,False

	data = r.text
	cookies = r.cookies
	return data,cookies

# POST请求函数
def request_post(url, data, cookies = {}):
	try:
		r = requests.post(url, data, cookies = cookies, timeout = 2)
		r.encoding = r.apparent_encoding
	except Exception as e:
		print ('can`t link the url: %s' % url)
		print (e)
		return False,False

	data = r.text
	cookies = r.cookies
	return data,cookies

# 获取主域名函数，从域名获取主域名
def getRootDoamin(domain):
	res = re.search(r'([a-zA-Z0-9-]+?)\.(com\.cn|edu\.cn|gov\.cn|org\.cn|net\.cn|gq|hk|im|info|la|mobi|so|tech|biz|co|tv|me|cc|org|net|cn|com)$', domain)
	if res == None:
		return ''
	return res.group(0)

# 主函数，获取主域名，参数为单个域名str
def get_root_domain(root_doamin):
	print ('Get the main domain name!')
	
	root_doamin_list = []

	url_aizhan = 'http://icp.aizhan.com/%s' % root_doamin
	url_chinaz = 'http://icp.chinaz.com'
	data_chinaz = {'type':'host', 's':root_doamin,}
	url_alexa =  'http://icp.alexa.cn/index.php?q=%s' % root_doamin
	url_links = 'http://beian.links.cn/beian.asp?beiantype=domain&keywords=%s' % root_doamin

	# 判断主域名是否正确
	if request_get('http://www.%s' % root_doamin) :
		root_doamin = getRootDoamin(root_doamin)
		root_doamin_list.append(root_doamin)

		# aizhan.com 
		# 判断aizhan是否可以访问
		data,cookies = request_get('http://icp.aizhan.com')
		if data :
			data, cookies = request_get(url_aizhan,cookies)
			# print (data)
			if data :
				res_domain = r'<tr style="text-align:center;">.*?<td>.*?</td>.*?<td>.*?</td>.*?<td>(.*?)</td>\n'
				# 正则获取域名信息
				root_doamin_re = re.findall(res_domain, data, re.S)
				for x in root_doamin_re:
					if x != None:
						x = getRootDoamin(x.strip())
						# print (x)
						if x == '' :
							continue
						if x not in root_doamin_list :
							print ('aizhan: ',x)
							root_doamin_list.append(x)
		print ('aizhan is ok !')
		
		# chinaz.com
		# 判断chinaz是否可以访问
		data,cookies = request_get('http://icp.chinaz.com')
		if data :
			data, cookies = request_post(url_chinaz, data_chinaz, cookies = cookies)
			# print (data)
			if data :
				res_domain = r'<td class="Now">(.*?)</td>'
				# 正则获取域名信息
				root_doamin_re = re.findall(res_domain, data, re.S)
				for x in root_doamin_re:
					if x != None:
						x = getRootDoamin(x.strip())
						# print (x)
						if x == '' :
							continue
						if x not in root_doamin_list :
							print ('chinaz: ',x)
							root_doamin_list.append(x)
		
		print ('chinaz is ok !')
		# alexa.cn
		# 判断alexa是否可以访问
		data,cookies = request_get('http://icp.alexa.cn')
		if data :
			data, cookies = request_get(url_alexa, cookies = cookies)
			# print (data)
			if data :
				res_domain = r'<tr align="center">.*?<td>.*?</td>.*?<td>.*?</a></td>.*?<td>(.*?)</td>\n'
				# 正则获取域名信息
				root_doamin_re = re.findall(res_domain, data, re.S)
				for x in root_doamin_re:
					if x != None:
						x = getRootDoamin(x.strip())
						# print (x)
						if x == '' :
							continue
						if x not in root_doamin_list :
							print ('alexa: ',x)
							root_doamin_list.append(x)
		print ('alexa is ok !')
		# links
		# 判断links是否可以访问
		for _ in range(3):
			try:
				data,cookies = request_get('http://beian.links.cn')
				if data :
					data,cookies = request_get(url_links, cookies = cookies)
					res = r'<tr bgcolor="#FFFFFF">.*?<td><a href=".*?>.*?<td><a href="(.*?)">.*?</td>'
					# 正则获取备案号链接
					icp_link_re = re.findall(res, data, re.S)
					if icp_link_re :
						icp_link = 'http://beian.links.cn/' + icp_link_re[0]

						data, cookies = request_get(icp_link, cookies = cookies)
						# print (data)
						res_domain = r'<tr bgcolor="#FFFFFF">.*?target=_blank>(.*?)</a>&nbsp;'
						root_doamin_re = re.findall(res_domain, data, re.S)
						for x in root_doamin_re :
							xs = x.split(',')
							for y in xs :
								y = getRootDoamin(y.strip())
								# print (y)
								if y == '' :
									continue
								if y not in root_doamin_list :
									print ('links: ',y)
									root_doamin_list.append(y)

						while 1:
							# print (data)
							res_next = r'</a><span title=".*?href="(.*?)"'
							link_next_re = re.search(res_next, data)
							if link_next_re :
								link_next = 'http://beian.links.cn/' + link_next_re.group(1)
								# print (link_next)
								data, cookies = request_get(link_next, cookies)
								# print (data)
								res_domain = r'<tr bgcolor="#FFFFFF">.*?target=_blank>(.*?)</a>&nbsp;'
								root_doamin_re = re.findall(res_domain, data, re.S)
								# print (root_doamin_re)
								for x in root_doamin_re :
									xs = x.split(',')
									for y in xs :
										y = getRootDoamin(y.strip())
										if y == '' :
											continue
										if y not in root_doamin_list :
											print ('links: ',y)
											root_doamin_list.append(y)
							else :
								break
				print ('links is ok !')
				break
			except Exception as e:
				continue
		
	else :
		print ('Please input correct root_domain!')
		return False

	# print (len(root_doamin_list))

	# 返回结果为list
	return root_doamin_list

if __name__ == '__main__':
	import time 
	start_time = time.time()
	result = get_root_domain('189store.com')
	end_time = time.time()
	print ('time: %s' % (end_time-start_time))
	print (len(result))
