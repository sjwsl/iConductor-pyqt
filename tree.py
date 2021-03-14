import numpy as np


class Instrument:

    # @param name 乐器名称
    # @param r 极径
    # @param c 极角
    def __init__(self, name, r, c):
        self.name = name
        self.r = r
        self.c = c


class InstrumentContainer:
    def __init__(self):
        self.ilist = []
        self.idict = dict()

    # 每次加入，传一个乐器
    # @param instrument 加入的乐器
    def add(self, instrument):
        self.ilist += [instrument]

    # 每次加入，传一个乐器列表
    # @param instrument_list 要加入的乐器列表
    def create(self, instrument_dict):
        for i, ins in enumerate(list(instrument_dict)):
            r, c = instrument_dict[ins][0], instrument_dict[ins][1]
            instrument = Instrument(ins, r, c)
            self.add(instrument)
            self.idict[ins] = i

    # 每次搜索，传入极径、极角和存储结果列表
    # @param r 极径
    # @param c 极角
    def ask(self, r, c):
        ask_list = []
        for instrument in self.ilist:
            if instrument.c < c - 25 or instrument.c > c + 25:
                continue
            if instrument.r < r - 100 or instrument.r > r + 100:
                continue
            ask_list += [instrument.name]
        return ask_list

    def update(self, ins, r, c):
        self.ilist[self.idict[ins]].r = r
        self.ilist[self.idict[ins]].c = c


def test():
    instruments = [Instrument('1_钢琴', 70, 30),
                   Instrument('1_立式钢琴', 100, 160),
                   Instrument('2_钢琴', 100, 97),
                   Instrument('1_合成弦1', 70, 105)]
    container = InstrumentContainer()
    for instrument in instruments:
        container.add(instrument)
    ask_list = container.ask(90, 100)
    cnt = 0
    for s in ask_list:
        cnt = cnt + 1
        print(s, end='')
        if cnt == len(ask_list):
            print()
        else:
            print(", ", end='')

#
# test()


class Notifier(object):

    def __init__(self, notes, r=5):
        self.notes, self.r = notes, r
        self.steps, self.paras = dict(), dict()
        for ins in list(notes):
            self.steps[ins] = 0
            self.paras[ins] = [0] * r
            self.notes[ins] = np.pad(self.notes[ins], (r-1, ), 'constant', constant_values=(0, 0))

    def update(self, ins, val):
        notes = self.notes[ins][self.steps[ins]: self.steps[ins] + self.r]
        self.steps[ins] = self.steps[ins] + 1
        self.paras[ins].append(val), self.paras[ins].pop(0)
        mat = np.cov([notes, self.paras[ins]])
        cov = mat[0][1] / np.sqrt(mat[0][0] * mat[1][1] + 0.01)
        return cov
