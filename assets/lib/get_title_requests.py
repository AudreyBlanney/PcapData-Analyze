#! /usr/bin/python
# coding=utf-8

'''
    进行业务发现，通过访问域名，获取title。
'''
import re
import requests
import threading

# 兼容python2和python3
try:
    import queue
    que = queue.Queue()  
    que_result = queue.Queue()
except Exception as e:
    import Queue
    que = Queue.Queue()  
    que_result = Queue.Queue()


# get请求函数
def request_get(url):
    try:
        r = requests.get(url, timeout = 2)
        r.encoding = r.apparent_encoding
    except Exception as e:
        print ('can`t link the url: %s' % url)
        # print (e)
        return False
    data = r.text
    return data

def runs(que):

    global que_result
    while not que.empty():
        host = que.get()
        data = request_get('http://%s' % host)
        # print (data)
        if data:
            # 获取页面的title
            r = re.search(r'(<title>|<TITLE>)(.*?)(</title>|</TITLE>)', data)
            if r :
                title = r.group(2)
            else:
                title = ''
        else:
            title = ''
        print (host, title)
        que_result.put((host,title))


# 主函数，参数为域名list
def get_titles(host):

    global que

    for x in host:
        que.put(x)

    threads = []
    for x in range(60):
        t = threading.Thread(target = runs, args = (que,))
        threads.append(t)
        t.start()

    for x in threads:
        x.join()

    lists = []
    title_dict = {}
    while not que_result.empty() :
        results = que_result.get()
        title_dict[results[0]] = results[1]
    # 返回结果为dict,{'bbs.mi.com':'miui'}
    return title_dict

if __name__ == '__main__':
    import time
    stat_time = time.time()
    result = get_titles(["123.206.65.100", "123.206.65.101", "123.206.65.102", "123.206.65.103", "123.206.65.104", "123.206.65.105", "123.206.65.106", "123.206.65.107", "123.206.65.108", "123.206.65.109", "123.206.65.110", "123.206.65.111", "123.206.65.112", "123.206.65.113", "123.206.65.114", "123.206.65.115", "123.206.65.116", "123.206.65.117", "123.206.65.118", "123.206.65.119", "123.206.65.120"])
    end_time = time.time()
    for x in result:
        print ('Domain:  %-20sTitle:  %s' % (x,result[x]))

    print ('Time:  %s' % (end_time - stat_time))