import random
import time
import string
import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow
)
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import pyqtSignal
# from PyQt5.uic import loadUi

from ui.gui import Ui_Form

class Window(QMainWindow, Ui_Form):
    keyPressed = QtCore.pyqtSignal(QtCore.QEvent)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.keyPressed.connect(self.on_key)

        self.chosen_word = random.choice(wordlist)
        self.won = False

        with open('ui/html') as f:
            self.html = f.read()

        self.T0 = [self.T01, self.T02, self.T03, self.T04, self.T05]
        self.T1 = [self.T11, self.T12, self.T13, self.T14, self.T15]
        self.T2 = [self.T21, self.T22, self.T23, self.T24, self.T25]
        self.T3 = [self.T31, self.T32, self.T33, self.T34, self.T35]
        self.T4 = [self.T41, self.T42, self.T43, self.T44, self.T45]
        self.T5 = [self.T51, self.T52, self.T53, self.T54, self.T55]
        self.T6 = [self.T61, self.T62, self.T63, self.T64, self.T65]
        self.T = self.T1 + self.T2 + self.T3 + self.T4 + self.T5 + self.T6 
        self.new_word = ''
        # print(T1)
        # for i in T1:
        #     i.setText('B')
        # self.show()
        # self.connectSignalsSlots()
        # self.keyPressEvent = self.keyPressEvent
        # self.show()
        # self.connect(keyPre)
        # self.connectSignalsSlots()

    @pyqtSlot()
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.keyPressed.emit(event)

    def reset(self):
        for i in self.T1 + self.T2 + self.T3 + self.T4 + self.T5 + self.T6:
            i.clear()
            self.color(i, '')
        self.chosen_word = random.choice(wordlist)
        print('reset')
        self.won = False

    def on_key(self, event):
        new_letter = None

        if event.key() == 16777220 and (self.T11.toPlainText() and self.T21.toPlainText() and self.T31.toPlainText()
                and self.T41.toPlainText() and self.T51.toPlainText() and self.T61.toPlainText()):
            return

        if 65 <= event.key() <= 90: # New Letter
            new_letter = chr(event.key())

        if event.key() == 16777219: # Backspace
            self.new_word = self.new_word[:-1]
            for t in reversed(self.T0):
                if t.toPlainText():
                    t.setText('')
                    break
            return

        if event.key() == 16777220: # Enter
            if self.won:
                self.reset()
            print(self.new_word)
            if len(self.new_word) != 5:
                return

            if self.chosen_word == self.new_word:
                self.won = True

            result = logic(self.new_word, self.chosen_word)
            if not result:
                return
            else:
                print(result)

            if not self.T11.toPlainText():
                T = self.T1
            elif not self.T21.toPlainText():
                T = self.T2
            elif not self.T31.toPlainText():
                T = self.T3
            elif not self.T41.toPlainText():
                T = self.T4
            elif not self.T51.toPlainText():
                T = self.T5
            elif not self.T61.toPlainText():
                T = self.T6
            else:
                return


            for i in range(5):
                html = self.html.replace('</p', self.new_word[i] + '</p')
                T[i].setHtml(html)
                self.color(T[i], result[i + 1])
                self.T0[i].clear()
            self.new_word = ''

        if new_letter and len(self.new_word) < 5 and not self.won:
                self.new_word += new_letter
                html = self.html.replace('</p', new_letter + '</p')
                if not self.T01.toPlainText():
                    self.T01.setHtml(html)
                elif not self.T02.toPlainText():
                    self.T02.setText(html)
                elif not self.T03.toPlainText():
                    self.T03.setText(html)
                elif not self.T04.toPlainText():
                    self.T04.setText(html)
                elif not self.T05.toPlainText():
                    self.T05.setText(html)
                return

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

    # def keyPressEvent(self, e):
    #     if e.key():
    #         # print(e.key().toString)
    #         # print(e.key())
    #         if 65 <= e.key() <= 90:
    #             print(chr(e.key()))
    #         self.T11.setAcceptRichText(True)
    #         self.T11.clear()
    #         self.T11.setText('AAAAAAAAAAAAA')
    #         # self.T11.repaint()
    #         # qApp.processEvents()
    #         print(self.T11.toPlainText())
    #         # self.T11.setText('A')
    #         # self.T11.setPlainText('A')
    #         # self.T11.insertPlainText('A')
    #         # self.T11.append('A')
    #         # self.T11.setStyleSheet('color: blue')
    #         # self.T11.setText('AAAAA')
    #
    #         # self.showMaximized()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)



def wordlist_loader():
    with open('words.txt') as w:
        wordlist = w.read()
        return wordlist.splitlines()

# def inp():
#     try:
#         return input('input word:').upper()
#     except EOFError:
#         pass
#     except KeyboardInterrupt:
#         pass
#     except SystemExit:
#         pass


def logic(current_word, chosen_word):
    # input_list = []
    # if rand_word:
    #     chosen_word = random.choice(wordlist)
    print(chosen_word)
    # current_word = ''
    correct_letters = {}
    print(current_word)


    if current_word not in wordlist:
        print('not in wordlist')
        return

    if current_word == chosen_word:
        print('YOU WON!')


    for l in range(5):

        if l+1 not in correct_letters.keys():
            correct_letters[l + 1] = ''

        if current_word[l] == chosen_word[l]:
            # correct_letters[l + 1] = current_word[l]
            correct_letters[l + 1] = 'green'
        elif current_word[l] in chosen_word:
            correct_letters[l + 1] = 'yellow'


    return correct_letters


if __name__ == "__main__":
    wordlist = wordlist_loader()

    app = QApplication([])
    MainWindow = QMainWindow()
    win = Window()
    # win.setupUi(MainWindow)
    win.show()
    import sys
    sys.excepthook = except_hook
    sys.exit(app.exec())
