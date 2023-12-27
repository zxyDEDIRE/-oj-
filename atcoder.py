import requests
import json
class Atcoder:
    def get_html(self,url):
        try:
            head = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42"

            }
            r=requests.get(url=url,headers=head)
            print(r.status_code)
            r.raise_for_status()
            r.encoding='utf-8'
            return r.text
        except:
            return "错误"
    def main(self,my_name):
        url='https://kenkoooo.com/atcoder/proxy/users/'+my_name+'/history/json'
        html = self.get_html(url)
        data=json.loads(html)
        for i in data:
            print(i)
if __name__ == '__main__':
    at=Atcoder()
    at.main('buns_out')