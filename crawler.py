# -*- coding: utf-8 -*-

from multiprocessing import Pool
from bs4 import BeautifulSoup
import urllib

baseurl = "http://krdic.naver.com/search.nhn?query=*&kind=keyword&page="

def process(q):
    for page in range(1, 200):
        url = baseurl.replace("*", q) + str(page)
        try:
            f = urllib.request.urlopen(url)
            html = f.read()
        except:
            print("error")
            continue
        soup = BeautifulSoup(html, "lxml")

        btns = soup.select("span.sound.play")

        sounds = [b['purl'] for b in btns]

        vocas = []
        for b in btns:
            for sib in b.parent.previous_siblings:
                if 'pronun' in str(sib):
                    pronun = sib.contents[0][1:-1].split('/')[0]
                    vocas.append(pronun)
                    break
                if sib.name == 'a':
                    for t in reversed(list(sib)):
                        t.extract()
                        if t.name == 'sup': break
                    vocas.append(sib.get_text())

        if vocas: print(page, vocas)

        for v, s in zip(vocas, sounds):
            try:
                mp3file = urllib.request.urlopen(s)
            except:
                print("error: ", v, s)
                continue
            with open('sounds/'+v+'.mp3', 'wb') as output:
                while True:
                    data = mp3file.read(4096)
                    if data:
                        output.write(data)
                    else:
                        break

        paginate = soup.find("div", class_="paginate")
        if paginate is None: break
        curp = paginate.find_all(["a", "strong"])
        if curp[-1].name == 'strong': break

with open('ksx1001.txt', 'r') as f:
    chars = f.read()

if __name__ == '__main__':
    r = chars
    for a in r:
        print(a)
        url = baseurl.replace("*", urllib.parse.quote((a+"*").encode('utf-8')))
        try:
            f = urllib.request.urlopen(url)
            html = f.read()
        except:
            print("error 2")
        soup = BeautifulSoup(html, "lxml")
        if soup.find("div", class_="section_noresult") is not None: continue

        q = [urllib.parse.quote((a+b+"*").encode('utf-8')) for b in r]
        with Pool(processes=8) as pool:
            pool.map(process, q)
