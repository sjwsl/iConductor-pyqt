import numpy as np

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


instr_1 = {'钢琴类': 1, '其他类': 2, '风琴类': 3, '吉他类': 4, '贝斯类': 5, '弦乐器': 6,
           '合唱组': 7, '铜管乐器': 8, '簧片乐器': 9, '管鸣乐器': 10, '合成领奏': 11,
           '合成长音': 12, '合成效果': 13, '民间乐器': 14, '打击乐器': 15, '音响效果': 16}
instr_2 = {'钢琴': 1, '立式钢琴': 2, '电钢琴': 3, '酒吧钢琴': 4, '电子琴': 5, '电子琴+合唱': 6, '羽管键琴': 7, '古钢琴': 8,
           '钢片琴': 9, '钟琴': 10, '音乐盒': 11, '电颤琴': 12, '马林巴琴': 13, '木琴': 14, '管钟': 15, '洋琴': 16,
           '击杆风琴': 17, '打击风琴': 18, '摇滚风琴': 19, '教堂风琴': 20, '簧风琴': 21, '手风琴': 22, '口琴': 23, '小手风琴': 24,
           '尼龙丝吉他': 25, '钢丝吉他': 26, '爵士吉他': 27, '清音吉他': 28, '弱音吉他': 29, '过载吉他': 30, '失真吉他': 31, '吉他泛音': 32,
           '原声贝斯': 33, '手弹贝斯': 34, '拨片贝斯': 35, '无品贝司': 36, '拍击贝斯1': 37, '拍击贝斯2': 38, '合成贝斯1': 39, '合成贝斯2': 40,
           '小提琴': 41, '中提琴': 42, '大提琴': 43, '低音提琴': 44, '颤音弦': 45, '拨弦': 46, '竖琴': 47, '定音鼓': 48,
           '弦': 49, '慢弦': 50, '合成弦1': 51, '合成弦2': 52, '人声合唱啊': 53, '人声嘟': 54, '合成人声': 55, '管弦乐齐奏': 56,
           '小号': 57, '长号': 58, '大号': 59, '弱音小号': 60, '圆号': 61, '铜管': 62, '合成铜管1': 63, '合成铜管2': 64,
           '高音萨克斯': 65, '中音萨克斯': 66, '次中音萨克斯': 67, '上低音萨克斯': 68, '双簧管': 69, '英国管': 70, '巴松管': 71, '单簧管': 72,
           '短笛': 73, '长笛': 74, '竖笛': 75, '排箫': 76, '瓶木管': 77, '尺八': 78, '口哨': 79, '奥卡雷那': 80,
           '方波': 81, '锯齿波': 82, '汽笛风琴': 83, '领奏': 84, '沙朗主奏': 85, '人声独唱': 86, '五度管乐': 87, '贝斯主奏': 88,
           '幻想曲': 89, '温暖背景': 90, '复合成': 91, '太空音': 92, '弧形波': 93, '金属背景': 94, '光晕背景': 95, '曲线波背景': 96,
           '冰雨': 97, '电影声效': 98, '水晶': 99, '气氛': 100, '轻柔': 101, '地精': 102, '回声滴答': 103, '星辰大海': 104,
           '西塔琴': 105, '班卓琴': 106, '三弦琴': 107, '十三弦古筝': 108, '克林巴琴': 109, '苏格兰风笛': 110, '古提琴': 111, '山奈': 112,
           '铃铛': 113, '摇摆舞铃': 114, '钢鼓': 115, '木块': 116, '太鼓': 117, '通通鼓': 118, '合成鼓': 119, '铜钹': 120,
           '吉他杂音': 121, '呼吸音': 122, '海浪': 123, '鸟': 124, '电话': 125, '直升机': 126, '掌声': 127, '枪射击': 128}


def getBox(parent, pos, size):
    box = QGroupBox(parent)
    box.setGeometry(QRect(pos[0], pos[1], size[0], size[1]))
    return box


