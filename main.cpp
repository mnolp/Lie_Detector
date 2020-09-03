#include <iostream>
#include <unistd.h>
#include <string>
#include <dirent.h>
#include "wiicpp.h"
#include <chrono>
#include <SFML/Graphics.hpp>
#include <SFML/Audio.hpp>
#include <algorithm>
#include <experimental/filesystem>
#include <Python.h>

namespace fs = experimental::filesystem;
using namespace std;
using namespace sf;

// Main functions
int AppModeCheck();
int GatherData(bool);
// Change this function if want to predict a specific test
int GetPrediction(char*);

string pickNextQuestion();

// Functions to set new folder to store data
void setNewTest();
void setTempTest();
string createStorageFolder();

// Functions to print on window
string printIntro();
string printHelp(bool);

// Functions for managing balance board
void BBRead(double, const string&);
void BBInit();
void DisconnectDevices(vector<CWiimote>);

// Function that converts from weight values of the four sensors to barycenter coordinates
int convertToXY(string);

// Outdated funcion. See below for explanation
int ReadBBData();

CWii scanner = CWii();
vector<CWiimote> wm;

string pathToWorkingDirectory, pathToStorageFolder;
static int mySample = 0, questionNumber = 1;
// Files where gathered data will be stored.
ofstream myBalanceOutF, myAnswerOutF;
// change this numbers to change number of questions per group
int qCup1=0, qCup2=0, qCup3=0, qRand=0, qNF=0;
vector<string> asked;
bool flag = false, connectedFlag = false, startReadingFlag = false, printFlag = true;
Font font;
Text text;


int main(int argc, char* argv[]) {
    AppModeCheck();
}

int AppModeCheck(){
    bool mode = true;

    RenderWindow check(VideoMode(1024, 768, 32), "Tool Mode Check");

//      Handling text for window
    font.loadFromFile("/usr/share/fonts/truetype/roboto/hinted/Roboto-Regular.ttf");
    text.setFillColor(Color::White);
    text.setFont(font);
    text.setCharacterSize(40);
    text.setString(printIntro());

// First window loop for event detection
    while (check.isOpen()){
        Event e;
        while(check.pollEvent(e)){
            switch(e.type){
                case Event::Closed:
                    check.close();
                    break;
                case Event::KeyPressed:
                    if (e.key.code == Keyboard::Q){
                        check.close();
                        break;
                    } else if (e.key.code == Keyboard::G){
                        check.close();
                        mode = false;
                        break;
                    } else if (e.key.code == Keyboard::P){
                        check.close();
                        mode = true;
                        break;
                    }
            }

        }
        check.clear();
        check.draw(text);
        check.display();
    }

// Call to main function with selected modality
// False: data gathering mode
// True: prediction mode
    GatherData(mode);
    return 0;
}


// Function to call python scripts and get prediction based on audio
int GetPrediction(char* test){
    char *myFile = "../predict_cup.py";
    if(FILE* pF = fopen(myFile, "r")) {

        int argc = 2;
        wchar_t *argv[argc];
        argv[0] = Py_DecodeLocale(myFile, nullptr);
        argv[1] = Py_DecodeLocale(test, nullptr);
        Py_Initialize();
        PyRun_SimpleString("import os\nimport sys\nos.chdir('../Scripts/')");
        PyRun_SimpleString("sys.path.insert(0, '/home/tiziano/CLionProjects/Small_Project/')");
        PyRun_SimpleString("sys.path.insert(0, '/home/tiziano/CLionProjects/Small_Project/venv/lib/python3.6/site-packages')");
        PyRun_SimpleString("print('Current working directory: {}'.format(os.getcwd()))");

        PySys_SetArgv(argc, argv);
        PyRun_SimpleFile(pF, "predict_cup.py");

        Py_Finalize();
        free(pF);
    } else{
        cerr << "InputError: " << myFile << ". No such file" << endl;
    }

    ifstream instream("predicted_cup.txt");
    int a;
    instream >> a;

    return a;
}

