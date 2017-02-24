# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import hashlib
import time
import random
import threading
import csv
import selenium
# from mayidali import ProxyConf


write_file_name='tianyancha_todo.csv'
read_file_name='company_todo.txt'
error_file_name='company_without_result.csv'

with open(write_file_name, 'w', encoding='utf-8', newline="") as fp_write:
    field_header = ['search_url',',','search_name',',','company_name',',', 'phone',',','email',',', 'website',',', 'address',',','legal_person',',','registration_value',',','status',',','est',',','industry',',','registration_num',',','company_type',',','organization_code',',','from_to',',','registeration_authority',',','approve_date',',','credit_code',',','registration_place',',','business_scope',',','score',',','leader1',',','leader1_title',',','leader2',',','leader2_title',',','leader3',',','leader3_title','\n']
    fp_write.writelines(field_header)

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

def gen_random_agent():
    rand_agent = random.choice(browser_user_agent_list)
    return rand_agent
##蚂蚁代理，最后返回一个app_key,每次请求都要连带请求体一起发送给蚂蚁动态代理

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

class TianYanCha(object):
    ##蚂蚁代理,返回PhantomJS的浏览器：
    dcap = dict(webdriver.DesiredCapabilities.PHANTOMJS)
    def __init__(self,search_name,retry_num=3):
        self.search_name=search_name
        self.retry_num=retry_num
    def authCode(self):
        proxy_conf = ProxyConf(demo_key)
        authHeader = proxy_conf.get_auth_header()
        return authHeader
    def Ph_browser(self):
        # 此处开始设置头信息
        TianYanCha.dcap["browserName"] = 'Firefox'
        # TianYanCha.dcap["version"] = '50.1.0'
        # TianYanCha.dcap["platform"] = 'Windows NT'
        # # TianYanCha.dcap["phantomjs.page.settings.resourceTimeout"] = 5000
        TianYanCha.dcap["phantomjs.page.settings.userAgent"] = (gen_random_agent())
        # TianYanCha.dcap["phantomjs.page.customHeaders.Accept-Language"] = 'en-US,en;q=0.5'
        # TianYanCha.dcap["phantomjs.page.customHeaders.Host"] = 'www.tianyancha.com'
        # TianYanCha.dcap["phantomjs.page.customHeaders.Accept"] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        # TianYanCha.dcap["phantomjs.page.customHeaders.Accept-Encoding"] = 'gzip, deflate'
        # TianYanCha.dcap["phantomjs.page.customHeaders.Referer"] = 'https://www.baidu.com/link?url=ZOn3q_2a1HAfd6t1YZ1XAEjXGcWdiHrV-FAh01vYfhj9qO5hgi3Y5aBSxOv8iAvZ&wd=&eqid=ab76f72800041cb20000000658afe682'
        # TianYanCha.dcap["phantomjs.page.customHeaders.Cookie"] = 'Hm_lvt_e92c8d65d92d534b0fc290df538b4758=1487748091,1487820218,1487922826; _pk_id.1.e431=beb3cecf78d3a18d.1481878272.10.1487922826.1487919431.; tnet=211.147.76.61; RTYCID=dad7d1b8122243a2b398d6cf5a4b6fd1; aliyungf_tc=AQAAAEnrUz3uhAQAPUyT063Y0Cp/rYLM; token=e2e1d61d51aa4a5ca34d8db76d8d0173; _utm=fnhs7fn4k7ht-n9-d--43sdsn3vs3d3r; Hm_lpvt_e92c8d65d92d534b0fc290df538b4758=1487922826; _pk_ref.1.e431=%5B%22%22%2C%22%22%2C1487919431%2C%22http%3A%2F%2Fantirobot.tianyancha.com%2Fcaptcha%2Fverify%3Freturn_url%3Dhttp%3A%2F%2Fwww.tianyancha.com%2Fcompany%2F2320260561%26rnd%3Didzb3prxoo1O7y4qDOsWWA%3D%3D%22%5D; _pk_ses.1.e431=*; TYCID=f09bf58079b44ee19835e72d60f87dcb'
        # TianYanCha.dcap["phantomjs.page.customHeaders.Connection"] = 'keep-alive'
        # TianYanCha.dcap["phantomjs.page.customHeaders.Cache-Control"] = 'max-age=0'
        # TianYanCha.dcap["phantomjs.page.customHeaders.Upgrade-Insecure-Requests"] = '1'
        # 此处带入proxy验证信息
        auth = self.authCode().get('Proxy-Authorization')
        TianYanCha.dcap["phantomjs.page.customHeaders.Proxy-Authorization"] = auth
        # By PhantomJS
        args = ['--load-images=false', '--disk-cache=false',
                '--proxy=%s:%s' % (demo_key.get('host'), demo_key.get('port'))]
        print(TianYanCha.dcap)
        br = webdriver.PhantomJS(service_args=args, desired_capabilities=TianYanCha.dcap,
                                 executable_path=r'C:\Users\jachen\Desktop\projects\tianyancha\phantomjs.exe')
        return br
    #挂上代理后继续爬虫
    def tianyancha_details(self):
        if self.retry_num>0:
            try:
                browser=self.Ph_browser()
                demo_url = 'http://www.tianyancha.com/'
                browser.get(demo_url)
                # print(browser.page_source)
                counter=1
                alarm1=0
                alarm2=0
                alarm1+=1
                print('search_name is %s' % self.search_name)
                domain_input = browser.find_element_by_id('live-search')
                domain_input.clear()
                domain_input.send_keys(self.search_name + Keys.ENTER)
                print('1-search company name')
                time.sleep(10)
                # print(browser.page_source)
                company=browser.find_element_by_class_name('query_name')
                print('2-find the company link')
                company.click()
                print('3-click company link')
                all_handles=browser.window_handles
                browser.switch_to_window(all_handles[-1])
                time.sleep(random.randint(5, 8))
                print('4.company_url是',browser.current_url)
                browser.get(browser.current_url)
                company_url=browser.current_url.strip().replace(' ', '').replace('\n','').replace('\t', '').replace('\r', '').replace(',', '，')
                time.sleep(10)
                bs_content=BeautifulSoup(browser.page_source, 'html.parser')
                # print(bs_content.prettify())
                print('6-BS解析company link...')
                child1=''
                child2=''
                child3=''
                child4=''
                child5=''
                child6=''
                try:
                    child1=bs_content.find('div',class_='company_info')
                except:
                    child1=''
                try:
                    child2 = bs_content.find('div', class_='row b-c-white company-content')
                except:
                    child2=''
                try:
                    child3 = child2.find_all('div', class_='c8')
                except:
                    child3=''
                try:
                    child4 = bs_content.find('table', class_='staff-table ng-scope').find_all('tr')
                except:
                    child4=''
                try:
                    child5 = child4[0].find_all('td')
                except:
                    child5=''
                try:
                    child6 = child4[1].find_all('td')
                except:
                    child6=''
                company_name=''
                phone=''
                email=''
                website=''
                address=''
                legal_person=''
                registration_value=''
                status=''
                est=''
                industry=''
                registration_num=''
                company_type=''
                organization_code=''
                from_to=''
                registeration_authority=''
                approve_date=''
                credit_code=''
                registration_place=''
                business_scope=''
                score=''
                leader1=''
                leader1_title=''
                leader2=''
                leader2_title=''
                leader3=''
                leader3_title=''
                try:
                    company_name=child1.find('div',class_='company_info_text').find('p').get_text().strip().replace(' ', '').replace('\n', '').replace('\t','').replace('\r', '').replace(',', '，')
                except:
                    pass
                try:
                    phone_raw=child1.find('span',class_='ng-binding')
                except:
                    pass
                try:
                    phone=phone_raw.get_text().strip().replace(' ', '').replace('\n', '').replace('\t','').replace('\r', '').replace(',', '，')
                except:
                    pass
                try:
                    email_raw=phone_raw.next_sibling
                except:
                    pass
                try:
                    email=email_raw.get_text().strip().replace(' ', '').replace('\n', '').replace('\t','').replace('\r', '').replace(',', '，')
                except:
                    pass

                try:
                    website_raw=bs_content.find('div',attrs={"class":"company_info"}).find('a',attrs={'class':'c9 ng-binding ng-scope'})
                except:
                    pass
                try:
                    website=website_raw.get_text().strip().replace(' ', '').replace('\n', '').replace('\t','').replace('\r', '').replace(',', '，')
                except:pass
                try:
                    address_raw=bs_content.find('div',attrs={"class":"company_info"}).find_all('span')[-2]
                except:
                    pass
                try:
                    address=address_raw.get_text().strip().replace(' ', '').replace('\n', '').replace('\t','').replace('\r', '').replace(',', '，')
                except:
                    pass
                try:
                    legal_person = child2.find('a', attrs={'ng-if': 'company.baseInfo.legalPersonName'}).get_text().strip().replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '').replace(',', '，')
                except:
                    pass
                try:
                    registration_value = child2.find('td', class_='td-regCapital-value').get_text().strip().replace(' ','').replace('\n', '').replace('\t', '').replace('\r', '').replace(',', '，')
                except:
                    pass
                try:
                    status = child2.find('td', class_='td-regStatus-value').get_text().strip().replace(' ', '').replace('\n','').replace('\t', '').replace('\r', '').replace(',', '，')
                except:
                    pass
                try:
                    est = child2.find('td', class_='td-regTime-value').get_text().strip().replace(' ', '').replace('\n','').replace('\t', '').replace('\r', '').replace(',', '，')
                except:
                    pass
                try:
                    industry = child3[1].find('span').get_text().strip().replace(' ', '').replace('\n', '').replace('\t','').replace('\r', '').replace(',', '，')
                except:
                    pass
                try:
                    registration_num = child3[2].find('span').get_text().strip().replace(' ', '').replace('\n', '').replace('\t','').replace('\r', '').replace(',', '，')
                except:
                    pass
                try:
                    company_type = child3[3].find('span').get_text().strip().replace(' ', '').replace('\n', '').replace('\t','').replace('\r', '').replace(',', '，')
                except:
                    pass
                try:
                    organization_code = child3[4].find('span').get_text().strip().replace(' ', '').replace('\n', '').replace('\t','').replace('\r', '').replace(',', '，')
                except:
                    pass
                try:
                    from_to = child3[5].find('span').get_text().strip().replace(' ', '').replace('\n', '').replace('\t','').replace('\r','').replace(',', '，')
                except:
                    pass
                try:
                    registeration_authority = child3[6].find('span').get_text().strip().replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '').replace(',', '，')
                except:
                    pass
                try:
                    approve_date = child3[7].find('span').get_text().strip().replace(' ', '').replace('\n', '').replace('\t','').replace('\r', '').replace(',', '，')
                except:
                    pass
                try:
                    credit_code = child3[8].find('span').get_text().strip().replace(' ', '').replace('\n', '').replace('\t','').replace('\r', '').replace(',', '，')
                except:
                    pass
                try:
                    registration_place = child3[9].find('span').get_text().strip().replace(' ', '').replace('\n', '').replace('\t','').replace('\r', '').replace(',', '，')
                except:
                    pass
                try:
                    business_scope = child3[10].find('span').get_text().strip().replace(' ', '').replace('\n', '').replace('\t','').replace('\r', '').replace(',', '，')
                except:
                    pass
                try:
                    score = child2.find('img',attrs={'class':'td-score-img'})['ng-alt'].strip().replace(' ', '').replace('\n', '').replace('\t','').replace('\r', '').replace(',', '，').replace('评分','')
                except Exception as e:
                    print(e)
                    pass
                try:
                    leader1 = child5[0].get_text().strip().replace(' ', '').replace('\n', '').replace('\t', '').replace('\r','').replace(',', '，')
                    leader1_title = child6[0].get_text().strip().replace(' ', '').replace('\n', '').replace('\t', '').replace('\r','').replace(',', '，')
                except:
                    pass
                try:
                    leader2 = child5[1].get_text().strip().replace(' ', '').replace('\n', '').replace('\t', '').replace('\r','').replace(',', '，')
                    leader2_title = child6[1].get_text().strip().replace(' ', '').replace('\n', '').replace('\t', '').replace('\r','').replace(',', '，')
                except:
                    pass
                try:
                    leader3 = child5[2].get_text().strip().replace(' ', '').replace('\n', '').replace('\t', '').replace('\r','').replace(',', '，')
                    leader3_title = child6[2].get_text().strip().replace(' ', '').replace('\n', '').replace('\t', '').replace('\r''').replace(',', '，')
                except:
                    pass
                with open(write_file_name, 'a', encoding='utf-8', newline='') as fp_write:
                    record_item = [company_url,',',search_name,',',company_name,',', phone,',', email,',', website,',', address,',',legal_person,',',registration_value,',',status,',',est,',',industry,',',registration_num,',',company_type,',',organization_code,',',from_to,',',registeration_authority,',',approve_date,',',credit_code,',',registration_place,',',business_scope,',',score,',',leader1,',',leader1_title,',',leader2,',',leader2_title,',',leader3,',',leader3_title,'\n']
                    print('7-网页解析结果是',record_item)
                    fp_write.writelines(record_item)
                fp_write.close()
                browser.switch_to_window(all_handles[0])
                counter+=1
                alarm2+=1
                browser.quit()
            except Exception as e:
                browser.quit()
                print('第%d次尝试失败,报错信息是%s' %(4-self.retry_num,e))
                self.retry_num=self.retry_num-1
                self.tianyancha_details()
        else:
            print('this item %s was abandon after 3 times retry'%self.search_name)
            with open(error_file_name, 'a', encoding='utf-8', newline='') as fp_write:
                fp_writer=csv.writer(fp_write,dialect='excel',delimiter='|')
                fp_writer.writerow([self.search_name])
    # self.tianyancha_details(self.search_name,retry_num=3)

