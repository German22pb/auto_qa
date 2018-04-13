# -*- coding: utf-8 -*-

from tkinter import ttk
from tkinter.filedialog import *
from tkinter.scrolledtext import ScrolledText

import fileinput
import subprocess as subp
import auto
import time
import os
from os.path import join
from datetime import datetime
import shutil
import sys
import signal

root = Tk()
root.title("AutoQA")
# root.iconbitmap(default='autoqa.ico')
root.resizable(False, False)
nb = ttk.Notebook(root)
frame_mob = Frame(nb)
frame_set = Frame(nb)




# --------------------Процесс тестирования--------------------------
def start_browsertest(project_name, url, test_case, mode, method, browserlist, resollist, video):
    global path_to_ffmpeg
    global path_to_ie_driver
    global path_to_firefox_driver
    global path_to_opera_driver
    global path_to_chrome_driver

    browserDict = {}
    browserDict.update({'Chrome': path_to_chrome_driver})
    browserDict.update({'Firefox': path_to_firefox_driver})
    browserDict.update({'Opera': path_to_opera_driver})
    browserDict.update({'Ie': path_to_ie_driver})

    print(video)
    time_project = datetime.now()
    time_index = str(time_project.strftime("[%m.%d.%Y]%H-%M-%S"))
    current_folder = os.getcwd()
    text_info.insert(END, current_folder + '\n')
    if mode == 'etalon':
        project_folder = os.mkdir('Etalon_' + project_name + time_index)
        folder = current_folder + '\\' + 'Etalon_' + project_name + time_index
    else:
        project_folder = os.mkdir(project_name + time_index)
        folder = current_folder + '\\' + project_name + time_index
    if video == 1:  # Запись видео в параллельном процессе
        log_dir = folder  # путь куда положить файл с записью
        CORE_DIR = 'C:\\'  # путь где лежит ffmpeg.exe
        video_file = join(log_dir, 'video.flv')
        FFMPEG_BIN = path_to_ffmpeg
        command = [
            FFMPEG_BIN,
            '-y',
            '-loglevel', 'error',
            '-f', 'gdigrab',
            '-framerate', '12',
            '-i', 'desktop',
            '-s', '960x540',
            '-pix_fmt', 'yuv420p',
            '-c:v', 'libx264',
            '-profile:v', 'main',
            '-fs', '50M',
            video_file]
        ffmpeg = subp.Popen(command, stdin=subp.PIPE, stdout=subp.PIPE, stderr=subp.PIPE)
    for browser in browserlist:
        # try :
        browser_folder = os.makedirs(folder + "\\" + browser)
        brow_folder = folder + "\\" + browser
        driver = auto.crossbrowser(url, browser, browserDict.get(browser))
        for resolution in resollist:
            file_index = 0
            screenshot_folder = auto.changeresolution(driver, brow_folder, resolution)
            text_info.insert(END, 'Resolution - OK \n')
            stand_url = url
            text_info.insert(END, 'STANDART URL: ' + stand_url + '\n')
            number_elements = auto.elements_in_dom(driver)
            text_info.insert(END, 'Elements in DOM: ' + str(number_elements) + '\n')
            case_test = open(test_case, 'rt', encoding='utf-8')
            text_info.insert(END, 'Open case - OK \n')
            for line in case_test:
                eval(line)
                text_info.insert(END, line + '\n')
                cur_url = driver.current_url[0: -1]
                cur_dom = auto.elements_in_dom(driver)
                text_info.insert(END, 'URL: ' + cur_url + '\n')
                text_info.see(END)
                # ------------Режим тестирования---------------------
                if mode == 'all':  # скрин после каждого действия
                    screen_image = auto.screenshot(screenshot_folder, driver, file_index)
                    file_index = file_index + 1
                elif mode == 'etalon':  # создает папку с эталонами
                    if method == 'url':
                        if stand_url != cur_url:
                            screen_image = auto.screenshot(screenshot_folder, driver, file_index)
                            stand_url = driver.current_url[0:-1]
                            file_index = file_index + 1
                        else:
                            stand_url = driver.current_url[0:-1]
                            file_index = file_index + 1
                    elif method == 'dom':
                        if number_elements != cur_dom:
                            screen_image = auto.screenshot(screenshot_folder, driver, file_index)
                            number_elements = auto.elements_in_dom(driver)
                            file_index = file_index + 1
                        else:
                            number_elements = auto.elements_in_dom(driver)
                            file_index = file_index + 1
                elif mode == 'auto':  # Сравнивает скрины с эталонами и сохраняет отличия
                    if method == 'url':
                        if stand_url != cur_url:
                            screen_image = auto.screenshot(screenshot_folder, driver, file_index)
                            stand_image = screen_image
                            stand_url = driver.current_url[0:-1]
                            name_of_screen = screenshot_folder + 'screenshot' + str(file_index) + '.png'
                            name_of_mockup = 'Etalon\\' + browser + '\\' + str(resolution) + '\\screenshot' + str(
                                file_index) + '.png'
                            auto.pixelperfect(name_of_mockup, name_of_screen)
                            file_index = file_index + 1
                        else:
                            stand_url = driver.current_url[0:-1]
                            file_index = file_index + 1

        driver.close()  # Закрыть браузер                    
        '''except :
        text_info.insert(END, 'ERROR - ' + browser + '\n')'''

    if mode == 'etalon':  # Удаление старой папки Эталон и копирование в неё этелонов
        shutil.rmtree(current_folder + '\\Etalon', ignore_errors=True)
        shutil.copytree(folder, current_folder + '\\Etalon')
    if video == 1:
        os.kill(ffmpeg.pid, signal.CTRL_C_EVENT)