// Function containing main loop
int GatherData(bool predicting){
        //      Setting working directory path
    char path[PATH_MAX];
    getcwd(path, sizeof(path));
    string temp = path;
    string word = "";
    bool lieOrTruth = false;
    float qTime, aTime;
    pathToWorkingDirectory = temp;//.substr(0, temp.find_last_of('/'));

//     SFML window
    RenderWindow window(VideoMode(1024, 768, 32), "Data Gathering Tool");

//      Handling audio buffers
    if(!SoundBufferRecorder::isAvailable())
        cout << "Please install a mic" << endl;
    SoundBufferRecorder recorder;
    SoundBuffer buffer, buffer2;
    Sound sound, sound2;
    vector<string> availableDevices = SoundRecorder::getAvailableDevices();
    recorder.setDevice(availableDevices[0]);
    string qPath;


//      Print help on console and set new test environment
    if (predicting){
        setTempTest();
    }else{
        setNewTest();
    }
    text.setString(printHelp(predicting));


//      Setting starting time
    auto start = chrono::high_resolution_clock::now();
    auto finish = chrono::high_resolution_clock::now();
    chrono::duration<double> elapsed = finish - start;
    int lastCheck = -1;

    bool questionSavedFlag = false, wordFlag = true, truthFlag = true;

//      Main loop
    while(window.isOpen()){
        Event event;
        finish = chrono::high_resolution_clock::now();
        elapsed = finish - start;

        while(window.pollEvent(event)){
            switch(event.type) {
                case Event::Closed:
                    window.close();
                    break;

                case Event::KeyPressed:
                    if (event.key.code == Keyboard::P) {
                        BBInit();
                        connectedFlag = true;
                    } else if (event.key.code == Keyboard::S) {
                        if (flag){
                            recorder.stop();
                            buffer = recorder.getBuffer();
                            buffer.saveToFile(pathToStorageFolder + "/" + to_string(mySample++) + ".wav");
                            cout << "Recording saved" << endl << endl;

                            flag = false;
                            questionSavedFlag = true;
                        } else {
                            cout << "No running registration to stop. Ask new question with \"c\"" << endl << endl;
                        }
                    } else if (event.key.code == Keyboard::Y){
                        if (questionSavedFlag && questionNumber<12){
                            cout << "Last answer was marked as \"yes\"" << endl << endl;
                            word = "yes";
                            wordFlag = true;
                        } else {
                            cout << "No question was saved. First register a question with \"S\"" << endl << endl;
                        }
                    } else if (event.key.code == Keyboard::N){
                        if (questionSavedFlag && questionNumber<12){
                            cout << "Last answer was marked as \"no\"" << endl << endl;
                            word = "no";
                            wordFlag = true;
                        } else {
                            cout << "No question was saved. First register a question with \"S\"" << endl << endl;
                        }
                    } else if (event.key.code == Keyboard::T){
                        if (questionSavedFlag && questionNumber<12){
                            cout << "Last answer was marked as \"true\"" << endl << endl;
                            lieOrTruth = true;
                            truthFlag = true;
                        } else {
                            cout << "No question was saved. First register a question with \"S\"" << endl;
                        }
                    } else if (event.key.code == Keyboard::F){
                        if (questionSavedFlag && questionNumber<12){
                            cout << "Last answer was marked as \"false\"" << endl << endl;
                            lieOrTruth = false;
                            truthFlag = true;
                        } else {
                            cout << "No question was saved. First register a question with \"S\"" << endl;
                        }
                    } else if (event.key.code == Keyboard::C) {
                        //  Check if Balance board is connected

//                              Checking if last recording has been correctly stored
                        if (flag) {
                            cout << "Not possible to reproduce next question!" << endl;
                            cout << "First save last registration with \"S\"." << endl;
                        } else if (!truthFlag && questionNumber>11) {
                            cout << "Not possible to reproduce next question!" << endl;
                            cout << "First assign a value to \"truth\" with \"T\" or \"F\"" << endl << endl;
                        } else if (!wordFlag && questionNumber>11) {
                            cout << "Not possible to reproduce next question!" << endl;
                            cout << "First assign a value to \"word\" with \"Y\" or \"N\"" << endl << endl;
                        } else {
                            wordFlag = false;
                            truthFlag = false;
                            questionSavedFlag = false;
                            if (questionNumber > 10) {
                                if (questionNumber == 11) {
                                    cout << "Experiment finished!\nSetting up for new test" << endl << endl;
                                    questionNumber++;
                                    convertToXY(pathToStorageFolder+"/balancedata.txt");
                                    myAnswerOutF.close();
                                    if (predicting){
                                        cout << GetPrediction("output/temp_test") << endl;
                                        system(("rm -rf "+pathToStorageFolder).c_str());
                                    }
                                    continue;
                                } else {
                                    if (predicting){
                                        setTempTest();
                                    }else{
                                        setNewTest();
                                    }
                                    printFlag = true;
                                    startReadingFlag = false;
                                    continue;
                                }
                            } else {
                                //                              Next question and save timestamp on file
                                qPath = pickNextQuestion();
                                buffer2.loadFromFile(qPath);
                                sound2.setBuffer(buffer2);
                                finish = chrono::high_resolution_clock::now();
                                elapsed = finish - start;
                                qTime = elapsed.count();
                                cout << "Question number: " << questionNumber << endl;
                                sound2.play();
                                recorder.start();

                                //                              Start recording and save timestamp on file
                                finish = chrono::high_resolution_clock::now();
                                elapsed = finish - start;
                                aTime = elapsed.count();
                                cout << "Starting audio record..." << endl;
                                flag = true;
                                questionNumber++;
                                myAnswerOutF << questionNumber - 1 << ";" << qPath << ";" << qTime
                                             << ";" << aTime << ";" << word << ";" << lieOrTruth << ";" << endl;
                            }
                        }

                    } else if (event.key.code == Keyboard::R){
                        //  Only works if a question has been asked.
                        //  The recording is stopped and not saved.
                        //  The last answer is repeated
                        if (flag){
                            recorder.stop();
                            buffer = recorder.getBuffer();
                            recorder.start();
                            finish = chrono::high_resolution_clock::now();
                            elapsed = finish - start;
                            qTime = elapsed.count();
                            sound2.play();
                            cout << "Repeating question" << endl;
                            while(sound2.getStatus() == Sound::Playing){
                                BBRead(elapsed.count(), pathToStorageFolder);
                            }
                            finish = chrono::high_resolution_clock::now();
                            elapsed = finish - start;
                            aTime = elapsed.count();
                        }
                    } else if (event.key.code == Keyboard::Q) {
                        if (predicting){
                            system(("rm -rf "+pathToStorageFolder).c_str());
                        }
                        convertToXY(pathToStorageFolder+"/balancedata.txt");
                        window.close();
                        break;
                    }
            }
        }
//          Start reading data from balance board
        if (startReadingFlag){
            if (printFlag) {
                cout << "Start reading from Balance Board" << endl;
                printFlag = false;
            }
            if ((int) (elapsed.count() * 1000) != lastCheck && (int) (elapsed.count() * 1000) % 2 == 0) {
                BBRead(elapsed.count(), pathToStorageFolder);
            }
        }
        lastCheck = (int)(elapsed.count()*1000);

        window.clear();
        window.draw(text);
        window.display();
    }
    myAnswerOutF.close();
    return 0;
}

