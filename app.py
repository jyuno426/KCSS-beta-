#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 17:45:03 2018
@author: Seunghyun Lee, Junho Han
"""
from flask import Flask, render_template
from datetime import datetime
import json, os, copy
from utils import *

data = {}
coauthor_data = {}
min_year = 1960
max_year = datetime.now().year
options = ['all', 'korean', 'first', 'last', 'korean_first', 'korean_last']
area_table = json.load(open('./database/area_table.json'))

app = Flask(__name__)  # placeholder for current module


@app.route('/')
def home():
    return render_template('home.html',
                           area_table=area_table,
                           years=range(min_year, max_year + 1))


@app.route('/<name>')
def display(name):
    fromyear = int(name[0:4])
    toyear = int(name[4:8])
    option = options[int(name[8])]
    howmany = [10, 25, 50, 100][int(name[9])]
    conf_list = sorted(name[10:].replace('-', ' ').lower().split('_')[1:-1])
    graph_heights = {10: "400px", 25: "600px", 50: "800px", 100: "1140px"}
    graph_height = graph_heights[howmany]

    data_dict = {}
    prob_dict = {}
    edge_dict = {}
    names = set()

    # load data from database, for each conf, fromyear ~ toyear
    for conf in conf_list:
        for year in range(toyear, fromyear-1, -1):
            temp = copy.deepcopy(data[conf][year][option])  # must use copy.deepcopy
            names.update(list(temp.keys()))
            dict_update1(data_dict, prob_dict, temp)
            temp = copy.deepcopy(coauthor_data[conf][year][option])  # must use copy.deepcopy
            dict_update2(edge_dict, temp)

    # Choose top "howmany" authors in terms of # of papers
    # Sort those authors by lexicographic order (last name, first name)

    temp = sorted([(-len(data_dict[x]), x) for x in names])
    while howmany < len(temp):
        if temp[howmany][0] == temp[howmany-1][0]:
            howmany += 1
        else:
            break
    temp = temp[:howmany]
    max_papers = -temp[0][0] if temp else 1
    temp = sorted([(x[1].split()[-1], x[1]) for x in temp])
    name_list = [x[1] for x in temp]

    for key in list(data_dict.keys()):
        if key not in name_list:
            del data_dict[key]
        else:
            data_dict[key] = [data_dict[key], len(data_dict[key])]

    for key in list(edge_dict.keys()):
        if key not in name_list:
            del edge_dict[key]
        else:
            for key2 in list(edge_dict[key].keys()):
                if key2 not in name_list:
                    del edge_dict[key][key2]

    # For display, e.g. AISTATS=4, ICML=3, NIPS=3
    info_dict = {}
    for author in name_list:
        info_dict[author] = {}
        for paper in data_dict[author][0]:
            try:
                info_dict[author][paper[3].upper()] += 1
            except KeyError:
                info_dict[author][paper[3].upper()] = 1

    for author in name_list:
        temp = ""
        for conf in sorted(info_dict[author].keys()):
            temp += conf + "=" + str(info_dict[author][conf]) + ', '
        info_dict[author] = temp[:-2]
    
    return render_template("display.html",
                           name_list=name_list,
                           data_dict=data_dict,
                           prob_dict=prob_dict,
                           info_dict=info_dict,
                           edge_dict=edge_dict,
                           max_papers=max_papers,
                           graph_height=graph_height)


@app.route('/backdoor/<name>')
def backdoor(name):
    fromyear = int(name[0:4])
    toyear = int(name[4:8])
    option = options[int(name[8])]
    howmany = [10, 25, 50, 100][int(name[9])]
    conf_list = sorted(name[10:].replace('-', ' ').lower().split('_')[1:-1])
    graph_heights = {10: "400px", 25: "600px", 50: "800px", 100: "1140px"}
    graph_height = graph_heights[howmany]

    data_dict = {}
    prob_dict = {}
    edge_dict = {}
    names = set()

    # load data from database, for each conf, fromyear ~ toyear
    for conf in conf_list:
        for year in range(toyear, fromyear - 1, -1):
            temp = copy.deepcopy(data[conf][year][option])  # must use copy.deepcopy
            names.update(list(temp.keys()))
            dict_update1(data_dict, prob_dict, temp)
            temp = copy.deepcopy(coauthor_data[conf][year][option])  # must use copy.deepcopy
            dict_update2(edge_dict, temp)

    # Choose top "howmany" authors in terms of # of papers
    # Sort those authors by lexicographic order (last name, first name)

    temp = sorted([(-len(data_dict[x]), x) for x in names])
    while howmany < len(temp):
        if temp[howmany][0] == temp[howmany - 1][0]:
            howmany += 1
        else:
            break
    temp = temp[:howmany]
    max_papers = -temp[0][0] if temp else 1
    # temp = sorted([(x[1].split()[-1], x[1]) for x in temp])
    name_list = [x[1] for x in temp]

    for key in list(data_dict.keys()):
        if key not in name_list:
            del data_dict[key]
        else:
            data_dict[key] = [data_dict[key], len(data_dict[key])]

    for key in list(edge_dict.keys()):
        if key not in name_list:
            del edge_dict[key]
        else:
            for key2 in list(edge_dict[key].keys()):
                if key2 not in name_list:
                    del edge_dict[key][key2]

    # For display, e.g. AISTATS=4, ICML=3, NIPS=3
    info_dict = {}
    for author in name_list:
        info_dict[author] = {}
        for paper in data_dict[author][0]:
            try:
                info_dict[author][paper[3].upper()] += 1
            except KeyError:
                info_dict[author][paper[3].upper()] = 1

    for author in name_list:
        temp = ""
        for conf in sorted(info_dict[author].keys()):
            temp += conf + "=" + str(info_dict[author][conf]) + ', '
        info_dict[author] = temp[:-2]

    return render_template("display.html",
                           name_list=name_list,
                           data_dict=data_dict,
                           prob_dict=prob_dict,
                           info_dict=info_dict,
                           edge_dict=edge_dict,
                           max_papers=max_papers,
                           graph_height=graph_height)


def init():
    from utils import get_file
    for conf in get_file('./data/conferences.txt'):
        data[conf] = {}
        coauthor_data[conf] = {}
        print('Initial Load: ' + conf.upper())
        for year in range(min_year, max_year + 1):
            data[conf][year] = {}
            coauthor_data[conf][year] = {}
            for option in options:
                path = './database/' + conf.upper() + '/' + conf.lower() + str(year) + '_'
                if os.path.exists(path + option + '.json'):
                    data[conf][year][option] = json.load(open(path + option + '.json'))
                    coauthor_data[conf][year][option] = json.load(open(path + 'coauthor_' + option + '.json'))
                else:
                    data[conf][year][option] = {}
                    coauthor_data[conf][year][option] = {}


if __name__ == '__main__':
    init()
    app.run(port=5002)