def loadSettings():
    global path_to_chrome_driver
    global path_to_firefox_driver
    global path_to_opera_driver
    global path_to_ie_driver
    global path_to_ffmpeg
    try:
        configFile = open('config.txt', 'r', encoding='utf-8')
        configDict = {}
        for line in configFile :
            line = line.strip('\n')
            if line.split('=')[1]=='' :
                text_info.insert(END, 'Не указан путь до ' + line.split('=')[0] + '\n')
            configDict.update({line.split('=')[0] : line.split('=')[1]})
        path_to_chrome_driver = configDict.get('chrome')
        path_to_firefox_driver = configDict.get('firefox')
        path_to_opera_driver = configDict.get('opera')
        path_to_ie_driver = configDict.get('ie')
        path_to_ffmpeg = configDict.get('ffmpeg')
        set_lab_path_chrome['text'] = path_to_chrome_driver
        set_lab_path_firefox['text'] = path_to_firefox_driver
        set_lab_path_opera['text'] = path_to_opera_driver
        set_lab_path_ie['text'] = path_to_ie_driver
        set_lab_path_ffmpeg['text'] = path_to_ffmpeg

    except :
        text_info.insert(END, 'Конфигурация не найдена. Необходимо настроить AutoQA \n')

# ------------------------------------------------------------------


# ----------------------Настройки------------------------------------




# Save settings
def save_settings():
    try:
        configFile = open('config.txt', 'r+')
    except IOError:
        configFile = open('config.txt', 'w')
    configList = []
    configList.append('chrome='+path_to_chrome_driver)
    configList.append('firefox='+path_to_firefox_driver)
    configList.append('opera='+path_to_opera_driver)
    configList.append('ie='+path_to_ie_driver)
    configList.append('ffmpeg='+path_to_ffmpeg)
    for element in configList:
        if element.split('=')[1] != '':
            configFile.write(element + '\n')
    configFile.close()

    print("SAVED")

set_title = Label(frame_set, text="Настройки   ", font='Arial 12 bold')

lab_set_drivers = LabelFrame(frame_set, text="Drivers :", font='Arial 10 bold')

def set_opendialog_chrome(label):
    global path_to_chrome_driver
    try:
        path_to_chrome_driver = askopenfilename()
        label['text'] = ' ' + path_to_chrome_driver
    except:
        label['text'] = ' ' + path_to_chrome_driver

def set_opendialog_firefox(label):
    global path_to_firefox_driver
    try:
        path_to_firefox_driver = askopenfilename()
        label['text'] = ' ' + path_to_firefox_driver
    except:
        label['text'] = ' ' + path_to_firefox_driver

def set_opendialog_opera(label):
    global path_to_opera_driver
    try:
        path_to_opera_driver = askopenfilename()
        label['text'] = ' ' + path_to_opera_driver
    except:
        label['text'] = ' ' + path_to_opera_driver

def set_opendialog_ie(label):
    global path_to_ie_driver
    try:
        path_to_ie_driver = askopenfilename()
        label['text'] = ' ' + path_to_ie_driver
    except:
        label['text'] = ' ' + path_to_ie_driver

def set_opendialog_ffmpeg(label):
    global path_to_ffmpeg
    try:
        path_to_ffmpeg = askopenfilename()
        label['text'] = ' ' + path_to_ffmpeg
    except:
        label['text'] = ' ' + path_to_ffmpeg

