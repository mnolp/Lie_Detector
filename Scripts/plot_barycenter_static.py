import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
import tkinter as tk
from tkinter import ttk
from scipy.signal import medfilt
import os

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

#infile = '../output/test_30/bar'

root = tk.Tk()
root.wm_title("Embedding in Tk")

frame = tk.Frame(master=root, relief=tk.RAISED, borderwidth=1)
frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=frame)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

ani = 0
running = True

counter = 0
test_path = ''

data = np.loadtxt('../output/tests/test_8_t/barycenter.txt', skiprows=1, delimiter=';', usecols=range(3))
question_times = np.loadtxt('../output/tests/test_8_t/answertimes.csv', skiprows=1, usecols=[3], delimiter=';')
t = data[:, 0]
x = data[:, 1]
y = data[:, 2]
#t = t.tolist()
#x = [(my_x-np.average(x))/np.max(np.absolute(x)) for my_x in x]
#y = [(my_y-np.average(y))/np.max(np.absolute(y)) for my_y in y]

new_x = medfilt(x, 305)
new_y = medfilt(y, 305)

ax1.plot(new_x, new_y, 'b-')

def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
    # Fatal Python Error: PyEval_RestoreThread: NULL tstate


def on_key_press(event):
    print("you pressed {}".format(event.key))
    if event.key=='q':
        _quit()
    key_press_handler(event, canvas, toolbar)

def on_combobox_question_select(event):
    q = int(combobox_question.get()[-1])
    global t, ax1, question_times
    if q in range(10):
        if q == 0:
            start = np.where(t == question_times[q-1])[0]
            if len(start) == 0:
                start = np.where(t > question_times[q-1])[0]
            end = len(new_x)
            start = int(start[0])
            ax1.clear()
            l, = ax1.plot(new_x[start: end], new_y[start: end], 'b-')

        else:
            # range1 = np.arange(question_times[q-1]-0.005, question_times[q-1]+0.005, 0.001)
            # range2 = np.arange(question_times[q]-0.005, question_times[q]+0.005, 0.001)
            start = np.where(t == question_times[q-1])[0]
            end = np.where(t == question_times[q])[0]
            if len(start) == 0:
                start = np.where(t > question_times[q-1])[0]
            if len(end) == 0:
                end = np.where(t > question_times[q])[0]
            start, end = int(start[0]), int(end[0])
            ax1.clear()
            l, = ax1.plot(new_x[start: end], new_y[start: end], 'b-')

        fig.canvas.draw()
    else:
        print("hello")
        ax1.clear()
        ax1.plot(new_x, new_y, 'b-')
        fig.canvas.draw()


def on_combobox_test_select(event):
    global test_path
    test_path = '../output/tests/{}/answertimes.csv'.format(combobox_test.get())
    global question_times
    question_times = np.loadtxt(test_path, skiprows=1, usecols=[3], delimiter=';')

    data = np.loadtxt('../output/tests/{}/barycenter.txt'.format(combobox_test.get()), skiprows=1, delimiter=';', usecols=range(3))
    global new_x, new_y
    global x, y, t
    t = data[:, 0]
    x = data[:, 1]
    y = data[:, 2]
    t = t.tolist()
    #x = [(my_x-np.average(x))/np.max(np.absolute(x)) for my_x in x]
    #y = [(my_y-np.average(y))/np.max(np.absolute(y)) for my_y in y]

    new_x = medfilt(x, 55)
    new_y = medfilt(y, 55)

    ax1.clear()
    ax1.plot(new_x, new_y, 'b-')
    fig.canvas.draw()


test_list = os.listdir('../output/tests')
test_list.sort()
combobox_question = ttk.Combobox(master=root, values=['all']+['question {}'.format(i) for i in range(1, 11)], state='readonly')
combobox_test = ttk.Combobox(master=root, values=test_list, state='readonly')

path = ''
def init_TK():
    v = tk.IntVar()
    canvas.mpl_connect("key_press_event", on_key_press)
    button = tk.Button(master=root, text="Quit", command=_quit)
    combobox_question.bind("<<ComboboxSelected>>", on_combobox_question_select)
    combobox_test.pack(fill=tk.X, padx=15, pady=15)
    combobox_test.bind("<<ComboboxSelected>>", on_combobox_test_select)
    combobox_test.set('test_8')
    combobox_question.pack(fill=tk.X, padx=15, pady=15)
    button.pack(fill=tk.BOTH, padx=15, pady=30)


def main():
    ### Parse csv with answer times
    ### put answertimes in variable and convert to frame
    init_TK()
    tk.mainloop()


if __name__ == '__main__':
    main()

