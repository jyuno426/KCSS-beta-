# -*- coding: utf-8 -*-
import json
import shutil
import requests
from bs4 import BeautifulSoup
from utils import *
from selenium import webdriver
from utils import webhook

dblp_url = 'https://dblp.org/db/conf/'


def BS(url):
    return BeautifulSoup(requests.get(url).text, 'lxml')


def get_arxiv(url):
    # print(url)
    html = BS(url)
    left = html.find('div', {'class': 'leftcolumn'})
    title = left.find('h1', {'class': 'title mathjax'}).text[6:]
    authors = [smooth(x) for x in left.find('div', {'class': 'authors'}).text.split(',')]

    pdf_url = 'https://arxiv.org' + html.find(
        'div', {'class': 'extra-services'}
    ).find_all('li')[0].find('a')['href']

    pages = 0

    return title, authors, pdf_url, pages


class Updater:
    def __init__(self):
        self.save_path = './database/'
        self.author_url_dic = {}
        self.author_dic = {}

    def initialize_database(self):
        if os.path.isdir(self.save_path):
            shutil.rmtree(self.save_path)
        os.mkdir(self.save_path)

    def save(self, conf, year, paper_list):
        path = self.save_path + conf.upper() + '/'
        if not os.path.isdir(path):
            os.mkdir(path)
        path = self.save_path + conf.upper() + '/' + conf + str(year) + '.json'
        with open(path, 'w') as f:
            json.dump(paper_list, f)
        print('success')
        webhook(conf + "-" + year + "is saved")

    def save_author_url_dic(self):
        path = './data/author_url_dic.json'
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.author_url_dic.update(json.load(f))
        with open(path, 'w') as f:
            json.dump(self.author_url_dic, f)

    def get_conf2dblp(self):
        conf2dblp = {}
        for conf in get_file('./data/conferences.txt'):
            conf2dblp[conf] = conf

        if 'iclr' in conf2dblp:
            conf2dblp.pop('iclr')
        if 'vis' in conf2dblp:
            conf2dblp.pop('vis')

        dblp_dict = {
            'ieee s&p': 'sp',
            'usenix security': 'uss',
            'usenix atc': 'usenix',
            'fse': 'sigsoft',
            'ase': 'kbse',
            'ec': 'sigecom',
            'ubicomp': 'huc',
            'neurips': 'nips'
        }
        for conf, dblp in dblp_dict.items():
            if conf in conf2dblp:
                conf2dblp[conf] = dblp

        return conf2dblp

    def parse_data(self, rawdata):
        data = rawdata.find('cite', {'class': 'data'})

        author_list = []
        for elem in data.find_all('span', {'itemprop': 'author'}):
            author = smooth(elem.find('span', {'itemprop': 'name'}).text)
            # url = elem.find('a')['href']
            author_list.append(author)
            # self.author_url_dic[author] = url
        title = data.find('span', {'class': 'title'}).text
        try:
            pagination = data.find('span', {'itemprop': 'pagination'}).text
            if '-' in pagination:
                page_from, page_to = pagination.split('-')
                pages = int(page_to) - int(page_from) + 1
            else:
                pages = 1
        except:
            pages = 0

        try:
            paper_url = rawdata.find(
                'nav', {'class': 'publ'}
            ).find_all(
                'li', {'class': 'drop-down'}
            )[0].find(
                'div', {'class': 'body'}
            ).find_all('a', {'itemprop': 'url'})[0]['href']
        except:
            paper_url = ''

        return title, author_list, paper_url, pages

    def get_paper_list(self, url):
        html = BS(url)

        paper_list = []
        for data in html.find_all('li', {'class': 'entry inproceedings'}):
            title, author_list, link_url, pages = self.parse_data(data)
            if title and author_list:
                paper_list.append([title, author_list, link_url, pages])

        if not paper_list:
            for data in html.find_all('li', {'class': 'entry article'}):
                title, author_list, link_url, pages = self.parse_data(data)
                if title and author_list:
                    paper_list.append([title, author_list, link_url, pages])

        return paper_list

    def update_conf(self, conf, dblp, fromyear, toyear):
        # conf should be in lower case.
        print(conf)
        path = self.save_path + conf.upper() + '/'
        if not os.path.isdir(path):
            os.mkdir(path)

        html = BS(dblp_url + dblp + '/').text

        success_years = []
        # exceptions = []
        for year in range(fromyear, toyear + 1):
            if os.path.exists(path + conf + str(year) + '.json') or not (str(year) in html):
                continue
            print(year)
            url = dblp_url + dblp + '/' + dblp + str(year) + '.html'
            paper_list = self.get_paper_list(url)
            if paper_list:
                self.save(conf, year, paper_list)
                success_years.append(year)
                continue

            url = dblp_url + dblp + '/' + dblp + str(year)[2:] + '.html'
            paper_list = self.get_paper_list(url)
            if paper_list:
                self.save(conf, year, paper_list)
                success_years.append(year)
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
                success_years.append(year)
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
                success_years.append(year)
                continue
            # exceptions.append(year)
        # with open('./data/exceptions.txt', 'a+') as f:
        #     f.write(conf)
        #     for year in exceptions:
        #         f.write(' ' + str(year))
        #     f.write('\n')
        # self.save_author_url_dic()
        return success_years

    def update(self, fromyear, toyear):
        # self.initialize_database()  # caution! It removes all database

        c = False
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

        # self.save_author_url_dic()

    def update_iclr(self):
        # os.mkdir(self.save_path + 'ICLR/')
        driver = webdriver.Chrome('./data/chromedriver.exe')
        driver.implicitly_wait(300)

        for year in range(2019, 2020):
            print(year)
            paper_list = []

            if year == 2013:
                url = 'https://openreview.net/group?id=ICLR.cc/2013/conference'
                driver.get(url)
                for x in driver.find_elements_by_class_name('note_content_pdf')[:23]:
                    arxiv_url = x.get_attribute('href')
                    if 'arxiv' in arxiv_url:
                        paper_list.append(get_arxiv(arxiv_url))

            elif year == 2014:
                url = 'https://iclr.cc/archive/2014/conference-proceedings/'
                html = BS(url)

                a_list = html.find(
                    'div', {'id': 'sites-chrome-everything-scrollbar'}
                ).find(
                    'table', {'id': 'sites-chrome-main'}
                ).find(
                    'div', {'id': 'sites-canvas-main'}
                ).find(
                    'div', {'dir': 'ltr'}
                ).find_all('a')

                for x in a_list:
                    arxiv_url = x['href']
                    if 'arxiv' in arxiv_url:
                        paper_list.append(get_arxiv(arxiv_url))

            elif year == 2015 or year == 2016:
                url = 'https://iclr.cc/archive/www/doku.php%3Fid=iclr' + str(year) + ':accepted-main.html'
                html = BS(url)

                for level3 in html.find_all('div', {'class': 'level3'})[:2]:
                    for x in level3.find_all('a'):
                        arxiv_url = x['href']
                        if 'arxiv' in arxiv_url:
                            paper_list.append(get_arxiv(arxiv_url))

            elif year == 2017:
                url = 'https://openreview.net/group?id=ICLR.cc/2017/conference'
                driver.get(url)

                for x in driver.find_elements_by_xpath('//*[starts-with(@id, "note_")]')[:198]:
                    title = x.find_element_by_class_name('note_content_title').text
                    authors = [smooth(y) for y in x.find_element_by_class_name('signatures').text.split(',')]
                    pdf_url = x.find_element_by_class_name('note_content_pdf').get_attribute('href')
                    pages = 0
                    paper_list.append([title, authors, pdf_url, pages])

            elif year == 2018 or year == 2019:
                url = 'https://openreview.net/group?id=ICLR.cc/' + str(year) + '/Conference'
                driver.get(url)

                aaa = []
                while not aaa:
                    try:
                        html = BeautifulSoup(driver.page_source, 'lxml')
                        aaa = html.find(
                            'div', {'id': 'accepted-oral-papers'}
                        ).find_all(
                            'li', {'class': 'note '}
                        )
                    except:
                        pass

                driver.find_element_by_xpath('//*[@id="notes"]/div/ul/li[2]/a').click()

                bbb = []
                while not bbb:
                    try:
                        html = BeautifulSoup(driver.page_source, 'lxml')
                        bbb = html.find(
                            'div', {'id': 'accepted-poster-papers'}
                        ).find_all(
                            'li', {'class': 'note '}
                        )
                    except:
                        pass

                for x in aaa + bbb:
                    try:
                        title = x.find('h4').text.strip()
                        authors = [smooth(y) for y in x.find('div', {'class': 'note-authors'}).text.split(',')]
                        pdf_url = 'https://openreview.net' + x.find('a', {'class': 'pdf-link'})['href']
                        pages = 0
                        paper_list.append([title, authors, pdf_url, pages])
                    except:
                        pass

            self.save('iclr', year, paper_list)

    def update_cvpr(self):
        paper_list = []
        path = './data/CVPR/cvpr2018.txt'
        with open(path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
            for i in range(len(lines)//4):
                title = lines[4*i]
                author_list = list(filter(None, [smooth(x) for x in lines[4*i+1].split(',')]))
                pages = 0
                paper_list.append([title, author_list, 'http://openaccess.thecvf.com/CVPR2018.py', pages])

        self.save('cvpr', 2018, paper_list)

    # def update_nips(self):
    #     paper_list = []
    #     path = './data/NIPS/nips2018.txt'
    #     with open(path, 'r', encoding='utf-8') as f:
    #         lines = [line.strip() for line in f.readlines()]
    #         for i in range(len(lines)//5):
    #             title = lines[5*i+2]
    #             author_list = list(filter(None, [smooth(x) for x in lines[5*i+4].split('·')]))
    #             paper_list.append([title, author_list, 'https://nips.cc/Conferences/2018/Schedule?type=Poster'])
    #
    #     self.save('nips', 2018, paper_list)

    def correct_names(self):
        with open('./data/author_url_dic.json', 'r') as f:
            self.author_url_dic = json.load(f)

        with open('./data/author_dic.json', 'r') as f:
            self.author_dic = json.load(f)

        with open('./data/skip_author.json', 'r') as f:
            skip = set(json.load(f))

        from db_maker import DB_Maker
        db_maker = DB_Maker()

        candidates = []
        for x in self.author_url_dic.keys():
            if db_maker.is_kr(x):  # ('.' in x or '-' in x or len(x.split()) > 3)
                candidates.append(x)

        candidates += [smooth(x) for x in get_file('./data/kr_hard_coding.txt')]
        candidates = sorted(list(set(candidates)))

        print(len(candidates))

        for i, author in enumerate(candidates):
            print(i, '/', len(candidates))
            if not(author in self.author_url_dic) or author in skip:
                continue
            url = self.author_url_dic[author]
            html = BS(url)

            primary = smooth(html.find('span', {'class': 'name primary'}).text)
            secondary_list = [smooth(x.text) for x in html.find_all('span', {'class': 'name secondary'})]

            print(primary, secondary_list)

            skip.add(primary)
            for name in secondary_list:
                if name and name != name.lower():
                    skip.add(name)
                    self.author_dic[name] = primary

            with open('./data/author_dic.json', 'w') as f:
                json.dump(self.author_dic, f)
            with open('./data/skip_author.json', 'w') as f:
                json.dump(sorted(list(skip)), f)



if __name__ == '__main__':
    # pass
    updater = Updater()
    # updater.update_conf('icassp', 'icassp', 1950, 2019)
    # updater.update_conf('interspeech', 'interspeech', 1950, 2019)
    # updater.update_exceptions()
    # updater.update(1950, 2019)
    # updater.update_iclr()
    # updater.update_cvpr()
    # updater.correct_names()
