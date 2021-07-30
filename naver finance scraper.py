from connect_info import *
import pymysql
import urllib.request
from bs4 import BeautifulSoup
import os, re, datetime

def connect_db():
    
    conn = pymysql.connect(host=connect_info["host"], user=connect_info["user"], password=connect_info["password"], db=connect_info["db"], charset=connect_info["charset"])
    return conn
    
#종목정보 DBMS에서 불러오기
conn = connect_db()
cur = conn.cursor()
cur.execute("select * from stock_info")

stock_info = cur.fetchall()
print("rows of data: "+str(len(stock_info)))
conn.close()

df1 = []
df2 = []
for row in stock_info:
    try:
        #네이버 금융에서 기업개요, 주주명, 지분율 데이터 수집
        data = urllib.request.urlopen("https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd="+row[0]).read().decode("utf-8")
        soup = BeautifulSoup(data, 'html.parser')
        data1 = soup.select(".cmp_comment > ul > li")
        data2 = soup.select("#cTB13 > tbody > tr > td:nth-child(1)")
        data3 = soup.select("#cTB13 > tbody > tr > td:nth-child(3)")
        
        print(row[1], '\n')

        
        #기업개요 추출
        overview = []
        for i in range(0, len(data1)):
            overview.append(data1[i].text)
        overview = '\"' + ' '.join(overview) + '\"'

        df1.append([row[0], overview])
        
        print(overview)
        
        #지분율 추출
        for i, j in zip(data2, data3):
            if i.attrs['title'] != '':                    
                share = [row[0], row[1], datetime.date.today().strftime("%y%m%d"), i.attrs['title'], j.text.strip()]
                df2.append(share)
                print(share)
                
            else:
                continue
        
    except:
        continue

#DBMS에 저장
conn = connect_db()
cur = conn.cursor()

for row in df1:
    try:
        cur.execute("update stock_info set overivew = "+str(row[1])+" where stock_code = "+str(row[0]))
        
    except:
        traceback.print_stack()
        traceback.print_exc()
        continue
    
for row in df2:
    try:
        cur.execute("insert share(stock_code, stock_name, date, holder_name, share) values("+str(row[0])+", "+str(row[1])+", "+str(row[2])+", "+str(row[3])+", "+row[4]+")")
        
    except:
        traceback.print_stack()
        traceback.print_exc()
        continue
    
conn.commit()
conn.close()
