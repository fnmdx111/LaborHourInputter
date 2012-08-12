import config
from data_prvd import l_h_d_prvd, w_prvd
import misc
from view_writer import ViewWriter
from xls_oprt import ExcelOperator

def auto_gen(title_index_pairs, data_prvd_class, max=config.split_page_at):
    for title, index in title_index_pairs:
        worker_tuples = misc.sort_dict_keys_numerically(
            ExcelOperator(config.XLS_PATH).\
            get_id_name_pairs(index)
        )

        for num, d in enumerate(misc.take(worker_tuples,
                                by=max)):
            view = ViewWriter(data_prvd_class(title, dict(d)))

            with open('%s%s.html' % (num, title.decode('utf-8')), 'w') as f:
                print >> f, view


if __name__ == '__main__':
    auto_gen(l_h_d_prvd.TITLE_INDEX_PAIRS, l_h_d_prvd.LaborHourDataProvider)
    auto_gen(w_prvd.TITLE_INDEX_PAIRS, w_prvd.WasteDataProvider, max=99999)

