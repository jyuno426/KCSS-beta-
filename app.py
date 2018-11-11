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
