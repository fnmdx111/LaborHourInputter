# encoding: utf-8
import misc

class ViewWriter(object):
    html = '''<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <style text="text/css">
            table {{
                border: 1px solid;
                width: auto;
            }}
            td.name {{
                width: 85px;
            }}
            td.num, td.day {{
                width: 50px;
            }}
        </style>
        <title>表格</title>
    </head>
    <body>
        {table_content}
    </body>
    </html>'''

    table_cont = '''<table cellpadding="6" width="{table_width}" height="auto" border="{table_border}">
    <colgroup span="2">
        <col width="30px" />
        <col width="80px" />
    </colgroup>
    <colgroup span="{date_colspan}" width="40px"></colgroup>
    <colgroup span="{misc_colspan}" width="40px"></colgroup>
    <tr>
        <th colspan="{title_colspan}"><font size="20px">{table_title}</font></th>
    </tr>
    <tr>
        {table_headers}
    </tr>
    <tr>
        {date_contents}
    <tr/>
        {table_rows_contents}
    </table>'''

    each_row = '''<tr>
    <td class="num">{id}</td>
    <td class="name">{name}</td>
    {days_content}
    </tr>'''

    day_cont = '''<td class="day">%s</td>'''

    def __init__(self, data_provider, table_width=None, table_border=1):
        """note that data_extractor should be a function which takes (id, day) as args"""
        self.worker_dict = data_provider.worker_dict
        self.month_days = misc.get_month_days()
        self.data_extractor = data_provider.data_extractor
        self.meta_dict = {
            'table_width': table_width if table_width else '100%', 'table_border': table_border,
            'table_title': data_provider.table_title,
            'title_colspan': misc.get_month_day_num() + 2 + data_provider.misc_colspan,
            'date_colspan': misc.get_month_day_num(),
            'date_contents': self._gen_date_cols(),
            'table_rows_contents': '\n'.join(data_provider.gen_worker_rows()),
            'table_headers': data_provider.table_headers,
            'misc_colspan': data_provider.misc_colspan
        }


    def _gen_date_cols(self):
        return '\n'.join(map(lambda x: '<th>%s</th>' % x, self.month_days))


    def _gen_worker_rows(self):
        for id, name in misc.sort_worker_dict(self.worker_dict):
            days_content, sum = [], 0
            for day in self.month_days:
                day_sum = self.data_extractor(id, day)
                sum += day_sum
                days_content.append(ViewWriter.day_cont % day_sum)
            days_content.append(ViewWriter.day_cont % sum)

            _ = {
                'id': id.encode('utf-8'),
                'name': name.encode('utf-8'),
                'days_content': '\n'.join(days_content)
            }

            yield ViewWriter.each_row.format(**_)


    def gen_html(self):
        return ViewWriter.html.format(
            **{
                'table_content': ViewWriter.table_cont.format(
                    **self.meta_dict
                )
            }
        )


    def __str__(self):
        return self.gen_html()



