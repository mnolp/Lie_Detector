import os
import io

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from pydub import AudioSegment


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
        enable_word_time_offsets = True,
        language_code='en-US',
        speech_contexts=[speech.types.SpeechContext(phrases=["yes", "no"],)],)

    # Detects speech in the audio file
    response = client.recognize(config, audio)
    '''
    for result in response.results[0].alternatives[0].words:
        print('Transcript: {}\nStart TIme: {}.{}\nEnd Time: {}.{}'.format(result.word, result.start_time.seconds, result.start_time.nanos, result.end_time.seconds, result.end_time.nanos))
    '''
    ret = response.results[0].alternatives[0].words if len(response.results) > 0 else None
    return ret

def call_to_google(root='../output/tests/'):
    csvpath = '/answertimes.csv'
    dirs = os.listdir(root)
    dirs = [x for x in dirs if int(x.split('/')[-1].split('_')[1]) in range(56)]
    for dir in dirs:
        files = os.listdir(root+dir)
        wavs = [root+dir+'/'+x for x in files if x.endswith('.wav') and not x.endswith('_trim.wav')]
        wavs.sort()
        timestamps = []

        with open(root+dir+csvpath, 'r+') as f:
            lines = f.readlines()
        features = [x.strip().split(';') for x in lines]
        for i, x in enumerate(features):
            x.remove('')
            features[i] = x
        anst = []
        for i in range(1, len(features)):
            anst.append(float(features[i][3])-float(features[i][2]))

        for i, wavf in enumerate(wavs):
            print(wavf)
            song = AudioSegment.from_wav(wavf)
            song1 = song[anst[i]*1000-100:]
            song1.export(wavf[:wavf.rfind('.')]+"_trim"+wavf[wavf.rfind('.'):], format="wav")
            timestamps.append(get_timestamps(wavf[:wavf.rfind('.')]+"_trim"+wavf[wavf.rfind('.'):]))

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
                features[i] += ['null', 'null']
            j+=1
        with open(root+dir+'/answertimes2.csv', 'w+') as f:
            for line in features:
                for feature in line:
                    f.write("{};".format(feature))
                f.write('\n')
        print(root+dir)

if __name__ == '__main__':
    import sys
    call_to_google()