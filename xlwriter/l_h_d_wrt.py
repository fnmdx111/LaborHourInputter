# encoding: utf-8
from win32com.client import Dispatch
import config
import misc
from sqlite_writer import SQLiteOperator
from xls_oprt import ExcelOperator


class LaborHourDataXLWriter(object):
    LH_OFFSET = 3
    WASTE_OFFSET = 3

    ASSIST_COL = 19

    INSERT_LH = 0x1
    INSERT_W = 0x2

    def __init__(self, sheet_index, base_name, xl_out_path, app_echo=True, save_per_worker=False):
        self.base_name = base_name

        self.app_echo = app_echo

        self.xl_app = Dispatch('Excel.Application')
        self.xl_app.Visible = app_echo
        self.xl_app.Workbooks.Open(xl_out_path)

        self.lh_sheet = self.xl_app.Sheets((base_name + config.lh_suffix).decode('utf-8').encode('gbk'))
        self.w_sheet = self.xl_app.Sheets((base_name + config.w_suffix).decode('utf-8').encode('gbk'))
        self.m_sheet = self.xl_app.Sheets(u'首页'.encode('gbk'))

        xl_operator = ExcelOperator(config.XLS_PATH)
        self.worker_dict_x = dict(xl_operator.get_id_name_pairs_with_row_number(sheet_index))
        self.main_worker_dict_x = dict(xl_operator.get_id_name_pairs_with_row_number(0))
        self.db_operator = SQLiteOperator()

        self.save_per_worker = save_per_worker


    def write_data_per_worker(self,
                              worker_id,
                              worker_row,
                              modes=(INSERT_LH,
                                     INSERT_W)):
        lh_offset = LaborHourDataXLWriter.LH_OFFSET # name is too long, need alias
        w_offset = LaborHourDataXLWriter.WASTE_OFFSET # name is too long, need alias

        cache = list(enumerate(self.db_operator.iterate_worker(worker_id)))

        _ = lambda offset: (worker_row, offset + col_cnt)
        assist_sum = 0
        if self.app_echo:
            self.lh_sheet.Select()
            # self.lh_sheet.Cells(worker_row, 0).Select()
        for col_cnt, (day_sum, aux, __, __) in cache:
            if LaborHourDataXLWriter.INSERT_LH in modes:
                s = day_sum + aux
                self.lh_sheet.Cells(*_(lh_offset)).Value = s if s else ''

        if self.app_echo:
            self.w_sheet.Select()
            # self.w_sheet.Cells(worker_row, 0).Select()
        for col_cnt, (__, __, day_waste, day_assist) in cache:
            if LaborHourDataXLWriter.INSERT_W in modes:
                self.w_sheet.Select()
                self.w_sheet.Cells(*_(w_offset)).Value = int(day_waste) if day_waste else ''

            assist_sum += day_assist

        if self.app_echo:
            self.m_sheet.Select()
        self.m_sheet.Cells(self.main_worker_dict_x[worker_id][1],
                           LaborHourDataXLWriter.ASSIST_COL).Value = assist_sum if assist_sum else ''

        if self.save_per_worker:
            self.xl_app.ActiveWorkbook.Save()


    def write_all_data(self):
        for worker_id, (worker_name, worker_row) in misc.sort_dict_keys_numerically(self.worker_dict_x):
            self.write_data_per_worker(worker_id, worker_row)

        if not self.save_per_worker:
            self.xl_app.ActiveWorkbook.Save()



