import matplotlib.pyplot as plt
import numpy as np
import os

def plot():
    root = '/home/tiziano/CLionProjects/Small_Project/output'
    yesno1 = root+'/test_7/answertimes.csv'
    yesno2 = root+'/test_8_false/answertimes.csv'

    with open(yesno1, 'r') as f:
        lines1 = f.readlines()
    values1 = [x.strip().split(';') for x in lines1]
    answers1 = list()
    for x in values1:
        if x[3] != '_':
            answers1.append(x[3])
    answers1.remove('Answer')
    with open(yesno2, 'r') as f:
        lines2 = f.readlines()
    values2 = [x.strip().split(';') for x in lines1]
    answers2 = list()
    for x in values2:
        if x[3] != '_':
            answers2.append(x[3])
    answers2.remove('Answer')

    files1 = os.listdir(root+'/test_7/')
    csvs1 = []
    for file in files1:
        if file.endswith('.csv') and len(file) < 8:
            csvs1.append(file)
    csvs1.sort()

    files2 = os.listdir(root+'/test_8_false/')
    csvs2 = []
    for file in files2:
        if file.endswith('.csv') and len(file) < 8:
            csvs2.append(file)
    csvs2.sort()

    yess = []
    for i, yn in enumerate(answers1):
        if yn == 'yes':
            yess.append(root+'/test_7/'+csvs1[i])
    for i, yn in enumerate(answers2):
        if yn == 'yes':
            yess.append(root+'/test_7/'+csvs2[i])

    nos = []
    for i, yn in enumerate(answers1):
        if yn == 'no':
            nos.append(root+'/test_7/'+csvs1[i])
    for i, yn in enumerate(answers2):
        if yn == 'no':
            nos.append(root+'/test_7/'+csvs2[i])

    for i, file in enumerate(nos):
        if i > 2:
            break
        data = np.loadtxt(file, skiprows=1, usecols=range(1, 41), delimiter=';')
        x = data[:,0]
        y = data[:,8]
        #data_cols = [data[:,i] for i in range(40)]
        plt.plot(x, y)
    plt.show()

def get_features():
    rootdir = '../output'
    audiofiles = []
    my_files = []
    path = ''
    for subdir, dirs, files in os.walk(rootdir):
        my_files += [os.path.join(subdir, file) for file in files]

    for file in my_files:
        if file.endswith('.wav'):
            audiofiles.append(file[file.index('/'):])
    for i, file in enumerate(audiofiles):
        os.system('SMILExtract -C /home/tiziano/Desktop/Lie_Detector/opensmile-2.3.0/config/MFCC12_0_D_A.conf -I /home/tiziano/CLionProjects/Small_Project'+file+' -csvoutput /home/tiziano/CLionProjects/Small_Project'+file[:file.rfind('.')]+'.csv')


def main():
    #get_features()
    #plot()
    data1 = np.loadtxt('/home/tiziano/2_try.csv', skiprows=1, usecols=range(1, 41), delimiter=';')
    data2 = np.loadtxt('/home/tiziano/3_try.csv', skiprows=1, usecols=range(1, 41), delimiter=';')
    plt.plot(data1[: ,0], data1[: ,3])
    plt.plot(data2[: ,0], data2[: ,3])
    plt.show()

if __name__ == '__main__':
    main()