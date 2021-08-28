#! /usr/bin/env python3.5
import os
import tornado.ioloop
import tornado.web
import studb
import pandas as pd

class Stud:
    name = ""
    id = 0
    N = 0
    group = 1

    pass

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        sdb = studb.StudentsDB('StudentBase.db')
        students = []
        group = ''
        try:
            group = self.get_argument("group")
            studs = sdb.select_students(group = group)
            print(1)
        except:
            studs = sdb.select_students(group = '134')
            print(2)

        studtata = {}
        #df = pd.DataFrame({'Data': [10, 20, 30, 20, 15, 30, 45]})


        studtata['Name'] = []
        studtata['Group'] = []
        studtata['ID'] = []
        for s in studs:
            student = Stud()
            student.name = s.fullname
            student.id = s.student_id
            student.N = s.id
            student.group = s.student_group
            students.append(student)
            studtata['Name'].append(s.fullname)
            studtata['Group'].append(s.student_group)
            studtata['ID'].append(s.student_id)

        df = pd.DataFrame(studtata)
        writer = pd.ExcelWriter('students.xlsx', engine='xlsxwriter')
        # Convert the dataframe to an XlsxWriter Excel object.
        df.to_excel(writer, sheet_name='Students', index = False)
        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

        self.render('index.html',students = students, group=group)

class DownloadHandler(tornado.web.RequestHandler):
    def get(self):
        file_name = "students.xlsx"#"students.db"
        _file_dir = os.path.abspath("") + "/"
        _file_path = "%s/%s" % (_file_dir, file_name)
        if not file_name or not os.path.exists(_file_path):
            raise tornado.web.HTTPError(404)
        self.set_header('Content-Type', 'application/force-download')
        self.set_header('Content-Disposition', 'attachment; filename=%s' % file_name)
        with open(_file_path, "rb") as f:
            try:
                while True:
                    _buffer = f.read(4096)
                    if _buffer:
                        self.write(_buffer)
                    else:
                        f.close()
                        self.finish()
                        return
            except:
                raise tornado.web.HTTPError(404)

        raise tornado.web.HTTPError(500)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/getfile", DownloadHandler)
    ])


if __name__ == "__main__":

    print("main")
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()