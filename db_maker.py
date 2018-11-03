from name_model import keras_Model
from utils import *
import numpy as np
import json, os

class DB_Maker:
    def __init__(self):
        self.kr_last_names = [
            name.lower() for name in get_file(
                './data/kr_last_names.txt'
            )
        ]
        self.kr_hard_coding = [
            ' '.join(line.split()) for line in get_file(
                './data/kr_hard_coding.txt'
            )
        ]
        var1 = [name.replace('-', ' ') for name in self.kr_hard_coding]
        var2 = [name.replace('-', '') for name in self.kr_hard_coding]
        self.kr_hard_coding += var1
        self.kr_hard_coding += var2

        self.kr_hard_coding = set(self.kr_hard_coding)

        self.model = keras_Model()
        self.model.load()

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
        parts = name.split()
        last = parts[-1]
        first = ' '.join(parts[:-1])
        return self.is_kr_last_name(last) and\
               self.is_kr_first_name(first)

    def update_dic(self, author, dic, elem):
        i = 0 if self.is_kr(author) else 1
        if author in dic[i]:
            dic[i][author].append(elem)
        else:
            dic[i][author] = [elem]

    def make_db(self, fromyear, toyear):
        conf_list = get_file('./data/conferences.txt')
        for conf in conf_list:
            for year in range(fromyear, toyear + 1):
                path = './database/' + conf.upper() + '/' + conf + str(year)
                if os.path.isfile(path + '.json'):
                    paper_list = json.load(open(path + '.json', 'r'))

                    every = [{}, {}]
                    first = [{}, {}]
                    last = [{}, {}]

                    for _title, author_list, url in paper_list:
                        elem = [_title.strip().strip('.'), author_list, url, conf, year]
                        for author in author_list:
                            self.update_dic(author, every, elem)
                        self.update_dic(author_list[0], first, elem)
                        self.update_dic(author_list[-1], last, elem)

                    json.dump(every[0], open(path + '_every_kr.json', 'w'))
                    json.dump(every[1], open(path + '_every_nonkr.json', 'w'))
                    json.dump(first[0], open(path + '_first_kr.json', 'w'))
                    json.dump(first[1], open(path + '_first_nonkr.json', 'w'))
                    json.dump(last[0], open(path + '_last_kr.json', 'w'))
                    json.dump(last[1], open(path + '_last_nonkr.json', 'w'))

                    print(conf, year)

if __name__ == '__main__':
    DB_Maker().make_db(2008, 2018)