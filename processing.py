# -*- coding: utf-8 -*-
import os, sys
import urllib.parse
import urllib.request
import json
import hgtk
from bs4 import BeautifulSoup
import requests
from utils import *
import random, time


def main():
    get_authors_from_dblp()


def get_authors_from_dblp():
    page = 1
    res = []
    # res = json.load(open('./training_data/dblp_names.json'))
    while page <= 2214601:
        print(page)
        url = 'https://dblp.org/pers?pos=' + str(page)
        while True:
            try:
                html = BeautifulSoup(requests.get(url).text, 'lxml')
                break
            except:
                print("try one more time")
        author_list = html.find('div', {'id': 'browse-person-output'}).find_all('li')
        for author in author_list:
            res.append(author.text)
        with open('./training_data/dblp_names.json', 'w') as f:
            json.dump(res, f)
        page += 300


def get_data_from_naver():
    client_id = 'zgGerd3D2SkUCMkiYq6g'
    client_secret = '6lElqTXswd'

    res = []
    kr_names = get_file('./training_data/kr_given_names.txt')
    for i, name in enumerate(kr_names):
        print(str(i+1) + '/' + str(len(kr_names)))
        encText = urllib.parse.quote(name)
        url = "https://openapi.naver.com/v1/krdict/romanization?query=" + encText
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if (rescode == 200):
            response_body = response.read()
            res.append(response_body.decode('utf-8'))
        else:
            print("Error Code:" + rescode)
            break

    with open('./training_data/naver_data.json', 'w') as f:
        json.dump(res, f)


def process_naver_data():
    res = []
    cnt = 0
    data = json.load(open('./training_data/naver_data.json'))
    for elem in data:
        temp = json.loads(elem)
        try:
            candidates = temp['aResult'][0]['aItems']
            for entry in candidates:
                res.append(entry['name'])
        except:
            cnt += 1

    print(cnt)

    res.sort()
    with open('./training_data/kr_first_names_naver.txt', 'w') as f:
        for name in res:
            f.write(name + '\n')


def aaa():
    pass
    # big = sorted([elem.lower() for elem in get_file('./data/kr_last_names(big).txt')])
    # small = [elem.lower() for elem in get_file('./data/kr_last_names.txt')]
    #
    # last_names = []
    # for a in big:
    #     if a not in small:
    #         last_names.append(a)
    #
    # import json
    # from db_maker import DB_Maker
    #
    # model = DB_Maker()
    #
    # with open('./database/author_url_dic.json', 'r') as f:
    #     author_list = list(json.load(f).keys())
    #
    # res = []
    # n = len(author_list)
    # for i, author in enumerate(author_list):
    #     print(str(i+1) + '/' + str(n))
    #     temp = author.split()
    #     last = temp[-1].lower()
    #     first = ' '.join(temp[:-1])
    #
    #     if last in last_names:
    #         res.append([author, model.prob_kr_first(first)])

    # with open('consider.json') as f:
    #     res = json.load(f)
    #
    # res.sort(key=lambda x: (x[0].split()[-1], -x[1]))
    #
    # with open('consider.json', 'w') as f:
    #     json.dump(res, f)

    # mod = []
    # lset = set()
    # for a in res:
    #     if 'q' in a[0].lower() or 'x' in a[0].lower() or a[1] < 0.8:
    #         continue
    #     lset.add(a[0].lower().split()[-1])
    #     mod.append(a)
    #
    # for a in mod:
    #     print(a)
    # print(len(mod))
    # print(lset)
    # print(len(lset))


