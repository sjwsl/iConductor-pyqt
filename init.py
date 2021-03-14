import sys
import time
import serial

import numpy as np
import pygame.midi
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import song
import util
import tree


class SerialThread(QThread):
    def __init__(self, ser, value, orche):
        QThread.__init__(self)
        self.ser = ser
        self.dct = dict()
        self.rel = {'lat': 0, 'laz': 1, 'lag': 2, 'lcr': 3}
        self.flg = [False, False, False, False]
        self.angle = 0
        self.pause = False
        self.value = value
        self.orche = orche

    kill = pyqtSignal(bool)
    stop = pyqtSignal(bool)
    mdfy = pyqtSignal(str, float)

    def run(self):
        stt, dua, lst_a = time.time(), 0.0, []
        while dua < 2.0:
            try:
                tmp = eval(self.ser.readline())
                if type(tmp) == dict:
                    key = list(tmp)[0]
                    if key == 'lag':
                        lst_a.append(float(tmp['lag'] % 360))
            except (TypeError, SyntaxError, NameError, KeyError):
                pass
            dua = time.time() - stt
        if lst_a:
            self.angle = np.array(lst_a).mean()
        acc_h = list(np.zeros(6, ))
        acc_v = list(np.zeros(6, ))
        val_0 = self.value
        val_m = [[1] * 5] * len(list(val_0))
        pau_t, pau_s = 0, 0
        while True:
            while True:
                try:
                    tmp = eval(self.ser.readline())
                    if type(tmp) == dict:
                        key = list(tmp)[0]
                        self.flg[self.rel[key]] = True
                        if key in ['lat', 'laz']:
                            self.dct[key] = tmp[key] / 100
                        elif key == 'lag':
                            self.dct[key] = tmp[key] % 360
                        elif key == 'lcr':
                            self.dct[key] = tmp[key] + 40
                        if self.flg[0] and self.flg[1] and self.flg[2] and self.flg[3]:
                            break
                except (SyntaxError, NameError, KeyError):
                    pass
                time.sleep(0.01)
            a_h = self.dct['lat']
            a_v = self.dct['laz']
            angle = (self.dct['lag'] + 90 - self.angle) % 360
            curve = max(self.dct['lcr'], 0)
            acc_h.append(a_h), acc_h.pop(0)
            acc_v.append(a_v), acc_v.pop(0)
            acc_h_, acc_v_ = np.array(acc_h), np.array(acc_v)
            val_s, vel_s = acc_h_.std() + 0.01, acc_v_.std() + 0.01
            acc_h_ = (acc_h_ - acc_h_.mean()) / val_s + acc_h_.mean()
            acc_v_ = (acc_v_ - acc_v_.mean()) / vel_s + acc_v_.mean()
            val_s, vel_s = max(val_s, 0), max(vel_s, 0)
            val_s, vel_s = min(np.log(val_s + 1) / 2, 1), min(np.log(vel_s + 1) / 4, 1.5)
            if val_s < 0.2 and vel_s < 0.2 and curve < 60:
                self.pause = True
                self.stop.emit(self.pause)
                pau_t = pau_t if pau_t != 0 else time.time()
                pau_s = time.time() - pau_t
                if pau_s > 3:
                    self.kill.emit(True)
                    break
            else:
                self.pause = self.pause if pau_t == 0 else False
                self.stop.emit(self.pause)
                pau_t, pau_s = 0, 0
                acc_hv, acc_vh = acc_h_ / (acc_v_ + 0.00001), acc_v_ / (acc_h_ + 0.00001)
                acc_hv, acc_vh = acc_hv[~np.isnan(acc_hv)], acc_vh[~np.isnan(acc_vh)]
                acc_hv, acc_vh = np.insert(acc_hv, -1, 1), np.insert(acc_vh, -1, 1)
                acc_hm, acc_vm = max(acc_vh.mean(), 0), max(acc_hv.mean(), 0)
                val_p, vel_p = np.log(acc_hm + 1) * 1.2, np.log(acc_vm + 1)
                lst = [] if curve < 60 else self.orche.ask(100, angle)
                for i, key in enumerate(list(self.value)):
                    val_e = np.array(val_m[i]).mean()
                    # val_s = np.round(val_s, 4)
                    val_a = curve / 60 if key in lst else 1
                    val_e = val_e * (1 - val_s) + val_p * val_s
                    val_e = val_0[key] * (1 - val_s) + val_e * val_s * val_a
                    self.value[key] = min(val_e, 2)
                    self.mdfy.emit(key, min(val_e, 2))
                    val_m[i].append(val_e), val_m[i].pop(0)
                    # val_p is the parameter of horizontal mov, val_s is the weight value
                    # val_0 is the initial value, val_e is the expected value
                    # val(t) = (1-a) val(0) + a(1-a) avg(val(t-5:t)) + a^2 val(^t)
                # print(str(round(val_p, 4)).ljust(7), str(round(vel_p, 4)).ljust(7),
                #       str(round(val_s, 4)).ljust(7), str(round(vel_s, 4)).ljust(7), curve, lst)
                print(angle, curve, lst)
            self.dct = dict()
            self.flg = [False, False, False, False]
        self.kill.emit(True)


