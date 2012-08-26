# encoding: utf-8
from libs import misc, config
from libs.xls_oprt import ExcelOperator
from xlwriter.abstract_wrt import AbstractXLWriter


class LaborHourDataXLWriter(AbstractXLWriter, object):
    LH_OFFSET = 3
    WASTE_OFFSET = 3

    ASSIST_COL = 19

    INSERT_LH = 0x1
    INSERT_W = 0x2
    INSERT_A = 0x3

    def __init__(self, sheet_index, base_name, xl_out_path, app_echo=True, save_per_worker=False):
        super(LaborHourDataXLWriter, self).__init__(xl_out_path, app_echo, save_per_worker)
        self.base_name = base_name

        self.lh_sheet = self.xl_app.Sheets((base_name + config.lh_suffix).decode('utf-8').encode('gbk'))
        self.w_sheet = self.xl_app.Sheets((base_name + config.w_suffix).decode('utf-8').encode('gbk'))
        self.m_sheet = self.xl_app.Sheets(u'首页'.encode('gbk'))

        xl_operator = ExcelOperator(config.XLS_PATH)
        self.worker_dict_x = dict(xl_operator.get_id_name_pairs_with_row_number(sheet_index))
        self.main_worker_dict_x = dict(xl_operator.get_id_name_pairs_with_row_number(0))

        self.write_dates()


    def write_dates(self):
        for col_cnt, day in enumerate(self.db_operator.get_month_days_in_db()):
            self.lh_sheet.Cells(3, LaborHourDataXLWriter.LH_OFFSET + col_cnt).Value = day
            self.w_sheet.Cells(3, LaborHourDataXLWriter.WASTE_OFFSET + col_cnt).Value = day


    def write_data_per_worker(self,
                              worker_id,
                              worker_row,
                              modes=(INSERT_LH,
                                     INSERT_W,
                                     INSERT_A)):
        lh_offset = LaborHourDataXLWriter.LH_OFFSET # name is too long, need alias
        w_offset = LaborHourDataXLWriter.WASTE_OFFSET # name is too long, need alias

        cache = list(enumerate(self.db_operator.iterate_worker(worker_id)))

        _ = lambda offset: (worker_row, offset + col_cnt)
        if LaborHourDataXLWriter.INSERT_LH in modes:
            if self.app_echo:
                self._echo_sheet(self.lh_sheet, worker_row)
            for col_cnt, (day_sum, aux, __, __) in cache:
                s = day_sum + aux
                self.lh_sheet.Cells(*_(lh_offset)).Value = s if s else ''

        if LaborHourDataXLWriter.INSERT_W in modes:
            if self.app_echo:
                self._echo_sheet(self.w_sheet, worker_row)
            for col_cnt, (__, __, day_waste, __) in cache:
                self.w_sheet.Cells(*_(w_offset)).Value = int(day_waste) if day_waste else ''

        if LaborHourDataXLWriter.INSERT_A in modes:
            assist_sum = 0
            for __, (__, __, __, day_assist) in cache:
                assist_sum += day_assist
            if self.app_echo:
                self._echo_sheet(self.m_sheet, self.main_worker_dict_x[worker_id][1])
            self.m_sheet.Cells(self.main_worker_dict_x[worker_id][1],
                               LaborHourDataXLWriter.ASSIST_COL).Value = assist_sum if assist_sum else ''

        if self.save_per_worker:
            self.xl_app.ActiveWorkbook.Save()


    def write_all_data(self):
        for worker_id, (_, worker_row) in misc.sort_dict_keys_numerically(self.worker_dict_x):
            self.write_data_per_worker(worker_id, worker_row)

        super(LaborHourDataXLWriter, self).write_all_data()


