# encoding: utf-8

# 对于未填的项目强制清除
FORCE_OVERRIDE = True
SKIP_NOT_FOUND_ATTENDANCE = False
DEFAULT_TEXT = u''

db_path = 'this_month.db'
XLS_PATH = 'data.xls'
max_pair_num = 9

db_echo = False
split_page_at = 43


title_index_pairs = (
    ('单多轴车间', 1),
    ('零件车间', 2),
    ('装配车间', 3),
    ('备料组', 4),
    ('清包车间', 5)
)

attendance_sheet_index = 12
performance_sheet_index = 7

