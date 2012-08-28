# encoding: utf-8
from data_prvd.abstract_prvd import AbstractDataProvider
from libs import misc, config
from _deprecated.view_writer import ViewWriter
from libs.xls_oprt import ExcelOperator


TITLE_INDEX_PAIRS = (
    ('单多轴车间员工绩效', 1),
    ('零件车间员工绩效', 2),
    ('装配车间员工绩效', 3),
    ('备料组员工绩效', 4),
    ('清包车间员工绩效', 5)
)


class WorkerData(object):

    ATTENDANCE_WEIGHT = .1
    LABOR_HOUR_WEIGHT = .6
    WASTE_WEIGHT = .15
    SIX_S_WEIGHT = .15

    def __init__(self, labor_hour, waste, attended, attendance, six_s):
        self.labor_hour = labor_hour
        self.waste = waste
        self.attended = float(attended)
        self.attendance = float(attendance)

        self.score_waste = 100
        self.score_six_s = six_s

        self.perf_labor_hour = 0
        self.perf_waste = 0
        self.perf_attendance = 0
        self.perf_six_s = 0

        self.perf_grade = 'D'

        self.process()


    def process(self):
        self.ratio_waste = round((self.waste / self.labor_hour) if self.labor_hour else 1., 2)

        self.ratio_attendance = round((self.attended / self.attendance) if self.attendance else 0., 3)
        self.score_attendance = self.ratio_attendance * 100

        labor_hour = min(600., self.labor_hour)
        self.score_labor_hour = 100 - (600 - labor_hour) * .1

        pairs = ((self.score_waste, WorkerData.WASTE_WEIGHT, 'perf_waste'),
                 (self.score_attendance, WorkerData.ATTENDANCE_WEIGHT, 'perf_attendance'),
                 (self.score_labor_hour, WorkerData.LABOR_HOUR_WEIGHT, 'perf_labor_hour'),
                 (self.score_six_s, WorkerData.SIX_S_WEIGHT, 'perf_six_s'))

        for score, weight, attr in pairs:
            self.__setattr__(attr, round(score * weight, 2))

        self.perf_sum = round(sum(map(lambda (_, __, attr): self.__getattribute__(attr), pairs)), 1)


    def get_performances(self):
        self.process()

        make_percentage = lambda p: ('%s%%' % (p * 100)) if p else ''
        self.ratio_attendance = make_percentage(self.ratio_attendance)
        self.ratio_waste = make_percentage(self.ratio_waste)

        self.perf_sum = round(self.perf_sum, 1)

        return (self.labor_hour, self.score_labor_hour, self.perf_labor_hour,
                self.ratio_attendance, self.score_attendance, self.perf_attendance,
                self.ratio_waste, self.score_waste, self.perf_waste,
                self.score_six_s, self.perf_six_s,
                self.perf_sum, self.perf_grade)


    @staticmethod
    def compare_waste(worker1, worker2):
        return cmp(worker1.ratio_waste, worker2.ratio_waste)



