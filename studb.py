from sqlalchemy import create_engine
from sqlalchemy import exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DATETIME, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey

Base = declarative_base()

# student['fullname'] = tds[2].get_text()
# student['student_id'] = tds[3].get_text()
# student['birth_date'] = tds[4].get_text()
# student['course'] = tds[5].get_text()
# student['group'] = tds[6].get_text()
# student['institute'] = tds[7].get_text()
# student['high_school'] = tds[8].get_text()
# student['education_form'] = tds[10].get_text()
# student['education_type'] = tds[11].get_text()
# student['code'] = tds[12].get_text()
# student['commerce'] = 1 if tds[13].img else 0
# student['current_state'] = tds[14].get_text()

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    fullname = Column(String(128))
    student_id = Column(String(32))
    birth_date = Column(String(64))
    course = Column(String(64))
    student_group = Column(String(32))
    institute = Column(String(32))
    high_school = Column(String(32))
    education_form = Column(String(32))
    education_type = Column(String(32))
    code = Column(String(32))
    commerce = Column(String(32))
    current_state = Column(String(128))

    def __repr__(self):
        rstr = "<Student(fullname='%s', student_id='%s',birth_date='%s'," \
               " student_group='%s', institute='%s', high_school='%s'" \
               ")>" %(self.fullname, self.student_id,
                self.birth_date, self.student_group, self.institute, self.high_school)
        return rstr

class Info(Base):
    __tablename__ = 'info'

    id = Column(Integer, primary_key=True)
    sid = Column(Integer, ForeignKey('students.id'))
    document = Column(String(128))
    sex = Column(String(128))
    citizenship = Column(String(128))
    post_index = Column(String(32))
    address = Column(String(512))
    phone = Column(String(128))
    high_school_desc = Column(String(256))
    okso_bac = Column(String(512))
    okso_mag = Column(String(512))
    student_residence = Column(String(32))
    celevoy = Column(String(32))


class Mark(Base):
    __tablename__ = 'marks'
    id = Column(Integer, primary_key=True)
    sid = Column(Integer, ForeignKey('students.id'))
    semester = Column(String(128))
    discipline = Column(String(256))
    session = Column(String(128))
    form = Column(String(64))
    result = Column(String(64))


class StudentsDB:
    def __init__(self, db_path):
        self.engine = create_engine('sqlite:///' + db_path, echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind= self.engine)
        self.session = Session()

    def insert(self, st):
        try:
            self.session.add(st)
            # self.session.commit()
        except exc.SQLAlchemyError as e:
            print(e)

    def inser_info(self,inft):
        try:
            self.session.add(inft)
            # self.session.commit()
        except exc.SQLAlchemyError as e:
            print(e)

    def inser_mark(self,mark):
        try:
            self.session.add(mark)
            # self.session.commit()
        except exc.SQLAlchemyError as e:
            print(e)

    def commit(self):
        try:
            self.session.commit()
        except exc.SQLAlchemyError as e:
            print(e)

    def select_students(self, group = None):
        try:
            if(group):
                return self.session.query(Student).filter(Student.student_group.like('%'+group+'%'))
            else:
                return self.session.query(Student)
        except exc.SQLAlchemyError as e:
            print(e)