path_to_chrome_driver = ''
set_lab_path_chrome = Label(lab_set_drivers, text=' ' + path_to_chrome_driver)
set_open_path_chrome = Button(lab_set_drivers, text='Chrome', width=10, command=lambda: set_opendialog_chrome(set_lab_path_chrome))
set_open_path_chrome.bind('<Button - 1>')

path_to_firefox_driver = ''
set_lab_path_firefox = Label(lab_set_drivers, text=' ' + path_to_firefox_driver)
set_open_path_firefox = Button(lab_set_drivers, text='Firefox', width=10, command=lambda: set_opendialog_firefox(set_lab_path_firefox))
set_open_path_firefox.bind('<Button - 1>')

path_to_opera_driver = ''
set_lab_path_opera = Label(lab_set_drivers, text=' ' + path_to_opera_driver)
set_open_path_opera = Button(lab_set_drivers, text='Opera', width=10, command=lambda: set_opendialog_opera(set_lab_path_opera))
set_open_path_opera.bind('<Button - 1>')

path_to_ie_driver = ''
set_lab_path_ie = Label(lab_set_drivers, text=' ' + path_to_ie_driver)
set_open_path_ie = Button(lab_set_drivers, text='IExplorer', width=10, command=lambda: set_opendialog_ie(set_lab_path_ie))
set_open_path_ie.bind('<Button - 1>')

lab_set_ffmpeg = LabelFrame(frame_set, text="Video codec :", font='Arial 10 bold')
path_to_ffmpeg = ''
set_lab_path_ffmpeg = Label(lab_set_ffmpeg, text=' ' + path_to_ffmpeg)
set_open_path_ffmpeg = Button(lab_set_ffmpeg, text='ffmpeg', width=10, command=lambda: set_opendialog_ffmpeg(set_lab_path_ffmpeg))
set_open_path_ffmpeg.bind('<Button - 1>')

set_save = Button(frame_set, text='Save', width=10, command=save_settings)
set_save.bind('<Button - 1>')


# --------------------Мобильное тестирование(Appium)----------------


# Запускает мобильное тестирование
def start_mobtest():
    print("START MOB TEST")


mob_title = Label(frame_mob, text="Тестирование мобильного приложения   ",
                  font='Arial 12 bold')

start_mob = Button(frame_mob, text='Start test', width=10, command=start_mobtest)
start_mob.bind('<Button-1>')


# Загрузка мобильного теста
def mob_opendialog():
    global mob_test_case
    try:
        mob_test_case = askopenfilename()
        mob_lab_case['text'] = 'Тест-кейс: ' + mob_test_case
        text_test.delete('1.0', END)
        for i in fileinput.input(mob_test_case):
            text_test.insert(END, i)
    except:
        mob_lab_case['text'] = 'Тест-кейс: ' + mob_test_case


mob_test_case = ''  # Здесь будет храниться адрес файла с тестом
mob_lab_case = Label(frame_mob, text='Тест-кейс: ' + mob_test_case)
mob_open_test = Button(frame_mob, text='Выбрать тест', width=20, command=mob_opendialog)
mob_open_test.bind('<Button - 1>')

# --------Тестирование в Браузере(Selenium)---------

frame_brow = Frame(nb)


# Запускает тестирование в браузерах
def start_browtest():
    choose_browser()
    choose_resol()
    record_video()
    text_info.insert(END, input_url.get() + '\n')
    text_info.insert(END, input_project.get() + '\n')
    text_info.insert(END, mode.get() + '\n')
    text_info.insert(END, test_case + '\n')
    text_info.insert(END, method.get() + '\n')
    text_info.insert(END, str(browserlist) + '\n')
    text_info.insert(END, str(resollist) + '\n')
    text_info.see(END)
    start_browsertest(input_project.get(), input_url.get(), test_case, mode.get(), method.get(), browserlist, resollist,
                      video)


brow_title = Label(frame_brow, text="Тестирование Desktop-приложения",
                   font='Arial 12 bold')

# Название папки для сохранения
lab_project = Label(frame_brow, text='Введите название проекта :')
input_project = Entry(frame_brow, width=50, bd=2)

# Адрес сайта для тестирования
lab_url = Label(frame_brow, text='Введите URL сайта :')
input_url = Entry(frame_brow, width=50, bd=2)

frame_start = Frame(frame_brow)


# Загрузка теста
def opendialog():
    global test_case
    try:
        test_case = askopenfilename()
        lab_case['text'] = 'Тест-кейс: ' + test_case
        text_test.delete('1.0', END)
        for i in fileinput.input(test_case):
            text_test.insert(END, i)
    except:
        lab_case['text'] = 'Тест-кейс: ' + test_case