class PerformanceDataProvider(AbstractDataProvider, object):
    table_headers_1 = '\n'.join(map('<th colspan="3">%s</th>'.__mod__,
                                    ('工时绩效（60分）',
                                     '考勤绩效（10分）',
                                     '废品率绩效（15分）'))) +\
                      '''<th colspan="2">综合绩效（15分）</th>
                      <th rowspan="2">绩效分</th>
                      <th rowspan="2">绩效等级</th>'''
    table_headers_2 = '\n'.join(map('''<th>%s</th>
    <th>得分</th>
    <th>加权分</th>'''.__mod__, ('实作工时', '出勤率', '废品率'))) +\
    '''<th>得分</th>
    <th>加权分</th>'''

    def __init__(self, table_title, worker_dict, worker_dict_show, attendance_dict, performance_dict):
        super(PerformanceDataProvider, self).__init__(table_title, worker_dict)

        self.worker_dict_show = worker_dict_show
        self.title_colspan = 15

        self.table_headers = AbstractDataProvider.table_headers.format(
            details_1=PerformanceDataProvider.table_headers_1,
            details_2=PerformanceDataProvider.table_headers_2
        )

        self.attendance_dict = attendance_dict
        self.performance_dict = performance_dict
        self.worker_data = {}


    def _gen_grade(self):
        _data = map(lambda (d, _): d.perf_sum, self.worker_data.values())
        _data = sorted(list(set(filter(lambda perf_sum: perf_sum != 0, _data))), reverse=True)

        def _g(score):
            score_cnt = len(_data)
            if score >= _data[int(score_cnt * .3) - 1]:
                return 'A'
            elif score >= _data[int(score_cnt * .7) - 1]:
                return 'B'
            else:
                return 'C'

        for worker_data, _ in self.worker_data.values():
            worker_data.process()
            worker_data.perf_grade = _g(worker_data.perf_sum)


    def gen_worker_data(self):
        for worker_id, name in misc.sort_dict_keys_numerically(self.worker_dict): # 第一轮for，收集数据，以便计算废品绩效
            lh_sum, waste_sum = 0, 0 # 各种求和
            for labor_hour, labor_hour_aux, waste, _ in self.db_operator.iterate_worker(worker_id):
                lh_sum += labor_hour + labor_hour_aux
                waste_sum += waste

            if worker_id not in self.attendance_dict:
                if config.SKIP_NOT_FOUND_ATTENDANCE:
                    continue
                else:
                    attendance = 0
                    attended = 0
            else:
                attendance = self.attendance_dict[worker_id][0]
                attended = self.attendance_dict[worker_id][1]
            self.worker_data[worker_id] = WorkerData(lh_sum, waste_sum,
                                                     attended,
                                                     attendance,
                                                     self.performance_dict[worker_id]), name

        # 计算废品分
        lowest_ratio = min(map(lambda (item, _): item.ratio_waste, self.worker_data.values()))
        for worker_data in map(lambda (item, _): item, self.worker_data.values()):
            worker_data.score_waste = max(0,
                                          worker_data.score_waste - (worker_data.ratio_waste - lowest_ratio) * 100)
            worker_data.process()

        self._gen_grade()

        return misc.sort_dict_keys_numerically(self.worker_data)


    def yield_worker_data(self):
        for worker_id, (worker_data, name) in self.gen_worker_data():
            if worker_id not in self.worker_dict_show:
                continue
            yield worker_id, worker_data.get_performances()


    def gen_worker_rows(self):
        self.gen_worker_data()

        def _gen_row(id, name, _cont):
            return AbstractDataProvider.each_row.format(
                id=id.encode('utf-8'),
                name=name.encode('utf-8'),
                details='\n'.join(_cont)
            )

        make_nullable = lambda x: x if x else '&nbsp;'
        for worker_id, (worker_data, name) in misc.sort_dict_keys_numerically(self.worker_data):
            if worker_id not in self.worker_dict_show:
                continue
            _cont = []
            for item in worker_data.get_performances():
                _cont.append(super(PerformanceDataProvider, self).day_cont % make_nullable(item))
            yield _gen_row(worker_id, name, _cont)


    def gen_table_cont(self):
        return super(PerformanceDataProvider, self).table_cont.format(
            date_colspan=11,
            sums_colspan=2,
            title_colspan=15,
            table_title=self.table_title,
            table_headers=self.table_headers,
            table_rows_contents='\n'.join(self.gen_worker_rows())
        )



if __name__ == '__main__':
    config.db_path = '..\\this_month.db'
    for title, index in TITLE_INDEX_PAIRS:
        xls_obj = ExcelOperator('..\\data.xls')
        worker_dict = xls_obj.get_id_name_pairs(index)

        for num, d in enumerate(misc.take(worker_dict, by=43)):
            view = ViewWriter(PerformanceDataProvider(title,
                                                      dict(worker_dict),
                                                      dict(worker_dict),
                                                      dict(xls_obj.get_attended_days_count_pairs()),
                                                      dict(xls_obj.get_work_performance(config.p_index_offset + index))))

            with open('%s%s.html' % (num, title.decode('utf-8')), 'w') as f:
                print >> f, view


