# -*- coding: utf-8 -*-
import os
import json
import shutil
import requests
from bs4 import BeautifulSoup
from utils import *

dblp_url = 'https://dblp.org/db/conf/'

class DBLP_Crawler:
    def __init__(self):
        return

    def parse_data(self, rawdata):
        data = rawdata.find('div', {'class': 'data'})

        author_list = []
        for elem in data.find_all('span', {'itemprop': 'author'}):
            author = elem.find('span', {'itemprop': 'name'})
            author_list.append(author.text)
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

    def crawl_dblp_paper(self, url):
        html = BeautifulSoup(requests.get(url).text, 'lxml')

        paper_list = []
        for data in html.find_all('li', {'class': 'entry inproceedings'}):
            title, author_list, link_url = self.parse_data(data)
            if title and author_list:
                paper_list.append([title, author_list, link_url])

        return paper_list

    def get_list(self, url):
        return self.crawl_dblp_paper(url)


class Updater:
    def __init__(self):
        self.save_path = './database/'
        self.dblp_crawler = DBLP_Crawler()

    def initialize_database(self):
        open('./data/exception.txt', 'w').close()
        if os.path.isdir(self.save_path):
            shutil.rmtree(self.save_path)
        os.mkdir(self.save_path)

    def add_exception(self, conf, year):
        print('exception:', conf, year)
        with open('./data/exception.txt', 'a+') as f:
            f.write(conf + '\t' + str(year) + '\n')

    def save(self, conf, year, paper_list):
        print('success:', conf, year)
        path = self.save_path + conf.upper() + '/' + conf + str(year) + '.json'
        with open(path, 'w') as f: json.dump(paper_list, f)

    def get_conf_list(self):
        conf_list = get_file('./data/conferences.txt')
        conf_list.remove('iclr')
        return conf_list

    def get_paper_list(self, url):
        return self.dblp_crawler.get_list(url)

    def update(self, fromyear, toyear):
        self.initialize_database()  # caution! It removes all database

        for conf in self.get_conf_list():
            # conf should be in lower case.
            os.mkdir(self.save_path + conf.upper() + '/')
            for year in range(fromyear, toyear + 1):
                url = dblp_url + conf + '/' + conf + str(year) + '.html'
                paper_list = self.get_paper_list(url)
                if paper_list:
                    self.save(conf, year, paper_list)
                else:
                    self.add_exception(conf, year)

    def update_exceptions(self):
        with open('./data/correction.txt', 'r') as f:
            for line in f.readlines():
                words = [word.strip() for word in line.strip().split()]
                conf = words[0]
                year = words[1]
                paper_list = []
                check = True
                for url in words[2:]:
                    paper_list += self.get_paper_list(url)
                if check:
                    self.save(conf, year, paper_list)

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
                    author_list = []
                    for author in lines[term*i+1].split(','):
                        normalized_name = ''
                        for word in author.split():
                            _word = normalize(word)
                            if len(_word) > 0:
                                normalized_name += (' ' + _word)
                        author_list.append(normalized_name.strip())
                    paper_list.append([title, author_list, url])

            self.save('iclr', year, paper_list)

if __name__ == '__main__':
    updater = Updater()
    updater.update(2008, 2018)
    updater.update_exceptions()
    updater.update_iclr()