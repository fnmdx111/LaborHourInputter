# encoding: utf-8
import misc
from sqlite_writer import SQLiteOperator
from view_writer import ViewWriter

TITLE_INDEX_PAIRS = (
    ('分厂员工废品明细', 6),
)

class WasteDataProvider(object):

    table_headers = '''<th rowspan="2" class="num">序号</th>
        <th rowspan="2" class="name">姓名</th>
        <th colspan="{date_colspan}" class="day">日期</th>
        <th rowspan="2" class="month">月合计</th>
        <th rowspan="2" class="month">实作工时</th>
        <th rowspan="2" class="month">废品率</th>
    '''.format(**{'date_colspan': misc.get_month_day_num()})

    def __init__(self, title, worker_dict):
        self.table_title = title
        self.worker_dict = worker_dict
        self.table_headers = WasteDataProvider.table_headers
        self.db_operator = SQLiteOperator()
        self.misc_colspan = 3
        self.month_days = misc.get_month_days()


    def _get_labor_hour_day_sum(self, result):
        day_sum = 0
        for lh_key, ra_key in misc.take(SQLiteOperator._db_keys[:18],
                                        by=2):
            labor_hour, real_amount = map(result.__getitem__,
                (lh_key, ra_key))

            if labor_hour and real_amount:
                labor_hour, real_amount = map(float,
                    (labor_hour, real_amount))
                day_sum += (real_amount / labor_hour)
        day_sum *= 8
        return round(day_sum, 1)


    def _get_waste_day_sum(self, result):
        def _(key):
            value = result[key]
            return value if value else 0
        return sum(map(_, SQLiteOperator._db_keys[18:21]))


    def data_extractor(self, worker_id, day):
        result = self.db_operator.retrieve(worker_id, unicode(day))
        if result:
            day_labor_hour_sum = self._get_labor_hour_day_sum(result)
            day_waste_sum = self._get_waste_day_sum(result)

            return day_labor_hour_sum, day_waste_sum

        return 0.0, 0.0


    def gen_worker_rows(self):
        for id, name in misc.sort_worker_dict(self.worker_dict):
            days_content, labor_hour_sum, waste_sum = [], 0.0, 0
            for day in self.month_days:
                lb_sum, day_waste = self.data_extractor(id, day)
                labor_hour_sum += lb_sum
                waste_sum += day_waste
                days_content.append(ViewWriter.day_cont % waste_sum)
            days_content.append(ViewWriter.day_cont % waste_sum)
            days_content.append(ViewWriter.day_cont % labor_hour_sum)
            days_content.append(ViewWriter.day_cont % (
                ('%s%%' % round((waste_sum / labor_hour_sum) * 100, 1)) if (
                    labor_hour_sum
                ) else '&nbsp;'
            ))

            _ = {
                'id': id.encode('utf-8'),
                'name': name.encode('utf-8'),
                'days_content': '\n'.join(days_content)
            }

            yield ViewWriter.each_row.format(**_)



