import os
import pymysql
import pymysql.cursors
import requests
import xlrd
from xlutils.copy import copy
import bs4


def Get_Html(url):
    try:
        head = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42",
            "cookie": '__client_id=b1ae527f23df6cdb5129bbd9b32cb96ffe2aa94c; _uid=478838'
        }
        r = requests.get(url=url, headers=head)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text
    except:
        return "错误"
def FillUnivList(html):
    soup=bs4.BeautifulSoup(html,"html.parser")
    for tr in soup.find('tbody').children:
        if isinstance(tr,bs4.element.Tag):
            tds=tr('td')
            yield {
                "运行ID":tds[0].a.string,
                "题目":tds[1].a.string,
                "运行结果":tds[2].a.string,
                "得分":tds[3].contents[0].string,
                "运行时间(ms)":tds[4].contents[0].string,
                "使用内存(KB)":tds[5].contents[0].string,
                "代码长度":tds[6].contents[0].string,
                "使用语言":tds[7].contents[0].string,
                "提交时间":tds[8].contents[0].string,
            }
def write_item_to_mysql(items):
    connection = pymysql.connect(host="localhost",user="root",password="ccsu",db="guliguli",port=3306)
    print("数据库连接成功")
    cur=connection.cursor()
    for item in items :
        sql="insert into nowcode values('%s','%s','%s','%s','%s','%s','%s','%s','%s');"%(
            str(item["运行ID"]),
            str(item["题目"]),
            str(item["运行结果"]),
            str(item["得分"]),
            str(item[ "运行时间(ms)"]),
            str(item["使用内存(KB)"]),
            str(item["代码长度"]),
            str(item["使用语言"]),
            str(item["提交时间"])
        )
        print(sql)
        cur.execute(sql)
    connection.commit()#提交
    connection.close()#断开
    print("数据库连接关闭")
def main(page):
    url="https://ac.nowcoder.com/acm/contest/profile/741959652/practice-coding?&pageSize=10&search=&statusTypeFilter=-1&languageCategoryFilter=-1&orderType=DESC&page="+str(page)
    html=Get_Html(url)
    item=FillUnivList(html)
    write_item_to_mysql(item)
if __name__ == "__main__":
    for i in range(1,8):
        main(i)