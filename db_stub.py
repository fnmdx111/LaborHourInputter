
from random import randint
from PyQt4.QtGui import QApplication
import sys
import datetime
import config
from main import Form
import misc
from xls_oprt import ExcelOperator

def gen_worker_data():
    r = []
    for _ in range(9):
        if randint(1, 2) > 1:
            r.append('')
            r.append('')
            continue

        labor = randint(300, 10000)
        if randint(1, 10) > 8:
            real = randint(300, labor)
        else:
            real = randint(labor, 12000)
        r.append(labor)
        r.append(real)


    for _ in range(3):
        if randint(1, 2) > 1:
            r.append('')
            r.append('')
            continue

        r.append(randint(2, 10))

    for _ in range(2):
        if randint(1, 2) > 1:
            r.append('')
            r.append('')
            continue

        r.append(randint(2, 10))

    if randint(1, 10) > 8:
        assist_worker_id = randint(1, 100)
        r.append(assist_worker_id)
    else:
        r.append('')

    return r



if __name__ == '__main__':
    config.db_echo = True
    what_month = datetime.datetime(2012, 10, 3)

    meta_attrs = ['le_day', 'le_month',
                  'le_worker_id']
    attrs = list(misc.interleave(Form._labor_hour_attrs, Form._real_amount_attrs)) +\
            Form._waste_attrs +\
            Form._assist_attrs +\
            ['le_worker_id_aux']

    app = QApplication(sys.argv)
    form = Form(app)

    month_days = misc.get_month_days(what_month)
    workers = ExcelOperator(config.XLS_PATH).get_id_name_pairs(0)

    for day in month_days:
        for worker_id in workers:
            r = gen_worker_data()
            m = [unicode(day), unicode(what_month.month), worker_id]
            print m, r

            for attr, data in zip(meta_attrs, m):
                form.__getattribute__(attr).setText(unicode(data))

            for attr, data in zip(attrs, gen_worker_data()):
                form.__getattribute__(attr).setText(unicode(data))

            form.btn_ok_clicked()





