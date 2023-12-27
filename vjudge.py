import requests
import pymysql
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import unquote

class vjudge:
    name=str()
    start=int()
    def __init__(self,name,start):
        self.name = name
        self.start = start
    def Get_Time(self,t):
        Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t/1000))
        return Time
    def Get_Html(self,url):
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
    def get_data(self,html_text):
        soup = BeautifulSoup(html_text, "html.parser")
        res = soup.get_text()
        data = json.loads(res)
        data = data['data']
        return data
    def check(self,item,cur):
        sql_1 = "SELECT * FROM vjudge WHERE run_id= %s" % (str(item['runId']))
        cur.execute(sql_1)
        data = cur.fetchone()
        if (data != None): return False
        return True
    def write_item_to_mysql(self,data):
        connection = pymysql.connect(host="localhost",user="root",password="ccsu",db="guliguli",port=3306)
        print("数据库连接成功")
        cur=connection.cursor()#创建一个游标对象
        for item in data :
            # op=self.check(item,cur)
            # print(op)
            print(item)
            if self.check(item,cur) == False:
                connection.close()  # 断开
                print("更新完成  数据库连接关闭")
                return 0
            sql="insert into vjudge values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');"%(
                item['memory'],
                item['statusType'],
                item['runtime'],
                item['language'],
                item['userName'],
                item['userId'],
                item['runId'],
                self.Get_Time(item['time']),
                item['oj'],
                item['problemId'],
                item['sourceLength'],
                item['probNum'],
                item['status']
            )
            print(sql)
            # cur.execute(sql)
            # connection.commit()  # 提交
        connection.close()#断开
        print("数据库连接关闭")
        return 1
    def main(self):
        for i in range(1, 2):
            url = "https://vjudge.net/status/data/?draw=" + str(90) + "&start=" + str((i - 1) * 20) + "&length=20&un=" \
                  + self.name + "&OJId=All&probNum=&res=0&language=&onlyFollowee=false&orderBy=run_id&_=" + str(self.start);
            html_text = self.Get_Html(url)
            if html_text == "{\"data\":[],\"recordsTotal\":9999999,\"recordsFiltered\":9999999,\"draw\":90}":
                print("结束")
                break
            data_text=self.get_data(html_text)
            self.write_item_to_mysql(data_text)
if __name__ == "__main__":
    v_1=vjudge("zxyxhpp",1669018365019)
    v_1.main()