import pymysql
import requests
from urllib.parse import unquote
from bs4 import BeautifulSoup
import json
import time
class luogu(object):
    user=""
    mycookie=""
    def __init__(self, user,mycookie):
        self.user = user
        self.mycookie=mycookie
    def Get_Html(self,url):
        try:
            head = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42",
                "cookie":self.mycookie
            }
            r=requests.get(url=url,headers=head)
            print(r.status_code)
            r.raise_for_status()
            r.encoding='utf-8'
            return r.text
        except:
            return "错误"
    def get_data(self,html_text):
        soup=BeautifulSoup(html_text,"html.parser")
        print(soup)
        res = soup.script.get_text()
        print(res)
        res = unquote(res.split('\"')[1])
        print(res)
        data = json.loads(res)
        data=data['currentData']['records']['result']
        return data
    def Get_Time(self,t):
        Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
        return Time
    def Score(self,a):
        if a==None :return 0;
        else :return a
    def check(self,item,cur):
        if 'score' not in item: return False
        sql_1 = "SELECT * FROM take_notes WHERE run_id= %s" % (str(item['id']))
        cur.execute(sql_1)
        data = cur.fetchone()
        if (data != None): return False
        return True
    def write_item_to_mysql(self,data):
        connection = pymysql.connect(host="localhost",user="root",password="ccsu",db="guliguli",port=3306)
        print("数据库连接成功")
        cur=connection.cursor()#创建一个游标对象
        for item in data :
            if '\'' in item['problem']['title']: continue
            if self.check(item,cur) == False:
                connection.close()  # 断开
                print("更新完成  数据库连接关闭")
                return 0
            sql="insert into take_notes values('%s','%s','%s','%s','%s','%s','%s','%s','%s');"%(
                str(item['id']),
                item['user']['name'],
                item['time'],
                item['problem']['pid'],
                item['problem']['title'],
                item['problem']['difficulty'],
                item['sourceCodeLength'],
                self.Get_Time(item['submitTime']),
                self.Score(item['score'])
            )
            print(sql)
            # cur.execute(sql)
            # connection.commit()  # 提交
        connection.close()#断开
        print("数据库连接关闭")
        return 1
    def main(self):
        try:
            for i in range(1,2):
                url = "https://www.luogu.com.cn/record/list?user=" + self.user + "&page=" + str(i)
                html_text = self.Get_Html(url)
                data_text = self.get_data(html_text)
                if(data_text==[]):
                    print("第{}页结束".format(i-1))
                    return
                print("第{}页".format(i))
                # op = self.write_item_to_mysql(data_text)
                # if op == 0:
                #     return
        except:
            return i+"结束"
if __name__ == "__main__":
    luogu_a=luogu('478838','__client_id=b1ae527f23df6cdb5129bbd9b32cb96ffe2aa94c; _uid=478838')
    luogu_a.main()
    # luogu_b=luogu('469768','__client_id=bb5b146a9396b825071d2e6fb0542ea016acbb87; login_referer=https%3A%2F%2Fwww.luogu.com.cn%2F; _uid=469768')
    # luogu_b.main()



