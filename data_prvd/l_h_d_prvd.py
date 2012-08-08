# encoding: utf-8
import config
import misc
from sqlite_writer import SQLiteOperator
from view_writer import ViewWriter
from xls_oprt import ExcelOperator


TITLE_INDEX_PAIRS = (
    ('单多轴车间实作工时明细', 1),
    ('零件车间实作工时明细', 2),
    ('装配车间实作工时明细', 3),
    ('备料组实作工时明细', 4),
    ('清包车间实作工时明细', 5)
)



class LaborHourDataProvider(object):

    table_headers = '''<th rowspan="2" class="num">序号</th>
        <th rowspan="2" class="name">姓名</th>
        <th colspan="{date_colspan}" class="day">日期</th>
        <th rowspan="2" class="month">月合计</th>
    '''.format(**{'date_colspan': misc.get_month_day_num()})

    def __init__(self, table_title, worker_dict):
        self.table_title = table_title
        self.worker_dict = worker_dict
        self.table_headers = LaborHourDataProvider.table_headers
        self.db_operator = SQLiteOperator()
        self.misc_colspan = 1
        self.month_days = misc.get_month_days()


    def data_extractor(self, worker_id, day):
        result = self.db_operator.retrieve(worker_id, unicode(day))
        if result:
            sum = 0
            for lh_key, ra_key in misc.take(SQLiteOperator._db_keys[:18],
                by=2):
                labor_hour, real_amount = map(result.__getitem__,
                    (lh_key, ra_key))

                if labor_hour and real_amount:
                    labor_hour, real_amount = map(float,
                        (labor_hour, real_amount))
                    sum += (real_amount / labor_hour)
            sum *= 8
            sum = round(sum, 1)

            return sum, result['labor_hour_aux_to']

        return 0.0, 0


    def gen_worker_rows(self):
        for id, name in misc.sort_worker_dict(self.worker_dict):
            days_content, sum = [], 0
            for day in self.month_days:
                day_sum, aux = self.data_extractor(id, day)
                day_sum += aux if aux else 0
                sum += day_sum
                days_content.append(ViewWriter.day_cont % (day_sum if day_sum else ''))
            days_content.append(ViewWriter.day_cont % (sum if sum else ''))

            _ = {
                'id': id.encode('utf-8'),
                'name': name.encode('utf-8'),
                'days_content': '\n'.join(days_content)
            }

            yield ViewWriter.each_row.format(**_)



if __name__ == '__main__':
    for title, index in TITLE_INDEX_PAIRS:
        worker_dict = misc.sort_worker_dict(
            ExcelOperator(config.XLS_PATH).\
                get_id_name_pairs(index)
        )

        for num, d in enumerate(misc.take(worker_dict, by=43)):
            view = ViewWriter(LaborHourDataProvider(title, dict(d)))

            with open('%s%s.html' % (num, title.decode('utf-8')), 'w') as f:
                print >> f, view


