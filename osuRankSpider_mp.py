import aiohttp
import asyncio
import time
import multiprocessing as mp
import requests
from bs4 import BeautifulSoup
import socket
import re
import pprint
import os
import pymongo


url = 'https://osu.ppy.sh/rankings/mania/performance?page='#+pageNum+'#scores'
page = [1, 5]  # 开始页数-结束页数
badRequest = {}  # pageNum:resCode
htmls=[]
colls={}
#way store in mongoDB : collection: {"_id":"1", "Rank":"1","Player Name":"Jakads","Accuracy":"97.59%","Play Count":""
#"Performance":"17288pp"}

def getPages(pageNum):  #每1秒获取一个页面当做缓存

    global url
    #global badRequest
    #global htmls
    try:
        print('开始get网页,pageNum=',pageNum)
        res = requests.get(url=url +str(pageNum)+'#scores', timeout=10)
        print(url +str(pageNum)+'#scores')
        time.sleep(.1)
        # 如果res不等于200 重试3次
        count = 0
        #print(res.status_code)
        while (res.status_code != 200 and count <= 3):
            res = requests.get(url=url +str(pageNum)+'#scores', timeout=10)
            print('restart get')
            count += 1
            if (res.status_code == 200):
                return res.text
            else:
                print('pageNum : ', pageNum, '返回码 : ', res.status_code)
        if(res.status_code==200):
            #print(res.url)
            #writez(res.text)
            return res.text
        else:
            print( 'pageNum : ', pageNum, '返回码 : ', res.status_code)
            return res.status_code
    except Exception as e:
        print(e)
        return None

def findTags(html,startNum):
    soup = BeautifulSoup(html, features='lxml')
    tables = soup.findAll('table')
    # print(len(tables))

    for t in tables:
        sec = 0 #table顺序
        for tr in t.tbody.findAll('tr'):
            # print('sec:',sec)
            td_sec = 0  #table内顺序
            for td in tr.findAll('td'):
                text = td.get_text().strip()
                # print(len(text))
                if (td_sec == 0):
                    dict = {"rank": text}
                elif (td_sec == 1):
                    dict.update({"Player Name": text})
                elif (td_sec == 2):
                    dict.update({"Accuracy": text})
                elif (td_sec == 3):
                    dict.update({"Play Count": text})
                elif (td_sec == 4):
                    dict.update({"Performance": text})
                elif (td_sec == 5):
                    dict.update({"SS": text})
                elif (td_sec == 6):
                    dict.update({"S": text})
                elif (td_sec == 7):
                    dict.update({"A": text})
                td_sec += 1 #每一次遍历+1
            colls[str(startNum+sec)] = dict
            sec += 1 #每一个用户+1

def writez(col):#写入文本文件tmp.txt
    if os.path.exists('tmp.txt'):
        os.remove('tmp.txt')
    with open('tmp.txt','a',encoding='utf-8') as f:
        for k,v in col.items():
            for k2,v2 in v.items():
                f.write(k2+" : "+v2+'\n')

def mongoConnection():
    conn=pymongo.MongoClient('127.0.0.1',27017)
    db=conn.osu
    collection=db.rank
    return collection

def mongoCreateIndex(connect):
    idx_result = connect.create_index([('rank', pymongo.ASCENDING)], unique=True)
    return idx_result

def mongoInsert(col,connect):
    tmpList = []
    for k, v in col.items():
        v.update({"_id":k})
        tmpList.append(v)
        # print('ok')
    result = connect.insert_many(tmpList)
    return result

def mongoCheckDuplicate(col,connect):
    for k,v in col.items():
        for k2,v2 in v.items():
            dictz={"rank":v2}
            result=connect.find_one(dictz)
            if(result!=None):
                res=connect.delete_one(dictz)
    print('check Duplicate ok')

if __name__=='__main__':

    startTime = time.time()
    pool = mp.Pool()
    jobs=[pool.apply_async(getPages,args=(pageNum,))for pageNum in range(page[0],page[1]+1)]
    results=[j.get() for j in jobs]

    pool.close()
    pool.join()

    osu = mongoConnection()

    startNum=1

    #检索分析网页中的Tag
    for h in range(0, len(results)):
        findTags(results[h], startNum)
        startNum += 50

    #重复值鉴定,如果重复就在数据库里删除
    mongoCheckDuplicate(colls,osu)

    #插入
    try:
        res=mongoInsert(colls,osu)
        print('insert res:',res)
    except Exception as e:
        print(e)

    #创建索引
    # try:
    #     res=mongoCreateIndex(osu)
    #     print('index res:',res)
    # except Exception as e:
    #     print(e)

    print('花费时间 : ', time.time() - startTime, 's')
    print('ok')






