from sqlalchemy import *
from sqlalchemy import exc
import config
from xls_oprt import ExcelOperator


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
        self.engine = create_engine('sqlite:///%s' % config.db_path, echo=config.db_echo)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        self.connection = self.engine.connect()
        self.worker_dict = worker_dict
        if day:
            self.create_table(day)
            self.default_name = day


    def init_table(self, table):
        if not self.worker_dict:
            return

        try:
            self.connection.execute(
                table.insert().values(),
                map(lambda x: {'worker_id': int(x)}, self.worker_dict.keys())
            )
        except exc.IntegrityError:
            # viewing older table, pass
            pass



    def create_table(self, name):
        name = name if name else self.default_name

        if name in self.metadata.tables:
            self.table = self.metadata.tables[name]
            self.init_table(self.table)

            return self.table

        self.table = Table(
            name, self.metadata,
            Column('worker_id', Integer, primary_key=True),
            *map(lambda key: Column(key, Integer, nullable=True),
                 SQLiteOperator._db_keys)
        )

        self.metadata.create_all(self.engine)

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


    def is_empty_row(self, worker_id, day=None):
        row = self.retrieve(worker_id, day)
        if not row:
            return True

        return not any(map(row.__getitem__, SQLiteOperator._db_keys[:-1]))


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

    for item in writer.retrieve(1, day='8'):
        print item

    print writer.is_empty_row(1, '8')
    print writer.is_empty_row(111, '8')

    # writer.insert({
    #     'worker_id': 5,
    #     'labor_hour_1': 100,
    #     'real_amount_1': 600,
    #     'waste_1': 20,
    #     'worker_id_aux': 101,
    #     'labor_hour_aux_to': 10
    # })


