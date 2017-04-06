from urllib.request import urlopen
from bs4 import BeautifulSoup

import threading
import sys
import datetime


DATABASE_MAX_SIZE = 25
CHECKING_TIMER_PERIOD = 30 * 1

def saveWebPage(url):
    filename = url
    filename = filename.replace("/", "")
    filename = filename.replace("http:", "")
    filename = filename.replace("https:", "")
    filename = filename + ".html"
    
    print("Write", filename)

    file = open(filename, 'wb')

    try:
        html = urlopen(url)
    except Exception as err:
        print(err)
    else:
        file.write(html.read())
    
    file.close()

def removeOldMinValue(newsDic, numOfLatestNews):
    global DATABASE_MAX_SIZE

    guardRegion = numOfLatestNews * 2
    if guardRegion >= DATABASE_MAX_SIZE:
        print("Error", numOfLatestNews)
        return
    
    numOfNews = 0
    for item in newsDic.items():
        numOfNews += 1

    while numOfNews > DATABASE_MAX_SIZE:
        itemIndex = 0
        removeRegion = numOfNews - guardRegion
        minValue = sys.maxsize

        for value in newsDic.values():
            itemIndex += 1
            if itemIndex > removeRegion:
                break
            
            if minValue > value:
                minValue = value

        for key in newsDic.keys():
            if newsDic[key] == minValue:
                break

        newsDic.pop(key)

        numOfNews -= 1

def updateNewNews(newsDic, newsArray):
    numOfLatestNews = 0

    for newsKey in newsArray:
        newsKey = newsKey.strip()
        if (newsKey + ' ').isspace() == False and \
            newsKey.find('브리핑') != 0 and \
            newsKey.find('전국날씨') != 0 and \
            newsKey.find('전국 날씨') != 0 and \
            newsKey.find('속보') != 0 and \
            newsKey.find('조간 1면') != 0 and \
            newsKey.find('날씨') != 0 and \
            newsKey.find('이시각 전국 날씨') != 0 and \
            newsKey.find('문답') != 0:
            if newsKey in newsDic.keys():
                newsValue = newsDic.pop(newsKey)
                newsValue += 1
            else:
                newsValue = 1
            newsDic[newsKey] = newsValue

            numOfLatestNews += 1

    if numOfLatestNews > 0:
        removeOldMinValue(newsDic, numOfLatestNews)

def checkDaumNews(newsDic):
    url = "http://m.daum.net/"
    
    saveWebPage(url)

    try:
        html = urlopen(url)
    except Exception as err:
        print(err)
    else:
        bsObj = BeautifulSoup(html.read(), "html.parser")

        newsTop = bsObj.find(id="channel_news1_top")
        newsItems = newsTop.div.ul
        newsText = newsItems.get_text()
        newsArray = newsText.splitlines()

        updateNewNews(newsDic, newsArray)

def checkNaverNews(newsDic):
    url = "http://m.naver.com/"
    
    saveWebPage(url)

    try:
        html = urlopen(url)
    except Exception as err:
        print(err)
    else:
        bsObj = BeautifulSoup(html.read(), "html.parser")

        newsTop = bsObj.find(id="_MM_FLICK_FIRST_PANEL")
        newsItems = newsTop.div.ul
        newsText = newsItems.get_text()
        newsArray = newsText.splitlines()

        updateNewNews(newsDic, newsArray)


daumNews = {}
naverNews = {}

count = 0

def onTimer():
    global daumNews
    global naverNews

    global count
    global CHECKING_TIMER_PERIOD

    count += 1
    print(count, "th", "Check,", datetime.datetime.now())
    
    checkDaumNews(daumNews)
    checkNaverNews(naverNews)

    print("")

    timer = threading.Timer(CHECKING_TIMER_PERIOD, onTimer)
    timer.start()

    print("Accumulated time of Daum news")
    for news in daumNews:
        print("{count:3d} {newsTitle}".format(count=daumNews[news], newsTitle=news))
    print("")

    print("Accumulated time of Naver news")
    for news in naverNews:
        print("{count:3d} {newsTitle}".format(count=naverNews[news], newsTitle=news))
    print("")


if __name__ == '__main__':
    onTimer()