def getLine(parent, pos, size, style):
    line = QFrame(parent)
    line.setGeometry(QRect(pos[0], pos[1], size[0], size[1]))
    line.setFrameShape(style)
    line.setFrameShadow(QFrame.Sunken)
    return line


def getPanel(parent, pos, size):
    panel = QFrame(parent)
    panel.setGeometry(QRect(pos[0], pos[1], size[0], size[1]))
    # panel.setFrameShape(QFrame.Panel)
    # panel.setFrameShadow(QFrame.Sunken)
    panel.setStyleSheet('QFrame{background-color:#ffffff;}')
    return panel


def getLabel(parent, pos, size, label):
    lbl = QLabel(label, parent)
    lbl.setFont(QFont("Dengxian"))
    lbl.setGeometry(QRect(pos[0], pos[1], size[0], size[1]))
    return lbl


def getAdaptiveLabel(parent, mid, label):
    lbl = QLabel(label, parent)
    lbl.setFont(QFont("Dengxian"))
    lbl.adjustSize()
    w, h = lbl.size().width(), lbl.size().height()
    x, y = mid[0] - w // 2, mid[1] - h // 2
    lbl.setGeometry(QRect(x, y, w, h))
    return lbl


def getPushButton(parent, pos, size, label):
    btn = QPushButton(label, parent)
    btn.setFont(QFont("Dengxian"))
    btn.setGeometry(QRect(pos[0], pos[1], size[0], size[1]))
    return btn


def getComboBox(parent, pos, size, idx, lst):
    cbb = QComboBox(parent)
    cbb.setFont(QFont("Dengxian"))
    cbb.setGeometry(QRect(pos[0], pos[1], size[0], size[1]))
    cbb.insertItems(idx, lst)
    return cbb


def getSlider(parent, pos, size, ran=(0, 99), style=Qt.Horizontal, focus=Qt.NoFocus):
    sld = QSlider(style, parent)
    sld.setFocusPolicy(focus)
    sld.setFont(QFont("Dengxian"))
    sld.setGeometry(QRect(pos[0], pos[1], size[0], size[1]))
    sld.setRange(ran[0], ran[1])
    return sld


def getProgressBar(parent, pos, size, ran=(0, 99), focus=Qt.NoFocus):
    pbr = QProgressBar(parent)
    pbr.setFocusPolicy(focus)
    pbr.setTextVisible(False)
    pbr.setFont(QFont("Dengxian"))
    pbr.setGeometry(QRect(pos[0], pos[1], size[0], size[1]))
    pbr.setRange(ran[0], ran[1])
    return pbr


color = {'r': QColor(180, 48, 19), 'g': QColor(19, 180, 48), 'b': QColor(48, 19, 180)}


class QGauge(QWidget):
    def __init__(self, parent, minw, minh, value, lst):
        assert len(lst) in [2, 4]
        super().__init__(parent=parent)
        self.setMinimumSize(minw, minh)
        self.value, self.range, self.color = value, lst, 'g'

    def setRange(self, lst):
        assert len(lst) in [2, 4]
        self.range = lst

    def setValue(self, value, cov=1):
        self.value = value
        self.color = 'g' if cov > 0.9 else ('b' if cov > 0.5 else 'r')
        self.repaint()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        size = self.size()
        w, h = size.width(), size.height()
        till = (self.value - self.range[0]) / (self.range[-1] - self.range[0])
        till = int(w * till)

        qp.setPen(color[self.color])
        qp.setBrush(color[self.color])
        qp.drawRect(0, 0, till, h)

        pen = QPen(QColor(20, 20, 20), 0.5, Qt.SolidLine)
        qp.setPen(pen)
        qp.setBrush(Qt.NoBrush)
        qp.drawRect(0, 0, w-1, h-1)


def getGauge(parent, pos, size, value, lst):
    if len(lst) > 4 or len(lst) < 2:
        raise AttributeError
    sld = QGauge(parent, size[0], size[1], value, lst)
    sld.setFont(QFont("Dengxian"))
    sld.setGeometry(QRect(pos[0], pos[1], size[0], size[1]))
    return sld


