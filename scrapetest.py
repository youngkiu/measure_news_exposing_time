from urllib.request import urlopen
from bs4 import BeautifulSoup

urlList = ("http://m.daum.net/", "http://m.naver.com/")

for url in urlList:
    print("Open", url)

    html = urlopen(url)

    filename = url
    filename = filename.replace("/", "")
    filename = filename.replace("http:", "")
    filename = filename.replace("https:", "")
    filename = filename + ".txt"
    
    print("Write", filename)

    file = open(filename, 'wt')
    file.write(html.read().decode('utf-8'))
    file.close()

    html = urlopen(url)

    bsObj = BeautifulSoup(html.read(), "html.parser")
    print(bsObj.h1)

    print("\n")
