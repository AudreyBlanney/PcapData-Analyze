#! /usr/bin/python
# coding=utf-8

import sys
import requests
import json
import re 

def requests_get(url):
	try:
		r = requests.get('http://192.168.2.143:5000%s' % url)
		r.encoding = r.apparent_encoding
		return json.loads(r.text)
	except Exception as e:
		print (e)
		sys.exit(1)

def list_run(domain, userid, openid):
	get_title = requests_get('/update?domainip=%s&userid=%s&openid=%s&lict=list' % (domain, userid, openid))
	if get_title['error'] == 'true':
		sys.exit(1)
	print ('list_run is ok !')

def dict_run(domain, userid, openid):
	get_root_domain = requests_get('/update?domainip=%s&userid=%s&openid=%s&lict=dict' % (domain, userid, openid))
	if get_root_domain['error'] == 'true':
		print '999999'
		sys.exit(1)
	print ('dict_run is ok !')

def getRootDoamin(domain):
	res = re.search(r'([a-zA-Z0-9-]+?)\.(com\.cn|edu\.cn|gov\.cn|org\.cn|net\.cn|gq|hk|im|info|la|mobi|so|tech|biz|co|tv|me|cc|org|net|cn|com)$', domain)
	if res == None:
		return False
	return res.group(0)


if len(sys.argv) != 5:
	print ('error! argv')
	sys.exit(1)

domain = sys.argv[1]
userid = sys.argv[2]
openid = sys.argv[3]

if getRootDoamin(domain) != False :
	dict_run(domain, userid, openid)
else :
	list_run(domain, userid, openid)
