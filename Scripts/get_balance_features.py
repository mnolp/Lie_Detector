import numpy as np
import os
import scipy
from scipy import spatial
from Scripts import PSQLDB_map as db


def get_all_tests():
    tests = db.session.query(db.Test).all()
    for test in tests:
        data = np.loadtxt(test.path_to_media + '/barycenter.txt', skiprows=1, delimiter=';', usecols=range(3))
    convert_to_bins(data)


def convert_to_bins(data):
    bins = np.zeros((2, 100,), dtype=np.int)
    for i in range(len(data)):

        bins[0][int(data[i][1] * 100)] += 1
        bins[1][int(data[i][2] * 100)] += 1
        print(bins)


def get_avg_std(data):
    return np.average(data[:, 0]), np.average(data[:, 1]), np.std(data[:, 0]), np.std(data[:, 1])


def oriented_points(data, eigvc):
    for i, d in enumerate(data):
        data[i] = np.linalg.solve(eigvc, d)

    return np.array(data)


def get_eigenvectors(data):
    cov = np.cov(data.T)
    eig_val, eig_vec = np.linalg.eig(cov)
    max_index = np.where(eig_val == max(eig_val))
    min_index = np.where(eig_val == min(eig_val))

    sorted_eigva = [eig_val[max_index],
                    eig_val[min_index]]


    return np.array([eig_vec[max_index][0],
                    eig_vec[min_index][0]])


def get_oriented_bbox(data, sorted_eigvc):

    bbox_measures = abs(max(data[:, 0]))-abs(min(data[:, 0])), abs(max(data[:, 1])-abs(min(data[:, 1])))

    return bbox_measures


def normalize(data):
    for i, d in enumerate(data):
        data[i] = [data[i][0]-np.nanmean(data[:, 0]), data[i][1]-np.nanmean(data[:, 1])]
    return data



def get_avg_point_distance(data):
    zero_distance = 0
    for i in range(1, len(data)):
        zero_distance += spatial.distance.euclidean(data[i], data[i-1])
    return zero_distance/len(data)

'''
def get_accel(data):
    for i in range(len(data)):
        if 0 < i < len(data):
            distance
'''

def get_local_minmaxima(data):
    count_max, count_min = 0, 0
    for i in range(2, len(data)-2):
        if data[i-1] < data[i] and data[i+1] < data[i] and data[i-2] < data[i] and data[i+2] < data[i]:
            count_max += 1
        if data[i-1] > data[i] and data[i+1] > data[i] and data[i-2] > data[i] and data[i+2] > data[i]:
            count_min += 1
    return count_max, count_min

def get_max_min(data):
    maxx = np.max(data[1])
    minx = np.min(data[1])
    maxy = np.max(data[2])
    miny = np.min(data[2])

    return maxx, minx, maxy, miny


def get_all_balancedata():
    arfffiles = []
    root = '../output/tests/'
    dirs = os.listdir(root)
    for dir in dirs:
        if int(dir.split('_')[1]) > 75:
            arfffiles += [root+dir+'/'+f for f in os.listdir(root+dir) if f == 'balancedata.txt']
    for f in arfffiles:
        print(f)
        barycenter_ratio(f)


def barycenter_ratio(file):
    my_data = np.loadtxt(file, skiprows=1, delimiter=';', usecols=[0, 2, 3, 4, 5])
    my_data = my_data.astype(np.float)

    outdata = np.zeros((len(my_data), 3,))
    for i in range(len(my_data)):
        outdata[i][0] = my_data[i][0]
        outdata[i][1] = (my_data[i][2]+my_data[i][4])/(my_data[i][2]+my_data[i][1]+my_data[i][4]+my_data[i][3])
        outdata[i][2] = (my_data[i][1]+my_data[i][2])/(my_data[i][2]+my_data[i][1]+my_data[i][4]+my_data[i][3])

    with open(file[:file.rfind('/')]+'/barycenter.txt', 'w+') as f:
        f.write('Time;X,Y;\n')
        for line in outdata:
            f.write('{};{};{};\n'.format(line[0], line[1], line[2]))


