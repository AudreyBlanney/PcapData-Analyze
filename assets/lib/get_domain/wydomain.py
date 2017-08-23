#!/usr/bin/env python
# encoding: utf-8


import os
import logging
import re
import shutil
import requests
import dns.resolver
try:
    from common import save_result, read_json
    from utils.fileutils import FileUtils
    from utils.alexa import Alexa
    from utils.threatminer import Threatminer
    from utils.threatcrowd import Threatcrowd
    from utils.sitedossier import Sitedossier
    from utils.netcraft import Netcraft
    from utils.ilinks import Ilinks
except Exception as e:
    pass
    from lib.get_domain.common import save_result, read_json
    from lib.get_domain.utils.fileutils import FileUtils

    from lib.get_domain.utils.alexa import Alexa
    from lib.get_domain.utils.threatminer import Threatminer
    from lib.get_domain.utils.threatcrowd import Threatcrowd
    from lib.get_domain.utils.sitedossier import Sitedossier
    from lib.get_domain.utils.netcraft import Netcraft
    from lib.get_domain.utils.ilinks import Ilinks

try:
    from queue import Queue
except Exception as e:
    from Queue import Queue


logging.basicConfig(
    level=logging.INFO, # filename='/tmp/wyproxy.log',
    format='%(asctime)s [%(levelname)s] %(message)s',
)

def run(domain):
    subdomains = []

    # alexa result json file
    logging.info("starting alexa fetcher...")
    result = Alexa(domain=domain).run()
    subdomains.extend(result)
    logging.info("alexa fetcher subdomains({0}) successfully...".format(len(result)))

    # threatminer result json file
    logging.info("starting threatminer fetcher...")
    result = Threatminer(domain=domain).run()
    subdomains.extend(result)
    logging.info("threatminer fetcher subdomains({0}) successfully...".format(len(result)))

    # threatcrowd result json file
    logging.info("starting threatcrowd fetcher...")
    result = Threatcrowd(domain=domain).run()
    subdomains.extend(result)
    logging.info("threatcrowd fetcher subdomains({0}) successfully...".format(len(result)))

    # sitedossier result json file
    logging.info("starting sitedossier fetcher...")
    result = Sitedossier(domain=domain).run()
    subdomains.extend(result)
    logging.info("sitedossier fetcher subdomains({0}) successfully...".format(len(result)))

    # netcraft result json file
    logging.info("starting netcraft fetcher...")
    result = Netcraft(domain=domain).run()
    subdomains.extend(result)
    logging.info("netcraft fetcher subdomains({0}) successfully...".format(len(result)))

    # ilinks result json file
    logging.info("starting ilinks fetcher...")
    result = Ilinks(domain=domain).run()
    subdomains.extend(result)
    logging.info("ilinks fetcher subdomains({0}) successfully...".format(len(result)))

    return subdomains

def request_get(url):
    try:
        r = requests.get(url)
        r.encoding = r.apparent_encoding
    except Exception as e:
        return ''
    return r.text

# 主函数，参数为list
def get_domain_api(root_domain_list):
    result = {}
    que = Queue()
    result_que = Queue()

    for root_domain in root_domain_list:
        domains = {}
        print ('%s is start' % root_domain)
        mydomains = list(set(run(root_domain)))
        # print (mydomains)

        if not mydomains :
            mydomains.append(root_domain)

        domains = {}
        for domain in mydomains :
            ips = []
            try:
                a = dns.resolver.query(domain,'A')
                for i in a.response.answer:
                    for j in i.items:
                        ips.append(j.address)
                        print (domain, j.address)
            except Exception as e:
                ips = ['none']

            domains[domain] = ips

        result[root_domain] = domains

    return result

if __name__ == '__main__':
    result = get_domain_api(["xiaomi.com"])
    print (result)