def str_list_indent(lst):
    for i in range(len(lst)):
        lst[i] = ' ' + lst[i]
    return lst


jpg_dict = {0: 'ins-1-8.png', 1: 'ins-9-16.png', 2: 'ins-17-24.png', 3: 'ins-25-32.png',
            4: 'ins-33-40.png', 5: 'ins-41-48.png', 6: 'ins-49-56.png', 7: 'ins-57-64.png',
            8: 'ins-65-72.png', 9: 'ins-73-80.png', 10: 'ins-81-112.png', 11: 'ins-81-112.png',
            12: 'ins-81-112.png', 13: 'ins-81-112.png', 14: 'ins-113-128.png', 15: 'ins-113-128.png', }


class QDraggableLabel(QLabel):
    signal = pyqtSignal(str, int, int)

    def __init__(self, title, mid, parent, ratio=1):
        super().__init__(parent=parent)
        self.mid = [mid[0], mid[1]]
        self.ratio = ratio
        self.title = title.split('_')[-1]
        w, h = 60 * ratio, 30 * ratio + max(48, 30 * ratio)
        x, y = mid[0] - w // 2, mid[1] - max(48, 30 * ratio)
        self.setGeometry(QRect(x, y, w, h))
        self.setStyleSheet('background-color: rgba(255,255,255,0);')
        w, h = 60 * ratio, 60 * ratio
        x, y = 0, max(48 - h // 2, 0)
        self.label = QLabel(title, self)
        self.label.setFont(QFont("Dengxian"))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(QRect(x, y, w, h))
        self.label.setStyleSheet('background-color: rgba(255,185,195,0.8); border: 0px; border-style:none; '
                                 'padding: 5px; border-radius: %dpx;' % (30 * self.ratio))
        self.pic = QLabel(self)
        idx = (instr_2[self.title] - 1) // 8
        self.pic.setPixmap(QPixmap(jpg_dict[idx]))
        self.pic.setStyleSheet('background-color: rgba(255,255,255,0);')
        self.pic.setGeometry(QRect(30 * ratio - 20, max(0, 30 * ratio - 48), 40, 40))

    def mousePressEvent(self, e):
        print("ppp", e.pos())
        # self.iniDragCor[0] = e.x()
        # self.iniDragCor[1] = e.y()

    def mouseMoveEvent(self, e):
        x = e.x() - self.size().width() // 2
        y = e.y() - self.size().height() // 2
        self.move(self.mapToParent(QPoint(x, y)))
        self.mid[0], self.mid[1] = self.mid[0] + x, self.mid[1] + y
        self.signal.emit(self.label.text(), self.mid[0], self.mid[1])

    def updateRatio(self, ratio):
        if 60 * ratio < 40:
            return
        w, h = 60 * ratio, 30 * ratio + max(48, 30 * ratio)
        x, y = self.mid[0] - w // 2, self.mid[1] - max(48, 30 * ratio)
        self.setGeometry(QRect(x, y, w, h))
        self.setGeometry(QRect(x, y, w, h))
        self.setStyleSheet('background-color: rgba(255,255,255,0);')
        w, h = 60 * ratio, 60 * ratio
        x, y = 0, max(48 - h // 2, 0)
        self.label.setGeometry(QRect(x, y, w, h))
        self.label.setFixedSize(QSize(60 * ratio, 60 * ratio))
        self.label.setStyleSheet('background-color: rgba(255,185,195,0.8); border: 0px; border-style:none; '
                                 'padding: 3px; border-radius: %dpx;' % (self.label.size().width() // 2))
        self.pic.setGeometry(QRect(30 * ratio - 20, max(0, 30 * ratio - 48), 40, 40))
        self.ratio = ratio


def getInstrumentLabel(parent, mid, label, ratio=1):
    lbl = QDraggableLabel(label, mid, parent, ratio)
    return lbl

