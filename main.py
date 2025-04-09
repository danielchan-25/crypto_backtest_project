# -*- coding: utf-8 -*-
from data.spider_data import get_klines


if __name__ == '__main__':
    while True:
        df = get_klines(k_type="30m")
