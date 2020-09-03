import os
import numpy as np
from Scripts import PSQLDB_map as db
from sklearn import preprocessing

def check_answer(rootdir = '../output/tests'):
    csvfiles = []
    my_files = []
    path = ''
    for subdir, dirs, files in os.walk(rootdir):
        my_files += [os.path.join(subdir, file) for file in files]
    my_files = [x for x in my_files if int(x.split('/')[-2].split('_')[1]) in range(56)]

    for file in my_files:
        if file.endswith('2.csv'):
            csvfiles.append(file)

    for file in csvfiles:
        with open(file, 'r') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if i==0:
                continue
            line = line.strip().split(';')
            try:
                line.remove('')
            except(ValueError):
                print('No space')
            if(len(line) < 7):
                os.rename(file[:file.rfind('/')+1]+str(i-1)+'_trim.wav', file[:file.rfind('/')+1]+str(i-1)+'_o.wav')
            else:
                truth = file.split('/')[-2].split('_')[-1]
                if line[6] == 'yes':
                    os.rename(file[:file.rfind('/')+1]+str(i-1)+'_trim.wav', file[:file.rfind('/')+1]+str(i-1)+'_'+truth+'_yes_trim.wav')
                elif line[6] == 'no':
                    os.rename(file[:file.rfind('/')+1]+str(i-1)+'_trim.wav', file[:file.rfind('/')+1]+str(i-1)+'_'+truth+'_no_trim.wav')
                else:
                    os.rename(file[:file.rfind('/')+1]+str(i-1)+'_trim.wav', file[:file.rfind('/')+1]+str(i-1)+'_o.wav')



def remove_added_features():
    rootdir = '../output'
    csvfiles = []
    my_files = []
    path = ''

    for subdir, dirs, files in os.walk(rootdir):
        my_files += [os.path.join(subdir, file) for file in files]

    for file in my_files:
        if file.endswith('_trim.wav') or file.endswith('_o.wav'):
            os.rename(file, file[:file.rfind('/')+2]+'_trim.wav')


answer, answer_test = [[], [], [], [], []], [[], [], [], [], []]
paths, paths_test = [[], [], [], [], []], [[], [], [], [], []]
config_file = 'IS09_emotion.conf '
# config_file = 'IS13_ComParE.conf '
# config_file = 'IS11_speaker_state.conf '
# config_file = 'ComParE_2016.conf '
def main_old(rootdir = '../output/tests/'):

    global answer, answer_test, paths, paths_test
    my_files = []
    for subdir, dirs, files in os.walk(rootdir):
        my_files += [os.path.join(subdir, file) for file in files if file.endswith('trim.wav')]


    for file in my_files:

        if int(file.split('/')[-2].split('_')[1]) in range(56, 66) or int(file.split('/')[-2].split('_')[1]) in range(46, 51):
            if splitfile[-2].split('_')[-1] == 't':
                answer_test.append(0)
                paths_test.append(file)
            elif splitfile[-2].split('_')[-1] == 'f':
                paths_test.append(file)
                answer_test.append(1)
            os.system('SMILExtract -C /home/tiziano/Desktop/Lie_Detector/opensmile-2.3.0/config/'+config_file+
                      '-I /home/tiziano/CLionProjects/Small_Project'+file[file.index('/'):]+' '
                      '-csvoutput /home/tiziano/CLionProjects/Small_Project/output/audio_features/Audio_Features_test.csv')
        else:
            if splitfile[-2].split('_')[-1] == 't':
                answer.append(0)
                paths.append(file)
            elif splitfile[-2].split('_')[-1] == 'f':
                answer.append(1)
                paths.append(file)
            os.system('SMILExtract -C /home/tiziano/Desktop/Lie_Detector/opensmile-2.3.0/config/'+config_file+
                  '-I /home/tiziano/CLionProjects/Small_Project'+file[file.index('/'):]+' '
                  '-csvoutput /home/tiziano/CLionProjects/Small_Project/output/audio_features/Audio_Features.csv')


    standardize()


