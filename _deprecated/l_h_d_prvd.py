# encoding: utf-8
from _deprecated.d_r_d_prvd import DateRelatedDataProvider
from libs import misc, config
from _deprecated.view_writer import ViewWriter
from libs.xls_oprt import ExcelOperator


class LaborHourDataProvider(DateRelatedDataProvider, object):

    table_headers_1 = '''<th colspan="%s">日期</th>
    <th rowspan="2" class="day">月合计</th>'''
    title_suffix = '实作工时明细'

    def __init__(self, table_title, worker_dict):
        each_day, each_row = self.define_funcs()
        super(LaborHourDataProvider, self).__init__(table_title + LaborHourDataProvider.title_suffix,
                                                    worker_dict,
                                                    sums_colspan=1,
                                                    table_headers_1=LaborHourDataProvider.table_headers_1,
                                                    each_day_f=each_day,
                                                    each_row_f=each_row)


    def define_funcs(self):
        day_cont = super(LaborHourDataProvider, self).day_cont
        make_nullable = lambda value: value if value else '&nbsp;'

        def each_day_f(day_sum, _, __):
            yield day_cont % make_nullable(day_sum)

        def each_row_f(labor_hour_sum, _):
            yield day_cont % make_nullable(labor_hour_sum)

        return each_day_f, each_row_f



if __name__ == '__main__':
    config.db_path = '..\\this_month.db'
    for title, index in config.title_index_pairs:
        worker_dict = ExcelOperator('..\\data.xls').get_id_name_pairs(index)

        for num, d in enumerate(misc.take(worker_dict, by=43)):
            view = ViewWriter(LaborHourDataProvider(title, dict(d)))

            with open('%s%s.html' % (num, (title + LaborHourDataProvider.title_suffix).decode('utf-8')),
                      'w') as f:
                print >> f, view