class PlayerThread(QThread):
    init = pyqtSignal()
    move = pyqtSignal(int, int)
    play = pyqtSignal(tuple)

    def __init__(self, beat, ev_lst):
        super().__init__()
        self.beat = beat
        self.term = False
        self.pause = False
        self.ev_lst = ev_lst

    def run(self):
        print(len(self.ev_lst))
        print(self.ev_lst[-1][0])
        self.init.emit()
        last = 0
        span = self.ev_lst[-1][0]
        for event in self.ev_lst:
            if self.term:
                return
            if self.pause:
                while self.pause:
                    time.sleep(0.01)
                    if self.term:
                        return
                if self.term:
                    return
            if event[0] > last:
                time.sleep((event[0] - last) / self.beat)
                self.move.emit(event[0], span)
                last = event[0]
            self.play.emit(event)


class SingleSldDialog(QDialog):
    signal = pyqtSignal(float)

    def __init__(self, title, val, min_, max_):
        super().__init__()
        self.setWindowTitle(title)

        self.min, self.max = min_, max_
        self.val = (val - self.min) * 100 / (self.max - self.min)
        self.sdd = util.getSlider(self, pos=(30, 20), size=(200, 15), style=Qt.Horizontal, focus=Qt.NoFocus)
        self.sdd.setValue(self.val)
        self.sdd.setRange(1, 100)
        self.sdd.valueChanged[int].connect(self.changeValue)
        self.lbl = QLabel("%.2f" % val, self)
        self.lbl.setGeometry(QRect(100, 50, 60, 20))
        self.lbl.setFont(QFont("Dengxian"))
        self.lbl.setAlignment(Qt.AlignHCenter)

    def changeValue(self, value):
        self.val = value * (self.max - self.min) / 100 + self.min
        self.lbl.setText("%.2f" % self.val)
        self.signal.emit(self.val)
        self.val = value


