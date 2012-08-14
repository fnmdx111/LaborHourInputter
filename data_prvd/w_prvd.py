# encoding: utf-8
import config
from data_prvd.d_r_d_prvd import DateRelatedDataProvider
import misc
from view_writer import ViewWriter
from xls_oprt import ExcelOperator


class WasteDataProvider(DateRelatedDataProvider, object):

    table_headers_1 = '''<th colspan="%s">日期</th>
    <th rowspan="2" class="day">月合计</th>
    <th rowspan="2" class="day">实作工时</th>
    <th rowspan="2" class="day">废品率</th>'''
    title_suffix = '员工废品明细'

    def __init__(self, table_title, worker_dict):
        each_day, each_row = self.define_funcs()

        super(WasteDataProvider, self).__init__(table_title + WasteDataProvider.title_suffix,
                                                worker_dict,
                                                sums_colspan=3,
                                                table_headers_1=WasteDataProvider.table_headers_1,
                                                each_day_f=each_day,
                                                each_row_f=each_row)


    def define_funcs(self):
        day_cont = super(WasteDataProvider, self).day_cont
        make_nullable = lambda value: value if value else '&nbsp;'

        def each_day_f(_, __, day_waste):
            yield day_cont % make_nullable(day_waste)

        def each_row_f(labor_hour_sum, waste_sum):
            yield day_cont % make_nullable(waste_sum)
            yield day_cont % make_nullable(labor_hour_sum)
            yield day_cont % (
                ('%s%%' % round((waste_sum / labor_hour_sum) * 100, 1))
                if labor_hour_sum else '&nbsp'
            )

        return each_day_f, each_row_f



if __name__ == '__main__':
    config.db_path = '..\\this_month.db'
    for title, index in config.title_index_pairs:
        worker_dict = ExcelOperator('..\\data.xls').get_id_name_pairs(index)

        for num, d in enumerate(misc.take(worker_dict, by=43)):
            view = ViewWriter(WasteDataProvider(title, dict(d)))

            with open('%s%s.html' % (num, (title + WasteDataProvider.title_suffix).decode('utf-8')),
                      'w') as f:
                print >> f, view


