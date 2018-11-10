from name_model import keras_Model
from utils import *
import numpy as np
import json, os

class DB_Maker:
    def __init__(self):
        self.model = keras_Model()
        self.model.load()

        self.kr_last_names = [
            name.lower() for name in get_file(
                './data/kr_last_names.txt'
            )
        ]
        self.kr_hard_coding = [
            smooth(' '.join(line.split())) for line in get_file(
                './data/kr_hard_coding.txt'
            )
        ]
        self.nonkr_hard_coding = [
            smooth(' '.join(line.split())) for line in get_file(
                './data/nonkr_hard_coding.txt'
            )
        ]

        var1 = [name.replace('-', ' ') for name in self.kr_hard_coding]
        var2 = [name.replace('-', '') for name in self.kr_hard_coding]
        self.kr_hard_coding += var1
        self.kr_hard_coding += var2
        self.kr_hard_coding = set(self.kr_hard_coding)

        self.ai_list = [
            ['MACHINE LEARNING', 'ML', [
                'AISTATS', 'COLT', 'ICLR', 'ICML', 'NIPS', 'UAI'
            ]],
            ['COMPUTER VISION & GRAPHICS', 'CVG', [
                'CVPR', 'ECCV', 'ICCV', 'SIGGRAPH'
            ]],
            ['DATA MINING & INFORMATION RETRIEVAL', 'DMIR', [
                'CIKM', 'ICDM', 'KDD', 'SIGIR', 'WSDM', 'WWW'
            ]],
            ['ARTIFICIAL INTELLIGENCE', 'AI', [
                'AAAI', 'IJCAI'
            ]],
            ['NATURAL LANGUAGE PROCESSING', 'NLP', [
                'ACL', 'EMNLP', 'NAACL'
            ]],
            ['ROBOTICS', 'R', [
                'ICRA', 'IROS', 'RSS'
            ]]
        ]
        self.non_ai_list = sorted([
            ['THEORY', 'T', [
                'FOCS', 'SIGMETRICS', 'SODA', 'STOC', 'ISIT'
            ]],
            ['COMPUTER ARCHITECTURE', 'CA', [
                'ASPLOS', 'HPCA', 'ISCA', 'MICRO'
            ]],
            ['NETWORKS', 'N', [
                'SIGCOMM', 'NSDI', 'INFOCOM', 'MOBIHOC', 'CONEXT'
            ]],
            ['SECURITY & CRYPTO', 'SC', [
                'CCS', 'IEEE-S&P', 'USENIX-SECURITY', 'NDSS', 'CRYPTO'
            ]],
            ['DATABASES', 'D', [
                'SIGMOD', 'VLDB', 'PODS', 'ICDE'
            ]],
            ['OPERATING SYSTEMS', 'OS', [
                'OSDI', 'SOSP', 'EUROSYS', 'FAST', 'USENIX-ATC'
            ]]
        ])

    def is_kr_last_name(self, last_name):
        return last_name.lower() in self.kr_last_names

    def is_kr_first_name(self, first_name):
        first = ''
        idx = set()
        for _part in first_name.split():
            part = normalize(_part)
            if len(part) > 1:
                # print(part, self.model.pred(part))
                idx.add(np.argmax(self.model.pred(part)))
                first += part
        if len(first) > 1:
            # print(first, self.model.pred(first))
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
        return self.is_kr_last_name(last) and\
           self.is_kr_first_name(first)

    def update_dic(self, author, dic, elem):
        i = 0 if self.is_kr(author) else 1
        if author in dic[i]:
            dic[i][author].append(elem)
        else:
            dic[i][author] = [elem]

    def make_area_table(self, fromyear, toyear):
        ai_table = []
        for area, id, conf_list in self.ai_list:
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
            ai_table.append([area, id, temp])

        non_ai_table = []
        for area, id, conf_list in self.non_ai_list:
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
            non_ai_table.append([area, id, temp])

        new_ai_table = []
        for i in range(len(ai_table)):
            if i % 3 == 0:
                new_ai_table.append([])
            new_ai_table[i // 3].append(ai_table[i])
        new_non_ai_table = []
        for i in range(len(non_ai_table)):
            if i % 3 == 0:
                new_non_ai_table.append([])
            new_non_ai_table[i // 3].append(non_ai_table[i])
        
        with open('./database/area_table.json', 'w') as f:
            json.dump([['AI', new_ai_table], ['non-AI (but related)', new_non_ai_table]], f)

    def make_db(self, fromyear, toyear):
        conf_list = get_file('./data/conferences.txt')
        author_dic = json.load(open('./database/author_dic.json'))
        for conf in conf_list:
            for year in range(fromyear, toyear + 1):
                path = './database/' + conf.upper() + '/' + conf + str(year)
                if not os.path.isfile(path + '.json'):
                    continue
                paper_list = json.load(open(path + '.json', 'r'))

                every = [{}, {}]
                first = [{}, {}]
                last = [{}, {}]

                for _title, _author_list, url in paper_list:
                    author_list = [
                        author_dic[author] if author in author_dic
                        else author for author in _author_list
                    ]
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
    db_maker = DB_Maker()
    db_maker.make_area_table(1950, 2018)
    # db_maker.make_db(1950, 2018)
