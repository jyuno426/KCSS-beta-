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
def sort_by_lastname(lst):
    temp = []
    for x in lst:
        pos = x.rfind(' ')
        first = x[:pos]
        last = x[pos+1:]
        temp.append(last + ' ' + first)
    lst = temp
    lst.sort()
    
    temp = []
    for x in lst:
        pos = x.lfind(' ')
        last = x[:pos]
        first = x[pos+1:]
        temp.append(first + ' ' + last)
        
    return temp

app = Flask(__name__) # placeholder for current module

@app.route('/')
def home():
    currentYear = datetime.now().year
    return render_template('home.html', years = [x for x in range(2008,currentYear+1)])

@app.route('/<name>')
def display(name):
    fromyear = int(name[0:4])
    toyear = int(name[4:8])
    option = int(name[8])
    kroption = int(name[9])
    conf_list = sorted(name[10:].lower().split('_')[1:-1])
    filters = ['every', 'every', 'first', 'last']

    # Display options:
    # 0. Default: Alphabetical
    # 1. Number of papers
    # 2. View first authors only
    # 3. View last authors only

    big_dic = {}
    kr_names = set()
    nonkr_names = set()

    # load data from database, for each conf, fromyear ~ toyear
    for conf in conf_list:
        for year in range(toyear, fromyear-1, -1):
            path = './database/' + conf.upper() + '/' +\
                   conf + str(year) + '_' + filters[option]
            if os.path.isfile(path + '_kr.json'):
                kr_dic = json.load(open(path + '_kr.json', 'r'))
                kr_names.update(list(kr_dic.keys()))
                big_dic.update(kr_dic)

                if kroption == 1:
                    nonkr_dic = json.load(open(path + '_nonkr.json', 'r'))
                    nonkr_names.update(list(nonkr_dic.keys()))
                    big_dic.update(nonkr_dic)

    # big_dictionary available
    big_dictionary = {}
    for key, value in big_dic.items():
        big_dictionary[key] = [value, len(value)]

    # Data ready: 1. (non_)korean_names (list), 2. big_dictionary

    korean_names = sorted(list(kr_names))
    non_korean_names = sorted(list(nonkr_names))

    if option == 1:
        kr = sorted([(-big_dictionary[x][1], x) for x in korean_names])
        korean_names = [x[1] for x in kr]
        nonkr = sorted([(-big_dictionary[x][1], x) for x in non_korean_names])
        non_korean_names = [x[1] for x in nonkr]
    
    return render_template('display.html',
                           name = name,
                           dictionary = big_dictionary,
                           korean_names = korean_names,
                           non_korean_names = non_korean_names,
                           kroption = kroption)


if __name__ == '__main__':
    app.run(port = 5002)