void setTempTest(){
    pathToStorageFolder = pathToWorkingDirectory+"/output/temp_test";
    if (DIR *dir = opendir((pathToStorageFolder).c_str())){
        system(("rm -rf "+pathToStorageFolder).c_str());
    }

//    Open in temp storage new file to store balance data
    system(("mkdir "+pathToStorageFolder).c_str());

//    Commented for prediction mode because balance is not giving good results
//    myBalanceOutF.open(pathToStorageFolder+"/balancedata.txt");
//    myBalanceOutF << "Time;Total;Top Left; Top Right;Bottom Left;Bottom Right;" << endl;
//    myBalanceOutF.close();
//
    myAnswerOutF.open(pathToStorageFolder+"/answertimes.csv");
    myAnswerOutF << "QuestionNumber;Path;QuestionTime;AnswerTime;Word;Truth;" << endl;
    questionNumber = 1;
    mySample = 0;
    qCup1 = 0;
    qCup2 = 0;
    qCup3 = 0;
    qRand = 0;
    qNF = 0;
    asked.clear();
    printFlag = true;

}

void setNewTest(){
// Random answer generator for data gathering mode. Uncomment to use
//    if (questionNumber > 10) {
//        srand(time(nullptr));
//        int randNumber = rand() % 100 % 3;
//        SoundBuffer buffer;
//        Sound sound;
//        buffer.loadFromFile(pathToWorkingDirectory + "/Questions/guess" + to_string(randNumber+1));
//        sound.setBuffer(buffer);
//        sound.play();
//        while (sound.getStatus() == Sound::Playing) {}
//    }


    //  Creating output storage folder
    pathToStorageFolder = createStorageFolder();
    //      Opening csv output file for balance data
    myBalanceOutF.open(pathToStorageFolder+"/balancedata.txt");
    myBalanceOutF << "Time;Total;Top Left; Top Right;Bottom Left;Bottom Right;" << endl;
    myBalanceOutF.close();
    //      Opening csv output file to mark answer times
    myAnswerOutF.open(pathToStorageFolder+"/answertimes.csv");
    myAnswerOutF << "QuestionNumber;Path;QuestionTime;AnswerTime;Word;Truth;" << endl;

// Setting values back to start for the new test
    questionNumber = 1;
    mySample = 0;
    qCup1 = 0;
    qCup2 = 0;
    qCup3 = 0;
    qRand = 0;
    qNF = 0;
    asked.clear();
    startReadingFlag = false;
    printFlag = true;
}


