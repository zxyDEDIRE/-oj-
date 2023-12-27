import requests
import pymysql
import time
import re
import bs4
class CF:
    url=str()
    def __init__(self,url):
        self.url=url
    def Get_Html(self,url):
        try:
            head ={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.52",
                "cookie":"lastOnlineTimeUpdaterInvocation=1669046751610; X-User-Sha1=9aac3398b61f1c"
                         "34cfff5dea661274f039aa0e50; X-User=80bf3aa12253cd8ed7880d5b84001e79f9b29a5"
                         "b54fd667a5188f6dd157b8d70ea2e41e7a2efab19; _ga=GA1.2.371384411.1664722804"
                         "; mjx.menu=locale%3Azh-hans%26%3Bzscale%3A400%25%26%3Bcollapsible%3Atrue; "
                         "__utmz=71512449.1668740635.94.8.utmcsr=vjudge.net|utmccn=(referral)|utmcmd"
                         "=referral|utmcct=/; JSESSIONID=05E35F913375DA001AB96795AE4D31E6-n1; 39ce7=C"
                         "FTYublL; __utmc=71512449; evercookie_png=nv58uj04kqbrahhwvl; evercookie_etag"
                         "=nv58uj04kqbrahhwvl; evercookie_cache=nv58uj04kqbrahhwvl; 70a7c28f3de=nv58uj0"
                         "4kqbrahhwvl; lastOnlineTimeUpdaterInvocation=1669045538192; RCPC=8843f1f86af"
                         "2244081c9861cf09e38e2; __utma=71512449.371384411.1664722804.1669041414.16690"
                         "46748.104; __utmt=1; __utmb=71512449.5.10.1669046748"
            }
            r = requests.get(url=url, headers=head)
            r.raise_for_status()
            r.encoding = 'utf-8'
            print("url 连接成功")
            return r.text
        except:
            return "错误"
    def user_in(self,a):
        if len(a)>1:
            return a[0]+' '+a[1]+' '+a[2]
        else :return a[0]
    def get_time(self,a):
        b=str()
        for i in a:
            if i=='/':b=b+' '
            else :b=b+i
        t=time.mktime(time.strptime(b,"%b %d %Y %H:%M"))
        Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
        return Time

    def check(self, i, cur):
        sql_1 = "SELECT * FROM cf WHERE submission_id= %s" % (i['submission_id'])
        print(sql_1)
        cur.execute(sql_1)
        data = cur.fetchone()
        if (data != None): return False
        return True
    def get_data(self,html_text):
        pattern_1 = re.compile('>*?<span class="hiddenSource">(.*?)</span>',re.S )
        pattern_2 = re.compile('.*?<span class="format-time" data-locale="en">(.*?)</span>', re.S)
        pattern_3 = re.compile('.*?/profile/(.*?)" title', re.S)
        pattern_4 = re.compile('<a href="(.*?)">\r\n                (.*?)\r\n.*?</a>', re.S)
        pattern_5 = re.compile('<td>\r\n        (.*?)\r.*?</td>', re.S)
        pattern_6 = re.compile('submissionid="(.*?)".*?submissionverdict="(.*?)"', re.S)
        pattern_7 = re.compile('>\r\n                (.*?)\xa0ms', re.S)
        pattern_8 = re.compile('>\r\n                (.*?)\xa0KB', re.S)
        soup = bs4.BeautifulSoup(html_text, "html.parser")
        a=soup.find_all('tr')
        data=[]
        for i in a:
            if isinstance(i, bs4.element.Tag):
                a=i.get('data-submission-id')
                b=i.get('data-a')
                if( a==None or b==None):continue
                li=[]
                li.append('1')
                cnt=0
                for j in i.childGenerator():
                    # print(cnt)
                    # print(j)
                    # print('*'*30)
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
                        # print(j)
                        li.append(t_6)
                        # print(t_6)
                    elif cnt == 13:
                        t_7 = re.findall(pattern_7, str(j))
                        li.append(t_7)
                    elif cnt == 15:
                        t_8 = re.findall(pattern_8, str(j))
                        li.append(t_8)
                    cnt += 1
                # print(li)
                data.append(li)
        print(len(data))
        for i in data:
            yield {
                'data_locale':self.get_time(i[1][0]),
                'user_in':self.user_in(i[2]),
                'url':'https://codeforces.com/'+i[3][0][0],
                'title':i[3][0][1],
                'geshi':i[4][0],
                'submissionVerdict':i[5][0][1],
                'submission_url':'"https://codeforces.com//contest/1560/submission/'+i[5][0][0],
                'submission_id':i[5][0][0],
                'ms':i[6][0],
                'KM':i[7][0]
            }
    def write_item_to_mysql(self,data):
        connection = pymysql.connect(host="localhost",user="root",password="ccsu",db="guliguli",port=3306)
        print("数据库连接成功")
        cur=connection.cursor()#创建一个游标对象
        for i in data :
            if '\'' in i['title']: continue
            if self.check(i,cur) == False:
                connection.close()  # 断开
                print("内容重复")
                return 0
            sql="insert into cf values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');"%(
                i['data_locale'],
                i['user_in'],
                i['url'],
                i['title'],
                i['geshi'],
                i['submissionVerdict'],
                i['submission_url'],
                i['submission_id'],
                i['ms'],
                i['KM'],
            )
            print(sql)
            cur.execute(sql)
            connection.commit()  # 提交
        connection.close()#断开
        print("数据库连接关闭")
        return 1
    def main(self):
        for i in range(1,100000):
            url = "https://codeforces.com/submissions/cphdpp/page/"+str(i)
            html_text=self.Get_Html(url)
            # print(html_text)
            data=self.get_data(html_text)
            for i in data:
                print(i)
            # print(type(data))
            # op = self.write_item_to_mysql(data)
            # if op == False:
            #     return
if __name__ == "__main__":
    cf_1=CF("https://codeforces.com/submissions/cphdpp/page/1")
    cf_1.main()
    # cf_1.get_time('')