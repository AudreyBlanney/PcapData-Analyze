import requests
try:
    from lib import myparser
except Exception as e:
    import myparser
import time


class search_baidu:

    def __init__(self, word, limit = 50):
        self.word = word
        self.total_results = ""
        self.limit = limit
        self.counter = 0
        self.cookies = {}
    def do_search(self):
        headers = {
            'User-Agent': "(Mozilla/5.0 (Windows; U; Windows NT 6.0;en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6",
            'X_FORWARDED_FOR': '',
            'Host': 'www.baidu.com',
        }
        try:
            r = requests.get('http://www.baidu.com/s?wd=%s&pn=%s' % (self.word, self.counter) , headers = headers, timeout = 3, cookies = self.cookies)
            r.encoding = r.apparent_encoding
            data = r.text
            self.cookies = r.cookies
        except Exception as e:
            print (e)
            data = ''

        self.total_results += data

    def process(self):
        while self.counter <= self.limit and self.counter <= 1000:
            self.do_search()
            # time.sleep(1)
            print ("Searching " + str(self.counter) + " results...")
            self.counter += 10

    def get_emails(self):
        rawres = myparser.parser(self.total_results, self.word)
        return rawres.emails()

def search(lists):
    results = {}
    print('get email:')
    for domain in lists:
        search = search_baidu(domain)
        search.process()
        all_emails = search.get_emails()
        if not all_emails :
            all_emails = ['']
        results[domain] = all_emails
        # print (type(all_emails))
    return results

if __name__ == '__main__':
    results = search(['xiaomi.com','lanou3g.com','cleverbao.blog'])
    for domain in results:
        print (domain)
        for email in results[domain] :
            print ('\t%s' % (email))