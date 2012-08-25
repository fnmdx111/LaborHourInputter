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
        id_name_dict = misc.invert_dict(dict(self.get_id_name_pairs(0)))

        _sheet = self.workbook.sheet_by_index(config.attendance_sheet_index)
        d = {}

        _ = lambda x: int(x) if not isinstance(x, basestring) else 0
        for name, attendance, attended in zip(_sheet.col_values(2),
                                              _sheet.col_values(3),
                                              _sheet.col_values(9)):
            if isinstance(name, basestring):
                if name in id_name_dict:
                    d[id_name_dict[name]] = _(attendance), _(attended)

        return misc.sort_dict_keys_numerically(d)


    def get_work_performance(self, sheet_index):
        # TODO all perf scores must be put in one sheet
        _sheet = self.workbook.sheet_by_index(sheet_index)
        d = {}
        _ = lambda x: int(x) if isinstance(x, basestring) and x.isdigit() else 0
        for id, performance in zip(_sheet.col_values(0),
                                   _sheet.col_values(11)):
            if isinstance(id, basestring) and id.isdigit():
                d[unicode(int(id))] = int(performance) if performance else 0

        return misc.sort_dict_keys_numerically(d)


    def get_id_name_pairs_with_row_number(self, sheet_index):
        _sheet = self.workbook.sheet_by_index(sheet_index)
        return misc.sort_dict_keys_numerically(
            {id: (name, row + 1) for row, (id, name) in enumerate(zip(_sheet.col_values(0),
                                                                  _sheet.col_values(1)))
             if id.isdigit() and name})



if __name__ == '__main__':
    def _(s):
        return s.encode('utf-8')

    xls_oprt = ExcelOperator(config.XLS_PATH)
    for key, item in xls_oprt.get_id_name_pairs(1):
        print _(key), _(item)

    for key, item in xls_oprt.get_attended_days_count_pairs():
        print _(key), item

    for key, (item, row) in xls_oprt.get_id_name_pairs_with_row_number(1):
        print _(key), _(item), row