def main(root='../output/tests/'):
    tests = os.listdir(root)

    for test in tests:
        wavs = os.listdir(root+test)
        with open(root+test+'/answertimes2.csv', 'r') as csvf:
            data = csvf.read()
        data = data.splitlines()[1:]
        for i, line in enumerate(data):
            if line.endswith(';'):
                data[i] = line[:-1]

        wavs = [x for x in wavs if x.endswith('trim.wav')]

        for wav in wavs:
            a = int(wav.split('_')[0]) + 1
            data_line = [x for x in data if a == int(x.split(';')[0])]
            if int(test.split('_')[1]) in range(56, 66) or int(test.split('_')[1]) in range(46, 51):
                os.system('SMILExtract -C /home/tiziano/Desktop/Lie_Detector/opensmile-2.3.0/config/' + config_file +
                          '-I /home/tiziano/CLionProjects/Small_Project' + root[root.index('/'):]+test+'/'+wav + ' '
                          '-csvoutput /home/tiziano/CLionProjects/Small_Project/output/audio_features/Audio_Features_test.csv')
                if data_line[0].split(';')[-1] == 'f':
                    answer_test.append(1)
                    paths_test.append(root+test+'/'+wav)
                else:
                    answer_test.append(0)
                    paths_test.append(root+test+'/'+wav)
            else:
                os.system('SMILExtract -C /home/tiziano/Desktop/Lie_Detector/opensmile-2.3.0/config/' + config_file +
                          '-I /home/tiziano/CLionProjects/Small_Project' +root[root.index('/'):]+'/'+test + '/' +wav+' '
                          '-csvoutput /home/tiziano/CLionProjects/Small_Project/output/audio_features/Audio_Features.csv')
                if data_line[0].split(';')[-1] == 'f':
                    answer.append(1)
                    paths.append(root + test + '/' + wav)
                else:
                    answer.append(0)
                    paths.append(root + test + '/' + wav)

    standardize()

def standardize():
    global answer, answer_test, paths, paths_test
    answer = answer[5:]
    paths = paths[5:]
    avg, std = standardize_results(add_yes_no('/home/tiziano/CLionProjects/Small_Project/output/audio_features/Audio_Features.csv', answer, paths))
    # with open('../output/audio_features_mean_std_.csv', 'w') as f:
    #     f.write(';'.join([str(x) for x in avg])+'\n')
    #     f.write(';'.join([str(x) for x in std])+'\n')
    # avg, std = standardize_results(add_yes_no('/home/tiziano/CLionProjects/Small_Project/output/audio_features/Audio_Features.csv', answer_test, paths_test))


def add_yes_no(inf, a, p):
    # data_t = np.loadtxt(inf, skiprows=1, usecols=range(2, 386), delimiter=';').tolist()
    data_t = np.loadtxt(inf, skiprows=1, dtype='str', delimiter=';')
    data_t = data_t[:, 2:]

    with open(inf[:inf.rfind('.')]+'_temp'+inf[inf.rfind('.'):], 'w+') as f:
        for i, line in enumerate(data_t):
            for feature in line:
                f.write('{},'.format(feature))
            f.write('{},{}\n'.format(a[i], p[i]))
    return inf[:inf.rfind('.')]+'_temp'+inf[inf.rfind('.'):]


def standardize_results(inf):
    with open(inf, 'r') as f:
        data = f.readlines()
    data = [x.strip() for x in data]
    data = [x.split(',') for x in data]
    paths_col = [x[-1] for x in data]
    data = [x[:-1] for x in data]
    data = np.array(data)
    data = data.astype(np.float)
    avg = np.average(data, axis=0)
    std = np.std(data, axis=0)

    with open(inf[:inf.rfind('.')]+'_standardized'+inf[inf.rfind('.'):], 'w+') as f:
        for i in range(len(data)):
            writeln = '{},'.format(paths_col[i])
            for j in range(len(data[0])):
                if j < len(data[0])-1:
                    if not std[j]==0:
                        writeln += '{},'.format((data[i][j]-avg[j])/std[j])
                    else:
                        writeln += '{},'.format(0.0)
                else:
                    writeln += str(data[i][j])+'\n'
            f.write(writeln)
    print('done')
    return avg, std

