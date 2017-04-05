from urllib.request import urlopen
from bs4 import BeautifulSoup

import threading


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

def checkDaumNews(newsDic):
    url = "http://m.daum.net/"
    
    saveWebPage(url)

    html = urlopen(url)
    bsObj = BeautifulSoup(html.read(), "html.parser")

    newsTop = bsObj.find(id="channel_news1_top")
    newsItems = newsTop.div.ul
    newsText = newsItems.get_text()
    newsArray = newsText.splitlines()
    for news in newsArray:
        if (news + ' ').isspace() == False:
            if news in newsDic.keys():
                value = newsDic.pop(news)
                value += 1
            else:
                value = 1
            newsDic[news] = value

def checkNaverNews(newsDic):
    url = "http://m.naver.com/"
    
    saveWebPage(url)

    html = urlopen(url)
    bsObj = BeautifulSoup(html.read(), "html.parser")

    newsTop = bsObj.find(id="_MM_FLICK_FIRST_PANEL")
    newsItems = newsTop.div.ul
    newsText = newsItems.get_text()
    newsArray = newsText.splitlines()
    for news in newsArray:
        if (news + ' ').isspace() == False and \
            news.find('브리핑') != 0 and \
            news.find('전국날씨') != 0:
            if news in newsDic.keys():
                value = newsDic.pop(news)
                value += 1
            else:
                value = 1
            newsDic[news] = value
    

daumNews = {}
naverNews = {}

period = 30 * 1
count = 0

def onTimer():
    global daumNews
    global naverNews

    global period
    global count

    count += 1
    print(count, "th", "Check")
    
    checkDaumNews(daumNews)
    checkNaverNews(naverNews)

    print("")

    timer = threading.Timer(period, onTimer)
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

