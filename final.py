import json
import os
from urllib.parse import unquote
import requests
import pymysql
import time
import re
import bs4
import xlrd
from xlutils.copy import copy


class CF:
    def get_html(self, url):
        try:
            head = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.52",
                "cookie": 'X-User-Sha1=9aac3398b61f1c34cfff5dea661274f039aa0e50; '
                          'X-User=80bf3aa12253cd8ed7880d5b84001e79f9b29a5b54fd667a5188f6dd157b8d70ea2e41e7a2efab19; '
                          '_ga=GA1.2.371384411.1664722804; '
                          'mjx.menu=locale%3Azh-hans%26%3Bzscale%3A400%25%26%3Bcollapsible%3Atrue; '
                          '__utmz=71512449.1668740635.94.8.utmcsr=vjudge.net|utmccn=('
                          'referral)|utmcmd=referral|utmcct=/; '
                          '__utma=71512449.371384411.1664722804.1669263859.1669298014.114; '
                          '70a7c28f3de=nv58uj04kqbrahhwvl; RCPC=bffa468b36de26e5683f16f5cba5f779; '
                          'JSESSIONID=F3E4B6A2D2D136FBC6A1D77DE2D80735-n1; 39ce7=CFmsDrPt '
            }
            r = requests.get(url=url, headers=head)
            r.raise_for_status()
            r.encoding = 'utf-8'
            print("url 连接成功")
            return r.text
        except:
            return "错误"

    def user_in(self, a):
        # print(len(a),a)
        if len(a) == 3:
            return a[0] + ' ' + a[1] + ' ' + a[2]
        else:
            return a[0]

    def get_time(self, a):
        b = str()
        for i in a:
            if i == '/':
                b = b + ' '
            else:
                b = b + i
        t = time.mktime(time.strptime(b, "%b %d %Y %H:%M"))
        Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
        return Time

    def check(self, i, cur):
        sql_1 = "SELECT * FROM take_notes WHERE submission_id= %s" % (i['submission_id'])
        cur.execute(sql_1)
        data = cur.fetchone()
        if (data != None):
            print(data)
            return False
        return True

    def show(self, data):
        for i in data:
            print(i)

    def sub(self, data):
        if data == 'OK':
            return "Accept"
        else:
            return data

    def get_data(self, html_text):
        pattern_1 = re.compile('>*?<span class="hiddenSource">(.*?)</span>', re.S)
        pattern_2 = re.compile('.*?<span class="format-time" data-locale="en">(.*?)</span>', re.S)
        pattern_3 = re.compile('.*?/profile/(.*?)" title', re.S)
        pattern_4 = re.compile('<a href="(.*?)">\r\n                (.*?)\r\n.*?</a>', re.S)
        pattern_5 = re.compile('<td>\r\n        (.*?)\r.*?</td>', re.S)
        pattern_6 = re.compile('submissionid="(.*?)".*?submissionverdict="(.*?)"', re.S)
        pattern_7 = re.compile('>\r\n                (.*?)\xa0ms', re.S)
        pattern_8 = re.compile('>\r\n                (.*?)\xa0KB', re.S)
        soup = bs4.BeautifulSoup(html_text, "html.parser")
        a = soup.find_all('tr')
        data = []
        for i in a:
            if isinstance(i, bs4.element.Tag):
                if (i.get('data-submission-id') == None or i.get('data-a') == None): continue
                li = []
                li.append('1')
                cnt = 0
                for j in i.childGenerator():
                    if cnt == 3:
                        t_2 = re.findall(pattern_2, str(j))
                        li.append(t_2)
                    elif cnt == 5:
                        t_3 = re.findall(pattern_3, str(j))
                        li.append(t_3)
                    elif cnt == 7:
                        t_4 = re.findall(pattern_4, str(j))
                        li.append(t_4)
                    elif cnt == 9:
                        t_5 = re.findall(pattern_5, str(j))
                        li.append(t_5)
                    elif cnt == 11:
                        t_6 = re.findall(pattern_6, str(j))
                        li.append(t_6)
                    elif cnt == 13:
                        t_7 = re.findall(pattern_7, str(j))
                        li.append(t_7)
                    elif cnt == 15:
                        t_8 = re.findall(pattern_8, str(j))
                        li.append(t_8)
                    cnt += 1
                data.append(li)
        for i in data:
            yield {
                'submission_id': i[5][0][0],
                'user_in': self.user_in(i[2]),
                'sub_time': self.get_time(i[1][0]),
                'title': i[3][0][1],
                'submissionVerdict': self.sub(i[5][0][1]),
                'language_in': i[4][0],
                'difficulty': 'None',
                'ms': i[6][0],
                'kb': i[7][0],
                'memory': 'None',
                'oj': 'CodeForces',
                'url': 'https://codeforces.com/' + i[3][0][0],
                'submission_url': '"https://codeforces.com//contest/1560/submission/' + i[5][0][0],
            }

    def write_item_to_mysql(self, data):
        connection = pymysql.connect(host="localhost", user="root", password="ccsu", db="guliguli", port=3306)
        print("数据库连接成功")
        cur = connection.cursor()  # 创建一个游标对象
        for i in data:
            if '\'' in i['title']: continue
            if self.check(i, cur) == False:
                connection.close()  # 断开
                print("内容重复,停止爬取")
                return False
            sql = "insert into take_notes values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                i['submission_id'],
                i['user_in'],
                i['sub_time'],
                i['title'],
                i['submissionVerdict'],
                i['language_in'],
                i['difficulty'],
                i['ms'],
                i['kb'],
                i['memory'],
                i['oj'],
                i['url'],
                i['submission_url'],
            )
            print(i)
            print(sql)
            cur.execute(sql)
            connection.commit()  # 提交
        connection.close()  # 断开
        print("数据库连接关闭")
        return True

    def main(self, name):
        for i in range(1, 1000):
            url = "https://codeforces.com/submissions/" + name + "/page/" + str(i)
            print(url)
            html_text = self.get_html(url)
            data = self.get_data(html_text)
            # self.show(data)
            op = self.write_item_to_mysql(data)
            print(op)
            if op == False:
                return


