# encoding: utf-8
import config
from data_prvd.abstract_prvd import AbstractDataProvider
import misc
from view_writer import ViewWriter
from xls_oprt import ExcelOperator


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

    def __init__(self, labor_hour, waste, attended, attendance):
        self.labor_hour = labor_hour
        self.waste = waste
        self.attended = attended
        self.attendance = attendance

        self.score_waste = 100
        self.score_six_s = 0

        self.perf_labor_hour = 0
        self.perf_waste = 0
        self.perf_attendance = 0
        self.perf_six_s = 0

        self.process()


    def process(self):
        pairs = ((self.score_waste, WorkerData.WASTE_WEIGHT, 'perf_waste'),
                 (self.score_attendance, WorkerData.ATTENDANCE_WEIGHT, 'perf_attendance'),
                 (self.score_labor_hour, WorkerData.LABOR_HOUR_WEIGHT, 'perf_labor_hour'),
                 (self.score_six_s, WorkerData.SIX_S_WEIGHT, 'perf_six_s'))

        self.ratio_waste = round((self.waste / self.labor_hour) if self.labor_hour else 1., 2)

        self.ratio_attendance = round((self.attended / self.attendance) if self.attendance else 0., 2)
        self.score_attendance = self.ratio_attendance * 100

        labor_hour = min(600., self.labor_hour)
        self.score_labor_hour = 100 - (600 - labor_hour) * .1

        for score, weight, attr in pairs:
            self.__setattr__(attr, round(score * weight, 2))


    def get_performances(self):
        self.process()

        return (self.labor_hour, self.score_labor_hour, self.perf_labor_hour,
                self.ratio_attendance, self.score_attendance, self.perf_attendance,
                self.ratio_waste, self.score_waste, self.perf_waste,
                self.score_six_s, self.perf_six_s)


    @staticmethod
    def compare_waste(worker1, worker2):
        return cmp(worker1.ratio_waste, worker2.ratio_waste)



class PerformanceDataProvider(AbstractDataProvider, object):
    table_headers_1 = '\n'.join(map('<th colspan="3">%s</th>'.__mod__,
                                    ('工时绩效（60分）',
                                     '考勤绩效（10分）',
                                     '废品率绩效（15分）'))) +\
                      '''<th colspan="2">工作+6S绩效（15分）</th>
                      <th>绩效分</th>
                      <th>绩效等级</th>'''
    table_headers_2 = '\n'.join(map('''<th>%s</th>
    <th>得分</th>
    <th>加权分</th>'''.__mod__, ('实作工时', '出勤率', '废品率'))) +\
    '''<th>得分</th>
    <th>加权分</th>'''

    def __init__(self, table_title, worker_dict, worker_attendance_dict):
        super(PerformanceDataProvider, self).__init__(table_title, worker_dict)

        self.title_colspan = 15

        self.table_headers = AbstractDataProvider.table_headers.format(
            details_1=PerformanceDataProvider.table_headers_1,
            details_2=PerformanceDataProvider.table_headers_2
        )

        self.attendance_dict = worker_attendance_dict
        self.worker_data = {}


    def gen_worker_rows(self):
        def _gen_row(id, name, _cont):
            return AbstractDataProvider.each_row.format(
                id=id.encode('utf-8'),
                name=name.encode('utf-8'),
                details='\n'.join(_cont)
            )

        for worker_id, name in misc.sort_dict_keys_numerically(self.worker_dict): # 第一轮for，收集数据，以便计算废品绩效
            lh_sum, waste_sum = 0, 0
            for labor_hour, labor_hour_aux, waste in self.db_operator.iterate_worker(worker_id):
                lh_sum += labor_hour + labor_hour_aux
                waste_sum += waste

            self.worker_data[worker_id] = WorkerData(lh_sum, waste_sum,
                                                     self.attendance_dict[worker_id][1],
                                                     self.attendance_dict[worker_id][0]), name

        lowest_ratio = min(map(lambda (item, _): item.ratio_waste, self.worker_data.values()))
        for worker_data in map(lambda (item, _): item, self.worker_data.values()):
            worker_data.score_waste = max(0, (worker_data.ratio_waste - lowest_ratio) * 100)

        for worker_id, (worker_data, name) in self.worker_data.iteritems():
            # TODO write to html
            pass





if __name__ == '__main__':
    for title, index in TITLE_INDEX_PAIRS:
        worker_dict = misc.sort_dict_keys_numerically(
            ExcelOperator(config.XLS_PATH).\
                get_id_name_pairs(index)
        )

        for num, d in enumerate(misc.take(worker_dict, by=43)):
            view = ViewWriter(PerformanceDataProvider(title, dict(d)))

            with open('%s%s.html' % (num, title.decode('utf-8')), 'w') as f:
                print >> f, view


