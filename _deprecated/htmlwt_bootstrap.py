# encoding: utf-8
from _deprecated.l_h_d_prvd import LaborHourDataProvider
from _deprecated.w_prvd import WasteDataProvider
from libs import misc, config
from _deprecated.view_writer import ViewWriter
from libs.xls_oprt import ExcelOperator

def auto_gen(provider_class):
    for title, index in config.title_index_pairs:
        worker_dict = ExcelOperator(config.XLS_PATH).get_id_name_pairs(index)

        for num, d in enumerate(misc.take(worker_dict, by=43)):
            view = ViewWriter(provider_class(title, dict(d)))

            with open('%s%s.html' % (num, (title + provider_class.title_suffix).decode('utf-8')),
                      'w') as f:
                print >> f, view


if __name__ == '__main__':
    for provider_class in [LaborHourDataProvider, WasteDataProvider]:
        auto_gen(provider_class)


