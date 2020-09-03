import os
import io
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from pydub import AudioSegment

from Scripts import PSQLDB_map as db


# All should be done with postgresql db

# transcribe answer with google
def get_timestamps(filename):
    # Set evinronment variable
    os.system('export GOOGLE_APPLICATION_CREDENTIALS=/home/tiziano/Downloads/lie-detector-260813-549d6f263b2c.json')

    # Instantiates a client
    client = speech.SpeechClient()

    # The name of the audio file to transcribe
    file_name = filename

    # Loads the audio into memory
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        enable_word_time_offsets=True,
        language_code='en-US',
        speech_contexts=[speech.types.SpeechContext(phrases=["yes", "no"], )], )

    # Detects speech in the audio file
    response = client.recognize(config, audio)
    '''
    for result in response.results[0].alternatives[0].words:
        print('Transcript: {}\nStart TIme: {}.{}\nEnd Time: {}.{}'.format(result.word, result.start_time.seconds, result.start_time.nanos, result.end_time.seconds, result.end_time.nanos))
    '''
    ret = response.results[0].alternatives[0].words if len(response.results) > 0 else None
    return ret


# trim audio with google time

def call_to_google(root):
    csvpath = 'answertimes.csv'
    files = os.listdir(root)
    wavs = [root + x for x in files if x.endswith('.wav') and not x.endswith('_trim.wav')]
    wavs.sort()
    timestamps = []

    with open(root + csvpath, 'r+') as f:
        lines = f.readlines()
    features = [x.strip().split(';') for x in lines]

    anst = []
    for i in range(1, len(features)):
        anst.append(float(features[i][3]) - float(features[i][2]))

    for i, wavf in enumerate(wavs):
        song = AudioSegment.from_wav(wavf)
        song1 = song[anst[i] * 1000 - 100:]
        song1.export(wavf[:wavf.rfind('.')] + "_trim" + wavf[wavf.rfind('.'):], format="wav")
        timestamps.append(get_timestamps(wavf[:wavf.rfind('.')] + "_trim" + wavf[wavf.rfind('.'):]))

    features[0] += ['AnswerStart', 'AnswerEnd', 'Answer']
    j = 0
    for i, line in enumerate(features):
        if i == 0:
            continue
        if timestamps[j] is not None:
            try:
                sts = timestamps[j][0].start_time.seconds
            except(AttributeError):
                sts = 0
            try:
                stn = timestamps[j][0].start_time.nanos
            except(AttributeError):
                stn = 0
            try:
                ets = timestamps[j][0].end_time.seconds
            except(AttributeError):
                ets = -1
            try:
                etn = timestamps[j][0].end_time.nanos
            except(AttributeError):
                etn = -1
            features[i] += ["{}.{}".format(sts, stn),
                            "{}.{}".format(ets, etn),
                            "{}".format(timestamps[j][0].word)]
        else:
            features[i] += ['null', 'null', 'null']
        j += 1

    for i, line in enumerate(features):
        if i == 0: continue
        path = '..' + line[1][line[1].index('/Question'):]
        q = db.session.query(db.Question.id).filter(db.Question.path_to_wav == path).first()[0]
        db.session.add(db.Answer(path_to_wav=wavs[i - 1],
                                 word=line[-1],
                                 time=line[3],
                                 q_time=line[2],
                                 number=i,
                                 test_id=
                                 db.session.query(db.Test.id).filter(db.Test.path_to_media == root[:-1]).first()[0],
                                 question_id=db.session.query(db.Question.id).filter(
                                     db.Question.path_to_wav == '..' + line[1][line[1].index('/Question'):]).first()[0]
                                 ))
    db.session.commit()

    with    open(root + '/answertimes2.csv', 'w+') as f:
        for line in features:
            for feature in line:
                f.write("{};".format(feature))
            f.write('\n')
    print(root)


# extract audio features
# get prediction from model
def get_audio_prediction(test, sgd_weights):
    from Scripts import get_audio_features as af
    from Scripts import SGDscript as sgd
    import numpy as np
    # answers = db.session.query(db.Answer).filter(db.Answer.test_id == (
    #     db.session.query(db.Test.id).filter(db.Test.path_to_media == test).first()[0]
    # )).all()

    correct_predictions = 0
    answers_files = [test[test.index('/output')+1:]+'/'+x for x in os.listdir(test) if x.endswith('.wav')]
    answers_data = np.loadtxt(test+"/answertimes.csv", delimiter=';', skiprows=1, dtype="str")

    prediction_sum = [0, 0, 0]
    audio_features = af.extract_features(answers_files)
    audio_features = np.delete(audio_features, np.where(np.isnan(audio_features[0])), 1)
    answers_db = db.session.query(db.Answer, db.Test).join(db.Test).filter(db.Test.path_to_media == test).all()

    for i, a in enumerate(answers_data):
        prediction = sgd.get_audio_prediction(audio_features[i], sgd_weights)
        path_to_q = '..'+a[1][a[1].index('/Question'):]
        question_group = -1
        question = db.session.query(db.Question, db.QuestionGroup).join(db.QuestionGroup).filter(
            db.Question.path_to_wav == path_to_q).first()

        if answers_db[i].Answer.truth == prediction:
            correct_predictions += 1

        if question.QuestionGroup.group == 'Cup1':
            question_group = 1
        elif question.QuestionGroup.group == 'Cup2':
            question_group = 2
        elif question.QuestionGroup.group == 'Cup3':
            question_group = 3
        elif question.QuestionGroup.group == 'Random':
            question_group = -1

        if question_group in range(1, 4):
            if (a[-2] == "yes" and prediction) or (a[-2] == "no" and not prediction):
                prediction_sum[question_group-1] += 1
            else:
                for j in range(1, 4):
                    if j != question_group:
                        prediction_sum[j-1] += 0.5

    return (prediction_sum, correct_predictions)