class vjudge:
    def Get_Time(self, t):
        Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t / 1000))
        return Time

    def Get_Html(self, url):
        try:
            head = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42"
            }
            r = requests.get(url=url, headers=head)
            r.raise_for_status()
            r.encoding = 'utf-8'
            return r.text
        except:
            return "错误"

    def get_data(self, html_text):
        soup = bs4.BeautifulSoup(html_text, "html.parser")
        res = soup.get_text()
        data = json.loads(res)
        data = data['data']
        return data

    def check(self, item, cur):
        sql_1 = "SELECT * FROM take_notes WHERE submission_id= %s" % (str(item['runId']))
        cur.execute(sql_1)
        data = cur.fetchone()
        if (data != None): return False
        return True

    def write_item_to_mysql(self, data):
        connection = pymysql.connect(host="localhost", user="root", password="ccsu", db="guliguli", port=3306)
        print("数据库连接成功")
        cur = connection.cursor()  # 创建一个游标对象
        for item in data:
            print(item)
            if self.check(item, cur) == False:
                connection.close()  # 断开
                print("更新完成  数据库连接关闭")
                return False
            sql = "insert into take_notes values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                item['runId'],  # submission_id
                item['userName'],  # user_in
                self.Get_Time(item['time']),  # sub_time
                item['oj'] + '-' + item['probNum'],  # 题目名称
                item['status'],  # 提交状态
                item['language'],  # 语言
                "None",  # 难度
                item['runtime'],  # 代码运行时间
                item['sourceLength'],  # 代码长度
                item['memory'],  # 代码占用空间大小
                "vjudge",  # 提交oj
                'https://vjudge.net/problem/' + item['oj'] + '-' + item['probNum'],  # 题目连接
                'None'  # 提交连接
            )
            print(sql)
            cur.execute(sql)
            connection.commit()  # 提交
        connection.close()  # 断开
        print("数据库连接关闭")
        return True

    def main(self, name, start):
        for i in range(1, 100000):
            # url= 'https://vjudge.net/status/data?draw=1&start=0&length=20&un=zxyxhpp&OJId=All&probNum=&res=1&language=&onlyFollowee=false&orderBy=run_id&_=1670421363788'
            url = "https://vjudge.net/status/data?draw=" + str(1) + "&start=" + str((i - 1) * 20) + "&length=20&un=" + name + "&OJId=All&probNum=&res=0&language=&onlyFollowee=false&orderBy=run_id&_=" + str(start)
            print(url)
            html_text = self.Get_Html(url)
            if html_text == "{\"data\":[],\"recordsTotal\":9999999,\"recordsFiltered\":9999999,\"draw\":90}":
                print("结束")
                break
            data_text = self.get_data(html_text)
            op = self.write_item_to_mysql(data_text)
            if not op: return


