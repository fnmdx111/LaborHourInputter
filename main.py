# encoding: utf-8
import calendar
from functools import partial
from itertools import chain

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import datetime
from misc import take, interleave, take_adj
import config
from xls_oprt import ExcelOperator


class Form(QDialog, object):

    _font = QFont(u'Arial', 14)
    _le_attributes = [[['day', 'month', 'labor_hour_sum'],
                       ['worker_id', 'worker_name', 'waste_sum']],
                      [['waste_1', 'waste_2', 'waste_3'],
                       ['assist_1', 'assist_2', 'assist_sum'],
                       ['worker_id_aux', 'worker_name_aux', 'labor_hour_sum_aux']]]
    _le_attributes = map(lambda sub_list: map(lambda l: map(lambda item: 'le_' + item, l), sub_list), _le_attributes)
    _le_labels = [[[u'日期', u'月份', u'工时合计'],
                   [u'编号', u'姓名', u'废品合计']],
                  [[u'废品1', u'废品2', u'废品3'],
                   [u'辅助1', u'辅助2', u'辅助合计'],
                   [u'编号', u'姓名', u'工时']]]
    _btn_attributes = ['ok', 'find', 'fix', 'reset']
    _btn_labels = [u'确定', u'找回', u'改正', u'重置']
    _max_le_amount = 9
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowMinMaxButtonsHint)
        self.resize(920, 670)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.setLayout(self.init_layouts())

        self.le_worker_name.setFixedSize(100, 30)

        self.set_time_attributes()
        for _le_attr in ['le_waste_sum', 'le_labor_hour_sum', 'le_assist_sum']:
            self.__getattribute__(_le_attr).setReadOnly(True)


        self.connect(self.le_worker_id,
                     SIGNAL('textChanged(QString)'),
                     partial(self.update_worker_name, which_one=self.le_worker_name))
        self.connect(self.le_worker_id_aux,
            SIGNAL('textChanged(QString)'),
            partial(self.update_worker_name, which_one=self.le_worker_name_aux))

        self.xls_operator = ExcelOperator(config.XLS_PATH)
        self.worker_dict = self.xls_operator.get_id_name_pairs()
        self.set_tab_order()
        self.le_worker_id.setFocus()
        # self.load_workers()


    def set_tab_order(self):
        def _(prefix):
            return lambda x: prefix + str(x)

        for prev, succ in take_adj(list(
                            chain(['le_worker_id', 'le_worker_name'],
                                  interleave(map(_('le_labor_hour_'),
                                                 range(1, Form._max_le_amount + 1)),
                                             map(_('le_real_amount_'),
                                                 range(1, Form._max_le_amount + 1))),
                                  map(_('le_waste_'), range(1, 4)),
                                  map(_('le_assist_'), range(1, 3)),
                                  ['le_worker_id_aux', 'le_worker_name_aux', 'le_labor_hour_sum_aux'],
                                  map(lambda x: 'btn_' + x, Form._btn_attributes)))):
            if succ:
                prev_widget = self.__getattribute__(prev)
                succ_widget = self.__getattribute__(succ)
                prev_widget.setFocusPolicy(Qt.StrongFocus)
                succ_widget.setFocusPolicy(Qt.StrongFocus)
                self.setTabOrder(prev_widget,
                                 succ_widget)
        self.setTabOrder(self.btn_reset, self.le_worker_id)


    def update_worker_name(self, worker_id, which_one):
        worker_id = unicode(worker_id)
        if worker_id.isdigit():
            if worker_id in self.worker_dict:
                which_one.setText(self.worker_dict[worker_id])
            else:
                which_one.setText(u'查无此人')


    def gen_update_sum_slot(self, target_attrs, sum_widget, func):
        pass


    def init_layouts(self):
        v_layout = QVBoxLayout()

        title = QLabel(u'<center><font color="blue"><b>保 持 架 分 厂 工 时 录 入 系 统</b></font></center>')
        title.setFont(QFont(u'Arial', 30))
        v_layout.addWidget(title)

        v_layout.addStretch()
        for _ in [self.gen_g_layout(Form._le_attributes[0], Form._le_labels[0]),
                  self.gen_labor_hour_layout(),
                  self.gen_g_layout(Form._le_attributes[1], Form._le_labels[1])]:
            v_layout.addLayout(_)
            v_layout.addStretch()

        h_layout = QHBoxLayout()
        h_layout.addStretch()
        for attr, label in zip(Form._btn_attributes, Form._btn_labels):
            btn = QPushButton(label)
            btn.setFont(Form._font)
            btn.setFixedSize(150, 50)

            h_layout.addWidget(btn)
            h_layout.addStretch()

            self.__setattr__('btn_' + attr, btn)

        layout = QVBoxLayout()
        layout.addLayout(v_layout)
        layout.addLayout(h_layout)

        return layout


    def gen_label(self, label):
        l = QLabel(label)
        l.setFont(Form._font)

        return l


    def gen_labor_hour_layout(self):
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        for col_num, nums in enumerate(take(range(1, Form._max_le_amount + 1),
                                            by=3)):
            gl = QGridLayout()
            gl.addWidget(self.gen_label(u'班产'), 0, 0, Qt.AlignLeft)
            gl.addWidget(self.gen_label(u'数量'), 0, 1, Qt.AlignLeft)

            for cnt, num in enumerate(nums):
                def _(attr_prefix, col):
                    line_edit = self.produce_eligible_line_edit(True)
                    gl.addWidget(line_edit, cnt + 1, col)
                    self.__setattr__(attr_prefix + str(num), line_edit)

                _('le_labor_hour_', 0)
                _('le_real_amount_', 1)
            h_layout.addLayout(gl)
            # if col_num < 2:
            h_layout.addStretch()

        return h_layout


    def set_time_attributes(self):
        dt = datetime.date.today()
        self.dt = dt
        self.le_day.setText(str(dt.day))
        self.le_day.last_content = self.le_day.text()
        self.le_month.setText(str(dt.month))
        self.le_month.last_content = self.le_month.text()

        self.le_day.maximum = calendar.monthrange(dt.year, dt.month)[1]
        self.le_month.maximum = 12

        self.connect(self.le_day, SIGNAL('textChanged(QString)'), self.restrict_content)
        self.connect(self.le_month, SIGNAL('textChanged(QString)'), self.restrict_content)
        self.connect(self.le_month, SIGNAL('textChanged(QString)'), self.update_le_day_maximum)


    def update_le_day_maximum(self, content):
        content = unicode(content)
        if content:
            self.le_day.maximum = calendar.monthrange(self.dt.year, int(content))[1]


    def restrict_content(self, content):
        maximum = self.sender().maximum

        content = unicode(content)
        if content:
            if not content.isdigit():
                self.sender().setText(self.sender().last_content)
            else:
                if int(content) > int(maximum):
                    self.sender().setText(unicode(maximum))
            self.sender().last_content = self.sender().text()


    def gen_g_layout(self, le_attrs, le_labels):
        gls = [QGridLayout() for _ in range(len(le_attrs[0]))]
        for row, (attrs, labels) in enumerate(zip(le_attrs, le_labels)):
            for i, (attr, label) in enumerate(zip(attrs, labels)):
                gls[i].addWidget(self.gen_label(label), row, 0)

                numeric_only = False if 'name' in attr else True
                line_edit = self.produce_eligible_line_edit(numeric_only)

                gls[i].addWidget(line_edit, row, 1)
                self.__setattr__(attr, line_edit)

        h_layout = QHBoxLayout()
        h_layout.addStretch()
        for gl in gls:
            h_layout.addLayout(gl)
            h_layout.addStretch()

        return h_layout


    def produce_eligible_line_edit(self, numeric_only, width=80):
        line_edit = QLineEdit()

        line_edit.setFixedSize(width, 30)
        line_edit.setAlignment(Qt.AlignRight)
        line_edit.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        line_edit.setFont(self._font)
        line_edit.setFocusPolicy(Qt.NoFocus)

        if numeric_only:
            line_edit.setValidator(QIntValidator())

        return line_edit



if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    app.exec_()
