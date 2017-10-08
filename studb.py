from sqlalchemy import create_engine
from sqlalchemy import exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DATETIME, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey

Base = declarative_base()


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    N = Column(Integer, unique=True)
    fullname = Column(String(128))
    student_id = Column(String(32))
    birth_date = Column(String(64))
    student_group = Column(String(32))
    department = Column(String(32))
    kafedra = Column(String(32))
    decanat = Column(String(32))
    ed_form = Column(String(32))
    ed_type = Column(String(32))
    code = Column(String(32))
    commerce = Column(String(32))
    current_state = Column(String(128))
    student_info = Column(Text)

    def __repr__(self):
        rstr = "<Student(N='%s', fullname='%s', student_id='%s',birth_date='%s'," \
               " student_group='%s', department='%s', kafedra='%s'" \
               ")>" %(self.N, self.fullname, self.student_id,
                self.birth_date, self.student_group, self.department, self.kafedra)
        return rstr


class Info(Base):
    __tablename__ = 'info'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    okso_bac = Column(String(512))
    okso_mag = Column(String(512))
    commerce = Column(String(32))
    doc = Column(String(128))
    phone = Column(String(128))
    programm = Column(String(128))
    citizenship = Column(String(128))
    sex = Column(String(128))
    markbook = Column(String(128))
    address = Column(String(512))
    post_index = Column(String(32))
    current_state = Column(String(128))
    group = Column(String(512))

class Mark(Base):
    __tablename__ = 'marks'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    semester = Column(String(128))
    discipline = Column(String(256))
    mark_type = Column(String(64))
    mark_value = Column(String(64))


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



