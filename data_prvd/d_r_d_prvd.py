from abc import ABCMeta
from data_prvd.abstract_prvd import AbstractDataProvider

class DateRelatedDataProvider(AbstractDataProvider, object):
    __metaclass__ = ABCMeta

    def __init__(self,
                 table_title,
                 worker_dict,
                 sums_colspan,
                 table_headers_1,
                 each_day_f, each_row_f):
        super(DateRelatedDataProvider, self).__init__(table_title, worker_dict)

        self.each_day_f = each_day_f
        self.each_row_f = each_row_f

        month_days = self.db_operator.get_month_days_in_db()
        self.date_colspan = len(month_days)
        self.sums_colspan = sums_colspan
        self.title_colspan = 2 + self.date_colspan + self.sums_colspan

        self.table_headers = super(DateRelatedDataProvider, self).table_headers.format(
            details_1=table_headers_1 % self.date_colspan,
            details_2='\n'.join(map('<th>%s</th>'.__mod__, month_days))
        )


    def gen_worker_rows(self):
        for id, name in self.worker_dict.iteritems():
            days_contents, labor_hour_sum, waste_sum = [], .0, 0
            for day_sum, aux, day_waste in self.db_operator.iterate_worker(id):
                labor_hour_sum += day_sum + aux
                waste_sum += day_waste
                for item in self.each_day_f(day_sum, aux, day_waste):
                    days_contents.append(item)
            for item in self.each_row_f(labor_hour_sum, waste_sum):
                days_contents.append(item)

            yield super(DateRelatedDataProvider, self).each_row.format(
                id=id.encode('utf-8'),
                name=name.encode('utf-8'),
                details='\n'.join(days_contents)
            )


    def gen_table_cont(self):
        return super(DateRelatedDataProvider, self).table_cont.format(
            date_colspan=self.date_colspan,
            sums_colspan=self.sums_colspan,
            title_colspan=self.title_colspan,
            table_title=self.table_title,
            table_headers=self.table_headers,
            table_rows_contents='\n'.join(self.gen_worker_rows())
        )


    def __str__(self):
        return self.gen_table_cont()


