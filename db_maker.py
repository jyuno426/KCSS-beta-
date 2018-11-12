from name_model import keras_Model
from utils import *
import numpy as np
import json, os


class DB_Maker:
    def __init__(self):
        self.model = keras_Model()
        self.model.load()

        self.kr_last_names = [name.lower() for name in get_file('./data/kr_last_names.txt')]
        self.kr_hard_coding = [smooth(' '.join(line.split())) for line in get_file('./data/kr_hard_coding.txt')]
        self.nonkr_hard_coding = [smooth(' '.join(line.split())) for line in get_file('./data/nonkr_hard_coding.txt')]

        var1 = [name.replace('-', ' ') for name in self.kr_hard_coding]
        var2 = [name.replace('-', '') for name in self.kr_hard_coding]
        self.kr_hard_coding = set(self.kr_hard_coding + var1 + var2)

        self.area_list = sorted(json.load(open('./data/area_list.json')))

    def is_kr_last_name(self, last_name):
        return last_name.lower() in self.kr_last_names

    def is_kr_first_name(self, first_name):
        first = ''
        idx = set()
        for _part in first_name.split():
            part = normalize(_part)
            if len(part) > 1:
                idx.add(np.argmax(self.model.pred(part)))
                first += part
        if len(first) > 1:
            arg = np.argmax(self.model.pred(first))
            if arg == 0:
                return True
            idx.add(arg)
        return (0 in idx) and (1 not in idx)

    def is_kr(self, name):
        if name in self.kr_hard_coding:
            return True
        if name in self.nonkr_hard_coding:
            return False
        parts = name.split()
        last = parts[-1]
        first = ' '.join(parts[:-1])
        return self.is_kr_last_name(last) and self.is_kr_first_name(first)

    def update_dict(self, author, dict, elem):
        if author in dict:
            dict[author].append(elem)
        else:
            dict[author] = [elem]

    def make_area_table(self, fromyear, toyear):
        area_table = []
        for i, area in enumerate(self.area_list):
            title, conf_list = area
            temp = []
            for x in sorted(conf_list):
                y = '('
                conf = x.replace('-', ' ')
                for year in range(fromyear, toyear + 1):
                    if os.path.exists('./database/' + conf.upper() + '/' + conf.lower() + str(year) + '.json'):
                        y += str(year)
                        break
                y += '-'
                for year in range(toyear, fromyear - 1, -1):
                    if os.path.exists('./database/' + conf.upper() + '/' + conf.lower() + str(year) + '.json'):
                        y += str(year)
                        break
                y += ')'
                temp.append([x, y])
            if i % 3 == 0:
                area_table.append([])
            area_table[-1].append([title, temp])
        
        with open('./database/area_table.json', 'w') as f:
            json.dump(area_table, f)

    def make_db(self, fromyear, toyear):
        conf_list = get_file('./data/conferences.txt')
        author_dic = json.load(open('./database/author_dic.json'))

        for conf in conf_list:
            for year in range(fromyear, toyear + 1):
                path = './database/' + conf.upper() + '/' + conf + str(year)
                if not os.path.isfile(path + '.json'):
                    continue
                paper_list = json.load(open(path + '.json', 'r'))
                dict = [{}, {}, {}, {}]

                for _title, _author_list, url in paper_list:
                    author_list = [
                        author_dic[author] if author in author_dic
                        else author for author in _author_list
                    ]
                    elem = [_title.strip().strip('.'), author_list, url, conf, year]
                    for author in author_list:
                        self.update_dict(author, dict[0], elem)
                        if self.is_kr(author):
                            self.update_dict(author, dict[1], elem)
                    self.update_dict(author_list[0], dict[2], elem)
                    self.update_dict(author_list[-1], dict[3], elem)

                for i, filter in enumerate(['all', 'korean', 'first', 'last']):
                    json.dump(dict[i], open(path + '_' + filter + '.json', 'w'))
                    coauthor_dict = {}
                    for author, paper_list in dict[i].items():
                        coauthor_dict[author] = {}
                        for _, coauthor_list, __, ___, ____ in paper_list:
                            for coauthor in coauthor_list:
                                if coauthor != author and (i != 1 or self.is_kr(coauthor)):
                                    try:
                                        coauthor_dict[author][coauthor] += 1
                                    except KeyError:
                                        coauthor_dict[author][coauthor] = 1
                    json.dump(coauthor_dict, open(path + '_coauthor_' + filter + '.json', 'w'))

                print(conf, year)


if __name__ == '__main__':
    db_maker = DB_Maker()
    # print(db_maker.is_kr('Myoungsoo Jung'))
    db_maker.make_area_table(1950, 2018)
    # db_maker.make_db(1950, 2018)