test_case = ''  # Здесь будет храниться адрес файла с тестом
lab_case = Label(frame_brow, text='Тест-кейс: ' + test_case)
open_test = Button(frame_brow, text='Выбрать тест', width=20, command=opendialog)
open_test.bind('<Button - 1>')

# Выбор режима тестирования
lab_mode = LabelFrame(frame_brow, text="Выбрать режим :", font='Arial 10 bold')
mode = StringVar()
mode.set('all')
mod_all = Radiobutton(lab_mode,
                      text='Скриншот после каждого действия',
                      variable=mode, value='all')
mod_etalon = Radiobutton(lab_mode,
                         text='Создать каталог с эталонными изображениями',
                         variable=mode, value='etalon')
mod_auto = Radiobutton(lab_mode,
                       text='Сравнить изображения с эталонными и сохранить результат     ',
                       variable=mode, value='auto')

# Выбор метода сравнения уникальности страниц
lab_method = LabelFrame(frame_brow, text="Сравнение уникальности страниц :", font='Arial 10 bold')
method = StringVar()
method.set('url')
method_url = Radiobutton(lab_method,
                         text='Сравнение по URL',
                         variable=method, value='url')
method_dom = Radiobutton(lab_method,
                         text='Сравнение по DOM',
                         variable=method, value='dom')

# Выбор метода сравнения изображений
lab_check_images = LabelFrame(frame_brow, text="Метод сравнения изображений :", font='Arial 10 bold')
check_image = StringVar()
check_image.set('pixel')
check_image_pixel = Radiobutton(lab_check_images,
                                text='Попиксельное сравнение',
                                variable=check_image, value='pixel')
check_image_phash = Radiobutton(lab_check_images,
                                text='Перцептивный хэш',
                                variable=check_image, value='phash')

start_brow = Button(frame_start, text='Start test', width=10, command=start_browtest)
start_brow.bind('<Button-1>')


# Выбор браузера

def choose_browser():
    global browserlist
    browserlist.clear()
    if brow1.get() == 1:
        browserlist.append('Firefox')
    if brow2.get() == 1:
        browserlist.append('Opera')
    if brow3.get() == 1:
        browserlist.append('Chrome')
    if brow4.get() == 1:
        browserlist.append('Ie')


lab_browser = LabelFrame(frame_brow, text="Выбор браузеров и разрешений :", font='Arial 10 bold')
browserlist = []  # Хранит список браузеров
brow1 = IntVar()
brow2 = IntVar()
brow3 = IntVar()
brow4 = IntVar()

cb1 = Checkbutton(lab_browser, text='Firefox', variable=brow1, onvalue=1, offvalue=None)
cb2 = Checkbutton(lab_browser, text='Opera', variable=brow2, onvalue=1, offvalue=None)
cb3 = Checkbutton(lab_browser, text='Chrome', variable=brow3, onvalue=1, offvalue=None)
cb4 = Checkbutton(lab_browser, text='Internet Explorer', variable=brow4, onvalue=1, offvalue=None)


# Выбор разрешения

def choose_resol():
    global resollist
    resollist.clear()
    if resol1.get() == 1:
        resollist.append([1920, 1080])
    if resol2.get() == 1:
        resollist.append([1366, 768])
    if resol3.get() == 1:
        resollist.append([1280, 1024])
    if resol4.get() == 1:
        resollist.append([1024, 768])
    if resol5.get() == 1:
        resollist.append([800, 600])


resollist = []  # Хранит список разрешений
resol1 = IntVar()
resol2 = IntVar()
resol3 = IntVar()
resol4 = IntVar()
resol5 = IntVar()

cr1 = Checkbutton(lab_browser, text='1920x1080', variable=resol1, onvalue=1, offvalue=None)
cr2 = Checkbutton(lab_browser, text='1366x768', variable=resol2, onvalue=1, offvalue=None)
cr3 = Checkbutton(lab_browser, text='1280x1024', variable=resol3, onvalue=1, offvalue=None)
cr4 = Checkbutton(lab_browser, text='1024x768', variable=resol4, onvalue=1, offvalue=None)
cr5 = Checkbutton(lab_browser, text='800x600', variable=resol5, onvalue=1, offvalue=None)


# Запись видео 
def record_video():
    global video
    video = 0
    if cv1.get() == 1:
        video = 1


video = 0
cv1 = IntVar()

