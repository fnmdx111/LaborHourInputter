# encoding: utf-8

import config
import xlrd
import misc


class ExcelOperator(object):
    """Object that does all the operation with excel
    """

    def __init__(self, xls_path):
        self.workbook = xlrd.open_workbook(xls_path)


    def get_id_name_pairs(self, sheet_index):
        _sheet = self.workbook.sheet_by_index(sheet_index)
        return misc.sort_dict_keys_numerically(
            {id: name for id, name in zip(_sheet.col_values(0),
                                          _sheet.col_values(1))
             if id.isdigit() and name})


    def get_attended_days_count_pairs(self):
        _sheet = self.workbook.sheet_by_index(12)
        d = {}
        _ = lambda x: int(x) if not isinstance(x, basestring) else 0
        for id, attendance, attended in zip(_sheet.col_values(0),
                                            _sheet.col_values(3),
                                            _sheet.col_values(9)):
            if not isinstance(id, basestring):
                d[unicode(int(id))] = _(attendance), _(attended)

        return misc.sort_dict_keys_numerically(d)




if __name__ == '__main__':
    def _(s):
        return s.encode('utf-8')

    xls_oprt = ExcelOperator(config.XLS_PATH)
    for key, item in xls_oprt.get_id_name_pairs(1).iteritems():
        print _(key), _(item)

    for key, item in xls_oprt.get_attended_days_count_pairs().iteritems():
        print _(key), item