def main_with_db(test=None):
    global paths, paths_test, answer, answer_test

    answers = db.session.query(db.Answer).order_by(db.Answer.id).all()

    for a in answers:
        os.system('SMILExtract -C /home/tiziano/Desktop/Lie_Detector/opensmile-2.3.0/config/' + config_file +
                  '-I /home/tiziano/CLionProjects/Small_Project' + a.path_to_wav[a.path_to_wav.index('/'):] + ' ' +
                  '-csvoutput /home/tiziano/CLionProjects/Small_Project/output/audio_features/Audio_Features.csv')
        answer.append(1 if a.truth else 0)
        paths.append(a.path_to_wav)

    standardize()

def main_with_db_crossv(test=None):
    global paths, paths_test, answer, answer_test

    answers = db.session.query(db.Answer).order_by(db.Answer.id).all()
    # Giada: 8-15 +
    # Marina C.: 16-23 +
    # Marco: 25-32
    # Alice: 37-40
    # Luisa: 41-45
    # Marina M.: 46-50/65-75 +
    # Mariano: 51-55 +
    # Tiziano: 56-64
    # Ronald: 76-85 +
    # Younger guy: 86-93 +
    # Older guy: 93-101


    for a in answers:
        test_number = db.session.query(db.Test.number).filter(db.Test.id==a.test_id).first()[0]
        if 41<test_number<50 or 65<test_number<75:
            os.system('SMILExtract -C /home/tiziano/Desktop/Lie_Detector/opensmile-2.3.0/config/' + config_file +
                      '-I /home/tiziano/CLionProjects/Small_Project' + a.path_to_wav[a.path_to_wav.index('/'):] + ' ' +
                      '-csvoutput /home/tiziano/CLionProjects/Small_Project/output/audio_features/Audio_Features_group0.csv')
            answer_test[0].append(1 if a.truth else 0)
            paths_test[0].append(a.path_to_wav)
        elif 8<test_number<15 or 76<test_number<85:
            os.system('SMILExtract -C /home/tiziano/Desktop/Lie_Detector/opensmile-2.3.0/config/' + config_file +
                      '-I /home/tiziano/CLionProjects/Small_Project' + a.path_to_wav[a.path_to_wav.index('/'):] + ' ' +
                      '-csvoutput /home/tiziano/CLionProjects/Small_Project/output/audio_features/Audio_Features_group1.csv')
            answer_test[1].append(1 if a.truth else 0)
            paths_test[1].append(a.path_to_wav)
        elif 16<test_number<23 or 86<test_number<93:
            os.system('SMILExtract -C /home/tiziano/Desktop/Lie_Detector/opensmile-2.3.0/config/' + config_file +
                      '-I /home/tiziano/CLionProjects/Small_Project' + a.path_to_wav[a.path_to_wav.index('/'):] + ' ' +
                      '-csvoutput /home/tiziano/CLionProjects/Small_Project/output/audio_features/Audio_Features_group2.csv')
            answer_test[2].append(1 if a.truth else 0)
            paths_test[2].append(a.path_to_wav)
        elif 36<test_number<40 or 93<test_number<101:
            os.system('SMILExtract -C /home/tiziano/Desktop/Lie_Detector/opensmile-2.3.0/config/' + config_file +
                      '-I /home/tiziano/CLionProjects/Small_Project' + a.path_to_wav[a.path_to_wav.index('/'):] + ' ' +
                      '-csvoutput /home/tiziano/CLionProjects/Small_Project/output/audio_features/Audio_Features_group3.csv')
            answer_test[3].append(1 if a.truth else 0)
            paths_test[3].append(a.path_to_wav)
        else:
            os.system('SMILExtract -C /home/tiziano/Desktop/Lie_Detector/opensmile-2.3.0/config/' + config_file +
                      '-I /home/tiziano/CLionProjects/Small_Project' + a.path_to_wav[a.path_to_wav.index('/'):] + ' ' +
                      '-csvoutput /home/tiziano/CLionProjects/Small_Project/output/audio_features/Audio_Features_group4.csv')
            answer_test[4].append(1 if a.truth else 0)
            paths_test[4].append(a.path_to_wav)

    standardize_groups()