class MultiSldDialog(QDialog):
    signal = pyqtSignal(str, float)

    def __init__(self, title, values):
        super().__init__()
        self.setWindowTitle(title)

        self.values = dict()
        self.inverse = dict()
        self.value = np.mean(np.array(list(values.values())))
        self.stt = util.getLabel(self, pos=(30, 30), size=(60, 20), label='整体系数')
        self.sld = util.getSlider(self, pos=(110, 31), size=(220, 20), ran=[0, 199])
        self.sld.setValue(self.value * 100)
        self.sld.valueChanged[int].connect(self.change_all)
        self.lbl = util.getLabel(self, pos=(350, 31), size=(30, 20), label='%.2f' % self.value)
        self.statics, self.sliders, self.labels = [], [], []
        self.value = self.value * 100
        instrs = list(values)
        widget = QWidget()
        widget.setMinimumSize(350, 40 * len(instrs))
        for i, instr in enumerate(instrs):
            self.inverse[instr] = i
            self.values[instr] = int(values[instr] * 100)
            static = util.getLabel(widget, pos=(0, 1+40*i), size=(60, 20), label=instr)
            self.statics.append(static)
            slider = util.getSlider(widget, pos=(80, 2+40*i), size=(220, 20), ran=[0, 199])
            slider.setValue(self.values[instr])
            slider.valueChanged[int].connect(lambda position, tmp=instr: self.change_one(position, tmp))
            self.sliders.append(slider)
            label = util.getLabel(widget, pos=(320, 2+40*i), size=(30, 20), label='%.2f' % (self.values[instr] / 100))
            self.labels.append(label)
        self.scroll = QScrollArea(self)
        self.scroll.setWidget(widget)
        self.scroll.setStyleSheet('border: none;')
        self.scroll.setGeometry(QRect(30, 70, 350, min(240, 40 * len(instrs))))
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.show()

    def change_all(self, value):
        self.lbl.setText("%.2f" % (value / 100))
        # d = value - self.value
        # instrs = list(self.values)
        # for i, instr in enumerate(instrs):
        #     self.values[instr] += d
        #     self.sliders[i].setValue(self.values[instr])
        #     self.labels[i].setText('%.2f' % (self.values[instr] / 100))
        self.value = value

    def change_one(self, value, instr):
        self.labels[self.inverse[instr]].setText("%.2f" % (value / 100))
        self.values[instr] = value
        self.signal.emit(instr, value)
        data = list(self.values.values())
        self.value = np.mean(np.array(data))
        self.sld.setValue(self.value)

    def fun(self, value):
        pass


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setFixedSize(780, 640)
        self.setWindowTitle('人机交互音乐指挥系统 v2.0')
        label = QLabel(text='<b>人机交互音乐指挥系统</b>', parent=self)
        label.setStyleSheet("font-size:50px;font-family:华文新魏;color:gray;background-color:rgba(255,255,255,0.5)")
        label.move(195, 35)
        palette = QPalette()
        palette.setBrush(self.backgroundRole(), QBrush(QPixmap('pic-1-4.jpg')))
        self.setPalette(palette)
        self.setWindowOpacity(0.95)

        # cbb_init, initialize those combo box for basic settings
        set_lst_a = [' COM4']
        set_lst_b = [' 9600', ' 19200', ' 28800', ' 57600', ' 115200']
        music_lst_1 = [' 所有', ]
        music_lst_2 = [' 天空之城', ' 我心永恒', ]
        util.getLabel(self, pos=(365, 120), size=(60, 30), label='参数设置')
        util.getLabel(self, pos=(365, 160), size=(60, 30), label='演奏控制')
        util.getLabel(self, pos=(60, 120), size=(60, 30), label='作者 :')
        util.getLabel(self, pos=(60, 160), size=(60, 30), label='曲目 :')
        self.set_a = util.getComboBox(self, pos=(440, 120), size=(80, 30), idx=0, lst=set_lst_a)
        self.set_b = util.getComboBox(self, pos=(530, 120), size=(80, 30), idx=0, lst=set_lst_b)
        self.cbb_1 = util.getComboBox(self, pos=(130, 120), size=(190, 30), idx=0, lst=music_lst_1)
        self.cbb_2 = util.getComboBox(self, pos=(130, 160), size=(190, 30), idx=0, lst=music_lst_2)
        self.cbb_2.currentTextChanged.connect(self.music_init)
        self.cbb_3 = None

        # btn_init, initialize those push button for music playing
        self.beat = 900
        # self.btn_0 = util.getPushButton(self, pos=(60, 240), size=(45, 30), label='*')
        self.btn_1 = util.getPushButton(self, pos=(130, 240), size=(90, 30), label='调整 : 1.00')
        self.btn_2 = util.getPushButton(self, pos=(242, 240), size=(30, 30), label='x')
        self.btn_3 = util.getPushButton(self, pos=(290, 240), size=(30, 30), label='+')
        self.btn_4 = util.getPushButton(self, pos=(440, 160), size=(90, 30), label='开始')
        self.btn_5 = util.getPushButton(self, pos=(540, 160), size=(80, 30), label='中止')
        self.btn_6 = util.getPushButton(self, pos=(630, 160), size=(80, 30), label='暂停')
        self.btn_7 = util.getPushButton(self, pos=(620, 120), size=(90, 30), label='节拍 : ' + str(self.beat))
        # self.btn_0.clicked.connect(self.mul)
        self.btn_1.clicked.connect(self.sld)
        self.btn_2.clicked.connect(self.rmv)
        self.btn_3.clicked.connect(self.add)
        self.btn_4.clicked.connect(self.play)
        self.btn_5.clicked.connect(self.kill)
        self.btn_6.clicked.connect(self.stop)
        self.btn_7.clicked.connect(self.ctr)
        util.getLabel(self, pos=(365, 200), size=(60, 30), label='演奏进度')
        util.getLabel(self, pos=(365, 240), size=(60, 30), label='总体音量')
        self.gau_1 = util.getProgressBar(self, pos=(440, 205), size=(270, 20), ran=(1, 100))
        self.gau_2 = util.getProgressBar(self, pos=(440, 245), size=(270, 20), ran=(0, 127))

        pygame.midi.init()
        self.output = pygame.midi.Output(pygame.midi.get_default_output_id())
        self.thread, self.player, self.serial = None, None, None
        self.ch_lst, self.ev_lst = None, None
        self.chan_0, self.chan_1, self.chan_2 = dict(), dict(), dict()
        self.gauges, self.statics = [], []
        self.panel, self.scroll = None, None
        self.value, self.confs = dict(), dict()
        self.groups = []
        self.angle = 90
        self.term = True
        self.pause = False
        self.orche, self.robin = None, None
        self.music_init(self.cbb_2.currentText())

    def music_init(self, text):
        text = text.strip()
        self.frame_init(text)
        self.panel_init()
        self.gauge_func()

    def frame_init(self, music):
        self.confs = song.songs[music]['confs']
        self.value = dict()
        for conf in list(self.confs):
            self.value[conf] = 1
        util.getLabel(self, pos=(60, 200), size=(40, 30), label='声道 :')
        if self.cbb_3 is not None:
            self.cbb_3.deleteLater()
        self.cbb_3 = util.getComboBox(self, pos=(130, 200), size=(190, 30), idx=0,
                                      lst=util.str_list_indent(list(self.value)))
        self.cbb_3.currentTextChanged.connect(self.volume_func)
        self.cbb_3.show()
        self.volume_func()

    def volume_func(self):
        grp = (self.cbb_3.currentText()).strip()
        self.btn_1.setText('调整 : %.2f' % self.value[grp])

    def panel_init(self):
        for group in self.groups:
            group.deleteLater()
        self.groups = []
        self.panel = util.getPanel(self, pos=(365, 280), size=(350, 300))
        self.panel.setStyleSheet('background-color:rgba(255,255,255,0.4)')
        self.panel.show()
        label = util.getLabel(self.panel, pos=(0, 0), size=(80, 30), label='乐器布局')
        label.show(), label.setStyleSheet('background-color:rgba(255,255,255,0)')
        label = util.getLabel(self.panel, label='<b>人</b>', pos=(150, 215), size=(50, 50))
        label.show(), label.setStyleSheet('background-color:rgba(185,195,255,0.8); border: 0px; border-style:none; '
                                          'padding: 12px; border-radius: 25px; font-size:18px')
        for i, instr in enumerate(list(self.confs)):
            pos_r = self.confs[instr][0]
            pos_a = self.confs[instr][1] / 180 * np.pi
            pos_x = int(175 + pos_r * np.cos(pos_a))
            pos_y = int(240 - pos_r * np.sin(pos_a))
            grp = util.getInstrumentLabel(self.panel, mid=(pos_x, pos_y), label=instr)
            grp.setObjectName(instr)
            grp.signal.connect(self.conf_func), self.groups.append(grp), grp.show()
            self.chan_0[i], self.chan_1[instr], self.chan_2[i] = instr, i, 2 * i

    def conf_func(self, text, x, y):
        x, y = x - 175, 240 - y
        r = np.sqrt(x ** 2 + y ** 2)
        a = np.arctan2(y, x) / np.pi * 180 if x != 0 else 90
        a = a if a > 0 else a + 180
        self.confs[text] = (int(r), int(a))
        print(self.confs)
        if self.thread is not None and not self.thread.isFinished():
            self.thread.orche.update(text, int(r), int(a))

    def gauge_func(self):
        for gauge in self.gauges:
            gauge.deleteLater()
        for static in self.statics:
            static.deleteLater()
        if self.scroll is not None:
            self.scroll.deleteLater()
        self.gauges, self.statics = [], []
        instrs = list(self.value)
        widget = QWidget()
        widget.setMinimumSize(270, 40 * len(instrs))
        widget.setStyleSheet('background-color:rgba(255,255,255,0)')
        for i, instr in enumerate(instrs):
            static = util.getLabel(widget, pos=(0, 1 + 40 * i), size=(60, 20), label=instr)
            self.statics.append(static), static.show()
            gauge = util.getGauge(widget, pos=(70, 2 + 40 * i), size=(190, 9), value=0, lst=[0, 199])
            self.gauges.append(gauge), gauge.show()
            gauge = util.getGauge(widget, pos=(70, 15 + 40 * i), size=(190, 9), value=0, lst=[0, 127])
            self.gauges.append(gauge), gauge.show()
            self.chan_2[self.chan_1[instr]] = 2 * i
        self.scroll = QScrollArea(self)
        self.scroll.setWidget(widget)
        self.scroll.setGeometry(QRect(60, 288, 270, 300))
        self.scroll.setStyleSheet('border: none; background-color:rgba(255,255,255,0.4)')
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.show()

    # part of frame_init, set the frame in the center of the window
    def centering(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        ver = (screen.width() - size.width()) // 2
        hor = (screen.height() - size.height()) // 2 - 50
        self.move(ver, hor)

    def sld(self):
        grp = (self.cbb_3.currentText()).strip()
        val = self.value[grp]
        dialog = SingleSldDialog('音量系数调整', val, 0, 2)
        dialog.signal.connect(self.sld_func)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()

    def sld_func(self, val):
        key = (self.cbb_3.currentText()).strip()
        self.value[key] = val
        self.btn_1.setText('调整 : %.2f' % self.value[key])
        grp = self.findChild(QWidget, key)
        grp.updateRatio(val)

    def rmv(self):
        if len(list(self.value)) == 1:
            return
        ins = (self.cbb_3.currentText()).strip()
        self.value.pop(ins)
        self.cbb_3.deleteLater()
        self.cbb_3 = util.getComboBox(self, pos=(130, 200), size=(190, 30), idx=0,
                                      lst=util.str_list_indent(list(self.value)))
        self.cbb_3.currentTextChanged.connect(self.volume_func)
        self.cbb_3.show()
        self.btn_1.setText('调整 : ' + str(self.value[list(self.value)[0]]))
        for i in range(len(self.groups)):
            label = self.groups[i].text()
            if label == ins:
                grp_st = self.groups.pop(i)
                grp_st.deleteLater()
                break
        self.gauge_func()

    def mul(self):
        dialog = MultiSldDialog('多声道系数调整', self.value)
        dialog.signal.connect(self.mul_func)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()

    def mul_func(self, instr, value):
        self.value[instr] = value / 100
        grp = (self.cbb_3.currentText()).strip()
        if grp == instr:
            self.btn_1.setText('调整 : %.2f' % self.value[grp])

    def add(self):
        pass

    def play(self):
        if not self.term and self.pause:
            self.player.pause = False
            self.pause = False
            return
        if self.term:
            self.play_pre()
        print('play.1')
        if self.serial is not None:
            self.thread.start()
            time.sleep(2)
        self.player.start()
        print('play.2')

    def play_pre(self):
        self.term, self.pause = False, False
        self.thread, self.serial = None, None
        self.ch_lst, self.ev_lst = None, None
        self.orche, self.robin = None, None
        self.angle = 90
        print('play_pre.1')
        self.gau_1.setValue(0)
        print('play_pre.2')
        music = (self.cbb_2.currentText()).strip()
        confs = self.confs
        events = song.songs[music]['events']
        confs_, vr_dct = dict(), dict()
        list_1 = list(self.value)
        list_2 = []
        for ins in list_1:
            confs_[ins] = confs[ins]
            vr_dct[ins] = [ev[2] for ev in events[ins]]
        for i, ev in enumerate(list(events)):
            list_2.append([i, ev])
        self.ch_lst = [ch for ch in list_2 if ch[1] in list_1]
        self.ev_lst = []
        for ch in self.ch_lst:
            self.ev_lst = self.ev_lst + events[ch[1]]
        self.orche = tree.InstrumentContainer()
        self.orche.create(confs_)
        self.robin = tree.Notifier(vr_dct)
        self.ev_lst = sorted(self.ev_lst)
        self.player = PlayerThread(self.beat, self.ev_lst)
        self.player.init.connect(self.init_of_play)
        self.player.move.connect(self.move_of_play)
        self.player.play.connect(self.play_of_play)
        print('play_pre.4')
        com = (self.set_a.currentText()).strip()
        fre = int((self.set_b.currentText()).strip())
        try:
            self.serial = serial.Serial(com, fre, timeout=0.5)
        except serial.serialutil.SerialException:
            cap = '传感器串口错误'
            meg = '请选择正确的串口，并保证开发板连接正常'
            QMessageBox.critical(self, cap, meg, QMessageBox.Ok, QMessageBox.Ok)
            # self.kill()
            return
        self.thread = SerialThread(self.serial, self.value, self.orche)
        self.thread.kill.connect(self.kill)
        self.thread.stop.connect(self.stop_of_play)
        self.thread.mdfy.connect(self.mdfy_of_play)
        print('play_pre.5')

    def init_of_play(self):
        for ch in self.ch_lst:
            ins = ch[1].split('_')[-1]
            idx = util.instr_2[ins] - 1
            self.output.set_instrument(idx, channel=ch[0])
            n1, n2 = self.chan_2[ch[0]], self.chan_0[ch[0]]
            self.gauges[n1].setValue(self.value[n2] * 100)

    def move_of_play(self, now, span):
        self.gau_1.setValue(now / span * 100)

    def play_of_play(self, event):
        value = self.value[self.chan_0[event[3]]]
        val = int(event[2] * value)
        cov = self.robin.update(self.chan_0[event[3]], val)
        if self.output is not None:
            self.output.note_on(event[1], min(val, 127), channel=event[3])
            self.gau_2.setValue(min(val, 127))
            num = self.chan_2[event[3]]
            if val > 0:
                self.gauges[num].setValue(value * 100, cov)
                self.gauges[num + 1].setValue(min(val, 127), cov)
            else:
                self.gauges[num].setValue(value * 100)
                self.gauges[num + 1].setValue(min(val, 127))

    def kill(self, close=False):
        self.term = True
        for note in range(0, 128):
            for chan in range(0, 16):
                self.output.note_off(note, channel=chan)
        print("main.kill")
        if self.player is not None and not self.player.isFinished():
            self.player.term = True
            self.player.terminate()
        if self.thread is not None and not self.thread.isFinished():
            self.thread.terminate()
        if self.serial is not None:
            self.serial.close()
            self.serial.__del__()
        self.serial = None
        self.thread, self.player = None, None
        self.ch_lst, self.ev_lst = None, None
        if not close:
            for gauge in self.gauges:
                gauge.setValue(0)
            self.gau_1.setValue(0)
            self.gau_2.setValue(0)

    def stop(self):
        self.pause = True
        if self.player is not None:
            self.player.pause = True

    def stop_of_play(self, flg):
        self.pause = flg
        if self.pause:
            self.stop()
        elif self.player is not None:
            self.player.pause = flg

    def mdfy_of_play(self, key, val):
        self.value[key] = val
        grp = self.findChild(QLabel, key)
        grp.updateRatio(val)
        lbl = (self.cbb_3.currentText()).strip()
        if lbl == key:
            self.btn_1.setText('调整 : %.2f' % self.value[key])

    def ctr(self):
        dialog = SingleSldDialog('节拍快慢调整', self.beat, 20, 2000)
        dialog.signal.connect(self.ctr_func)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()

    def ctr_func(self, val):
        self.beat = int(val)
        self.btn_7.setText('节拍 : %d' % self.beat)
        if self.player is not None and not self.player.isFinished():
            self.player.beat = self.beat


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

    # app = QApplication(sys.argv)
    # win = MainWindow()
    # win.show()
    # app.exec_()
