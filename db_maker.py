from name_model import keras_Model
from name_gender_model import keras_gender_Model
from utils import *
import json, os, copy
from datetime import datetime

min_year = 1960
max_year = datetime.now().year


class DB_Maker:
    def __init__(self):
        self.model = None
        self.gender_model = None

        self.kr_last_names = [name.lower() for name in get_file('./data/kr_last_names.txt')]
        self.kr_hard_coding = [smooth(' '.join(line.split())) for line in get_file('./data/kr_hard_coding.txt')]
        self.nonkr_hard_coding = [smooth(' '.join(line.split())) for line in get_file('./data/nonkr_hard_coding.txt')]

        var1 = [name.replace('-', ' ') for name in self.kr_hard_coding]
        var2 = [name.replace('-', '') for name in self.kr_hard_coding]
        self.kr_hard_coding = set(self.kr_hard_coding + var1 + var2)

        self.man_hard_coding = [smooth(' '.join(line.split())) for line in get_file('./data/man_hard_coding.txt')]
        self.woman_hard_coding = [smooth(' '.join(line.split())) for line in get_file('./data/woman_hard_coding.txt')]

        self.area_list = sorted(json.load(open('./data/area_list.json')), key=lambda x: (-len(x[1]), x[0]))

    def load_model(self):
        self.model = keras_Model()
        self.model.load()

        self.gender_model = keras_gender_Model()
        self.gender_model.load()

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

    def prob_woman_first(self, first_name):
        first = ''.join([normalize(part) for part in first_name.split()])
        return self.gender_model.pred(first)[0]

    def prob_woman(self, name):
        if name in self.woman_hard_coding:
            return 1
        if name in self.man_hard_coding:
            return 0

        parts = name.split()
        if len(parts) > 1:
            first = ' '.join(parts[:-1])
        else:
            first = parts[0]
        return self.prob_woman_first(first)

    def update_dict(self, author, _dict, elem):
        if author in _dict:
            _dict[author].append(elem)
        else:
            _dict[author] = [self.prob_kr(author), elem]

    def make_gender_dict(self, fromyear, toyear):
        gender_dict = {}
        # key: author name / value: prob for woman
        conf_list = get_file('./data/conferences.txt')

        for conf in conf_list:
            for year in range(fromyear, toyear + 1):
                path = './database/' + conf.upper() + '/' + conf + str(year) + '_korean.json'
                if not os.path.isfile(path):
                    continue
                data = json.load(open(path))
                print('predict genders on ' + path)
                for author in data.keys():
                    if author not in gender_dict:
                        gender_dict[author] = self.prob_woman(author)

        with open('./database/gender_dict.json', 'w') as f:
            json.dump(gender_dict, f)

    def make_configuration(self, fromyear, toyear):
        area_table = []
        recent_year_dict = {}
        for i, area in enumerate(self.area_list):
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
                        recent_year_dict[conf.lower()] = year
                        break
                y += ')'
                temp.append([x, y])
            if i % 3 == 0:
                area_table.append([])
            area_table[-1].append([title, temp])
        
        with open('./database/area_table.json', 'w') as f:
            json.dump(area_table, f)
        with open('./data/recent_year_dict.json', 'w') as f:
            json.dump(recent_year_dict, f)

    def make_conf_year_db(self, conf, year):
        author_dic = json.load(open('./data/author_dic.json'))
        options = ['all', 'korean', 'first', 'last', 'korean_first', 'korean_last']

        # if conf != 'cvpr' or year != 2018: continue
        path = './database/' + conf.upper() + '/' + conf + str(year)
        if not os.path.isfile(path + '.json'):
            return False

        paper_list = json.load(open(path + '.json', 'r'))
        data = [{} for _ in range(len(options))]

        for _title, _author_list, url, _pages in paper_list:
            author_list = [
                author_dic[author] if author in author_dic
                else author for author in _author_list
            ]
            if conf == 'sigmetrics' and year >= 2018:
                pages = 6
            else:
                pages = _pages
            elem = [_title.strip().strip('.'), author_list, url, pages, conf, year]
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
        #     coauthor_dict = {}
        #     for author, value in data[i].items():
        #         paper_list = value[1:]
        #         coauthor_dict[author] = {}
        #         for _, coauthor_list, __, ___, ____, _____ in paper_list:
        #             for coauthor in coauthor_list:
        #                 # if coauthor != author and (i != 1 or self.is_kr(coauthor)):
        #                 if coauthor != author:
        #                     try:
        #                         coauthor_dict[author][coauthor] += 1
        #                     except KeyError:
        #                         coauthor_dict[author][coauthor] = 1
        #     json.dump(coauthor_dict, open(path + '_coauthor_' + option + '.json', 'w'))

        print(conf, year)
        return True

    def make_conf_db(self, conf, fromyear, toyear):
        for year in range(fromyear, toyear + 1):
            self.make_conf_year_db(conf, year)

    def make_all_db(self, fromyear, toyear):
        conf_list = get_file('./data/conferences.txt')
        for conf in conf_list:
            self.make_conf_db(conf, fromyear, toyear)

    def fix_db(self, fromyear, toyear):
        author_dic = json.load(open('./data/author_dic.json'))
        options = ['all', 'korean', 'first', 'korean_first', 'last', 'korean_last']
        conf_list = get_file('./data/conferences.txt')

        for conf in conf_list:
            for year in range(fromyear, toyear + 1):
                path = './database/' + conf.upper() + '/' + conf + str(year)
                if not os.path.isfile(path + '.json'):
                    continue

                # assumption: there is no person who used two names in one (conf, year)
                for i, option in enumerate(options):
                    data = json.load(open(path + '_' + option + '.json'))
                    new_data = {}

                    for author, value in data.items():
                        new_value = copy.deepcopy(value)

                        for j in range(1, len(value)):
                            coauthor_list = value[j][1]
                            for k in range(len(coauthor_list)):
                                coauthor = coauthor_list[k]
                                if coauthor in author_dic:
                                    new_value[j][1][k] = author_dic[coauthor]

                        if author in author_dic:
                            new_data[author_dic[author]] = new_value
                        else:
                            new_data[author] = new_value

                    json.dump(new_data, open(path + '_' + option + '.json', 'w'))

                # for co in ['', 'coauthor_']:
                for i in range(0, 6, 2):
                    all = options[i]
                    kor = options[i + 1]
                    all_data = json.load(open(path + '_' + all + '.json'))
                    kor_data = json.load(open(path + '_' + kor + '.json'))
                    for author in all_data.keys():
                        if author in self.kr_hard_coding:
                            all_data[author][0] = 1
                            kor_data[author] = all_data[author]
                        if author in self.nonkr_hard_coding:
                            all_data[author][0] = 0
                            if author in kor_data:
                                del kor_data[author]

                    json.dump(all_data, open(path + '_' + all + '.json', 'w'))
                    json.dump(kor_data, open(path + '_' + kor + '.json', 'w'))

                print(conf, year)


if __name__ == '__main__':
    db_maker = DB_Maker()
    db_maker.load_model()  # It takes some time

    db_maker.make_gender_dict(min_year, max_year)

    # db_maker.make_conf_db('icassp', min_year, max_year)
    # db_maker.make_conf_db('interspeech', min_year, max_year)

    # db_maker.make_conf_year_db('sigmetrics', 2018)
    # db_maker.fix_db(min_year, max_year)
    # print(db_maker.is_kr('Sungjin Im'))
    # db_maker.make_configuration(min_year, max_year)
    # db_maker.make_all_db(min_year, max_year)
