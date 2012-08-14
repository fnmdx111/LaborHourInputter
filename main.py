# encoding: utf-8
import calendar
from functools import partial
from itertools import chain

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
from misc import take, interleave, take_adj, concat_prf, get_today, get_month_day_num
import config
from sqlite_writer import SQLiteOperator
from xls_oprt import ExcelOperator


class Form(QDialog, object):

    _font = QFont(u'Consolas', 14)
    _le_attributes = [[['day', 'month', 'labor_hour_sum'],
                       ['worker_id', 'worker_name', 'waste_sum']],
                      [['waste_1', 'waste_2', 'waste_3'],
                       ['assist_1', 'assist_2', 'assist_sum'],
                       ['worker_id_aux', 'worker_name_aux', 'labor_hour_aux']]]
    _le_attributes = map(lambda sub_list: map(lambda l: map(lambda item: 'le_' + item, l), sub_list), _le_attributes)
    _le_labels = [[[u'日期', u'月份', u'工时合计'],
                   [u'编号', u'姓名', u'废品合计']],
                  [[u'废品1', u'废品2', u'废品3'],
                   [u'辅助1', u'辅助2', u'辅助合计'],
                   [u'编号', u'姓名', u'工时']]]
    _max_le_amount = config.max_pair_num
    _pair_widget_range = range(1, _max_le_amount + 1)
    _waste_widget_range = range(1, 4)
    _assist_widget_range = range(1, 3)
    _labor_hour_prf = 'le_labor_hour_'
    _real_amount_prf = 'le_real_amount_'
    _labor_hour_attrs = map(concat_prf(_labor_hour_prf),
                            _pair_widget_range)
    _real_amount_attrs = map(concat_prf(_real_amount_prf),
                             _pair_widget_range)
    _hour_amount_pair = zip(_labor_hour_attrs,
                            _real_amount_attrs)
    _waste_attrs = map(concat_prf('le_waste_'), _waste_widget_range)
    _assist_attrs = map(concat_prf('le_assist_'), _assist_widget_range)
    _btn_attributes = ['ok', 'find', 'fix', 'reset']
    _btn_labels = [u'确定', u'找回', u'改正', u'重置']
    _editable_widget_attrs = list(interleave(_labor_hour_attrs, _real_amount_attrs)) +\
                             _waste_attrs + _assist_attrs + ['le_worker_id_aux']

    def __init__(self, app, parent=None):
        super(Form, self).__init__(parent)

        self.current_focus = None
        self.app = app
        self.connect(self.app, SIGNAL('focusChanged(QWidget*, QWidget*)'), self.focus_changed)

        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowMinMaxButtonsHint)
        self.resize(920, 670)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.setLayout(self.gen_main_layout())

        self.le_worker_name.setFixedSize(100, 30)

        self.set_time_attributes()
        for _le_attr in ['le_waste_sum',
                         'le_labor_hour_sum',
                         'le_assist_sum',
                         'le_labor_hour_aux']:
            self.__getattribute__(_le_attr).setReadOnly(True)

        self.make_connections()

        self.worker_dict = ExcelOperator(config.XLS_PATH).get_id_name_pairs(0)
        self.set_tab_orders()
        self.le_worker_id.setFocus()

        self.db_operator = SQLiteOperator(self.worker_dict, unicode(self.dt.day))

        self.validate_worker_id = lambda text: self._validate_text(text, u'请检查员工信息！')
        self.validate_day = lambda text: self._validate_text(text, u'请检查日期！')


    def focus_changed(self, _, now):
        self.current_focus = now


    _sqlite_attrs = ['le_worker_id'] +\
                    list(interleave(_labor_hour_attrs,
                                    _real_amount_attrs)) +\
                   _waste_attrs + _assist_attrs +\
                   ['le_worker_id_aux']
    _sqlite_col_names = map(lambda s: unicode(s[3:]), _sqlite_attrs)
    def dump_all(self):
        result = {}
        for key, attr in zip(Form._sqlite_col_names,
                             Form._sqlite_attrs):
            text = unicode(self.__getattribute__(attr).text())
            if attr == 'le_worker_id':
                if not self.validate_worker_id(text):
                    return {}

            if text.isdigit():
                result[key] = int(text)
            else:
                if config.FORCE_OVERRIDE:
                    result[key] = None

        return result


    def make_connections(self):
        self.connect(self.le_worker_id,
                     SIGNAL('textEdited(QString)'),
                     partial(self.update_worker_name,
                             which_one=self.le_worker_name))
        # self.connect(self.le_worker_id,
        #              SIGNAL('returnPressed()'),
        #              self.go_to_next_tab)
        self.connect(self.le_worker_id_aux,
                     SIGNAL('textEdited(QString)'),
                     partial(self.update_worker_name,
                             which_one=self.le_worker_name_aux))
        self.connect(self.le_worker_id_aux,
                     SIGNAL('textEdited(QString)'),
                     self.update_labor_hour_aux)
        # self.connect(self.le_worker_id_aux,
        #              SIGNAL('returnPressed()'),
        #              self.go_to_next_tab)
        self.connect(self.le_worker_name,
                     SIGNAL('textEdited(QString)'),
                     partial(self.update_worker_id,
                             which_one=self.le_worker_id))
        self.connect(self.le_worker_name_aux,
                     SIGNAL('textEdited(QString)'),
                     partial(self.update_worker_id,
                             which_one=self.le_worker_id_aux))
        self.connect_lot(Form._waste_attrs,
                         self.le_waste_sum)
        self.connect_lot(Form._assist_attrs,
                         self.le_assist_sum)
        self.connect_group()
        self.connect(self.btn_ok,
                     SIGNAL('clicked()'),
                     self.btn_ok_clicked)
        self.connect(self.btn_find,
                     SIGNAL('clicked()'),
                     self.btn_find_clicked)
        self.connect(self.le_labor_hour_sum,
                     SIGNAL('textChanged(QString)'),
                     self.update_labor_hour_aux)
        self.connect(self.btn_fix,
                     SIGNAL('clicked()'),
                     partial(self.btn_ok_clicked, override=True))


    def update_labor_hour_aux(self):
        if not self.le_worker_id_aux.text():
            self.le_labor_hour_aux.setText(u'')
            return

        content = self.le_labor_hour_sum.text()
        if content:
            content = float(content)
            if content < 8:
                hour_aux = 4
            elif 8 <= content < 12:
                hour_aux = 6
            elif 12 <= content < 16:
                hour_aux = 8
            else:
                hour_aux = 10
            self.le_labor_hour_aux.setText(unicode(hour_aux))


    def _validate_text(self, text, error_msg):
        if (not text) or (text == u'0'):
            QMessageBox.critical(self, u'错误', error_msg, QMessageBox.Ok)
            return False

        return True


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if event.modifiers() == Qt.ControlModifier:
                event.accept()
                self.btn_ok_clicked()
                return
            if isinstance(self.current_focus, QPushButton):
                event.accept()
                self.btn_ok_clicked()
                return
            if any(map(self.current_focus.name.startswith,
                       ['le_labor_hour', 'le_real_amount',
                        'le_waste', 'le_assist', 'le_worker_id'])):
                self.current_focus.tab_next.setFocus()
                event.accept()
            elif isinstance(self.current_focus, QPushButton):
                event.accept()
            else:
                event.ignore()


    def clear_all_editable(self, except_=('le_worker_name',)):
        for attr in Form._editable_widget_attrs + ['le_worker_name', 'le_worker_name_aux']:
            if attr in except_:
                continue
            self.__getattribute__(attr).setText(u'')


    def query_last_worker_aux(self, worker_id, day):
        result = self.db_operator.retrieve(worker_id, day)
        if result:
            result = result['worker_id_aux']
            if result:
                return result

        return False


    def btn_ok_clicked(self, override=False):
        day = unicode(self.le_day.text())
        if not self.validate_day(day):
            return

        dumped = self.dump_all()
        if not override:
            if not self.db_operator.is_empty_row(worker_id=dumped['worker_id'], day=day):
                QMessageBox.critical(self, u'错误', u'修改请用改正按钮！', QMessageBox.Ok)
                return


        # 先清除上个辅助工人的工时
        last_worker_id_aux = self.query_last_worker_aux(dumped['worker_id'],
                                                        day)
        if last_worker_id_aux:
            self.db_operator.write_back_single(
                last_worker_id_aux,
                None, day
            )

        if dumped:
            self.db_operator.write_back(dumped, day)

        worker_aux = unicode(self.le_worker_id_aux.text())
        if worker_aux:
            worker_aux = int(worker_aux)
            self.update_labor_hour_sum()
            self.update_labor_hour_aux()
            labor_hour_aux = int(self.le_labor_hour_aux.text())

            self.db_operator.write_back_single(worker_aux, labor_hour_aux, day)

        self.clear_all_editable(except_=())
        self.le_worker_id.setFocus()
        self.le_worker_id.setText(u'')


    def btn_find_clicked(self):
        worker_id = unicode(self.le_worker_id.text())
        day = unicode(self.le_day.text())
        if not self.validate_worker_id(worker_id):
            return
        else:
            worker_id = int(worker_id)
        if not self.validate_day(day):
            return

        results = self.db_operator.retrieve(worker_id, day)
        if results:
            results = results.items()

            _, labor_hour_aux_to = results[-1]

            self.clear_all_editable()
            for attr, (_, item) in zip(Form._editable_widget_attrs,
                                       results[1:-1]):
                if item:
                    self.__getattribute__(attr).setText(unicode(item))

            self.update_worker_name(self.le_worker_id_aux.text(), self.le_worker_name_aux)
            self.update_worker_name(self.le_worker_id.text(), self.le_worker_name)


    def connect_lot(self, attrs, sum_widget):
        target_func = self.gen_update_sum_slot(attrs, sum_widget)
        for attr in attrs:
            widget = self.__getattribute__(attr)
            self.connect(widget,
                         SIGNAL('textChanged(QString)'),
                         target_func)
            # self.connect(widget,
            #              SIGNAL('returnPressed()'),
            #              self.go_to_next_tab)


    def connect_group(self):
        for attrs in Form._hour_amount_pair:
            for attr in attrs:
                widget = self.__getattribute__(attr)
                self.connect(widget,
                             SIGNAL('textChanged(QString)'),
                             self.update_labor_hour_sum)
                # self.connect(widget,
                #              SIGNAL('returnPressed()'),
                #              self.go_to_next_tab)


    def go_to_next_tab(self):
        self.sender().tab_next.setFocus()


    def update_labor_hour_sum(self):
        labor_hour_sum = .0
        for lb_attr, ra_attr in Form._hour_amount_pair:
            labor_hour = unicode(self.__getattribute__(lb_attr).text())
            real_amount = unicode(self.__getattribute__(ra_attr).text())

            if labor_hour and real_amount:
                labor_hour, real_amount = map(float, (labor_hour, real_amount))
                if labor_hour:
                    labor_hour_sum += (real_amount / labor_hour) if labor_hour else .0
        labor_hour_sum *= 8
        labor_hour_sum = round(labor_hour_sum, 1)

        self.le_labor_hour_sum.setText(unicode(labor_hour_sum))


    def update_worker_id(self, worker_name, which_one):
        inverted = {value: key for key, value in self.worker_dict.iteritems()}
        text = ''
        worker_name = unicode(worker_name)
        if worker_name in inverted:
            text = inverted[worker_name]
        elif worker_name:
            text = u'查无此人'
        which_one.setText(text)


    _tab_order = list(chain(
                        ['le_worker_id'], # , 'le_worker_name'],
                        interleave(_labor_hour_attrs,
                                   _real_amount_attrs),
                        _waste_attrs,
                        _assist_attrs,
                        ['le_worker_id_aux'],#, 'le_worker_name_aux',
                        # 'le_labor_hour_aux'],
                        map(concat_prf('btn_'), _btn_attributes)))
    def set_tab_orders(self):
        for prev, succ in take_adj(Form._tab_order):
            if succ:
                prev_widget = self.__getattribute__(prev)
                succ_widget = self.__getattribute__(succ)
                prev_widget.tab_next = succ_widget

                prev_widget.setFocusPolicy(Qt.StrongFocus)
                succ_widget.setFocusPolicy(Qt.StrongFocus)
                self.setTabOrder(prev_widget,
                                 succ_widget)
        self.setTabOrder(self.btn_reset, self.le_worker_id)

        self.le_day.setFocusPolicy(Qt.StrongFocus ^ Qt.TabFocus)
        self.le_month.setFocusPolicy(Qt.StrongFocus ^ Qt.TabFocus)
        self.le_worker_name.setFocusPolicy(Qt.StrongFocus ^ Qt.TabFocus)
        self.le_worker_name_aux.setFocusPolicy(Qt.StrongFocus ^ Qt.TabFocus)

        self.le_real_amount_3.tab_next = self.le_waste_1


    def update_worker_name(self, worker_id, which_one):
        worker_id = unicode(worker_id)
        text = ''
        if worker_id in self.worker_dict:
            text = self.worker_dict[worker_id]
        elif worker_id:
            text = u'查无此人'
        which_one.setText(text)


    def gen_update_sum_slot(self, target_attrs, sum_widget):
        def _():
            values = map(int,
                         filter(lambda x: x,
                                map(lambda attr: self.__getattribute__(attr).text(),
                                    target_attrs)))
            sum_widget.setText(unicode(sum(values)))

        return _


    def gen_main_layout(self):
        v_layout = QVBoxLayout()

        title = QLabel(u'<center><font color="blue"><b>保 持 架 分 厂 工 时 录 入 系 统</b></font></center>')
        title.setFont(QFont(u'Arial', 30))
        v_layout.addWidget(title)

        v_layout.addStretch()
        for _ in (self.gen_g_layout(Form._le_attributes[0], Form._le_labels[0]),
                  self.gen_labor_hour_layout(),
                  self.gen_g_layout(Form._le_attributes[1], Form._le_labels[1])):
            v_layout.addLayout(_)
            v_layout.addStretch()

        h_layout = QHBoxLayout()
        h_layout.addStretch()
        for attr, label in zip(Form._btn_attributes, Form._btn_labels):
            btn = QPushButton(label)
            btn.setFont(Form._font)
            btn.setFixedSize(150, 50)
            btn.setAutoDefault(False)

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
        for col_num, nums in enumerate(take(Form._pair_widget_range,
                                            by=3)):
            gl = QGridLayout()
            gl.addWidget(self.gen_label(u'班产'), 0, 0, Qt.AlignLeft)
            gl.addWidget(self.gen_label(u'数量'), 0, 1, Qt.AlignLeft)

            for cnt, num in enumerate(nums):
                def _(attr_prefix, col):
                    line_edit = self.produce_eligible_line_edit(True)
                    line_edit.name = attr_prefix + str(num)
                    gl.addWidget(line_edit, cnt + 1, col)
                    self.__setattr__(attr_prefix + str(num), line_edit)

                _(Form._labor_hour_prf, 0)
                _(Form._real_amount_prf, 1)
            h_layout.addLayout(gl)
            # if col_num < 2:
            h_layout.addStretch()

        return h_layout


    def set_time_attributes(self):
        self.dt = get_today()
        self.le_day.setText(unicode(self.dt.day))
        self.le_day.last_content = self.le_day.text()
        self.le_month.setText(unicode(self.dt.month))
        self.le_month.last_content = self.le_month.text()

        self.le_day.maximum = get_month_day_num()
        self.le_month.maximum = 12

        self.connect(self.le_day, SIGNAL('textEdited(QString)'), self.restrict_content)
        self.connect(self.le_month, SIGNAL('textEdited(QString)'), self.restrict_content)
        self.connect(self.le_month, SIGNAL('textEdited(QString)'), self.update_le_day_maximum)


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

                numeric_only = False if ('name' in attr) or ('sum' in attr) else True
                line_edit = self.produce_eligible_line_edit(numeric_only)
                line_edit.name = attr

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
        line_edit.setText(config.DEFAULT_TEXT)

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
    form = Form(app)
    form.show()
    app.exec_()
