# -*- coding: utf-8 -*-
import os
import json
import shutil
import requests
from bs4 import BeautifulSoup
from utils import *

dblp_url = 'https://dblp.org/db/conf/'

class Updater:
    def __init__(self):
        self.save_path = './database/'
        self.author_url_dic = {}
        self.author_dic = {}

    def initialize_database(self):
        open('./data/exceptions.txt', 'w').close()
        if os.path.isdir(self.save_path):
            shutil.rmtree(self.save_path)
        os.mkdir(self.save_path)

    def save(self, conf, year, paper_list):
        path = self.save_path + conf.upper() + '/' + conf + str(year) + '.json'
        with open(path, 'w') as f:
            json.dump(paper_list, f)
        print('success')

    def save_author_url_dic(self):
        path = './database/author_url_dic.json'
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.author_url_dic.update(json.load(f))
        with open(path, 'w') as f:
            json.dump(self.author_url_dic, f)

    def get_conf2dblp(self):
        conf2dblp = {}
        for conf in get_file('./data/conferences.txt'):
            conf2dblp[conf] = conf

        if 'iclr' in conf2dblp: conf2dblp.pop('iclr')

        dblp_dict = {
            'ieee s&p': 'sp',
            'usenix security': 'uss',
            'usenix atc': 'usenix',
            'fse': 'sigsoft',
            'ase': 'kbse',
            'ec': 'sigecom',
            'ubicomp': 'huc'
        }
        for conf, dblp in dblp_dict.items():
            if conf in conf2dblp:
                conf2dblp[conf] = dblp

        return conf2dblp

    def parse_data(self, rawdata):
        data = rawdata.find('div', {'class': 'data'})

        author_list = []
        for elem in data.find_all('span', {'itemprop': 'author'}):
            author = smooth(elem.find('span', {'itemprop': 'name'}).text)
            url = elem.find('a')['href']
            author_list.append(author)
            self.author_url_dic[author] = url
        title = data.find('span', {'class': 'title'}).text

        try:
            url = rawdata.find(
                'nav', {'class': 'publ'}
            ).find_all(
                'li', {'class': 'drop-down'}
            )[0].find(
                'div', {'class': 'body'}
            ).find_all('a', {'itemprop': 'url'})[0]['href']
        except:
            url = ''

        return title, author_list, url

    def get_paper_list(self, url):
        html = BeautifulSoup(requests.get(url).text, 'lxml')

        paper_list = []
        for data in html.find_all('li', {'class': 'entry inproceedings'}):
            title, author_list, link_url = self.parse_data(data)
            if title and author_list:
                paper_list.append([title, author_list, link_url])

        if not paper_list:
            for data in html.find_all('li', {'class': 'entry article'}):
                title, author_list, link_url = self.parse_data(data)
                if title and author_list:
                    paper_list.append([title, author_list, link_url])

        return paper_list

    def update_conf(self, conf, dblp, fromyear, toyear):
        # conf should be in lower case.
        print(conf)
        path = self.save_path + conf.upper() + '/'
        if not os.path.isdir(path):
            os.mkdir(path)

        html = BeautifulSoup(requests.get(dblp_url + dblp + '/').text, 'lxml').text

        exceptions = []
        for year in range(fromyear, toyear + 1):
            if os.path.exists(path + conf + str(year) + '.json') or not (str(year) in html):
                continue
            print(year)
            url = dblp_url + dblp + '/' + dblp + str(year) + '.html'
            paper_list = self.get_paper_list(url)
            if paper_list:
                self.save(conf, year, paper_list)
                continue

            url = dblp_url + dblp + '/' + dblp + str(year)[2:] + '.html'
            paper_list = self.get_paper_list(url)
            if paper_list:
                self.save(conf, year, paper_list)
                continue

            url = dblp_url + dblp + '/' + dblp + str(year) + '-1.html'
            paper_list = self.get_paper_list(url)
            if paper_list:
                i = 2
                while True:
                    url = dblp_url + dblp + '/' + dblp + str(year) + '-' + str(i) + '.html'
                    temp = self.get_paper_list(url)
                    if temp:
                        paper_list += temp
                    else:
                        break
                    i += 1
                self.save(conf, year, paper_list)
                continue

            url = dblp_url + dblp + '/' + dblp + str(year)[2:] + '-1.html'
            paper_list = self.get_paper_list(url)
            if paper_list:
                i = 2
                while True:
                    url = dblp_url + dblp + '/' + dblp + str(year)[2:] + '-' + str(i) + '.html'
                    temp = self.get_paper_list(url)
                    if temp:
                        paper_list += temp
                    else:
                        break
                    i += 1
                self.save(conf, year, paper_list)
                continue
            exceptions.append(year)
        with open('./data/exceptions.txt', 'a+') as f:
            f.write(conf)
            for year in exceptions:
                f.write(' ' + str(year))
            f.write('\n')
        self.save_author_url_dic()

    def update(self, fromyear, toyear):
        # self.initialize_database()  # caution! It removes all database

        for conf, dblp in self.get_conf2dblp().items():
            self.update_conf(conf, dblp, fromyear, toyear)

    def update_exceptions(self):
        with open('./data/corrections.txt', 'r') as f:
            for line in f.readlines():
                words = [word.strip() for word in line.strip().split()]
                conf = words[0].replace('-', ' ')
                year = words[1]
                print(conf, year)

                paper_list = []
                for url in words[2:]:
                    paper_list += self.get_paper_list(url)
                self.save(conf, year, paper_list)

        self.save_author_url_dic()

    def update_iclr(self):
        os.mkdir(self.save_path + 'ICLR/')
        for year in [2013, 2017, 2018]:
            if year == 2013:
                term = 3
                url = 'https://openreview.net/group?id=ICLR.cc/2013'
            elif year == 2017:
                term = 4
                url = 'https://openreview.net/group?id=ICLR.cc/2017/conference'
            else:
                term = 4
                url = 'https://openreview.net/group?id=ICLR.cc/2018/Conference'

            paper_list = []
            path = './data/ICLR/iclr' + str(year) + '.txt'
            with open(path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines()]
                for i in range(len(lines)//term):
                    title = lines[term*i]
                    author_list = [smooth(x) for x in lines[term*i+1].split(',')]
                    paper_list.append([title, author_list, url])

            self.save('iclr', year, paper_list)

    def correct_names(self):
        with open('./database/author_url_dic.json', 'r') as f:
            self.author_url_dic = json.load(f)

        with open('./database/author_dic.json', 'r') as f:
            self.author_dic = json.load(f)

        with open('./database/skip_author.json', 'r') as f:
            skip = set(json.load(f))

        from db_maker import DB_Maker
        db_maker = DB_Maker()

        candidates = []
        for x in self.author_url_dic.keys():
            if ('.' in x or '-' in x or len(x.split()) > 3) and db_maker.is_kr(x):
                candidates.append(x)

        candidates += [smooth(x) for x in get_file('./data/kr_hard_coding.txt')]
        candidates = sorted(list(set(candidates)))

        for i, author in enumerate(candidates):
            print(i, '/', len(candidates))
            if not(author in self.author_url_dic) or author in skip:
                continue
            url = self.author_url_dic[author]
            html = BeautifulSoup(requests.get(url).text, 'lxml')

            primary = smooth(html.find('span', {'class': 'name primary'}).text)
            secondary_list = [smooth(x.text) for x in html.find_all('span', {'class': 'name secondary'})]

            print(primary, secondary_list)

            skip.add(primary)
            for name in secondary_list:
                if name and name != name.lower():
                    skip.add(name)
                    self.author_dic[name] = primary

            with open('./database/author_dic.json', 'w') as f:
                json.dump(self.author_dic, f)
            with open('./database/skip_author.json', 'w') as f:
                json.dump(sorted(list(skip)), f)



if __name__ == '__main__':
    # pass
    updater = Updater()
    updater.update_conf('icassp', 'icassp', 1950, 2018)
    # updater.update(1950, 2018)
    # updater.update_exceptions()
    # updater.update_iclr()
    updater.correct_names()