def main():
    tests = db.session.query(db.Test).order_by(db.Test.number).all()
    # tests = [db.session.query(db.Test).filter(db.Test.number==77).first()]
    for test in tests:
        print(test.path_to_media)
        data = np.loadtxt(test.path_to_media+'/barycenter.txt', usecols=range(3), skiprows=1, delimiter=';')
        data = np.delete(data, np.where(np.isnan(data[:, 1])), axis=0)
        times = data[:, 0]
        data = data[:, [1, 2]]

        answers = db.session.query(db.Answer).\
                             filter(db.Answer.test_id == test.id).\
                             order_by(db.Answer.number).\
                             all()

        with open(test.path_to_media+'/barycenter_features.csv', 'w') as outf:
            outf.write('Number;File;Max_X;Min_X;Max_Y;Min_Y;Avg_X;Avg_Y;Std_X;Std_Y;Main_eig_X;Main_eig_Y;Min_eig_X;Min_eig_Y;Avg_P_Dist;Elongation;X_Local_Max;X_Local_Min;Y_Local_Max;Y_Local_Min\n')

        for i in range(len(answers)):
            bound1 = np.where(times in np.arange(answers[i].time - 0.003, answers[i].time + 0.003, 0.001))
            if len(bound1) == 1:
                bound1 = np.where(times > answers[i].time)[0][0]
            if i < len(answers)-1:
                bound2 = np.where(times in np.arange(answers[i+1].time-0.003, answers[i+1].time+0.003, 0.001))
                if len(bound2) == 1:
                    bound2 = np.where(times > answers[i+1].time)[0][0]
                ans_data = data[bound1: bound2]

            else:
                ans_data = data[bound1:]

            #norm_data = normalize(ans_data)
            eigenvectors = get_eigenvectors(ans_data)
            final_data = oriented_points(ans_data, eigenvectors)
            maxx, minx, maxy, miny = get_max_min(final_data)
            avgx, avgy, stdx, stdy = get_avg_std(final_data)
            maineig, mineig = eigenvectors
            maineigx, maineigy = maineig
            mineigx, mineigy = mineig
            xmins, xmaxs = get_local_minmaxima(final_data[:,0])
            ymins, ymaxs = get_local_minmaxima(final_data[:,1])
            point_avg = get_avg_point_distance(final_data)

            with open(test.path_to_media+'/barycenter_features.csv', 'a+') as outf:
                outf.write('{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}\n'.format(i, answers[i].path_to_wav,
                                                                                  maxx, minx, maxy, miny,
                                                                                  avgx, avgy, stdx, stdy,
                                                                                  maineigx, maineigy, mineigx, mineigy,
                                                                                  point_avg, (maxx-minx)/(maxy-miny),
                                                                                  xmins, xmaxs, ymins, ymaxs))

def single_barycenter_ratio(file):
    my_data = np.loadtxt(file, skiprows=1, delimiter=';', usecols=[0, 2, 3, 4, 5])
    my_data = my_data.astype(np.float)

    outdata = np.zeros((len(my_data), 3,))

    for i in range(len(my_data)):
        outdata[i][0] = my_data[i][0]
        outdata[i][1] = (my_data[i][2]+my_data[i][4])/(my_data[i][2]+my_data[i][1]+my_data[i][1]+my_data[i][3])
        outdata[i][2] = (my_data[i][1]+my_data[i][2])/(my_data[i][2]+my_data[i][1]+my_data[i][1]+my_data[i][3])

    return outdata

def single_main(path):

    test = db.session.query(db.Test).filter(db.Test.path_to_media == path).first()
    data = single_barycenter_ratio(path+'/balancedata.txt')

    avg_std = np.loadtxt('../output/balance_backup.csv', skiprows=1, usecols=range(1, 13), delimiter=';')

    data = np.delete(data, np.where(np.isnan(data[:, 1])), axis=0)
    times = data[:, 0]
    data = data[:, [1, 2]]
    outdata = []

    answers = db.session.query(db.Answer). \
        filter(db.Answer.test_id == test.id). \
        order_by(db.Answer.number). \
        all()

    for i in range(len(answers)):
        bound1 = np.where(times in np.arange(answers[i].time - 0.003, answers[i].time + 0.003, 0.001))
        if len(bound1) == 1:
            bound1 = np.where(times > answers[i].time)[0][0]
        if i < len(answers)-1:
            bound2 = np.where(times in np.arange(answers[i+1].q_time-0.003, answers[i+1].q_time+0.003, 0.001))
            if len(bound2) == 1:
                bound2 = np.where(times > answers[i+1].time)[0][0]
            ans_data = data[bound1: bound2]

        else:
            ans_data = data[bound1:]

        norm_data = normalize(ans_data)
        eigenvectors = get_eigenvectors(norm_data)
        final_data = oriented_points(norm_data, eigenvectors)
        maxx, minx, maxy, miny = get_max_min(final_data)
        avgx, avgy, stdx, stdy = get_avg_std(final_data)
        maineig, mineig = eigenvectors
        maineigx, maineigy = maineig
        mineigx, mineigy = mineig
        point_avg = get_avg_point_distance(final_data)

        outdata.append(np.array([i, answers[i].path_to_wav,
                                 (maxx-avg_std[0][0])/avg_std[0][1],
                                 (minx-avg_std[1][0])/avg_std[1][1],
                                 (maxy-avg_std[2][0])/avg_std[2][1],
                                 (miny-avg_std[3][0])/avg_std[3][1],
                                 (avgx-avg_std[4][0])/avg_std[4][1],
                                 (avgy-avg_std[5][0])/avg_std[5][1],
                                 (stdx-avg_std[6][0])/avg_std[6][1],
                                 (stdy-avg_std[7][0])/avg_std[7][1],
                                 (maineigx-avg_std[8][0])/avg_std[8][1],
                                 (maineigy-avg_std[9][0])/avg_std[9][1],
                                 (mineigx-avg_std[10][0])/avg_std[10][1],
                                 (mineigy-avg_std[11][0])/avg_std[11][1],
                                 (point_avg-avg_std[12][0])/avg_std[12][1]]))

    return np.array(outdata)