def standardize_groups():
    global answer, answer_test, paths, paths_test

    backup_data = np.loadtxt('../output/audio_features_mean_std_IS09.csv', delimiter=';')
    backup_data = backup_data.astype(np.float)
    for i in range(5):
        new_path = add_yes_no('/home/tiziano/CLionProjects/Small_Project/output/audio_features/Audio_Features_group'+str(i)+'.csv', answer_test[i], paths_test[i])
        data = np.loadtxt(new_path,  delimiter=',', dtype='str')
        paths = data[:, -1]
        data = data[:, :-1].astype(np.float)
        x_data = data[:, :-1]
        y_data = data[:, -1]
        for j in range(len(x_data[0])):
            x_data[:, j] = (x_data[:, j]-backup_data[0][j])/backup_data[1][j]
        with open('../output/audio_features/Audio_Features_group'+str(i)+'_std.csv', 'w') as f:
            for j in range(len(x_data)):
                f.write(';'.join([str(x) for x in x_data[j]])+';'+str(y_data[j])+'\n')



def extract_features(answers):
    for a in answers:
        os.system('SMILExtract -C /home/tiziano/Desktop/Lie_Detector/opensmile-2.3.0/config/' + config_file +
                  '-I /home/tiziano/CLionProjects/Small_Project/' + a + ' ' +
                  '-csvoutput /home/tiziano/CLionProjects/Small_Project/output/audio_features/temp_af.csv')

    data = np.loadtxt('../output/audio_features/temp_af.csv', dtype='str', delimiter=';', skiprows=1)
    data = data[:, 1:].astype(np.float)
    avg_std = np.loadtxt('../output/audio_features_mean_std_IS09.csv', delimiter=';')
    for i in range(len(data)):
        for j in range(len(data[0])):
            data[i][j] = (data[i][j]-avg_std[0][j])/avg_std[1][j]
    # This is only good for big training
    # data = preprocessing.scale(data)


    return data


if __name__ == '__main__':

    '''
    root = '../output/tests'
    tests = os.listdir(root)
    tests = [x for x in tests if int(x.split('/')[-1].split('_')[1]) in range(76, 102)]

    for test in tests:
        wavs_o = os.listdir(root+'/'+test)
        wavs_o = [x for x in wavs_o if x.endswith('o.wav')]

        for wav in wavs_o:
            os.rename(root+'/'+test+'/'+wav, root+'/'+test+'/'+wav.split('_')[0]+'_trim.wav')
    
    for test in tests:
        with open(root+'/'+test+'/answertimes2.csv', 'r') as inf:
            csvdata = inf.read()
        csvdata = csvdata.splitlines()
        startline = csvdata[0]+'Truth;'
        csvdata = [x+test.split('/')[-1].split('_')[-1]+';' for i, x in enumerate(csvdata) if i > 0]
        csvdata.insert(0, startline)
        hi = 1

        with open(root+'/'+test+'/answertimes2.csv', 'w') as outf:
            for i, line in enumerate(csvdata, 1):
                outf.write('{}\n'.format(line))
        #for i in range(1, 11):
    '''
    main_with_db()
    main_with_db_crossv()
    # avg, std = standardize_results(add_yes_no('/home/tiziano/CLionProjects/Small_Project/output/audio_features/Audio_Features_temp.csv')