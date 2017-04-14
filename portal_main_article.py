__author__ = "Youngki LYU"
__copyright__ = "Copyright 2017, Youngki LYU"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "youngkiu@gmail.com"


from urllib.request import urlopen
from bs4 import BeautifulSoup

import threading
import sys
import datetime


DATABASE_MAX_SIZE = 20
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

LAST_STRING = "Last String"
SHORT_STRING_SIZE = 10
MAX_STRING_SIZE = 40

def concatenateNewsTitle(news, newsArray, newsIter, newsTitles):
    global LAST_STRING
    newsIndex = newsArray.index(news)
    prevDist = 0

    while newsIndex != 0:
        newsIndex -= 1
        prevDist += 1

        #print("prev", newsIndex, prevDist)
        if len(newsArray[newsIndex].strip()) > 0:
            prevDist = ((prevDist - len(newsArray)) * MAX_STRING_SIZE) - len(newsArray[newsIndex])
            break

    newsIndex = newsArray.index(news)
    nextDist = 0
    while newsIndex != (newsArray.index(LAST_STRING) - 1):
        newsIndex += 1
        nextDist += 1

        #print("next", newsIndex, nextDist)
        if len(newsArray[newsIndex].strip()) > 0:
            nextDist = ((nextDist - len(newsArray)) * MAX_STRING_SIZE) - len(newsArray[newsIndex])
            break

    newsTitle = news.strip()

    #print(prevDist, nextDist)
    if prevDist >= 0 and nextDist >= 0:
        concatenatedNewsTitle = newsTitle
    else:
        if prevDist < nextDist:
            concatenatedNewsTitle = "{0} | {1}".format(newsTitles.pop(), newsTitle)
        else:
            newsIndex = newsArray.index(news)
            while newsIndex != (newsArray.index(LAST_STRING) - 1):
                newsIndex += 1
                nextNews = next(newsIter)
                if len(nextNews.strip()) > 0:
                    break

            nextNewsTitle = nextNews.strip()

            if len(nextNewsTitle) < SHORT_STRING_SIZE:
                concatenatedNewsTitle = "{0} | {1}".format(newsTitle, concatenateNewsTitle(nextNews, newsArray, newsIter, newsTitles))
            else:
                concatenatedNewsTitle = "{0} | {1}".format(newsTitle, nextNewsTitle)

    return concatenatedNewsTitle

def buildNewsTitle(newsText):
    global LAST_STRING

    newsArray = newsText.splitlines()
    newsArray.append(LAST_STRING)

    newsTitles = []
    newsIter = iter(newsArray)

    news = newsArray[0]
    while news != LAST_STRING:
        newsTitle = news.strip()

        if len(newsTitle) > 0:
            if len(newsTitle) < SHORT_STRING_SIZE:
                newsTitle = concatenateNewsTitle(news, newsArray, newsIter, newsTitles)

            newsTitles.append(newsTitle)

        news = next(newsIter)

    return newsTitles

def updateNewNews(newsDic, newsTitles):
    for newsKey in newsTitles:
        if newsKey in newsDic.keys():
           newsValue = newsDic.pop(newsKey)
           newsValue += 1
        else:
           newsValue = 1

        newsDic[newsKey] = newsValue

    removeOldMinValue(newsDic, len(newsTitles))

def checkDaumNews(newsDic):
    url = "http://m.daum.net/"
    
    saveWebPage(url)

    try:
        html = urlopen(url)
    except Exception as err:
        print(err)
    else:
        bsObj = BeautifulSoup(html, "html.parser")

        newsTop = bsObj.find(id="channel_news1_top")
        newsItems = newsTop.div.ul
        newsText = newsItems.get_text()

        newsTitles = buildNewsTitle(newsText)
        if len(newsTitles) > 0:
            updateNewNews(newsDic, newsTitles)

def checkNaverNews(newsDic):
    url = "http://m.naver.com/"
    
    saveWebPage(url)

    try:
        html = urlopen(url)
    except Exception as err:
        print(err)
    else:
        bsObj = BeautifulSoup(html, "html.parser")

        newsTop = bsObj.find(id="_MM_FLICK_FIRST_PANEL")
        newsItems = newsTop.div.ul
        newsText = newsItems.get_text()
        #print(newsText)

        newsTitles = buildNewsTitle(newsText)
        if len(newsTitles) > 0:
            updateNewNews(newsDic, newsTitles)


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
        print("{count:4d} {newsTitle}".format(count=daumNews[news], newsTitle=news))
    print("")

    print("Accumulated time of Naver news")
    for news in naverNews:
        print("{count:4d} {newsTitle}".format(count=naverNews[news], newsTitle=news))
    print("")


if __name__ == '__main__':
    onTimer()

