# encoding: utf-8

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
                width: 60px;
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

    def __init__(self, data_provider, table_width=None, table_border=1):
        self.table_cont = data_provider.gen_table_cont()
        self.table_width = table_width
        self.table_border = table_border


    def gen_html(self):
        return ViewWriter.html.format(**{
                'table_content': self.table_cont.format(
                    table_content=self.table_cont,
                    table_width=self.table_width,
                    table_border=self.table_border
                )})


    def __str__(self):
        return self.gen_html()