string createStorageFolder(){
    string command = pathToWorkingDirectory+"/output/test_1";
    DIR* dir = opendir(command.c_str());
    while(dir){
        command = command.substr(0, command.find_last_of('_')+1)+to_string((stoi(command.substr(command.find_last_of('_')+1))+1));
        dir = opendir(command.c_str());
    }
    closedir(dir);
    system(("mkdir "+command).c_str());
    return command;
}


void DisconnectDevices(vector<CWiimote> wm){
    //  Closing connection with devices and ending program
    cout << "Disconnecting devices..." << endl;
    for (auto i=0; i<wm.size(); i++) {
        wm[i].Disconnect();
        cout << "Succesfully disconnected device " << i << endl;
    }
}

void BBInit() {
    cout << "Searching for devices (3s)..." << endl;
    wm = scanner.FindAndConnect(3);

    if (scanner.GetNumConnectedWiimotes() == 0){
        cout << "No devices found ending process." << endl;
        return;
    }

    wm[0].SetLEDs(WIIMOTE_LED_1);

//    Loop to set up correctly the balance board expansion
    auto start = chrono::high_resolution_clock::now();
    auto finish = chrono::high_resolution_clock::now();
    chrono::duration<double> elapsed = finish - start;
    cout << "Setting expansion device..." << endl;
    while(wm[0].ExpansionDevice.GetType() == 0){
        finish = chrono::high_resolution_clock::now();
        elapsed = finish - start;
        scanner.Poll();

        if(elapsed.count() > 10){
            cout << "No expansion device found.\nPlease connect a Balance Board\nEnding program" << endl;
            break;
        }
    }
    cout << "Expansion ok" << endl;
}

void BBRead(double elapsed, const string& pathToOutput) {
    CBalanceBoard myBalanceBoard = CBalanceBoard(wm[0].ExpansionDevice.BalanceBoard);
//      Opening out file
    ofstream myOutF;
    myOutF.open(pathToOutput+"/balancedata.txt", ios_base::app);

//      Reading data from the device
    float top_left = -1, top_right = -1, bottom_left = -1, bottom_right = -1, total_weight = -1;
    scanner.Poll();
    myBalanceBoard.WeightSensor.GetWeight(total_weight, top_left, top_right, bottom_left,
                                          bottom_right);
    myOutF << elapsed << ";" << total_weight << ";" << top_left << ";" << top_right << ";" << bottom_left << ";"
           << bottom_right << ";" << endl;

    myOutF.close();
}

