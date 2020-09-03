import numpy as np


def main2():
    data = np.loadtxt('../output/audio_features/Audio_Features.csv', usecols=range(1,385), skiprows=1, delimiter=';')

    metadata = np.loadtxt('../output/audio_features/Audio_Features_temp_standardized.csv', usecols=range(1, 386), delimiter=',')
    metadata = metadata[:, -1]

    data = np.delete(data, -2, 1)
    data = np.delete(data, -4, 1)

    outfdata = open('../output/audio_features/Single_group/Audio_Features.tsv', 'w')
    outfmeta = open('../output/audio_features/Single_group/Audio_Metadata.tsv', 'w')
    for i in range(len(data)):
        outfdata.write('\t'.join([str(x) for x in data[i]])+'\n')
        outfmeta.write(str(metadata[i])+'\t'+str(i)+'\n')

    outfdata.close()
    outfmeta.close()

def main():
    data = np.loadtxt('../output/audio_features/Audio_Features_temp_standardized.csv', skiprows=1, delimiter=',', dtype='str')

    metadata = data[:,-1].astype(np.float)
    data = data[:, 1:-1].astype(np.float)


    outfdata = open('../output/audio_features/audio_data.tsv', 'w')
    outfmeta = open('../output/audio_features/audio_metadata.tsv', 'w')
    outfnumber = open('../output/audio_features/audio_number.tsv', 'w')
    outfmeta.write('Class\tNumber\n')
    for i in range(len(data)):
        outfdata.write('\t'.join([str(x) for x in data[i]])+'\n')
        outfmeta.write(str(metadata[i])+'\t'+str(i)+'\n')

    outfdata.close()
    outfmeta.close()
    outfnumber.close()

if __name__ == '__main__':
    main()