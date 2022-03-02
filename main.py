import random
import time
import json
import threading

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QTableWidget, QTableWidgetItem
)

from ui.gui import Ui_Form
from ui.stats import Ui_Dialog
from ui.info import Ui_Info

class Window(QMainWindow, Ui_Form):
    keyPressed = QtCore.pyqtSignal(QtCore.QEvent)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.keyPressed.connect(self.on_key)
        self.status.setVisible(False)
        self.screen_width = self.frameGeometry().width()
        self.invalid_width = self.status.width()
        self.done = True

        self.palette_r = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        self.palette_r.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)

        self.palette_g = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(78, 184, 48))
        self.palette_g.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)

        self.status.setPalette(self.palette_r)

        self.used_letters = set()
        self.used_words = []

        self.chosen_word = random.choice(wordlist)
        self.won = False

        with open('ui/format.html') as f:
            self.html = f.read()

        buttons = [[self.info, './ui/info-32.png'], [self.hint, './ui/hint-32.png'], [self.stats, './ui/stats-32.png']]
        for b in buttons:
            b[0].setIcon(QtGui.QIcon(b[1]))
            b[0].setIconSize(QtCore.QSize(24,24))
            b[0].setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.info.clicked.connect(self.info_dialog)
        self.stats.clicked.connect(self.stats_dialog)
        self.hint.clicked.connect(self.hint_apply)

        self.T0 = [self.T01, self.T02, self.T03, self.T04, self.T05]
        self.T1 = [self.T11, self.T12, self.T13, self.T14, self.T15]
        self.T2 = [self.T21, self.T22, self.T23, self.T24, self.T25]
        self.T3 = [self.T31, self.T32, self.T33, self.T34, self.T35]
        self.T4 = [self.T41, self.T42, self.T43, self.T44, self.T45]
        self.T5 = [self.T51, self.T52, self.T53, self.T54, self.T55]
        self.T6 = [self.T61, self.T62, self.T63, self.T64, self.T65]
        self.T = {1:self.T1, 2:self.T2, 3:self.T3, 4:self.T4, 5:self.T5, 6:self.T6}
        self.new_word = ''

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        statistics_saver(statistics)
        print('END!')

    # @pyqtSlot()
    def keyPressEvent(self, event):
        self.keyPressed.emit(event)

    def reset(self):
        for word in self.T.values():
            for letter in word:
                letter.clear()
                self.color(letter, '')
        for letter in self.T0:
            letter.clear()
            self.color(letter, '')
        self.chosen_word = random.choice(wordlist)
        self.used_words = []
        self.used_letters = set()
        self.won = False

    def add_word(self):
        if self.won:
            self.reset()

        if len(self.new_word) != 5:
            return

        if self.chosen_word == self.new_word:
            self.won = True
            statistics['Times Won'] += 1
            if statistics['Best guess count']:
                statistics['Best guess count'] = min(statistics['Best guess count'], len(self.used_words) + 1)
            else:
                statistics['Best guess count'] = len(self.used_words) + 1
            th = threading.Thread(target=statistics_saver, args=(statistics, ))
            th.start()
            self.status.setPalette(self.palette_g)
            self.status.setText('You Won !, press Enter to play again')
            self.status.setVisible(True)

        result = logic(self.new_word, self.chosen_word)
        if not result:
            self.status.setPalette(self.palette_r)
            self.status.setText('not a word !')
            self.status.setVisible(True)
            y = self.status.pos().y()
            for i in range(4):
                if i % 2:
                    self.status.move(int((self.screen_width - self.invalid_width) / 2 + 5), y)
                else:
                    self.status.move(int((self.screen_width - self.invalid_width) / 2 - 5), y)
                QApplication.processEvents()
                time.sleep(0.05)
            self.status.move(int((self.screen_width - self.invalid_width) / 2), y)
            return

        self.used_letters.update(self.new_word)
        self.used_words.append(self.new_word)

        T = self.T[len(self.used_words)]
        statistics['Guesses'] += 1

        for i in range(5):
            html = self.html.replace('</p', self.new_word[i] + '</p')
            T[i].setHtml(html)
            self.color(T[i], result[i])
        [x.clear() for x in self.T0]
        self.new_word = ''

        if self.chosen_word != self.new_word and len(self.used_words) == 6 and not self.won:
            statistics['Times Lost'] += 1
            th = threading.Thread(target=statistics_saver, args=(statistics,))
            th.start()
            self.done = False
            for i in range(5):
                html = self.html.replace('</p', self.chosen_word[i] + '</p')
                self.T0[i].setHtml(html)
                self.color(self.T0[i], 'green')
                QApplication.processEvents()
                time.sleep(0.3)
            self.done = True

    def hint_apply(self):
        statistics['Hints Used'] += 1
        inter_len = 5
        random.shuffle(wordlist)
        for w in wordlist:
            inter = len(set(w).intersection(self.used_letters))
            if inter_len > inter and w not in self.used_words:
                inter_len = inter
                self.new_word = w
            if inter == 0:
                break
        self.add_word()

    def info_dialog(self):
        dialog2 = QDialog()
        dialog2.ui = Ui_Info()
        dialog2.ui.setupUi(dialog2)
        dialog2.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialog2.setWindowFlags(QtCore.Qt.Popup)

        # center the dialog
        point = self.rect().center()
        global_point = self.mapToGlobal(point)
        dialog2.move(global_point + QtCore.QPoint(-165, -240))

        dialog2.exec()

    def stats_dialog(self):
        dialog = QDialog()
        dialog.ui = Ui_Dialog()
        dialog.ui.setupUi(dialog)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialog.setWindowFlags(QtCore.Qt.Popup)

        w = dialog.width()
        dialog.ui.tableWidget.setColumnWidth(0, w * 2 / 3)
        dialog.ui.tableWidget.setColumnWidth(1, w / 3)

        for n, key in enumerate(statistics.keys()):
            newitem = QTableWidgetItem(key)
            dialog.ui.tableWidget.setItem(n, 0, newitem)
            newitem = QTableWidgetItem(str(statistics[key]))
            dialog.ui.tableWidget.setItem(n, 1, newitem)

        # center the dialog
        point = self.rect().center()
        global_point = self.mapToGlobal(point)
        dialog.move(global_point + QtCore.QPoint(-130, -200))

        dialog.exec()
        self.activateWindow()

    def on_key(self, event):
        new_letter = None
        self.status.setVisible(False)
        if not self.done:
            return

        if event.key() in [16777220, 16777217] and len(self.used_words) == 6:
            self.reset()
            return
        elif len(self.used_words) == 6:
            return
        elif 65 <= event.key() <= 90:  # New Letter
            new_letter = chr(event.key())
            if len(self.new_word) < 5 and not self.won:
                self.new_word += new_letter
                html = self.html.replace('</p', new_letter + '</p')
                self.T0[len(self.new_word) - 1].setText(html)
            return

        elif event.key() == 16777219:  # `Backspace`
            self.new_word = self.new_word[:-1]
            self.T0[len(self.new_word)].setText('')
            return
        elif event.key() == 16777220:  # `Enter`
            self.add_word()
        elif event.key() == 16777217:  # hint `TAB`
            self.hint_apply()
        elif event.key() == 96:  # stats `tilde`
            self.stats_dialog()
        elif event.key() == 16777264:  # Help `F1`
            self.info_dialog()


    def color(self, letter, color):
        palette = QtGui.QPalette()
        if not color:
            brush = QtGui.QBrush(QtGui.QColor(160, 160, 160))
        elif color == 'yellow':
            brush = QtGui.QBrush(QtGui.QColor(243, 194, 16))
        elif color == 'green':
            brush = QtGui.QBrush(QtGui.QColor(78, 184, 48))

        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)

        letter.setPalette(palette)

