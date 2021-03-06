# encoding: utf-8

# import sys
# sys.path.append("../")

import re
try:
    from common import curl_get_content, http_request_get, is_domain
except Exception as e:
    from lib.get_domain.common import curl_get_content, http_request_get, is_domain

class Threatminer(object):
    """docstring for Threatminer"""
    def __init__(self, domain):
        super(Threatminer, self).__init__()
        self.domain = domain
        self.subset = []
        self.website = "https://www.threatminer.org"
    
    def run(self):
        try:
            url = "{0}/getData.php?e=subdomains_container&q={1}&t=0&rt=10&p=1".format(self.website, self.domain)
            # content = curl_get_content(url).get('resp')
            content = http_request_get(url).text

            _regex = re.compile(r'(?<=<a href\="domain.php\?q=).*?(?=">)')
            for sub in _regex.findall(content):
                if is_domain(sub):
                    self.subset.append(sub)

            return list(set(self.subset))
        except Exception as e:
            return self.subset