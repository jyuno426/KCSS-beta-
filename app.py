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
    fromyear = 1960
    toyear = datetime.now().year
    ai_list = [
        ['MACHINE LEARNING', 'ML', [
            'AISTATS', 'COLT', 'ICLR', 'ICML', 'NIPS', 'UAI'
        ]],
        ['DATA MINING & INFORMATION RETRIEVAL', 'DMIR', [
            'CIKM', 'ICDM', 'KDD', 'SIGIR', 'WSDM', 'WWW'
        ]],
        ['COMPUTER VISION & GRAPHICS', 'CVG', [
            'BMVC', 'CVPR', 'ECCV', 'ICCV', 'SIGGRAPH', 'WACV'
        ]],
        ['NATURAL LANGUAGE PROCESSING', 'NLP', [
            'ACL', 'EMNLP', 'NAACL'
        ]],
        ['SPEECH & SIGNAL PROCESSING', 'SSP', [
            'AES', 'ICASSP'
        ]],
        ['ROBOTICS', 'R', [
            'ICRA', 'IROS', 'RSS'
        ]]
    ]
    non_ai_list = [
        ['THEORY', 'T', [
            'FOCS', 'SIGMETRICS', 'SODA', 'STOC', 'ISIT'
        ]],
        ['COMPUTER ARCHITECTURE', 'CA', [
            'ASPLOS', 'HPCA', 'ISCA', 'MICRO'
        ]],
        ['Networks', 'N', [
            'SIGCOMM', 'NSDI', 'INFOCOM', 'MOBIHOC'
        ]],
        ['SECURITY', 'S', [
            'CCS', 'IEEE-S&P', 'USENIX-SECURITY', 'NDSS'
        ]],
        ['DATA BASES', 'DB', [
            'SIGMOD', 'VLDB', 'PODS'
        ]],
        ['OPERATING SYSTEMS', 'OS', [
            'OSDI', 'SOSP', 'EUROSYS', 'FAST', 'USENIX-ATC'
        ]]
    ]

    ai_table = []
    ai_list.sort()
    for area, id, conf_list in ai_list:
        temp = []
        for x in sorted(conf_list):
            conf = x.replace('-', ' ')
            for year in range(fromyear, toyear + 1):
                if os.path.exists('./database/' + conf.upper() + '/' + conf.lower() + str(year) + '.json'):
                    min_year = str(year)
                    break
            for year in range(toyear, fromyear - 1, -1):
                if os.path.exists('./database/' + conf.upper() + '/' + conf.lower() + str(year) + '.json'):
                    max_year = str(year)
                    break
            temp.append([x, '(' + min_year + '-' + max_year + ')'])
        ai_table.append([area, id, temp])

    non_ai_table = []
    non_ai_list.sort()
    for area, id, conf_list in non_ai_list:
        print(area, id, conf_list)
        temp = []
        for x in sorted(conf_list):
            conf = x.replace('-', ' ')
            for year in range(fromyear, toyear + 1):
                if os.path.exists('./database/' + conf.upper() + '/' + conf.lower() + str(year) + '.json'):
                    min_year = str(year)
                    break
            for year in range(toyear, fromyear - 1, -1):
                if os.path.exists('./database/' + conf.upper() + '/' + conf.lower() + str(year) + '.json'):
                    max_year = str(year)
                    break
            temp.append([x, '(' + min_year + '-' + max_year + ')'])
        non_ai_table.append([area, id, temp])

    new_ai_table = []
    for i in range(len(ai_table)):
        if i % 3 == 0:
            new_ai_table.append([])
        new_ai_table[i//3].append(ai_table[i])
    new_non_ai_table = []
    for i in range(len(non_ai_table)):
        if i % 3 == 0:
            new_non_ai_table.append([])
        new_non_ai_table[i//3].append(non_ai_table[i])

    return render_template('home.html',
                           years=range(fromyear, toyear+1),
                           ai_table=new_ai_table,
                           non_ai_table=new_non_ai_table)


@app.route('/<name>')
def display(name):
    fromyear = int(name[0:4])
    toyear = int(name[4:8])
    option = int(name[8])
    howmany = [10, 25, 50, 100, 200][int(name[9])]
    conf_list = sorted(
        name[10:].replace('-', ' ').lower().split('_')[1:-1]
    )
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
    for conf in conf_list:
        for year in range(toyear, fromyear-1, -1):
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
    
    if option == 1:
        kr = sorted([(-big_dictionary[x][1], x) for x in korean_names])
        korean_names = [x[1] for x in kr]                
        names_list = korean_names[:howmany]
    else:
        combined_names = korean_names + non_korean_names
        temp = sorted([(-big_dictionary[x][1], x) for x in combined_names])
        combined_names = [x[1] for x in temp]
        names_list = combined_names[:howmany]
    
    # names_list available 
    
    
    
    # for display, e.g. Jinwoo Shin (12, NIPS=3, ICML=3, AISTATS=4)
    info_dict = {}
    for author in korean_names + non_korean_names:
        info_dict[author] = {}
        for paper in big_dictionary[author][0]:
            try:
                info_dict[author][paper[3].upper()] += 1
            except KeyError:
                info_dict[author][paper[3].upper()] = 1
    

    for author in info_dict.keys():
        temp = ""
        for journal in sorted(info_dict[author].keys()):
            temp += journal + "=" + str(info_dict[author][journal]) + ', '
        temp = temp[:-2]
        info_dict[author] = temp
    
    
    return render_template('display.html',
                           name=name,
                           dictionary=big_dictionary,
                           names_list=names_list,
                           info_dict=info_dict,
                           kroption=option - 1)


if __name__ == '__main__':
    app.run(port=5002, debug=True)
