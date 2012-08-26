# encoding: utf-8
from abc import ABCMeta, abstractmethod
from libs.sqlite_writer import SQLiteOperator

class AbstractDataProvider(object):
    __metaclass__ = ABCMeta

    table_headers = '''<tr>
    <th rowspan="2" class="num">序号</th>
    <th rowspan="2" class="name">姓名</th>
    {details_1}
    </tr>
    <tr>
    {details_2}
    </tr>'''

    table_cont = '''<table cellpadding="6" width="{{table_width}}" height="auto" border="{{table_border}}">
    <colgroup span="2">
        <col width="30px" />
        <col width="80px" />
    </colgroup>
    <colgroup span="{date_colspan}" width="40px"></colgroup>
    <colgroup span="{sums_colspan}" width="40px"></colgroup>
    <tr>
        <th colspan="{title_colspan}"><font size="20px">{table_title}</font></th>
    </tr>
    {table_headers}
    {table_rows_contents}
    </table>'''

    each_row = '''<tr>
    <td class="num">{id}</td>
    <td class="name">{name}</td>
    {details}
    </tr>'''

    day_cont = '''<td class="day">%s</td>'''

    def __init__(self, table_title, worker_dict):
        self.table_title = table_title
        self.worker_dict = worker_dict
        self.db_operator = SQLiteOperator()


    @abstractmethod
    def gen_worker_rows(self):
        pass