def wordlist_loader():
    with open('words.txt', 'r') as w:
        words = w.read()
        return words.splitlines()

def statistics_loader():
    try:
        with open('stats.txt', 'r') as s:
            return json.load(s)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return {'Times Played': 0, 'Times Won': 0, 'Times Lost': 0, 'Won %': 0, 'Hints Used': 0,
                'Guesses': 0, 'Average guess count': 0, 'Best guess count': None}

def statistics_saver(statistics):
    statistics['Times Played'] = statistics['Times Won'] + statistics['Times Lost']
    if statistics['Times Played']:
        statistics['Won %'] = round(statistics['Times Won'] / statistics['Times Played'] * 100)
        statistics['Average guess count'] = round(statistics['Guesses'] / statistics['Times Played'], 2)
    else:
        statistics['Won %'], statistics['Average guess count'] = 0, 0

    with open('stats.txt', 'w') as s:
        s.write(json.dumps(statistics))


def logic(current_word, chosen_word) -> dict:
    correct_letters = {}
    matches = ''
    if current_word not in wordlist:
        return

    for l in range(5):
        if current_word[l] == chosen_word[l]:
            correct_letters[l] = 'green'
            matches += current_word[l]
    for l in range(5):
        if l not in correct_letters.keys():
            correct_letters[l] = ''
        if current_word[l] in chosen_word and correct_letters[l] != 'green':
            r_count = current_word[:l+1].count(current_word[l])
            h_count = chosen_word.count(current_word[l])
            are_green = matches.count(current_word[l])
            if r_count <= h_count - are_green:
                correct_letters[l] = 'yellow'
            else:
                correct_letters[l] = ''

    return correct_letters

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == "__main__":
    wordlist = wordlist_loader()
    statistics = statistics_loader()
    app = QApplication([])
    MainWindow = QMainWindow()
    win = Window()
    win.show()
    import sys
    sys.excepthook = except_hook
    sys.exit(app.exec())
