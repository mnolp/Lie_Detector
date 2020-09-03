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
frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
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

data = np.loadtxt('../output/tests/test_30_f/barycenter.txt', skiprows=1, delimiter=';', usecols=(1,2))
x = data[:,0]
y = data[:,1]
x = [(my_x-np.average(x))/np.max(np.absolute(x)) for my_x in x]
y = [(my_y-np.average(y))/np.max(np.absolute(y)) for my_y in y]
ax1.set_xlim(-1, 1)
ax1.set_ylim(-1, 1)
l, = ax1.plot([],[], 'bo')

new_x = medfilt(x, 15)
new_y = medfilt(y, 15)


def animate(i):
    global counter
    l.set_xdata(new_x[counter-1:counter])
    l.set_ydata(new_y[counter-1:counter])
    counter += 1
    return l,


def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
    # Fatal Python Error: PyEval_RestoreThread: NULL tstate


def on_key_press(event):
    print("you pressed {}".format(event.key))
    if event.key.isspace():
        global running
        if running:
            ani.event_source.stop()
            running = False
        else:
            ani.event_source.start()
            running = True
    key_press_handler(event, canvas, toolbar)


question_times = []
def on_combobox_question_select(event):
    global counter
    q_number = int(combobox_question.get()[-1])
    counter = int(question_times[q_number-1]*2000)


def on_combobox_test_select(event):
    global test_path
    test_path = '../output/tests/{}/answertimes.csv'.format(combobox_test.get())
    global question_times
    question_times = np.loadtxt(test_path, skiprows=1, usecols=[2], delimiter=';')

    data = np.loadtxt('../output/tests/{}/barycenter.txt'.format(combobox_test.get()), skiprows=1, delimiter=';', usecols=(1,2))
    global new_x, new_y, x, y
    x = data[:,0]
    y = data[:,1]
    x = [(my_x-np.average(x))/np.max(np.absolute(x)) for my_x in x]
    y = [(my_y-np.average(y))/np.max(np.absolute(y)) for my_y in y]
    l, = ax1.plot([],[], 'bo')

    new_x = medfilt(x, 15)
    new_y = medfilt(y, 15)

    animate_TK()


def update_value(event):
    global counter
    counter = scale.get()


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
        outdata[i][1] = (my_data[i][2]+my_data[i][4])/(my_data[i][2]+my_data[i][1]+my_data[i][1]+my_data[i][3])
        outdata[i][2] = (my_data[i][1]+my_data[i][2])/(my_data[i][2]+my_data[i][1]+my_data[i][1]+my_data[i][3])

    with open(file[:file.rfind('/')]+'/barycenter.txt', 'w+') as f:
        f.write('Time;X,Y;\n')
        for line in outdata:
            f.write('{};{};{};\n'.format(line[0], line[1], line[2]))


def get_barycenter(file):
    my_data = np.loadtxt(file, skiprows=1, delimiter=';', usecols=[0, 2, 3, 4, 5])
    my_data = my_data.astype(np.float)

    outdata = np.zeros((len(my_data), 3,))
    for i in range(len(my_data)):
        outdata[i][0] = my_data[i][0]
        outdata[i][1] = (my_data[i][2]+my_data[i][4])-(my_data[i][1]+my_data[i][3])
        outdata[i][2] = (my_data[i][1]+my_data[i][2])-(my_data[i][3]+my_data[i][4])

    with open(file[:file.rfind('/')]+'/barycenter.txt', 'w+') as f:
        f.write('Time;X,Y;\n')
        for line in outdata:
            f.write('{};{};{};\n'.format(line[0], line[1], line[2]))

test_list = os.listdir('../output/tests')
test_list.sort()
combobox_question = ttk.Combobox(master=root, values=['question {}'.format(i) for i in range(1, 11)], state='readonly')
combobox_test = ttk.Combobox(master=root, values=test_list, state='readonly')
scale = tk.Scale(master=root, orient=tk.HORIZONTAL, label='Seconds', command=update_value, from_=0, to=len(x))

path = ''
def init_TK():
    v = tk.IntVar()
    canvas.mpl_connect("key_press_event", on_key_press)
    button = tk.Button(master=root, text="Quit", command=_quit)
    combobox_question.bind("<<ComboboxSelected>>", on_combobox_question_select)
    combobox_test.pack(fill=tk.X, padx=15, pady=15)
    combobox_test.bind("<<ComboboxSelected>>", on_combobox_test_select)
    combobox_test.set('test_8')
    scale.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)
    '''
    tk.Radiobutton(master=root, text="0.25", variable=v, value=1).pack(anchor=tk.W, pady=5)
    tk.Radiobutton(master=root, text="0.50", variable=v, value=2).pack(anchor=tk.W, pady=5)
    tk.Radiobutton(master=root, text="1.00", variable=v, value=3).pack(anchor=tk.W, pady=5)
    '''
    combobox_question.pack(fill=tk.X, padx=15, pady=15)
    button.pack(fill=tk.BOTH, padx=15, pady=30)


def animate_TK():
    global ani
    ani = animation.FuncAnimation(fig, animate, frames=len(x), interval=0.001, blit=True, repeat=True)
    tk.mainloop()

def main():
    ### Parse csv with answer times
    ### put answertimes in variable and convert to frame
    init_TK()
    animate_TK()


if __name__ == '__main__':
    get_all_balancedata()

