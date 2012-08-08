# encoding: utf-8

import config
import xlrd


class ExcelOperator(object):
    """Object that does all the operation with excel
    """

    def __init__(self, xls_path):
        self.workbook = xlrd.open_workbook(xls_path)


    def get_id_name_pairs(self, sheet_index):
        _sheet = self.workbook.sheet_by_index(sheet_index)
        return {id: name for id, name in zip(_sheet.col_values(0),
                                             _sheet.col_values(1))
                if id.isdigit() and name}



if __name__ == '__main__':
    def _(s):
        return s.encode('utf-8')

    xls_oprt = ExcelOperator(config.XLS_PATH)
    for key, item in xls_oprt.get_id_name_pairs(1).iteritems():
        print _(key), _(item)


