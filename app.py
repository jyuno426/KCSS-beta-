#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 17:45:03 2018
@author: Seunghyun Lee, Junho Han
"""
from flask import Flask, render_template
from datetime import datetime
import json, os, copy
import numpy as np

#############################
#####  HELPER FUNCTIONS #####
#############################
def dict_update(dict1, dict2):
    for key, value in dict2.items():
        if key in dict1:
            dict1[key] += value
        else:
            dict1[key] = value

def dict_update2(dict1, dict2):
    for key, value in dict2.items():
        if key in dict1:
            for subkey, subvalue in dict2[key].items():
                if subkey in dict1[key]:
                    dict1[key][subkey] += subvalue
                else:
                    dict1[key][subkey] = subvalue
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
    max_papers = -temp1[0][0]
    temp2 = sorted([(x[1].split()[-1], x[1]) for x in temp1])
    name_list = [x[1] for x in temp2]

    # For display, e.g. Jinwoo Shin (10) AISTATS=4, ICML=3, NIPS=3

    part_dict = {}
    info_dict = {}
    for author in name_list:
        info_dict[author] = {}
        part_dict[author] = [big_dict[author], len(big_dict[author])]
        for paper in big_dict[author]:
            try:
                info_dict[author][paper[3].upper()] += 1
            except KeyError:
                info_dict[author][paper[3].upper()] = 1
    
    temp_dict = copy.deepcopy(info_dict) # for later
    
    for author in name_list:
        temp = ""
        for conf in sorted(info_dict[author].keys()):
            temp += conf + "=" + str(info_dict[author][conf]) + ', '
        info_dict[author] = temp[:-2]

    
    author_colour_dict = {}
    if len(conf_list) <= 5:
        colours = [(0,255,255), (251,161,0), (230,230,250), (182,161,146), (255,247,192)]
        colour_dict = {x.upper():np.array(colours[conf_list.index(x)]) for x in conf_list}
        for author in temp_dict.keys():
            total = sum([temp_dict[author][x] for x in temp_dict[author].keys()])
            coefficients_dict = {x:temp_dict[author][x]/total for x in temp_dict[author].keys()}
            temp = 0
            for x in temp_dict[author].keys():
                temp += coefficients_dict[x]*(np.power(colour_dict[x],2))
            temp = np.sqrt(temp).astype(int)
            author_colour_dict[author] = 'rgba(' + ','.join(temp.astype(str))+',0.8)'
    
    else:
        author_colour_dict = {x:"rgba(204,203,198,0.8)" for x in temp_dict.keys()}

    temp_edge_dict = {}
    
    for conf in conf_list:
        for year in range(toyear, fromyear-1, -1):
            temp = copy.deepcopy(coauthor_dict[conf][year][filter])  # must use copy.deepcopy
            dict_update2(temp_edge_dict, temp)    
    
    
    edge_dict = {}
    # dic = json.load(open("./database/ICML/icml2018_coauthor_all.json"))
    for author in name_list:
        edge_dict[author] = {}
        for key, value in temp_edge_dict[author].items():
            if key in name_list:
                edge_dict[author][key] = value
    
    edge_scaling_factor = max([max(x.values()) for x in edge_dict.values() if bool(x)])
    
    return render_template("display.html",
                           name_list = name_list,
                           dictionary = part_dict,
                           info_dict = info_dict,
                           node_colour_dict = author_colour_dict,
                           edge_dict = edge_dict,
                           edge_scaling_factor = edge_scaling_factor,
                           max_papers = max_papers)


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
