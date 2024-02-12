# coding=utf-8
import os
import csv
import shutil
import time
import json

import pandas as pd


def if_num_dot(str_):
    return all(map(lambda x: x.isdigit(), str_.split('.')))


def any_func(text, ele):
    return any(el in text for el in ele)


def write_csv(path, data, mode='a'):
    with open('{}.csv'.format(path), mode, newline='', encoding='utf-8') as f:
        tsv_w = csv.writer(f)
        tsv_w.writerow(data)


def write_into_json(path, data, mode='a'):
    with open('{}.json'.format(path), mode, encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False)
        json_file.write('\n')


def loads_json(path, mode='r'):
    json_file = open(f'{path}.json', mode, encoding='utf-8')
    json_ls = [json.loads(js) for js in json_file]
    json_file.close()
    return json_ls


def load_json(filename, mode='r'):
    with open('{}.json'.format(filename), mode, encoding='utf-8') as json_file:
        return json.loads(json_file.read())