def bbb():
    pass
    # remove_long_name('./data/ch_first_names.txt', 9)
    # dump_list(sorted(list(set(
    #     get_file('./data/ch_first_names.txt')
    # ))), './data/ch_first_names.txt')

    # korean_romanization()
    # remove_long_name('./data/kr_first_names.txt', 10)
    # remove_first('ee', './data/kr_first_names.txt')
    # temp = extract_first('chee', './data/kr_first_names.txt')
    # remove_first('che', './data/kr_first_names.txt')
    # dump_list(sorted(list(set(
    #     get_file('./data/kr_first_names.txt') + temp
    # ))), './data/kr_first_names.txt')

    # res = []
    # nlist = get_file('./data/ch_first_names.txt')
    # res += nlist
    # for name in nlist:
    #     if len(name) >= 2 and name[0] == 'e' and name[1] in 'fghpsxyz':
    #         res.append('e'+name)
    # dump_list(sorted(list(set(res))), './data/ch_first_names.txt')

    # remove_long_name('./data/ch_first_names.txt', 10)
    # remove_same_prefix('./data/ch_first_names.txt')

    # name_list = []
    # with open('./raw data/NationalNames.csv', 'r') as f:
    #     for word in f.readlines():
    #         name_list.append(word.lower().strip().split(',')[1])
    # with open('./raw data/StateNames.csv', 'r') as f:
    #     for word in f.readlines():
    #         name_list.append(word.lower().strip().split(',')[1])
    #
    # name_list = sorted(list(set(name_list)))
    # dump_list(name_list, './data/us_first_names.txt')

    # remove_long_name('./data/us_first_names.txt', 15)
    # remove_same_prefix('./data/us_first_names.txt')

    # print(len(name_list))
    # for name in name_list:
    #     print(name)

def remove_long_name(path, max_len):
    res = []
    name_list = get_file(path)
    for name in name_list:
        if len(name) <= max_len:
            res.append(name)
    dump_list(sorted(res), path)


def check_prefix(str1, str2):
    n = len(str1)
    m = len(str2)
    if n > m: return False
    for i in range(n):
        if str1[i] != str2[i]:
            return False
    return True


def remove_same_prefix(path):
    name_list = get_file(path)
    name_list.sort()

    res = []
    n = len(name_list)
    for i in range(n - 1):
        if not check_prefix(name_list[i], name_list[i + 1]):
            res.append(name_list[i])
    res.append(name_list[-1])
    dump_list(sorted(res), path)


def remove_first(str, path):
    name_list = get_file(path)
    res = []
    for name in name_list:
        if not check_prefix(str, name):
            res.append(name)
    dump_list(sorted(res), path)


def extract_first(str, path):
    name_list = get_file(path)
    res = []
    for name in name_list:
        if check_prefix(str, name):
            res.append(name)
    return res


def korean_romanization():
    idx = [{}, {}, {}]

    for i in range(3):
        with open('./raw data/idx' + str(i) + '.txt', 'r') as f:
            for line in f.readlines():
                aa = line.split()
                if len(aa) > 1:
                    idx[i][aa[0]] = aa[1:]
                elif len(aa) == 1:
                    idx[i][aa[0]] = ['']
    idx[2][''] = ['']

    exception = {}
    except_list = get_file('./data/kr_exceptions.txt')
    for line in except_list:
        _line = line.split()
        exception[_line[0]] = _line[1:]

    def remove_duplicate(str):
        ja = 'bcdfghjklmnpqrstvwxyz'
        res = str[0]
        for i in range(1, len(str)):
            if str[i] in ja:
                if str[i-1] != str[i]:
                    res += str[i]
            else:
                res += str[i]
        return res

    def replace_hn_to_n(str):
        res = ''
        for i in range(len(str)-1):
            if str[i] == 'h' and str[i+1] == 'n':
                pass
            else:
                res += str[i]
        res += str[-1]
        return res

    def processing(str):
        return remove_duplicate(replace_hn_to_n(str))

    def all_combination(kr_letter):
        if kr_letter in exception:
            res = exception[kr_letter]
        else:
            res = []
        if len(kr_letter) == 1:
            a, b, c = hgtk.letter.decompose(kr_letter)
            for aa in idx[0][a]:
                for bb in idx[1][b]:
                    for cc in idx[2][c]:
                        res.append(processing(aa + bb + cc))
        return res

    def combine(list_1, list_2):
        res = []
        for a in list_1:
            for b in list_2:
                res.append(a + b)
        return res

    name_list = []
    with open('./raw data/kr_first_names.txt', 'r') as f:
        for kr_name in [w.strip() for w in f.readlines()]:
            if len(kr_name) == 1:
                name_list += all_combination(kr_name)
            else:
                name_list += combine(
                    all_combination(kr_name[0]),
                    all_combination(kr_name[1])
                ) + all_combination(kr_name)
    # name_list += get_file('./data/name data/ko.txt')


    with open('./data/kr_first_names.txt', 'w') as f:
        for name in sorted(list(set(name_list))):
            if len(name) > 3:
                f.write(name + '\n')


if __name__=='__main__':
    main()