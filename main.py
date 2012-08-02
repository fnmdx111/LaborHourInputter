# encoding: utf-8
import calendar

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import datetime
from misc import take

class Form(QDialog, object):

    _le_attributes = [[['day', 'month', 'labor_hour_sum'],
                       ['worker_id', 'worker_name', 'waste_sum']],
                      [['waste_1', 'waste_2', 'waste_3'],
                       ['assist_1', 'assist_2', 'assist_sum']]]
    _le_attributes = map(lambda sub_list: map(lambda l: map(lambda item: 'le_' + item, l), sub_list), _le_attributes)
    _le_labels = [[[u'日期', u'月份', u'工时合计'],
                    [u'编号', u'姓名', u'废品合计']],
                    [[u'废品1', u'废品2', u'废品3'],
                    [u'辅助1', u'辅助2', u'辅助3']]]

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.resize(400, 250)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.setLayout(self.init_layouts())

        self.le_worker_name.setFixedSize(60, 20)
        self.set_time_attributes()
        for _le_attr in ['le_waste_sum', 'le_labor_hour_sum']:
            self.__getattribute__(_le_attr).setReadOnly(True)

        # self.load_workers()


    def init_layouts(self):
        v_layout = QVBoxLayout()
        v_layout.addStretch()
        for _ in [self.gen_g_layout(Form._le_attributes[0], Form._le_labels[0]),
                  self.gen_labor_hour_layout(),
                  self.gen_g_layout(Form._le_attributes[1], Form._le_labels[1])]:
            v_layout.addLayout(_)
            v_layout.addStretch()

        self.btn_ok = QPushButton(u'确定')
        self.btn_find = QPushButton(u'找回')
        h_layout = QHBoxLayout()
        h_layout.addStretch(2)
        h_layout.addWidget(self.btn_ok)
        h_layout.addStretch()
        h_layout.addWidget(self.btn_find)

        layout = QVBoxLayout()
        layout.addLayout(v_layout)
        layout.addLayout(h_layout)

        return layout


    def gen_labor_hour_layout(self):
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        for col_num, nums in enumerate(take(range(1, 7), by=2)):
            gl = QGridLayout()
            gl.addWidget(QLabel(u'班产'), 0, 0, Qt.AlignLeft)
            gl.addWidget(QLabel(u'数量'), 0, 1, Qt.AlignLeft)

            for cnt, num in enumerate(nums):
                def _(attr_prefix, col):
                    line_edit = self.produce_eligible_line_edit()
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
            if content.isdigit():
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
                gls[i].addWidget(QLabel(label), row, 0)
                line_edit = self.produce_eligible_line_edit()
                gls[i].addWidget(line_edit, row, 1)
                self.__setattr__(attr, line_edit)

        h_layout = QHBoxLayout()
        h_layout.addStretch()
        for gl in gls:
            h_layout.addLayout(gl)
            h_layout.addStretch()

        return h_layout


    def produce_eligible_line_edit(self, width=40):
        line_edit = QLineEdit()
        line_edit.setFixedSize(width, 20)
        line_edit.setAlignment(Qt.AlignRight)
        line_edit.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        return line_edit



if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    app.exec_()

