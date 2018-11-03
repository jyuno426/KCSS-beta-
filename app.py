#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 17:45:03 2018
@author: Seunghyun Lee, Junho Han
"""
from flask import Flask, render_template
from datetime import datetime
import json, os

#############################
#####  HELPER FUNCTIONS #####
#############################
def dic_update(dic1, dic2):
    for key, value in dic2.items():
        if key in dic1:
            dic1[key] += value
        else:
            dic1[key] = value


app = Flask(__name__)  # placeholder for current module


@app.route('/')
def home():
    fromyear = 2008
    toyear = datetime.now().year
    return render_template('home.html', years=range(fromyear, toyear+1))


@app.route('/<name>')
def display(name):
    fromyear = int(name[0:4])
    toyear = int(name[4:8])
    option = int(name[8])
    howmany = [10, 25, 50, 100, 200][int(name[9])]
    conf_list = sorted(name[10:].lower().split('_')[1:-1])
    filters = ['every', 'every', 'first', 'last']

    # Display options:
    # 0. all
    # 1. only korean
    # 2. only first author
    # 3. only last author

    big_dic = {}
    kr_names = set()
    nonkr_names = set()

    # load data from database, for each conf, fromyear ~ toyear
    for year in range(toyear, fromyear-1, -1):
        for conf in conf_list:
            path = './database/' + conf.upper() + '/' +\
                   conf + str(year) + '_' + filters[option]
            if os.path.isfile(path + '_kr.json'):
                kr_dic = json.load(open(path + '_kr.json', 'r'))
                kr_names.update(list(kr_dic.keys()))
                dic_update(big_dic, kr_dic)

                if option != 1:
                    nonkr_dic = json.load(open(path + '_nonkr.json', 'r'))
                    nonkr_names.update(list(nonkr_dic.keys()))
                    dic_update(big_dic, nonkr_dic)

    # big_dictionary available
    big_dictionary = {}
    for key, value in big_dic.items():
        big_dictionary[key] = [value, len(value)]

    # Data ready: 1. (non_)korean_names (list), 2. big_dictionary

    korean_names = list(kr_names)
    non_korean_names = list(nonkr_names)

    # Basically sort result by # of papers
    kr = sorted([(-big_dictionary[x][1], x) for x in korean_names])
    korean_names = [x[1] for x in kr]
    if option != 1:
        nonkr = sorted([(-big_dictionary[x][1], x) for x in non_korean_names])
        non_korean_names = [x[1] for x in nonkr]

    korean_names = korean_names[:howmany]
    non_korean_names = non_korean_names[:howmany]
    
    # for display, e.g. Jinwoo Shin (12, NIPS=3, ICML=3, AISTATS=4)
    info_dict = {}
    for author in korean_names + non_korean_names:
        info_dict[author] = {}
        for paper in big_dictionary[author][:-1]:
            try:
                info_dict[author][paper[0][3].upper()] += 1
            except KeyError:
                info_dict[author][paper[0][3].upper()] = 1
                
    for author in info_dict.keys():
        temp = ""
        for journal in info_dict[author].keys():
            temp += journal + "=" + str(info_dict[author][journal]) + ', '
        temp = temp[:-2]
        info_dict[author] = temp
    
    
    return render_template('display.html',
                           name=name,
                           dictionary=big_dictionary,
                           korean_names=korean_names,
                           non_korean_names=non_korean_names,
                           info_dict = info_dict,
                           kroption=option - 1)


if __name__ == '__main__':
    app.run(port=5002)
