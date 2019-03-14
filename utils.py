# -*- coding: utf-8 -*-

import numpy as np
import unidecode
import sys
import os

alphabet = 'abcdefghijklmnopqrstuvwxyz'


def is_alpha(name):
    for c in name:
        if c.lower() not in alphabet:
            return False
    return True


def smooth(name):
    al = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz -."
    res = ""
    for c in unidecode.unidecode(name):
        if c in al:
            res += c
    return res.strip()


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


def scale(x):
    if x < 1/3:
        return x * 1.5
    else:
        return 0.75*x + 0.25


def dict_update1(dict1, dict2, dict3):
    for key, value in dict3.items():
        if key in dict1:
            dict1[key] += value[1:]
        else:
            dict1[key] = value[1:]
            dict2[key] = int(value[0] * 100)


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


def restart_program():
    """
    Restarts the current program.
    Note: this function does not return.
    Any cleanup action (like saving data) must
    be done before calling this function.
    """
    python = sys.executable
    os.execl(python, python, * sys.argv)


if __name__=='__main__':
    print(smooth('Rémi Leblond'))
    pass