cv = Checkbutton(frame_start, text='Запись видео', variable=cv1, onvalue=1, offvalue=None)

# --------------------Экран сценария-------------------------
frame_text = Frame(root)
lab_text = Label(frame_text, text="Сценарий теста :", font='Arial 12 bold')
text_test = ScrolledText(frame_text, width=50, height=30, font='10', wrap=NONE, bd=3)
scrollx = Scrollbar(frame_text, command=text_test.xview, orient=HORIZONTAL)
text_test['xscrollcommand'] = scrollx.set

# ---------------------Строка состояния----------------------------

lab_info = LabelFrame(root, text="Строка состояния", font='Arial 10')
text_info = ScrolledText(lab_info, width=95, height=5, font='10', wrap=WORD, bd=3)

# -------------Расположение виджетов на экране----------------------

nb.add(frame_brow, text=' Desktop-тестирование ')
#nb.add(frame_mob, text=' Mobile-тестирование ')
nb.add(frame_set, text=' Настройки ')
nb.grid(row=0, column=0, sticky=W + N)

frame_text.grid(row=0, column=1, sticky=W)
mob_title.grid(row=0, column=0, padx=20, sticky=W)
start_mob.grid(row=12, column=0, padx=20)
brow_title.grid(row=0, column=1, sticky=W)
set_title.grid(row=0, column=0, padx=40, sticky=W)
lab_project.grid(row=1, column=1, sticky=W)
input_project.grid(row=2, column=1)
lab_url.grid(row=3, column=1, sticky=W)
input_url.grid(row=4, column=1)
lab_case.grid(row=5, column=1, sticky=W)
lab_text.grid(row=0, column=2, sticky=W, padx=10, pady=5)
text_test.grid(row=1, column=2, rowspan=24, padx=0, pady=0)  # textarea
scrollx.grid(row=25, column=2, sticky='nwes')
open_test.grid(row=6, column=1)
mob_open_test.grid(row=4, column=0)
mob_lab_case.grid(row=3, column=0, sticky=W, padx=10)
lab_set_drivers.grid(row=1, column=0, sticky=W + E, padx=10, pady=10)
set_open_path_chrome.grid(row=3, column=0)
set_lab_path_chrome.grid(row=3, column=1)
set_open_path_firefox.grid(row=4, column=0)
set_lab_path_firefox.grid(row=4, column=1)
set_open_path_opera.grid(row=5, column=0)
set_lab_path_opera.grid(row=5, column=1)
set_open_path_ie.grid(row=6, column=0)
set_lab_path_ie.grid(row=6, column=1)
lab_set_ffmpeg.grid(row=7, column=0, sticky=W + E, padx=10, pady=10)
set_open_path_ffmpeg.grid(row=8, column=0)
set_lab_path_ffmpeg.grid(row=8, column=1)
set_save.grid(row=11, column=0)
lab_mode.grid(row=7, column=1, sticky=W + E, padx=10, pady=10)  # mode
mod_all.grid(row=8, column=1, sticky=W)
mod_etalon.grid(row=9, column=1, sticky=W)
mod_auto.grid(row=10, column=1, sticky=W)
lab_method.grid(row=11, column=1, sticky=W + E, padx=10, pady=10)  # method
method_url.grid(row=12, column=1, sticky=W)
method_dom.grid(row=13, column=1, sticky=W)
lab_check_images.grid(row=14, column=1, sticky=W + E, padx=10, pady=10)  # check_images
check_image_pixel.grid(row=15, column=1, sticky=W)
check_image_phash.grid(row=16, column=1, sticky=W)
lab_browser.grid(row=17, column=1, sticky=W + E, padx=10, pady=10)  # browsers
cb1.grid(row=18, column=1, sticky=W, padx=15)
cb2.grid(row=19, column=1, sticky=W, padx=15)
cb3.grid(row=20, column=1, sticky=W, padx=15)
cb4.grid(row=21, column=1, sticky=W, padx=15)
cr1.grid(row=18, column=0, sticky=W)
cr2.grid(row=19, column=0, sticky=W)
cr3.grid(row=20, column=0, sticky=W)
cr4.grid(row=21, column=0, sticky=W)
cr5.grid(row=22, column=0, sticky=W)

frame_start.grid(row=25, column=1, sticky=W)
cv.grid(row=25, column=0, sticky=W, padx=10)
start_brow.grid(row=25, column=1, padx=20)

lab_info.grid(row=26, column=0, columnspan=2, sticky=W + E)
text_info.grid(row=27, column=0, columnspan=2, sticky=W + E)
loadSettings()
root.mainloop()


