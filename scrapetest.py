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
    file.write(urlopen(url).read())
    file.close()

def removeOldMinValue(newsDic, numOfLatestNews):
    global DATABASE_MAX_SIZE
    
    numOfNews = 0
    for item in newsDic.items():
        numOfNews += 1

    if numOfNews > DATABASE_MAX_SIZE:
        guardRegion = numOfLatestNews * 2
        if guardRegion >= DATABASE_MAX_SIZE:
            print("Error", numOfLatestNews)
            return
        
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

def checkDaumNews(newsDic):
    url = "http://m.daum.net/"
    
    saveWebPage(url)

    html = urlopen(url)
    bsObj = BeautifulSoup(html.read(), "html.parser")

    numOfLatestNews = 0

    newsTop = bsObj.find(id="channel_news1_top")
    newsItems = newsTop.div.ul
    newsText = newsItems.get_text()
    newsArray = newsText.splitlines()
    for news in newsArray:
        news = news.strip()
        if (news + ' ').isspace() == False and \
            news.find('전국날씨') != 0 and \
            news.find('전국 날씨') != 0:
            if news in newsDic.keys():
                value = newsDic.pop(news)
                value += 1
            else:
                value = 1
            newsDic[news] = value

            numOfLatestNews += 1

    removeOldMinValue(newsDic, numOfLatestNews)

def checkNaverNews(newsDic):
    url = "http://m.naver.com/"
    
    saveWebPage(url)

    numOfLatestNews = 0

    html = urlopen(url)
    bsObj = BeautifulSoup(html.read(), "html.parser")

    newsTop = bsObj.find(id="_MM_FLICK_FIRST_PANEL")
    newsItems = newsTop.div.ul
    newsText = newsItems.get_text()
    newsArray = newsText.splitlines()
    for news in newsArray:
        news = news.strip()
        if (news + ' ').isspace() == False and \
            news.find('브리핑') != 0 and \
            news.find('전국날씨') != 0 and \
            news.find('속보') != 0 and \
            news.find('조간 1면') != 0 and \
            news.find('날씨') != 0 and \
            news.find('이시각 전국 날씨') != 0:
            if news in newsDic.keys():
                value = newsDic.pop(news)
                value += 1
            else:
                value = 1
            newsDic[news] = value
    
            numOfLatestNews += 1

    removeOldMinValue(newsDic, numOfLatestNews)


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
        print(daumNews[news], news)
    print("")

    print("Accumulated time of Naver news")
    for news in naverNews:
        print(naverNews[news], news)
    print("")


if __name__ == '__main__':
    onTimer()