string pickNextQuestion(){
    string dirs[5] = {"/Cup1", "/Cup2", "/Cup3", "/Random", "/NotFirst"};
    string theQuestion = "prova";
    int firstQ = questionNumber > 1 ? 5 : 4;

    int randomNumber;
    bool rnset = false;
    vector<string> questions;
    while (!rnset) {
        srand(time(nullptr));
        randomNumber = rand()%100%firstQ;
        if(qCup1 < 0 || qCup2 < 0 || qCup3 < 0 || qRand < 0 || qNF < 0){
            cout << "hello" << endl;
        }
        switch (randomNumber) {
            case 0:
                if (qCup1 > 1) {
                    continue;
                }
                qCup1++;
                for (const auto & entry : fs::directory_iterator(pathToWorkingDirectory+"/Questions"+dirs[randomNumber])){
                    questions.push_back(entry.path());
                }
                rnset = true;
                break;
            case 1:
                if (qCup2 > 1) {
                    continue;
                }
                qCup2++;
                for (const auto & entry : fs::directory_iterator(pathToWorkingDirectory+"/Questions"+dirs[randomNumber])){
                    questions.push_back(entry.path());
                }
                rnset = true;
                break;
            case 2:
                if (qCup3 > 1) {
                    continue;
                }
                qCup3++;
                for (const auto & entry : fs::directory_iterator(pathToWorkingDirectory+"/Questions"+dirs[randomNumber])){
                    questions.push_back(entry.path());
                }
                rnset = true;
                break;
            case 3:
                if (qRand > 1) {
                    continue;
                }
                qRand++;
                for (const auto & entry : fs::directory_iterator(pathToWorkingDirectory+"/Questions"+dirs[randomNumber])){
                    questions.push_back(entry.path());
                }
                rnset = true;
                break;
            case 4:
                if ((qNF + qRand) > 3) {
                    continue;
                }
                qNF++;
                for (const auto & entry : fs::directory_iterator(pathToWorkingDirectory+"/Questions"+dirs[randomNumber])){
                    if(!(find(questions.begin(), questions.end(), entry.path()) != questions.end()))
                        questions.push_back(entry.path());
                }
                rnset = true;
                break;
        }
    }

    int randomNumber2 = rand()%100;
    if(questionNumber>2) {
        while (find(asked.begin(), asked.end(), questions[randomNumber2 % questions.size()]) != asked.end()) {
            srand(time(nullptr));
            randomNumber2 = rand() % 100;
        }
    }else if (questionNumber==2){
        while (asked[0].compare(questions[randomNumber2%questions.size()]) == 0){
            srand(time(nullptr));
            randomNumber2 = rand() % 100;
        }
    }
    theQuestion = questions[randomNumber2%questions.size()];
    asked.push_back(theQuestion);

    return theQuestion;
}

int convertToXY(string filePath){
    ofstream myOutFile;
    string outTest = filePath.substr(filePath.find("put/")+4, filePath.find("/bal"));
    myOutFile.open(pathToStorageFolder+"/barycenter.txt");
    myOutFile << "X;Y;" << endl;

    string line;
    stringstream ss;
    double temp, x, y;
    vector<double> data;
    bool flag = true;
    ifstream myInFile(filePath);

    if (myInFile.is_open()){
        while (getline (myInFile,line))
        {
            data.clear();
            if (flag){
                flag = false;
                continue;
            }
            ss = stringstream(line);
            replace(line.begin(), line.end(), ';', ' ');
            while (ss >> temp){
                data.push_back(temp);
            }

            x = (data[2]+data[3])-(data[4]+data[5]);
            y = (data[2]+data[4])-(data[3]+data[5]);
            myOutFile << x << ";" << y << ";" << endl;
        }
        myInFile.close();
    }else{
        cout << "No file named \"" << filePath << "\" found" << endl;
        return -5;
    }
    myOutFile.close();
    return 0;
}

string printHelp(bool predicting){
    cout << "*************************************************" << endl;
    cout << "-\tWelcome to the data gathering tool!" << endl;
    cout << "-\tYou can perform these actions:" << endl;
    cout << "-\tP: peer the system to the balance board." << endl;
    cout << "-\tS: Save last registered answer." << endl;
    cout << "-\tC: next question and record new answer." << endl;
    cout << "-\tT: mark last answer as true" << endl;
    cout << "-\tF: mark last answer as false" << endl;
    cout << "-\tY: mark last answer as yes" << endl;
    cout << "-\tN: mark last answer as no" << endl;
    cout << "-\tR: repeat last question." << endl;
    cout << "-\tQ: quit" << endl;
    cout << "*************************************************" << endl;

    stringstream s;
    s << "*************************************************" << endl;
    if (predicting) {
        s << "-\tTest Prediction Mode" << endl;
    }else{
        s << "-\tData Gathering Mode" << endl;
    }
    s << "*************************************************" << endl;
    s << "-\tThe following actions can be performed:" << endl;
    s << "-\tP: peer the system to the balance board." << endl;
    s << "-\tS: Save last registered answer." << endl;
    s << "-\tC: next question and record new answer." << endl;
    s << "-\tT: mark last answer as true" << endl;
    s << "-\tF: mark last answer as false" << endl;
    s << "-\tY: mark last answer as yes" << endl;
    s << "-\tN: mark last answer as no" << endl;
    s << "-\tR: repeat last question." << endl;
    s << "-\tQ: quit" << endl;
    s << "*************************************************" << endl;

    return s.str();
}