class luogu(object):
    def Get_Html(self, url, mycookie):
        try:
            head = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42",
                "cookie": mycookie
            }
            r = requests.get(url=url, headers=head)
            r.raise_for_status()
            r.encoding = 'utf-8'
            return r.text
        except:
            return "错误"

    def get_data(self, html_text):
        soup = bs4.BeautifulSoup(html_text, "html.parser")
        res = soup.script.get_text()
        res = unquote(res.split('\"')[1])
        data = json.loads(res)
        data = data['currentData']['records']['result']
        return data

    def Get_Time(self, t):
        Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
        return Time

    def Score(self, a):
        if a == 0:
            return 'Wrong Answer'
        else:
            return 'Accepted'

    def lan(self, a):
        if a == 27:
            return 'G++20'
        else:
            return None

    def check(self, item, cur):
        sql_1 = "SELECT * FROM take_notes WHERE submission_id= %s" % (item['id'])
        cur.execute(sql_1)
        data = cur.fetchone()
        print(data)
        if data is not None: return False
        return True

    def show_data(self, data):
        for i in data:
            print(i)

    def write_item_to_mysql(self, data):
        connection = pymysql.connect(host="localhost", user="root", password="ccsu", db="guliguli", port=3306)
        print("数据库连接成功")
        cur = connection.cursor()  # 创建一个游标对象
        for item in data:
            if '\'' in item['problem']['title']: continue
            if 'score' not in item: continue
            op = self.check(item, cur)
            print(item)
            if self.check(item, cur) == False:
                connection.close()  # 断开
                print("更新完成  数据库连接关闭")
                return False
            sql = "insert into take_notes values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                item['id'],  # submission_id
                item['user']['name'],  # 用户
                self.Get_Time(item['submitTime']),  # 提交时间
                item['problem']['title'],  # 题目名称
                self.Score(item['score']),  # 提交状态
                self.lan(item['language']),  # 语言
                item['problem']['difficulty'],  # 难度
                item['time'],  # 代码运行时间
                item['sourceCodeLength'],  # 代码长度
                item['memory'],  # 代码占用空间大小
                '洛谷',  # 提交oj
                'https://www.luogu.com.cn/problem/' + item['problem']['pid'],  # 题目连接
                'https://www.luogu.com.cn/record/' + str(item['id'])  # 提交连接
            )
            print(sql)
            cur.execute(sql)
            connection.commit()  # 提交
        connection.close()  # 断开
        print("数据库连接关闭")
        return True

    def main(self, user, mycookie):
        try:
            for i in range(1, 10000):
                url = "https://www.luogu.com.cn/record/list?user=" + user + "&page=" + str(i)
                print(url)
                html_text = self.Get_Html(url, mycookie)
                data_text = self.get_data(html_text)
                if not data_text:
                    print("第{}页结束".format(i - 1))
                    return
                print("第{}页".format(i))
                # self.show_data(data_text)
                op = self.write_item_to_mysql(data_text)
                if op == False:
                    return
        except:
            return "结束"


def call(x):
    connection = pymysql.connect(host="localhost", user="root", password="ccsu", db="guliguli", port=3306)
    print("数据库连接成功")
    cur = connection.cursor()  # 创建一个游标对象
    sql = "call pro"+str(x)+"();"
    cur.execute(sql)
    ans = list()
    while True:
        data = cur.fetchone()
        if data is None: break
        ans.append(data)
        print(data)
    return ans


def write_item_to_excel(items):
    path = "C:\\Users\\tob\\Desktop\\提交记录.xls"
    rb = xlrd.open_workbook(path)
    wb = copy(rb)
    worksheet = wb.get_sheet(0)
    col = ("提交", "用户", "提交时间", "题目名称", "提交状态", "语言", "难度", "代码运行时间", "代码长度", "代码占用空间大小", "提交oj", "题目连接", "提交连接")
    for i in range(0, 13):
        worksheet.write(0, i, col[i])
    j = 1
    for item in items:
        worksheet.write(j, 0, str(item[0]))
        worksheet.write(j, 1, str(item[1]))
        worksheet.write(j, 2, str(item[2]))
        worksheet.write(j, 3, str(item[3]))
        worksheet.write(j, 4, str(item[4]))
        worksheet.write(j, 5, str(item[5]))
        worksheet.write(j, 6, str(item[6]))
        worksheet.write(j, 7, str(item[7]))
        worksheet.write(j, 8, str(item[8]))
        worksheet.write(j, 9, str(item[9]))
        worksheet.write(j, 10, str(item[10]))
        worksheet.write(j, 11, str(item[11]))
        worksheet.write(j, 12, str(item[12]))
        j = j + 1
    os.remove(path)
    wb.save(path)


if __name__ == "__main__":
    cf = CF()
    cf.main("cphdpp")
    cf.main("20km_shimakaze")
    cf.main('Yukikaze_nanoda')

    vj = vjudge()
    vj.main("zxyxhpp", 1670421363788)
    vj.main('red_pigeon', 1669103745690)

    lg = luogu()
    lg.main('478838', '__client_id=b1ae527f23df6cdb5129bbd9b32cb96ffe2aa94c; _uid=478838')
    lg.main('469768', '__client_id=bb5b146a9396b825071d2e6fb0542ea016acbb87; '
                      'login_referer=https%3A%2F%2Fwww.luogu.com.cn%2F; _uid=469768')
    data = call(3)
    write_item_to_excel(data)
