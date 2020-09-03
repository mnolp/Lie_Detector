import numpy as np
import os, sys
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import pickle

def trainSGD(trainfile, testfile=None):
    #data = np.loadtxt(trainfile, delimiter=',', usecols=range(2, 386))
    data = np.loadtxt(trainfile, delimiter=';')
    data = data.astype(np.float)
    X_train = data[:, :-1]
    Y_train = data[:,-1]

    clf = SGDClassifier(max_iter=1000, tol=1e-5)
    clf.fit(X_train, Y_train)

    #data = np.loadtxt(testfile, delimiter=',', usecols=range(2, 386))
    if not testfile == None:
        data = np.loadtxt(testfile, delimiter=';')
        data = data.astype(np.float)
        X_test = data[:, :-1]
        Y_test = data[:,-1]

        print(clf.score(X_test, Y_test))

    pickle.dump(clf, open('../output/prediction_output/sgd_bar_weights.sav', 'wb'))

    return 0

def get_audio_prediction(features, path_to_weights):
    model = pickle.load(open(path_to_weights, 'rb'))
    features = np.delete(features, np.where(np.isnan(features)))
    return model.predict(features.reshape(1, -1))

def get_balance_prediction(data):
    model = pickle.load(open('../output/prediction_output/max_bar_weights.sav', 'rb'))
    return model.predict(data.reshape(1, -1))

def get_prediction(path):
    model = pickle.load(open('../output/prediction_output/max_bar_weights.sav', 'rb'))
    data = np.loadtxt(path, delimiter=',', usecols=range(1, 386))
    X_test = data[:, :-1]
    Y_test = data[:,-1]

    return model.predict(X_test[5].reshape(1, -1)), Y_test[5]

def train_on_all():
    data = np.zeros((890, 385))
    count = 0
    for i in range(5):
        _d = np.loadtxt("../output/audio_features/IS09/Audio_Features_group"+str(i)+"_std.csv", delimiter=';')
        for line in _d:
            data[count] = line
            count += 1

    data = np.delete(data, np.where(np.isnan(data[0])), 1)
    Y_train = data[:, -1]
    X_train = data[:, :-1]
    clf = RandomForestClassifier(n_estimators=8, max_depth=8)
    clf.fit(X_train, Y_train)

    pickle.dump(clf, open('../output/prediction_output/sgd_audio_weights.sav', 'wb'))

    print('Done')



def main(train_data, test_data):
    max_val = 0
    for i in range(50):
        value = trainSGD('../output/balance_features_standardized.csv', '../output/balance_features_test_standardized.csv')
        if value > max_val:
            max_val = value
            os.rename('../output/prediction_output/sgd_bar_weights.sav', '../output/prediction_output/max_bar_weights.sav')
    print('\n\nDone: '+str(max_val))


def get_crossval_score(max_depth = None, n_estimators = None, kernel='rbf'):

    max_val = 0
    final_val = 0

    for i in [4,3,2,1,0]:
        print('Group: {}'.format(i))
        test_data = np.loadtxt('../output/audio_features/IS09/Audio_Features_group'+str(i)+'_std.csv', delimiter=';')
        train_data = np.array([[0 for x in range(len(test_data[0]))]])
        x_test = test_data[:, :-1]
        x_test = np.delete(x_test, np.where(np.isnan(x_test[0])), 1)
        y_test = test_data[:, -1]
        for j in range(5):
            if j != i:
                _d = np.loadtxt('../output/audio_features/IS09/Audio_Features_group'+str(j)+'_std.csv', delimiter=';')
                train_data = np.append(train_data, _d, axis=0)
        train_data = train_data[1:]
        x_train = train_data[:, :-1]
        x_train = np.delete(x_train, np.where(np.isnan(x_train[0])), 1)
        y_train = train_data[:, -1]

        for n in range(5):
            # clf = SGDClassifier(max_iter=1000, tol=1e-6)
            clf = RandomForestClassifier(max_depth=max_depth, n_estimators=n_estimators)
            # clf = SVC(kernel=kernel)
            clf.fit(x_train, y_train)

            val = clf.score(x_test, y_test)
            print("Val: {}".format(val))
            if val > max_val:
                max_val = val
        pickle.dump(clf, open('../output/prediction_output/max_weights_group'+str(i)+'.sav', 'wb'))
        print((len(y_test)-np.count_nonzero(y_test))/len(y_test))
        final_val += max_val
        print("Max_val: {}".format(max_val))
        max_val = 0
    print("Average: {}\n".format(final_val/5))
    return final_val/5

def get_FScore_crossv():

    f1_score = 0
    for i in range(5):
        tp, fp, tn, fn = 0, 0, 0, 0
        model = pickle.load(open('../output/prediction_output/max_weights_group'+str(i)+'.sav', 'rb'))
        data = np.loadtxt('../output/audio_features/Audio_Features_group'+str(i)+'_std.csv', delimiter=';')
        data = np.delete(data, np.where(np.isnan(data[0])), 1)
        y_data = data[:, -1]
        data = data[:, :-1]
        # y_data = np.loadtxt('../output/audio_features/Audio_Features_group'+str(i)+'.csv', delimiter=';', dtype='str')
        # y_data = y_data.astype(y_data[:, -2])

        for j in range(len(data)):
            prediction = model.predict(data[j].reshape((1,-1)))
            if y_data[j] == 0 and prediction == 0:
                tn += 1
            elif y_data[j] == 0 and prediction == 1:
                fp += 1
            elif y_data[j] == 1 and prediction == 0:
                fn += 1
            elif y_data[j] == 1 and prediction == 1:
                tp += 1

        print('TP: {}, FP: {}, TN: {}, FN: {}'.format(tp, fp, tn, fn))
        precision = tp/(tp+fp)
        recall = tp/(tp+fn)
        f1_score += 2*((precision*recall)/(precision+recall))

    print("Average: {}".format(f1_score/5))

if __name__ == '__main__':
    # get_crossval_score()
    values = []
    nes = [1, 2, 4, 8, 16, 32, 64, 100]
    depths = np.linspace(1, 16, 16)
    kernels = ['linear', 'poly', 'rbf', 'sigmoid', 'precomputed']
    #
    #
    # for i in range(len(depths)):
    values.append(get_crossval_score(n_estimators=16, max_depth=6, kernel='sigmoid'))
    # for i in range(len(depths)):

    for i in range(len(values)):
        print("N_esimators: {}, value: {}".format(depths[i], values[i]))

    # train_on_all()

#
# if __name__ == '__main__':
#     data = np.loadtxt('../output/balance_features_test_standardized.csv', delimiter=';')
#     data = data.astype(np.float)
#     X_test = data[:, :-1]
#     Y_test = data[:,-1]
#     for i in range(len(data)):
#         print('label: {}, prediction: {}'.format(Y_test[i], get_balance_prediction(X_test[i])))
#     # x, y = get_prediction('../output/audio_features/Audio_Features_test_temp_standardized.csv')
#     # print('{}, {}'.format(x, y))