# split balance for every answer
# extract balance features
# def get_balance_data(start, end):
def get_balance_data(path):
    from Scripts import get_balance_features as bf
    return bf.single_main(path)


# get prediction from model
# assign points to cups
def get_balance_prediction(path):
    from Scripts import SGDscript as sgd
    import numpy as np

    data = get_balance_data(path)
    data = data[:, range(2, len(data[0]))]

    return np.array([sgd.get_balance_prediction(x.astype(np.float)) for x in data])


# give cup prediction from above data
def predict_crossval_cup():
    tests = db.session.query(db.Test).all()
    analyzed_tests = 0
    correct_predictions = 0
    corr_ans = 0
    only_right_cups = 0

    questions_query = db.session.query(db.Question.path_to_wav).order_by(db.Question.path_to_wav).all()
    questions_dic = {}
    questions_times = {}
    for _q in questions_query:
        questions_dic[_q.path_to_wav] = 0
        questions_times[_q.path_to_wav] = 0

    for test in tests:
        if test.ball_position != -1:
            analyzed_tests += 1
            coefficients = [0, 0, 0]
            sgd_weights = '../output/prediction_output/max_weights_group'
            if 41 < test.number < 50 or 65 < test.number < 75:
                _coef, cp = get_audio_prediction(test.path_to_media, sgd_weights + '0.sav')
                corr_ans += cp
                coefficients = [sum(x) for x in zip(coefficients, _coef)]
            elif 8 < test.number < 15 or 76 < test.number < 85:
                _coef, cp = get_audio_prediction(test.path_to_media, sgd_weights + '1.sav')
                corr_ans += cp
                coefficients = [sum(x) for x in zip(coefficients, _coef)]
            elif 16 < test.number < 23 or 86 < test.number < 93:
                _coef, cp = get_audio_prediction(test.path_to_media, sgd_weights + '2.sav')
                corr_ans += cp
                coefficients = [sum(x) for x in zip(coefficients, _coef)]
            elif 36 < test.number < 40 or 93 < test.number < 101:
                _coef, cp = get_audio_prediction(test.path_to_media, sgd_weights + '3.sav')
                corr_ans += cp
                coefficients = [sum(x) for x in zip(coefficients, _coef)]
            else:
                _coef, cp = get_audio_prediction(test.path_to_media, sgd_weights + '4.sav')
                corr_ans += cp
                coefficients = [sum(x) for x in zip(coefficients, _coef)]

            _aquery = db.session.query(db.Answer.question_id).filter(db.Answer.test_id == test.id).all()
            test_questions = db.session.query(db.Question.path_to_wav) \
                .filter(db.Question.id.in_(_aquery)) \
                .all()
            if coefficients.index(max(coefficients)) + 1 == test.ball_position:
                correct_predictions += 1
                only_right_cups += cp
            else:
                if coefficients.count(max(coefficients)) > 1:
                    if coefficients.index(max(coefficients[coefficients.index(max(coefficients)) + 1:])) + 1 == test.ball_position:
                        correct_predictions += 1

            for _tq in test_questions:
                questions_times [_tq[0]] += 1
                if coefficients.index(max(coefficients)) + 1 == test.ball_position:
                    questions_dic[_tq[0]] += 1

                else:
                    if coefficients.count(max(coefficients)) > 1:
                        if coefficients.index(max(coefficients[coefficients.index(max(coefficients)) + 1:])) + 1 == test.ball_position:
                            questions_dic[_tq[0]] += 1

    os.remove('../output/audio_features/temp_af.csv')
    for k, v in questions_dic.items():
        print('{}: {}/{} ---> {}%'.format(k, v, questions_times[k], v/questions_times[k]))
    print('\n\nTotal number of tests: {}\n'
          'Number of analyzed tests: {}\n'
          'Number of tests predicted correctly: {}\n'
          'Precision: {}\n'
          'Average correct answers when test correct: {}\n'
          'Average correct answers per test: {}\n'.format(len(tests), analyzed_tests, correct_predictions,
                                   correct_predictions / analyzed_tests, only_right_cups/correct_predictions, corr_ans/analyzed_tests))

    return correct_predictions / analyzed_tests


def main():

    val = get_audio_prediction('../output/temp_test', "../output/prediction_output/sgd_audio_weights.sav")
    with open("../predicted_cup.txt", "w") as outf:
        outf.write(str(val.index(max(val))))


# To get crossvalidation values on all the gathered tests
# change here main() to predict_crossval_cup()
if __name__ == '__main__':
    main()