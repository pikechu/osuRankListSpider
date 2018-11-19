import asyncio
import time
import requests

header='http://osu.ppy.sh/'
middle='p/pp/?'
mode='m=3'   # 0=stanard 1=taiko 2=ctb 3=mania
url=header+middle+mode+'&'
page=[1,10] #开始页数-结束页数

def getPages(pageNum):

    global url
    try:
        print('开始get网页')
        res=requests.get(url=url+str(pageNum),timeout=10)
        print('返回码 : ',res)

    except Exception as e:
        print(e)

def main():
    startTime = time.time()
    for n in range(page[0],page[1]+1):
        getPages(n)
    print('总花费时间 : ', time.time() - startTime, 's')

if __name__=='__main__':

    startTime=time.time()
    main()
    print('花费时间 : ', time.time() - startTime, 's')
    print('ok')


