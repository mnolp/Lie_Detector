from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

'''
change this line with information from your database
'''
db = create_engine("postgres://tiziano:Tnatali93@localhost/new_lie_detector")
base = declarative_base()

# create a configured "Session" class
Session = sessionmaker(bind=db)

# create a Session
session = Session()


class Answer(base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True)
    path_to_wav = Column(String(150), nullable=False)
    word = Column(String(10), nullable=False)
    truth = Column(Boolean, nullable=False)
    time = Column(Float, nullable=False)
    q_time = Column(Float)
    number = Column(Integer, nullable=False)
    test_id = Column(Integer, ForeignKey("tests.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))


class Question(base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    path_to_wav = Column(String(100), nullable=False)
    group_id = Column(Integer, ForeignKey("question_groups.id"))
    test = relationship("QTime")
    answer = relationship("Answer")


class QuestionGroup(base):
    __tablename__ = "question_groups"
    id = Column(Integer, primary_key=True)
    group = Column(String(50), nullable=False)
    question = relationship("Question")


class QTime(base):
    __tablename__ = "q_times"
    time = Column(Float, nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
    test_id = Column(Integer, ForeignKey("tests.id"), primary_key=True)
    position = Column(Integer)


class Test(base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True)
    path_to_media = Column(String(150), nullable=False)
    ball_position = Column(Integer, nullable=False)
    truth = Column(Boolean, nullable=False)
    number = Column(Integer)
    answer = relationship("Answer")
    question = relationship("QTime")


def main():
    import os
    root = '../output/tests'
    dirs = os.listdir(root)

    answer_list = []
    for test in dirs:
        if int(test.split('_')[1]) in range(56, 76):
            with open('/'.join([root, test, 'answertimes2.csv']), 'r') as csvf:
                data = csvf.read()
            data = data.splitlines()
            files = os.listdir(root+'/'+test)
            files = [x for x in files if len(x)>5 and x.endswith('wav')]

            new_test = Test(path_to_media=root + '/' + test,
                            truth=False,
                            ball_position=-1
                            )

            session.add(new_test)
            session.commit()

            for i in range(1, len(data)):
                data[i] = data[i].split(';')
                path_to_answer = [x for x in files if x.startswith(str(i-1))]
                print(int(data[i][0]))
                answer_list.append(Answer(path_to_wav='/'.join([root, test, path_to_answer[0]]),
                                          word=data[i][6],
                                          time=float(data[i][3]),
                                          number=int(data[i][0])-1,
                                          truth=True if test.split('_')[-1] == 't' else False,
                                          test_id=session.query(Test.id).filter(Test.path_to_media == root+'/'+test).first(),
                                          question_id=session.query(Question.id).filter(Question.path_to_wav == data[i][1]).first(),
                                          ))

    session.add_all(answer_list)
    session.commit()

def add_answers(root='../output/tests/'):
    import os
    dirs = os.listdir(root)

    for d in dirs:
        wav_files = os.listdir(root+d)
        wav_files = [x for x in wav_files if x.endswith('trim.wav') or x.endswith('o.wav')]

        with open(root+d+'/answertimes2.csv', 'r') as f:
            csv_data = f.read()
        csv_data = csv_data.splitlines()
        csv_data = csv_data[1:]
        csv_data = [x.split(';') for x in csv_data]

        test = session.query(Test).filter(Test.path_to_media==root+d).first()

        test_path = test.path_to_media

        answers = []
        for line in csv_data:
            answer_file = [x for x in wav_files if x.startswith(str(int(line[0])-1))]
            if len(line)<7:
                print('hi')
            answers.append(Answer(path_to_wav=root+d+'/'+answer_file[0],
                            word=line[6],
                            truth=True if line[7] == 't' else False,
                            time=line[3],
                            q_time=line[2],
                            number=line[0],
                            test_id=test.id,
                            question_id=session.query(Question.id).filter(Question.path_to_wav==line[1]).first()
                            ))
        session.add_all(answers)
        session.commit()


def add_question_to_answers(root='../output/tests/'):
    import os
    dirs = os.listdir(root)
    dirs = [x for x in dirs if len(x.split('_'))>2]

    for d in dirs:
        wav_files = os.listdir(root+d)
        wav_files = [x for x in wav_files if x.endswith('trim.wav') or x.endswith('o.wav')]

        with open(root+d+'/answertimes2.csv', 'r') as f:
            csv_data = f.read()
        csv_data = csv_data.splitlines()
        csv_data = csv_data[1:]
        csv_data = [x.split(';') for x in csv_data]

        test = session.query(Test).filter(Test.path_to_media==root+d).first()

        test_path = test.path_to_media

        answers = []
        for line in csv_data:
            question_id = session.query(Question.id).filter(Question.path_to_wav==line[1]).first()
            answer_file = [x for x in wav_files if x.startswith(str(int(line[0])-1))]
            if len(line)<7:
                print('hi')
            answer = session.query(Answer).filter(Answer.path_to_wav == root+d+'/'+answer_file[0]).first()
            if answer is None:
                answer = session.query(Answer).filter(Answer.path_to_wav == root+d+'/'+answer_file[1]).first()
            answer.question_id = question_id

            session.commit()


if __name__ == '__main__':
    # answers = session.query(Answer).all()
    # print(answers[0].truth)
    #add_answers()
    import sys
    print(sys.executable)