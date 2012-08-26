# encoding: utf-8
from abc import ABCMeta, abstractmethod
from win32com.client import Dispatch
from libs.sqlite_writer import SQLiteOperator

class AbstractXLWriter(object):
    __metaclass__ = ABCMeta

    def __init__(self, xl_out_path, app_echo, save_per_worker):
        self.app_echo = app_echo

        self.xl_app = Dispatch('Excel.Application')
        self.xl_app.Visible = self.app_echo
        self.xl_app.Workbooks.Open(xl_out_path)

        self.db_operator = SQLiteOperator()

        self.save_per_worker = save_per_worker


    def _echo_sheet(self, sheet, worker_row, select_sheet=True):
        if select_sheet:
            sheet.Select()
        sheet.Range('A%s' % worker_row).Select()


    @abstractmethod
    def write_all_data(self):
        if not self.save_per_worker:
            self.xl_app.ActiveWorkbook.Save()


