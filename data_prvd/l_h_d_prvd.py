# encoding: utf-8
import config
from data_prvd.abstract_prvd import AbstractDataProvider
import misc
from view_writer import ViewWriter
from xls_oprt import ExcelOperator


TITLE_INDEX_PAIRS = (
    ('单多轴车间实作工时明细', 1),
    ('零件车间实作工时明细', 2),
    ('装配车间实作工时明细', 3),
    ('备料组实作工时明细', 4),
    ('清包车间实作工时明细', 5)
)


class LaborHourDataProvider(AbstractDataProvider, object):

    table_headers_1 = '''<th colspan="%s">日期</th>
    <th rowspan="2" class="day">月合计</th>'''

    def __init__(self, table_title, worker_dict):
        super(LaborHourDataProvider, self).__init__(table_title, worker_dict)

        month_days = self.db_operator.get_month_days_in_db()
        self.date_colspan = len(month_days)
        self.sums_colspan = 1
        self.title_colspan = 2 + self.date_colspan + self.sums_colspan

        self.table_headers = AbstractDataProvider.table_headers.format(
            details_1=LaborHourDataProvider.table_headers_1 % self.date_colspan,
            details_2='\n'.join(map('<th>%s</th>'.__mod__, month_days))
        )


    def gen_worker_rows(self):
        for id, name in self.worker_dict:
            days_contents, sum = [], 0
            for _, day_sum, aux, _ in self.db_operator.iterate_worker(id):
                sum += day_sum + aux
                days_contents.append(AbstractDataProvider.day_cont % (day_sum if day_sum else '&nbsp;'))
            days_contents.append(AbstractDataProvider.day_cont % (sum if sum else '&nbsp;'))

            yield AbstractDataProvider.each_row.format(
                id=id.encode('utf-8'),
                name=name.encode('utf-8'),
                details='\n'.join(days_contents)
            )


    def gen_table_cont(self):
        return AbstractDataProvider.table_cont.format(
            date_colspan=self.date_colspan,
            sums_colspan=self.sums_colspan,
            title_colspan=self.title_colspan,
            table_title=self.table_title,
            table_headers=self.table_headers,
            table_rows_contents='\n'.join(self.gen_worker_rows())
        )


    def __str__(self):
        return self.gen_table_cont()



if __name__ == '__main__':
    config.db_path = '..\\this_month.db'
    for title, index in TITLE_INDEX_PAIRS:
        worker_dict = ExcelOperator('..\\data.xls').get_id_name_pairs(index)

        for num, d in enumerate(misc.take(worker_dict, by=43)):
            view = ViewWriter(LaborHourDataProvider(title, dict(d)))

            with open('%s%s.html' % (num, title.decode('utf-8')), 'w') as f:
                print >> f, view


