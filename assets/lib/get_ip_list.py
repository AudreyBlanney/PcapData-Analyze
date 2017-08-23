#! /usr/bin/python
# coding=utf-8

'''
    IP分离模块，给一个IP段，可以返回这个段内的所有IP.
'''

# 获取一个IP列表，可以传入一个IP，也可以传入一个IP段 192.168.1.1 or 192.168.1.1-192.168.1.55
# 参数为str
def get_ip_list(ip):
    ip_list = []
    iptonum = lambda x: sum([256**j*int(i) for j,i in enumerate(x.split('.')[::-1])])
    numtoip = lambda x: '.'.join([str(x/(256**i)%256) for i in range(3,-1,-1)])
    if '-' in ip:
        ip_range = ip.split('-')
        ip_start = long(iptonum(ip_range[0]))
        ip_end = long(iptonum(ip_range[1]))
        ip_count = ip_end - ip_start
        if ip_count >= 0 and ip_count <= 65536:
            for ip_num in range(ip_start,ip_end+1):
                ip_list.append(numtoip(ip_num))
        else:
            print ('the input ip is error!')
            return False
    else:
        ip_split = ip.split('.')
        net = len(ip_split)
        if net == 2:
            for b in range(1,255):
                for c in range(1,255):
                    ip = "%s.%s.%d.%d"%(ip_split[0],ip_split[1],b,c)
                    ip_list.append(ip)
        elif net == 3:
            for c in range(1,255):
                ip = "%s.%s.%s.%d"%(ip_split[0],ip_split[1],ip_split[2],c)
                ip_list.append(ip)
        elif net == 4:
            ip_list.append(ip)
        else:
            print ("the input ip is error!")
            return False
    return ip_list
 

if __name__ == '__main__':
    print (get_ip_list('123.206.65'))