from urllib.request import urlopen

url = ("http://m.daum.net/", "http://m.naver.com/")

for i in range(0, len(url)):
    print("Open", url[i])

    html = urlopen(url[i])

    filename = url[i]
    filename = filename.replace("/", "")
    filename = filename.replace("http:", "")
    filename = filename.replace("https:", "")
    filename = filename + ".txt"
    
    print("Write", filename)

    file = open(filename, 'wt')
    file.write(html.read().decode('utf-8'))
    file.close()
