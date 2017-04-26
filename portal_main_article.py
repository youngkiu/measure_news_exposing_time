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

        try:
            page = html.read()
        except Exception as err:
            print(err)
        else:
            file.write(page)

    except Exception as err:
        print(err)
    
    file.close()

def removeOldMinValue(newsDic, numOfLatestNews):
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
SHORT_STR_LEN = 8
MAX_STR_LEN = 39
MIN_STR_LEN = MAX_STR_LEN

def concatenateNewsTitle(news, newsArray, newsIter, newsTitles):
    global MIN_STR_LEN

    newsIndex = newsArray.index(news)
    prevDist = 0

    while newsIndex != 0:
        newsIndex -= 1
        prevDist += MAX_STR_LEN

        #print("prev", newsIndex, prevDist)
        if len(newsArray[newsIndex].strip()) > 0:
            prevDist = prevDist - (len(newsArray) * MAX_STR_LEN) - len(newsArray[newsIndex])
            break

    newsIndex = newsArray.index(news)
    nextDist = 0
    while newsIndex != (newsArray.index(LAST_STRING) - 1):
        newsIndex += 1
        nextDist += MAX_STR_LEN

        #print("next", newsIndex, nextDist)
        if len(newsArray[newsIndex].strip()) > 0:
            nextDist = nextDist - (len(newsArray) * MAX_STR_LEN) - len(newsArray[newsIndex])
            break

    newsTitle = news.strip()

    #print(prevDist, nextDist)
    if prevDist >= 0 and nextDist >= 0:
        concatenatedNewsTitle = newsTitle
    else:
        if prevDist < nextDist:
            concatenatedNewsTitle = "{0} | {1}".format(newsTitles.pop(), newsTitle)

            if len(newsTitle) >= SHORT_STR_LEN and \
               len(newsTitle) < MIN_STR_LEN:
                MIN_STR_LEN = len(newsTitle)
        else:
            newsIndex = newsArray.index(news)
            while newsIndex != (newsArray.index(LAST_STRING) - 1):
                newsIndex += 1
                nextNews = next(newsIter)
                if len(nextNews.strip()) > 0:
                    break

            nextNewsTitle = nextNews.strip()

            if len(nextNewsTitle) < SHORT_STR_LEN:
                concatenatedNewsTitle = "{0} | {1}".format(newsTitle, concatenateNewsTitle(nextNews, newsArray, newsIter, newsTitles))
            else:
                concatenatedNewsTitle = "{0} | {1}".format(newsTitle, nextNewsTitle)

                if len(nextNewsTitle) >= SHORT_STR_LEN and \
                   len(nextNewsTitle) < MIN_STR_LEN:
                    MIN_STR_LEN = len(nextNewsTitle)

    return concatenatedNewsTitle

def buildNewsTitle(newsText):
    global MAX_STR_LEN
    
    newsArray = newsText.splitlines()
    newsArray.append(LAST_STRING)

    newsTitles = []
    newsIter = iter(newsArray)

    news = newsArray[0]
    while news != LAST_STRING:
        newsTitle = news.strip()

        if len(newsTitle) > 0:
            if len(newsTitle) < SHORT_STR_LEN:
                newsTitle = concatenateNewsTitle(news, newsArray, newsIter, newsTitles)
                
            if len(newsTitle) > MAX_STR_LEN:
                MAX_STR_LEN = len(newsTitle)

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
        print(newsText)

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

    count += 1
    print(count, "th", "Check,", datetime.datetime.now())
    
    checkDaumNews(daumNews)
    checkNaverNews(naverNews)

    print("[Debug] News Title Length - Min({0}), Max({1})".format(MIN_STR_LEN, MAX_STR_LEN))

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

