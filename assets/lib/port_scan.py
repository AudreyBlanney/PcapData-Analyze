#! /usr/bin/env python
# coding=utf-8


'''
    进行端口扫描，使用python-nmap和多线程，速度还可以。
'''
import time
import nmap
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


# 多线程主函数
def run(que):
    nm = nmap.PortScanner()
    global que_result
    ips = ''
    # 获取队列内容，进行端口扫描
    while not que.empty() :
        ip = que.get()
        ips = ips + ' ' + ip
        if len(ips.split(' ')) >= 5 :
            try:
                # 扫描主机 
                nm.scan(hosts = ips, arguments = '-Pn -A -p21,22,23,25,53,80,110,139,143,389,443,445,465,873,993,995,1080,1723,1433,1521,3306,3389,3690,5000,5432,5800,5900,6379,7001,8000,8001,8080,8081,8888,9200,9300,9080,9999,11211,27017')
            except Exception as e :
                pass
            # 获取扫描结果
            for ip in nm.all_hosts():
                if 'tcp' not in nm[ip] :
                    continue
                if len(nm[ip]['tcp']) > 30 :
                    continue
                ports = []
                print ('%s:' % ip)
                for port in nm[ip]['tcp'] :
                    service = nm[ip]['tcp'][port]['name']
                    version = nm[ip]['tcp'][port]['version']
                    title = nm[ip]['tcp'][port]['product']
                    ports.append([port, service, '%s-%s-%s' % (title, version, 'tcp')])
                    print ('\t%-10s%-10s%s' % (str(port), service, '%s-%s-%s' % (title, version, 'tcp')))
                que_result.put({ip:ports})
            ips = ''
    try:
        # 扫描主机 
        nm.scan(hosts = ips, arguments = '-Pn -A -p21,22,23,25,53,80,110,139,143,389,443,445,465,873,993,995,1080,1723,1433,1521,3306,3389,3690,5000,5432,5800,5900,6379,7001,8000,8001,8080,8081,8888,9200,9300,9080,9999,11211,27017')
    except Exception as e:
        pass
    # 获取扫描结果
    for ip in nm.all_hosts():
        if 'tcp' not in nm[ip] :
            continue
        if len(nm[ip]['tcp']) > 30 :
            continue
        ports = []
        print ('%s:' % ip)
        for port in nm[ip]['tcp'] :
            service = nm[ip]['tcp'][port]['name']
            version = nm[ip]['tcp'][port]['version']
            title = nm[ip]['tcp'][port]['product']
            ports.append([port, service, '%s-%s-%s' % (title, version, 'tcp')])
            print ('\t%-10s%-10s%s' % (str(port), service, '%s-%s-%s' % (title, version, 'tcp')))
        que_result.put({ip:ports})
            
        que_result.put({ip:ports})

# 扫描主函数，参数为list
def Nmap(host):
    global que
    port_result = {}

    print('开始扫描主机：')
    for ip in host:
        if ip == 'none' :
            continue
        que.put(ip)

    threads = []
    # 多线程函数，可以设置线程数
    for x in range(20):
        t = threading.Thread(target = run, args = (que,))
        threads.append(t)
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()

    # 获取爆破结果，和服务对照，返回dict
    while not que_result.empty():
        result = que_result.get()
        for ip in result:
            if ip not in port_result:
                port_result[ip] = result[ip]

    for ip in host:
        if ip not in port_result:
            port_result[ip] = [('','','')]

    # 返回结果是dict {'192.168.1.1':{'22':'ssh','80':'http',}}
    return port_result

if __name__ == '__main__':
    host = ['192.168.199.1', '123.206.65.121', '123.206.65.122', '123.206.65.123', '123.206.65.124', '123.206.65.125', '123.206.65.126', '123.206.65.127', '123.206.65.128', '123.206.65.129', '123.206.65.130', '123.206.65.131', '123.206.65.132', '123.206.65.133', '123.206.65.134', '123.206.65.135', '123.206.65.136', '123.206.65.137', '123.206.65.138', ]
    # print (len(host))
    start_time = time.time()
    result = Nmap(host)
    print (result)
    end_time = time.time()
    print ('time: %d' % (end_time-start_time) )
