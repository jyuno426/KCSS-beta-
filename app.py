#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 17:45:03 2018
@author: Seunghyun Lee, Junho Han
"""
from flask import Flask, render_template
from datetime import datetime
import json, os, copy

#############################
#####  HELPER FUNCTIONS #####
#############################
def dict_update(dict1, dict2):
    for key, value in dict2.items():
        if key in dict1:
            dict1[key] += value
        else:
            dict1[key] = value


data = {}
coauthor_dict = {}
min_year = 1960
max_year = datetime.now().year
area_table = json.load(open('./database/area_table.json'))

app = Flask(__name__)  # placeholder for current module


@app.route('/')
def home():
    return render_template('home.html', years=range(min_year, max_year + 1), area_table=area_table)


@app.route('/<name>')
def display(name):
    fromyear = int(name[0:4])
    toyear = int(name[4:8])
    filter = ['all', 'korean', 'first', 'last'][int(name[8])]
    howmany = [10, 25, 50, 100, 200][int(name[9])]
    conf_list = sorted(name[10:].replace('-', ' ').lower().split('_')[1:-1])

    big_dict = {}
    names = set()

    # load data from database, for each conf, fromyear ~ toyear
    for conf in conf_list:
        for year in range(toyear, fromyear-1, -1):
            temp = copy.deepcopy(data[conf][year][filter])  # must use copy.deepcopy
            names.update(list(temp.keys()))
            dict_update(big_dict, temp)

    # Choose top "show_howmany" authors in terms of # of papers
    # Sort those authors by lexicographic order (last name, first name)

    temp1 = sorted([(-len(big_dict[x]), x) for x in names])[:howmany]
    temp2 = sorted([(x[1].split()[-1], x[1]) for x in temp1])
    name_list = [x[1] for x in temp2]

    # For display, e.g. Jinwoo Shin (10) AISTATS=4, ICML=3, NIPS=3

    part_dict = {}
    info_dict = {}
    for author in name_list:
        info_dict[author] = {}
        part_dict[author] = (big_dict[author], len(big_dict[author]))
        for paper in big_dict[author]:
            try:
                info_dict[author][paper[3].upper()] += 1
            except KeyError:
                info_dict[author][paper[3].upper()] = 1

    for author in name_list:
        temp = ""
        for conf in sorted(info_dict[author].keys()):
            temp += conf + "=" + str(info_dict[author][conf]) + ', '
        info_dict[author] = temp[:-2]

    return render_template('display.html', name=name, name_list=name_list,
                           dictionary=part_dict, info_dict=info_dict)


# @app.route('/<name>/graph')
# def graph(name):
#     fromyear = int(name[0:4])
#     toyear = int(name[4:8])
#     option = int(name[8])
#     howmany = [10, 25, 50, 100, 200][int(name[9])]
#     conf_list = sorted(
#         name[10:].replace('-', ' ').lower().split('_')[1:-1]
#     )
#     filters = ['every', 'every', 'first', 'last']
#
#     # Display options:
#     # 0. all
#     # 1. only korean
#     # 2. only first author
#     # 3. only last author
#
#     big_dic = {}
#     kr_names = set()
#     nonkr_names = set()
#
#     # load data from database, for each conf, fromyear ~ toyear
#     for conf in conf_list:
#         for year in range(toyear, fromyear - 1, -1):
#             path = './database/' + conf.upper() + '/' + \
#                    conf + str(year) + '_' + filters[option]
#             if os.path.isfile(path + '_kr.json'):
#                 kr_dic = json.load(open(path + '_kr.json', 'r'))
#                 kr_names.update(list(kr_dic.keys()))
#                 dic_update(big_dic, kr_dic)
#
#                 if option != 1:
#                     nonkr_dic = json.load(open(path + '_nonkr.json', 'r'))
#                     nonkr_names.update(list(nonkr_dic.keys()))
#                     dic_update(big_dic, nonkr_dic)
#
#     # big_dictionary available
#     big_dictionary = {}
#     for key, value in big_dic.items():
#         big_dictionary[key] = [value, len(value)]
#
#     # Data ready: 1. (non_)korean_names (list), 2. big_dictionary
#
#     korean_names = list(kr_names)
#     non_korean_names = list(nonkr_names)
#
#     # Basically sort result by # of papers
#
#     if option == 1:
#         kr = sorted([(-big_dictionary[x][1], x) for x in korean_names])
#         korean_names = [x[1] for x in kr]
#         names_list = korean_names[:howmany]
#     else:
#         combined_names = korean_names + non_korean_names
#         temp = sorted([(-big_dictionary[x][1], x) for x in combined_names])
#         combined_names = [x[1] for x in temp]
#         names_list = combined_names[:howmany]
#
#     max_papers = big_dictionary[names_list[0]][1]
#
#     info_dict = {}
#
#     for author in korean_names + non_korean_names:
#         info_dict[author] = {}
#         for paper in big_dictionary[author][0]:
#             try:
#                 info_dict[author][paper[3].upper()] += 1
#             except KeyError:
#                 info_dict[author][paper[3].upper()] = 1
#
#     author_colour_dict = {}
#     if len(conf_list) <= 5:
#         colours = [(0, 255, 255), (251, 161, 0), (230, 230, 250), (182, 161, 146), (255, 247, 192)]
#         colour_dict = {x.upper(): np.array(colours[conf_list.index(x)]) for x in conf_list}
#         for author in info_dict.keys():
#             total = sum([info_dict[author][x] for x in info_dict[author].keys()])
#             coefficients_dict = {x: info_dict[author][x] / total for x in info_dict[author].keys()}
#             temp = 0
#             for x in info_dict[author].keys():
#                 temp += coefficients_dict[x] * (np.power(colour_dict[x], 2))
#             temp = np.sqrt(temp).astype(int)
#             author_colour_dict[author] = 'rgba(' + ','.join(temp.astype(str)) + ',0.8)'
#
#     else:
#         author_colour_dict = {x: "rgba(204,203,198,0.8)" for x in info_dict.keys()}
#
#     for author in info_dict.keys():
#         temp = ""
#         for journal in sorted(info_dict[author].keys()):
#             temp += journal + "=" + str(info_dict[author][journal]) + ', '
#         temp = temp[:-2]
#         info_dict[author] = temp
#
#     return render_template('graph.html',
#                            names_list=names_list,
#                            dictionary=big_dictionary,
#                            max_papers=max_papers,
#                            info_dict=info_dict,
#                            node_colour_dict=author_colour_dict)


def init():
    from utils import get_file
    for conf in get_file('./data/conferences.txt'):
        data[conf] = {}
        coauthor_dict[conf] = {}
        print('Initial Load: ' + conf.upper())
        for year in range(min_year, max_year + 1):
            data[conf][year] = {}
            coauthor_dict[conf][year] = {}
            for filter in ['all', 'korean', 'first', 'last']:
                path = './database/' + conf.upper() + '/' + conf.lower() + str(year) + '_'
                if os.path.exists(path + filter + '.json'):
                    data[conf][year][filter] = json.load(open(path + filter + '.json'))
                    coauthor_dict[conf][year][filter] = json.load(open(path + 'coauthor_' + filter + '.json'))
                else:
                    data[conf][year][filter] = {}
                    coauthor_dict[conf][year][filter] = {}


if __name__ == '__main__':
    init()
    app.run(port=5002)
