# encoding: utf-8
import calendar

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import datetime

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

        self.resize(350, 400)

        layout = QVBoxLayout()
        layout.addLayout(self.gen_v_layout(Form._le_attributes[0],
                                           Form._le_labels[0]))
        self.setLayout(layout)

        for _le_attr in ['le_waste_sum', 'le_labor_hour_sum']:
            self.__getattribute__(_le_attr).setReadOnly(True)

        self.set_time_attributes()

        self.load_workers()


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


    def gen_v_layout(self, le_attrs, le_labels):
        v_layout = QVBoxLayout()
        for attrs, labels in zip(le_attrs, le_labels):
            v_layout.addLayout(self._gen_h_layout(attrs, labels))

        return v_layout


    def _gen_h_layout(self, le_attrs, le_labels):
        def _gen_layout(attribute, label):
            _layout = QHBoxLayout()

            line_edit = QLineEdit()
            line_edit.setFixedSize(40, 20)
            line_edit.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

            _layout.addWidget(QLabel(label))
            _layout.addWidget(line_edit)

            self.__setattr__(attribute, line_edit)

            return _layout

        h_layout = QHBoxLayout()
        for args in zip(le_attrs, le_labels)[:-1]:
            h_layout.addLayout(apply(_gen_layout, args))
            h_layout.addStretch()
        h_layout.addLayout(_gen_layout(le_attrs[-1], le_labels[-1]))

        return  h_layout



if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    app.exec_()

