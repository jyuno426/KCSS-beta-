# -*- coding: utf-8 -*-

import numpy as np
import unidecode

alphabet = 'abcdefghijklmnopqrstuvwxyz'


def is_alpha(name):
    for c in name:
        if c.lower() not in alphabet:
            return False
    return True


def normalize(name):
    result = ''
    for c in unidecode.unidecode(name):
        if c.lower() in alphabet:
            result += c
    return result


def name_one_hot(name, max_seq_len):
    if not is_alpha(name):
        raise Exception('input name is not alphabet string!: ' + name)

    result = []
    for char in name.lower()[:max_seq_len]:
        v = np.zeros(26, dtype=np.int)
        try:
            v[alphabet.index(char)] = 1
            result.append(v)
        except ValueError:
            pass
    while len(result) < max_seq_len:
        result.append(np.zeros(26, dtype=np.int))
    return np.array(result)


def np_softmax(x):
    return np.exp(x) / np.sum(np.exp(x))


def get_file(path):
    return [_.strip() for _ in open(path, 'r').readlines()]


def dump_list(_list, path):
    with open(path, 'w') as f:
        for word in _list:
            f.write(word + '\n')


if __name__=='__main__':
    pass