def make_single_file():
    tests = db.session.query(db.Test).order_by(db.Test.number).all()

    outf = open('../output/balance_data/balance_features.csv', 'w')
    outf.write('Number;File;Max_X;Min_X;Max_Y;Min_Y;Avg_X;Avg_Y;Std_X;Std_Y;Main_eig_X;Main_eig_Y;Min_eig_X;Min_eig_Y;Avg_P_Dist;Elongation;X_Local_Max;X_Local_Min;Y_Local_Max;Y_Local_Min\n')
    outf_test = open('../output/balance_data/balance_features_test.csv', 'w')
    outf_test.write('Number;File;Max_X;Min_X;Max_Y;Min_Y;Avg_X;Avg_Y;Std_X;Std_Y;Main_eig_X;Main_eig_Y;Min_eig_X;Min_eig_Y;Avg_P_Dist;Elongation;X_Local_Max;X_Local_Min;Y_Local_Max;Y_Local_Min\n')
    i = 0
    for test in tests:
        with open(test.path_to_media+'/barycenter_features.csv', 'r') as csvf:
            data = csvf.read()
        data = data.splitlines()
        data = data[1:]
        data = [x.split(';')[1:] for x in data]

        if test.number in range(56, 66) or test.number in range(45, 51):
            where_to_write = outf_test
        else:
            where_to_write = outf

        for line in data:
            answer = db.session.query(db.Answer).filter(db.Answer.path_to_wav == line[0]).first()
            # if answer.word == 'yes':
            #     t = 1
            # elif answer.word == 'no':
            #     t = 0
            # else:
            #     t = -1
            t = 1 if answer.truth else 0
            where_to_write.write(str(i)+';'+';'.join(line)+';'+str(t)+'\n')
            i+=1

    outf.close()
    outf_test.close()


def standardize(inf='../output/balance_features_test.csv'):
    data = np.loadtxt(inf, skiprows=1, delimiter=';', usecols=range(2, 20))
    labels = data[:, -1]
    data = data[:, range(len(data[0])-1)]

    backupf = open('../output/balance_data/balance_backup.csv', 'w')
    backupf.write('Backup;Max_X;Min_X;Max_Y;Min_Y;Avg_X;Avg_Y;Std_X;Std_Y;Main_eig_X;Main_eig_Y;Min_eig_X;Min_eig_Y;Avg_P_Dist;Elongation;X_Local_Max;X_Local_Min;Y_Local_Max;Y_Local_Min\n')
    avg_out_str = 'Average;'
    std_out_str = 'Standard Deviation;'
    for i in range(len(data[0])):
        average = np.average(data[:, i])
        stdev = np.std(data[:, i])
        avg_out_str += str(average)+';'
        std_out_str += str(average)+';'

        for j in range(len(data)):
             (data[j][i]-average)/stdev

    backupf.write(avg_out_str[:-1]+'\n')
    backupf.write(std_out_str[:-1]+'\n')
    backupf.close()
    outf = open(inf[:inf.rfind('.')] + '_standardized' + inf[inf.rfind('.'):], 'w')

    for i in range(len(data)):
        temp = ';'.join([str(x) for x in data[i,:]]+[str(labels[i])])+'\n'
        outf.write(temp)
    outf.close()

def new_standardize():
    from sklearn import preprocessing
    data = np.loadtxt('../output/balance_data/balance_features.csv', delimiter=';', dtype='str', skiprows=1)
    label = data[:, -1:].astype(np.float)
    data = data[:, 2:-1].astype(np.float)
    data = preprocessing.scale(data)

    data = np.insert(data, len(data[0]),label.reshape(len(label)), axis=1)

    with open('../output/balance_data/balance_features_standardized.csv', 'w') as outf:
        for i, line in enumerate(data):
            outstr = ';'.join([str(x) for x in line])
            outf.write(outstr)
            outf.write('\n')

if __name__ == '__main__':
    # main()
    # make_single_file()
    new_standardize()

