# encoding: utf-8
from data_prvd.p_d_prvd import PerformanceDataProvider
from libs import config, misc
from libs.xls_oprt import ExcelOperator
from xlwriter.abstract_wrt import AbstractXLWriter

class PerformanceXLWriter(AbstractXLWriter, object):

    P_OFFSET = 3

    def __init__(self, sheet_index, base_name, xl_out_path, app_echo=True, save_per_worker=False):
        super(PerformanceXLWriter, self).__init__(xl_out_path, app_echo, save_per_worker)

        self.perf_sheet = self.xl_app.Sheets((base_name + config.p_suffix).decode('utf-8').encode('gbk'))

        xl_operator = ExcelOperator(config.XLS_PATH)
        self.worker_dict_x = dict(xl_operator.get_id_name_pairs_with_row_number(sheet_index))
        self.main_worker_dict_x = dict(xl_operator.get_id_name_pairs_with_row_number(0))

        worker_dict = xl_operator.get_id_name_pairs(sheet_index)
        self.perf_data_provider = PerformanceDataProvider('',
                                                          dict(worker_dict),dict(worker_dict),
                                                          dict(xl_operator.get_attended_days_count_pairs()),
                                                          dict(xl_operator.get_work_performance(
                                                              config.p_index_offset + sheet_index
                                                          )))


    def write_data_per_worker(self, worker_row, data):
        p_offset = PerformanceXLWriter.P_OFFSET
        percentage_columns = [3, 6]

        self._echo_sheet(self.perf_sheet, worker_row)

        _ = lambda offset: (worker_row, offset + col_cnt)
        for col_cnt, col_data in enumerate(data.get_performances()):
            # self._echo_sheet(self.perf_sheet, worker_row, select_sheet=False)
            if col_cnt in percentage_columns:
                self.perf_sheet.Cells(*_(p_offset)).Style = 'Percent'
            self.perf_sheet.Cells(*_(p_offset)).Value = col_data if col_data and not col_data == '&nbsp;' else ''


    def write_all_data(self):
        worker_data = dict(self.perf_data_provider.gen_worker_data())
        for worker_id, (_, worker_row) in misc.sort_dict_keys_numerically(self.worker_dict_x):
            self.write_data_per_worker(worker_row, worker_data[worker_id][0])

        super(PerformanceXLWriter, self).write_all_data()