def tianyancha_multithreading(company_list,list):
    for num in range(list[0],list[1]):
        tyc=TianYanCha(company_list[num],3)
        tyc.tianyancha_details()

if __name__=="__main__":

    #每次跑代码前先进行代理服务器测试：
    for i in range(0,3):
        br=TianYanCha('').Ph_browser()
        br.get("http://1212.ip138.com/ic.asp")
        # 设置页面等待时间
        time.sleep(6)
        print(br.page_source)
        br.quit()
    #现在正式开始多线程跑代码
    # company_list=[]
    # with open(read_file_name,'r',encoding='utf-8')as file_reader:
    #     spamreader = file_reader.readlines()
    #     for row in spamreader:
    #         search_name = row.strip()
    #         company_list.append(search_name)
    # company_count=len(company_list)
    # print('总共有%d个公司待查'%company_count)
    # company_divided_list=[
    #     (0,int(1/4*company_count)),
    #     (int(1/4*company_count),int(1/2*company_count)),
    #     (int(1/2*company_count),int(3/4*company_count)),
    #     (int(3/4*company_count),company_count+1),]
    # print('总共分了%d个线程,分别是%s'%(len(company_divided_list),company_divided_list))
    # threading_list=[]
    # for company_pool in company_divided_list:
    #     th=threading.Thread(target=tianyancha_multithreading,args=(company_list,company_pool))
    #     threading_list.append(th)
    #
    # for th in threading_list:
    #     th.start()
    #     time.sleep(5)
    # for th in threading_list:
    #     th.join()

#
if __name__=="__main__":
    with open(read_file_name, 'r', encoding='utf-8')as file_reader:
        spamreader = file_reader.readlines()
        for row in spamreader:
            search_name = row.strip()
            print(search_name)
            tyc=TianYanCha(search_name, retry_num=3)
            tyc.tianyancha_details()

