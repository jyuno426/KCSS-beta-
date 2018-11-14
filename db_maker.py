from name_model import keras_Model
from utils import *
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

        self.area_table = json.load(open('./data/area_list.json'))

    def is_kr_last(self, last_name):
        return last_name.lower() in self.kr_last_names

    def prob_kr_first(self, first_name):
        first = ''
        idx = set()
        a, b, c = 0, 0, 0.5
        for _part in first_name.split():
            part = normalize(_part)
            if len(part) > 1:
                prob = self.model.pred(part)
                arg = np.argmax(prob)
                if arg == 0:
                    a = max(a, scale(prob[0]))
                elif arg == 1:
                    b = max(b, scale(prob[1]))
                c = min(c, scale(prob[0]))
                idx.add(arg)
                first += part
        if len(first) > 1:
            prob = self.model.pred(first)
            arg = np.argmax(prob)
            if arg == 0:
                return scale(prob[0])
            elif arg == 1:
                b = max(b, scale(prob[1]))
            c = min(c, scale(prob[0]))
            idx.add(arg)
        if 0 in idx:
            if 1 in idx:
                return 1 - b
            else:
                return a
        else:
            return c

    def prob_kr(self, name):
        if name in self.kr_hard_coding:
            return 1
        if name in self.nonkr_hard_coding:
            return 0

        parts = name.split()
        last = parts[-1]
        first = ' '.join(parts[:-1])

        if not self.is_kr_last(last):
            return 0
        else:
            return self.prob_kr_first(first)

    def is_kr(self, name):
        return self.prob_kr(name) >= 0.5

    def update_dict(self, author, _dict, elem):
        if author in _dict:
            _dict[author].append(elem)
        else:
            _dict[author] = [self.prob_kr(author), elem]

    def make_area_table(self, fromyear, toyear):
        area_table = []
        for ai, area_list in self.area_table:
            area_table.append([ai, []])
            for i, area in enumerate(area_list):
                title, conf_list = area
                temp = []
                for x in sorted(conf_list):
                    y = '('
                    conf = x.replace('*', '')
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
                    area_table[-1][-1].append([])
                area_table[-1][-1][-1].append([title, temp])
        
        with open('./database/area_table.json', 'w') as f:
            json.dump(area_table, f)

    def make_db(self, fromyear, toyear):
        conf_list = get_file('./data/conferences.txt')
        author_dic = json.load(open('./database/author_dic.json'))
        options = ['all', 'korean', 'first', 'last', 'korean_first', 'korean_last']

        for conf in conf_list:
            for year in range(fromyear, toyear + 1):
                path = './database/' + conf.upper() + '/' + conf + str(year)
                if not os.path.isfile(path + '.json'):
                    continue
                paper_list = json.load(open(path + '.json', 'r'))
                data = [{} for _ in range(len(options))]

                for _title, _author_list, url in paper_list:
                    author_list = [
                        author_dic[author] if author in author_dic
                        else author for author in _author_list
                    ]
                    elem = [_title.strip().strip('.'), author_list, url, conf, year]
                    for author in author_list:
                        self.update_dict(author, data[0], elem)
                        if self.is_kr(author):
                            self.update_dict(author, data[1], elem)
                    first, last = author_list[0], author_list[-1]
                    self.update_dict(first, data[2], elem)
                    self.update_dict(last, data[3], elem)
                    if self.is_kr(first):
                        self.update_dict(first, data[4], elem)
                    if self.is_kr(last):
                        self.update_dict(last, data[5], elem)

                for i, option in enumerate(options):
                    json.dump(data[i], open(path + '_' + option + '.json', 'w'))
                    coauthor_dict = {}
                    for author, value in data[i].items():
                        paper_list = value[1:]
                        coauthor_dict[author] = {}
                        for _, coauthor_list, __, ___, ____ in paper_list:
                            for coauthor in coauthor_list:
                                if coauthor != author and (i != 1 or self.is_kr(coauthor)):
                                    try:
                                        coauthor_dict[author][coauthor] += 1
                                    except KeyError:
                                        coauthor_dict[author][coauthor] = 1
                    json.dump(coauthor_dict, open(path + '_coauthor_' + option + '.json', 'w'))

                print(conf, year)


if __name__ == '__main__':
    db_maker = DB_Maker()
    # print(db_maker.is_kr('Myoungsoo Jung'))
    db_maker.make_area_table(1950, 2018)
    # db_maker.make_db(1950, 2018)
