import datetime
from sqlalchemy import *
from sqlalchemy import exc
import config
import misc
from xls_oprt import ExcelOperator

DEBUG = True
days = misc.get_month_days(datetime.datetime(2012, 10, 3))

class SQLiteOperator(object):

    _db_keys = (
        'labor_hour_1', 'real_amount_1',
        'labor_hour_2', 'real_amount_2',
        'labor_hour_3', 'real_amount_3',
        'labor_hour_4', 'real_amount_4',
        'labor_hour_5', 'real_amount_5',
        'labor_hour_6', 'real_amount_6',
        'labor_hour_7', 'real_amount_7',
        'labor_hour_8', 'real_amount_8',
        'labor_hour_9', 'real_amount_9',
        'waste_1', 'waste_2', 'waste_3',
        'assist_1', 'assist_2',
        'worker_id_aux', 'labor_hour_aux_to'
    )

    def __init__(self, worker_dict=None, day=None):
        """note: day and worker_dict is only needed when you want to initialize the entire database,
        that is to say, a read-only SQLiteOperator need no parameter to initialize with."""
        self.engine = create_engine('sqlite:///%s' % config.db_path, echo=config.db_echo)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        self.connection = self.engine.connect()
        self.worker_dict = worker_dict
        if day:
            self.create_table(day)
            self.default_name = day

        if DEBUG:
            for day in days:
                self.table = Table(
                    unicode(day), self.metadata,
                    Column('worker_id', Integer, primary_key=True),
                    *map(lambda key: Column(key, Integer, nullable=True),
                         SQLiteOperator._db_keys),
                    extend_existing=True
                )
                self.metadata.create_all(self.engine)
                self.init_table(self.table)


    def init_table(self, table):
        if not self.worker_dict:
            return

        for worker_id in self.worker_dict:
            try:
                self.connection.execute(
                    table.insert().values(),
                    {'worker_id': int(worker_id)}
                )
            except exc.IntegrityError:
                # already have that row, moving on
                pass


    def create_table(self, name):
        name = name if name else self.default_name

        if name in self.metadata.tables:
            self.table = self.metadata.tables[name]
        else:
            self.table = Table(
                name, self.metadata,
                Column('worker_id', Integer, primary_key=True),
                *map(lambda key: Column(key, Integer, nullable=True),
                     SQLiteOperator._db_keys)
            )

            if not DEBUG:
                self.metadata.create_all(self.engine)

        if DEBUG:
            return self.table

        self.init_table(self.table)

        return self.table


    def write_back(self, dumped, day=None):
        table = self.create_table(day)
        self.connection.execute(table.update().
                                      where(table.c.worker_id == dumped['worker_id']).
                                      values(**dumped))


    def write_back_single(self, worker_id_aux, labor_hour_aux, day=None):
        table = self.create_table(day)
        self.connection.execute(table.update().
                                      where(table.c.worker_id == worker_id_aux).
                                      values(labor_hour_aux_to=labor_hour_aux))


    def retrieve(self, worker_id, day=None):
        table = self.create_table(day)
        result =  self.connection.execute(
            table.select().
                  where(table.c.worker_id == worker_id)
        ).fetchall()

        if result:
            return result[0]


    def is_empty_row(self, worker_id=None, row=None, day=None):
        row = self.retrieve(worker_id, day) if not row else row
        if not row:
            return True

        return not any(map(row.__getitem__, SQLiteOperator._db_keys[:-1]))


    def get_month_days_in_db(self):
        l = map(lambda item: item[0], misc.sort_dict_keys_numerically(self.metadata.tables))
        l = l[27:] + l[:27]

        return l


    def get_data_per_day(self, worker_id, day):
        result = self.retrieve(worker_id, unicode(day))
        if not self.is_empty_row(row=result):
            lh_sum, waste_sum, assist_sum = 0, 0, 0

            for lh_key, ra_key in misc.take(SQLiteOperator._db_keys[:18], by=2):
                labor_hour, real_amount = map(result.__getitem__, (lh_key, ra_key))
                if labor_hour and real_amount:
                    labor_hour, real_amount = map(float, (labor_hour, real_amount))
                    if labor_hour:
                        lh_sum += real_amount / labor_hour
            lh_sum = round(lh_sum * 8, 1)

            for key in SQLiteOperator._db_keys[18:21]:
                waste = result[key]
                waste_sum += waste if waste else 0

            for key in SQLiteOperator._db_keys[21:23]:
                assist = result[key]
                assist_sum += assist if assist else 0

            labor_hour_aux_to = result['labor_hour_aux_to']
            labor_hour_aux_to = labor_hour_aux_to if labor_hour_aux_to else 0

            return lh_sum, labor_hour_aux_to, waste_sum, assist_sum

        return .0, 0, 0, 0


    def iterate_worker(self, worker_id):
        for day in self.get_month_days_in_db():
            yield self.get_data_per_day(worker_id, day)


    def __del__(self):
        self.connection.close()




if __name__ == '__main__':
    writer = SQLiteOperator(ExcelOperator(config.XLS_PATH).get_id_name_pairs(0), '5')

    writer.write_back({
        'worker_id': 2,
        'labor_hour_1': 100,
        'real_amount_1': 600,
        'waste_1': 20,
        'worker_id_aux': 101,
        'labor_hour_aux_to': 10
    })

    for item in writer.retrieve(1, day='9'):
        print item

    print writer.is_empty_row(worker_id=1, day='8')
    print writer.is_empty_row(worker_id=111, day='8')

    # writer.insert({
    #     'worker_id': 5,
    #     'labor_hour_1': 100,
    #     'real_amount_1': 600,
    #     'waste_1': 20,
    #     'worker_id_aux': 101,
    #     'labor_hour_aux_to': 10
    # })


