# -*- coding: utf-8 -*-

# Transparent Proxy
import requests
import hashlib
import time
import random
from urllib.parse import urlparse

browser_user_agent_list = [
'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0 ',
'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0',
'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36 ',
'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36',
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET4.0C; .NET4.0E) ',
'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36',
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET4.0C; .NET4.0E) ',
'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0); 360Spider',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36 ',
'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0',
]


def gen_rand_header():
    rand_ua = random.choice(browser_user_agent_list)
    rand_header = {'User-Agent':rand_ua,
                   'Accept-Language':'en-US,en;q=0.5',
                   'Accept-Encoding':'gzip, deflate, br',
                   'Connection':'keep-alive',
                   'Referer':'https://www.baidu.com'}
    # print(rand_header)
    return rand_header

class ProxyConf(object):

    def __init__(self, key):
        self.app_key = key['app_key']
        self.secret = key['secret']
        self.host = key['host']
        self.port = key['port']
        self.auth_header_key = 'Proxy-Authorization'

    def get_proxy(self):
        return {'http': '%s:%s' % (self.host, self.port)}

    def get_auth_header(self, lock_id=0, release_id=0):
        param_map = {
            "app_key": self.app_key,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),  # 如果你的程序在国外，请进行时区处理
            "retrypost": "true"
            #  ,"with-transaction": '1'
        }
        if lock_id > 0:
            param_map['with-transaction'] = str(lock_id)
        if release_id > 0:
            param_map['release-transaction'] = str(release_id)
        # 排序
        keys = list(param_map.keys())
        keys.sort()
        codes = "%s%s%s" %(self.secret, ''.join('%s%s' % (key, param_map[key]) for key in keys), self.secret)
        encoded_codes = codes.encode('utf-8')
        # 计算签名
        sign = hashlib.md5(encoded_codes).hexdigest().upper()
        param_map["sign"] = sign

        # 拼装请求头Proxy-Authorization的值
        keys = param_map.keys()
        auth_header_value = "MYH-AUTH-MD5 " + str('&').join('%s=%s' % (key, param_map[key]) for key in keys)
        auth_header = {self.auth_header_key:auth_header_value}
        print(auth_header)
        return auth_header

class UrlConnect(object):

    def __init__(self, i_conn_type, i_key=''):
        '''

        :param i_conn_type: 0(default)--direct, 1--via transparent proxy
        :param i_key:
        :return:
        '''
        self.conn_type = i_conn_type
        self.auth_key = i_key
        self.proxy_config = None
        self.proxies = None
        self.auth_header = None
        self.request_session = requests.session()

        if self.conn_type == 1:
            self.request_session.verify=False       # turn off cert verfication
            self.proxy_config = ProxyConf(self.auth_key)
            self.proxies = self.proxy_config.get_proxy()
            self.auth_header = self.proxy_config.get_auth_header()
            self.request_session.proxies = self.proxies
            self.request_session.headers.update(self.auth_header)
            # print(self.request_session.headers)
        elif self.conn_type == 0:
            self.header = gen_rand_header()

    def url_connect_get(self, i_url, retry_num=1, i_max_timeout=6):
        try:
            if self.conn_type == 0:
                url_parse_result = urlparse(i_url)
                url_root = '%s//%s/' %(url_parse_result.scheme, url_parse_result.netloc)
                # print(url_root)
                ref_dict = {'Referer':url_root}
                self.header.update(ref_dict)
                # print(self.header)
            resp = self.request_session.get(i_url, timeout=i_max_timeout)
            if resp.status_code != 200:
                print('%s get error response code: %s' %(i_url, resp.status_code))
            return resp
        except Exception as e:
            if retry_num > 0:
                print("%s\n%s retry left" %(i_url, retry_num))
                return self.url_connect_get(i_url, retry_num-1)
            else:
                print([e, 'Connection Issue'])
                return None


if __name__ == '__main__':

    demo_key = {'app_key': '5934525',
                'secret': 'd2f4c808b4f9a1800b7290b8907e9f76',
                'host': '123.57.138.199',
                'port': '8123'
               }

    demo_key_1 = {'app_key': '263177855',
                'secret': '4e3e4ed98bfb70d29417d7fdcf62e311',
                'host': '123.57.145.174',
                'port': '8123'
               }

    check_url = 'http://1212.ip138.com/ic.asp'

    # # Check Proxy
    # demo_config = ProxyConf(demo_key)
    # demo_header = demo_config.get_auth_header()
    #
    # demo_session = requests.session()
    # demo_session.proxies = demo_config.get_proxy()
    # check_content = demo_session.get(check_url, headers=demo_header)
    # check_content.encoding = 'gbk'
    # print(check_content.text)

    # demo_url = 'https://www.liepin.com/zhaopin/?pubTime=30&salary=&jobKind=2&sortFlag=15&industries=040&dqs=200060'
    # url_conn_instance = UrlConnect(i_conn_type=1, i_key=demo_key)
    # check_content = url_conn_instance.url_connect_get(demo_url)
    # print(check_content.status_code, check_content.text)

    # via proxy mode(OK)
    url_conn_instance = UrlConnect(i_conn_type=1, i_key=demo_key)
    check_content = url_conn_instance.url_connect_get(check_url)
    check_content.encoding = 'gbk'
    print(check_content.text)

    # # direct mode(OK)
    # url_conn_instance = UrlConnect(i_conn_type=0, i_key=demo_key)
    # check_content = url_conn_instance.url_connect_get(check_url)
    # check_content.encoding = 'gbk'
    # print(check_content.text)
    #
    # # Test the https and disable verify in cert
    # demo_url = 'https://www.liepin.com/company/010-000/'
    #
    # demo_config = ProxyConf(demo_key)
    # demo_header = demo_config.get_auth_header()
    #
    # demo_session = requests.session()
    # demo_session.verify = False
    # demo_session.proxies = demo_config.get_proxy()
    # check_content = demo_session.get(demo_url, headers=demo_header)
    # print(check_content.text)
    #
    #
    # url_conn_instance = UrlConnect(i_conn_type=1, i_key=demo_key)
    # check_content = url_conn_instance.url_connect_get(demo_url)
    # print(check_content.text)