string printIntro(){
    stringstream s;
    s << "*************************************************" << endl;
    s << "Press G for data gathering mode" << endl;
    s << "Press P for prediction mode" << endl;
    s << "*************************************************" << endl;

    return s.str();
}


// Outdated function.
// Calling this function will set up and read data from a balance board.
// Above functions split this in initialization and reading from device
int ReadBBData() {
//    Instantiation of "Wii device". Scann for WiiMotes and connect to found
    CWii scanner = CWii();
    vector<CWiimote> wm = scanner.FindAndConnect(3);
    if (scanner.GetNumConnectedWiimotes() == 0){
        cout << "No devices found ending process." << endl;
        return -1;
    }

    wm[0].SetLEDs(WIIMOTE_LED_1);

//    Loop to set up correctly the balance board expansion
    auto start = chrono::high_resolution_clock::now();
    auto finish = chrono::high_resolution_clock::now();
    chrono::duration<double> elapsed = finish - start;
    cout << "Setting expansion device..." << endl;
    while(wm[0].ExpansionDevice.GetType() == 0){
        finish = chrono::high_resolution_clock::now();
        elapsed = finish - start;
        scanner.Poll();

        if(elapsed.count() < 10){
            cout << "No expansion device found.\nPlease connect a Balance Board\nEnding program" << endl;
            break;
        }
    }
    cout << "Expansion ok" << endl;

//    Check if the found devices have  expansions and in case check which one they have
    for (auto & i : wm) {
        if (i.isUsingEXP()) {
            switch (i.ExpansionDevice.GetType()) {
                case 0:
                    cout << "No expansion device found" << endl;
                    return -2;
                case 1:
                    cout << "Nunchuck set" << endl;
                    cout << "Not what this program works with" << endl;
                    return -2;
                case 2:
                    cout << "Classic controller set" << endl;
                    cout << "Not what this program works with" << endl;
                    return -2;
                case 3:
                    cout << "Guitar Hero controller set" << endl;
                    cout << "Not what this program works with" << endl;
                    return -2;
                case 4:
                    cout << "Motion Plus set" << endl;
                    cout << "Not what this program works with" << endl;
                    return -2;
                case 5:
                    cout << "Balance board set" << endl;
                    CBalanceBoard bb = CBalanceBoard(i.ExpansionDevice.BalanceBoard);
                    cout << "Created BB correctly" << endl;

//                    Opening out file
                    ofstream myOutF;
                    myOutF.open("../output/rawData.csv");
                    myOutF << "Time;Total;Top Left; Top Right;Bottom Left;Bottom Right;" << endl;

//                    Setting start time
                    start = chrono::high_resolution_clock::now();
                    finish = chrono::high_resolution_clock::now();
                    elapsed = finish - start;
                    int last_check = -1;

//                    Reading data from the device
                    float top_left = -1, top_right = -1, bottom_left = -1, bottom_right = -1, total_weight = -1;

                    CBalanceBoard myBalanceBoard = CBalanceBoard(i.ExpansionDevice.BalanceBoard);
                    cout << "Reading from device..." << endl;
                    while (elapsed.count() < 60) {
                        scanner.Poll();
                        finish = chrono::high_resolution_clock::now();
                        elapsed = finish - start;

                        myBalanceBoard.WeightSensor.GetWeight(total_weight, top_left, top_right, bottom_left,
                                                              bottom_right);

                        if ((int) (elapsed.count() * 10) % 2 == 0 && (int) (elapsed.count() * 10) != last_check) {
                            cout << "***********************" << endl;
                            cout << "Time: " << (int) elapsed.count() << endl;
                            cout << "Total weight:\t" << total_weight << endl;
                            cout << "Top Left:\t\t" << top_left << endl;
                            cout << "Top Right:\t\t" << top_right << endl;
                            cout << "Bottom Left:\t" << bottom_left << endl;
                            cout << "Bottom Right:\t" << bottom_right << endl << endl;
                            myOutF << elapsed.count() << ";" << total_weight << ";" << top_left << ";" << top_right << ";" << bottom_left << ";"
                                   << bottom_right << ";" << endl;
                        }
                        last_check = (int) (elapsed.count() * 10);

                    }
                    myOutF.close();
                    cout << "Done reading";
            }
        }
    }

    DisconnectDevices(wm);
    return 0;
}
