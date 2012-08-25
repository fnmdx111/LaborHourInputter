# encoding: utf-8
from win32com.client import Dispatch
import config
from sqlite_writer import SQLiteOperator
from xls_oprt import ExcelOperator


class LaborHourDataXLWriter(object):
    LH_OFFSET = 3
    WASTE_OFFSET = 3

    INSERT_LH = 0x1
    INSERT_W = 0x2

    def __init__(self, sheet_index, base_name, xl_out_path, app_visible=True):
        self.base_name = base_name

        self.xl_app = Dispatch('Excel.Application')
        self.xl_app.Visible = app_visible
        self.xl_app.Workbooks.Open(xl_out_path)

        self.lh_sheet = self.xl_app.Sheets((base_name + config.lh_suffix).decode('utf-8').encode('gbk'))
        self.w_sheet = self.xl_app.Sheets((base_name + config.w_suffix).decode('utf-8').encode('gbk'))

        self.worker_dict_x = dict(ExcelOperator(config.XLS_PATH).get_id_name_pairs_with_row_number(sheet_index))
        self.db_operator = SQLiteOperator()


    def write_data_per_worker(self,
                              worker_id,
                              worker_row,
                              modes=(INSERT_LH,
                                     INSERT_W)):
        lh_offset = LaborHourDataXLWriter.LH_OFFSET # name is too long, need alias
        w_offset = LaborHourDataXLWriter.WASTE_OFFSET # name is too long, need alias
        for col_cnt, (day_sum, aux, day_waste) in enumerate(self.db_operator.iterate_worker(worker_id)):
            _ = lambda offset: (worker_row, offset + col_cnt)
            if LaborHourDataXLWriter.INSERT_LH in modes:
                s = day_sum + aux
                self.lh_sheet.Cells(*_(lh_offset)).Value = s if s else ''
            if LaborHourDataXLWriter.INSERT_W in modes:
                self.w_sheet.Cells(*_(w_offset)).Value = int(day_waste) if day_waste else ''

        # self.xl_app.ActiveWorkbook.Save()


    def write_all_data(self):
        for worker_id, (worker_name, worker_row) in self.worker_dict_x.iteritems():
            self.write_data_per_worker(worker_id, worker_row)
        self.xl_app.ActiveWorkbook.Save()



