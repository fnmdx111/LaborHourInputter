# encoding: utf-8
import os
from libs import config
from xlwriter.l_h_d_wrt import LaborHourDataXLWriter


if __name__ == '__main__':
    for base_name, index in config.short_title_index_pairs:
        writer = LaborHourDataXLWriter(index, base_name, os.path.abspath('data_copy.xls'))
        writer.write_all_data()