#! /usr/bin/python

# coding=utf-8

import requests
import re

# proxy = {'http':'http://127.0.0.1:8080'}
proxy = {}
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36', 'Referer':'http://cha.hx99.net/', 'DNT':'1', 'Connection':'close', 'X-Requested-With':'XMLHttpRequest'}

def requests_get(url, cookies = {}):
	try:
		r = requests.get(url, cookies = cookies, headers = header, proxies = proxy)
		r.encoding = r.apparent_encoding
	except Exception as e:
		# print ('can`t link the url: %s' % url, e)
		return False,False
	data = r.text
	cookies = r.cookies
	return data,cookies

def search_soc(email):
	data,cookies = requests_get('http://email.70sec.com/')
	if not data :
		return None
	
	lists = []
	for i in range(1, 5) :
		_url = 'http://email.70sec.com/PHPDatas/email_%s.php?f=1&q=%s' % (i,email)
		data,cookies = requests_get(_url, cookies = cookies)
		# print (data)
		if not data :
			continue
		res = r'<td class="center">(.*?)\['
		data_re = re.findall(res, data)
		for x in data_re :
			# print(x)
			x = x.split()
			lists.append(tuple(x))
	if not lists :
		lists = [('','')]
	return lists

def Social(domain_list):
	print ('Get sensitive information!')
	result = {}
	for domain in domain_list :
		chinaz_url = 'http://whois.chinaz.com/%s' % domain
		data,cookies = requests_get(chinaz_url)
		# print (data)
		if not data :
			continue
		res = r'<span>.*?<span>.*?<span>(.*?)</span>'
		r = re.search(res, data)
		if not r :
			continue
		email = r.group(1)
		# print (email)
		lists = search_soc(email)
		result[domain] = lists
	return result

if __name__ == '__main__':
	result = Social(['meizu.com','lanou3g.com'])
	for x in result:
		for y in result[x]:
			print ('%s:\n\t%s' % (x,y))
