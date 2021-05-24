# BorisM138
import sys
import sqlite3
import datetime
# Импортируем из PyQt5.QtWidgets классы для создания приложения и виджет
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout
from PyQt5.QtWidgets import QLabel, QPushButton, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QFileDialog, QInputDialog


class Error(Exception):
    pass


class nameError(Error):
    pass


class Example(QWidget):
    def __init__(self):
        # Надо не забыть вызвать инициализатор базового класса
        super().__init__()
        # В метод initUI() будем выносить всю настройку интерфейса,
        # чтобы не перегружать инициализатор
        self.initUI()

    def initUI(self):
        self.today_date = datetime.date.today()
        # Зададим размер и положение нашего виджета,
        self.setGeometry(0, 0, 600, 600)
        # А также его заголовок
        self.setWindowTitle('Редактор заметок')

        self.text_edit = QTextEdit(self)
        self.text_edit.resize(540, 310)
        self.text_edit.move(30, 30)
        self.text_edit.setReadOnly(True)

        self.grid_layout = QGridLayout()
        self.central_widget = QWidget(self)
        self.central_widget.setLayout(self.grid_layout)
        self.tableWidget = QTableWidget(self)  # Создаём таблицу
        self.tableWidget.move(30, 410)
        self.tableWidget.setColumnCount(2)     # Устанавливаем три колонки
        self.tableWidget.setRowCount(1)        # и одну строку в таблице

        self.btn_open = QPushButton('ОТКРЫТЬ', self)
        self.btn_open.resize(90, 30)
        self.btn_open.move(30, 370)
        self.btn_open.clicked.connect(self.openFile)

        self.btn_new = QPushButton('НОВЫЙ', self)
        self.btn_new.resize(90, 30)
        self.btn_new.move(150, 370)
        self.btn_new.clicked.connect(self.newFile)

        self.btn_save = QPushButton('СОХРАНИТЬ', self)
        self.btn_save.resize(90, 30)
        self.btn_save.move(360, 370)
        self.btn_save.clicked.connect(self.saveFile)
        self.btn_save.setEnabled(False)

        self.btn_today = QPushButton('СЕГОДНЯ', self)
        self.btn_today.resize(90, 30)
        self.btn_today.move(480, 370)
        self.btn_today.clicked.connect(self.todayFile)

        self.date_label = QLabel(self)
        self.date_label.setText(str(self.today_date))
        self.date_label.move(490, 405)

        self.error_label = QLabel(self)
        self.error_label.move(350, 485)
        self.error_label.resize(130, 200)

        self.btn_date = QPushButton('ПО ДАТЕ', self)
        self.btn_date.resize(90, 30)
        self.btn_date.move(480, 430)
        self.btn_date.clicked.connect(self.dateFile)

        self.btn_date = QPushButton('ПО ИМЕНИ', self)
        self.btn_date.resize(90, 30)
        self.btn_date.move(480, 490)
        self.btn_date.clicked.connect(self.nameFile)

        self.btn_date = QPushButton('УДАЛЕНИЕ', self)
        self.btn_date.resize(90, 30)
        self.btn_date.move(360, 430)
        self.btn_date.clicked.connect(self.deleteFile)

        self.con = sqlite3.connect("notes.sqlite")
        self.titles = None

    def todayFile(self):
        try:
            cur = self.con.cursor()
            # Получили результат запроса, который ввели в текстовое поле
            result = cur.execute(f"""
            SELECT * FROM notes
            WHERE date = '{str(self.today_date)}'""").fetchall()
            # Заполнили размеры таблицы
            self.tableWidget.setRowCount(len(result))
            # Если запись не нашлась, то не будем ничего делать
            self.tableWidget.setColumnCount(len(result[0]))
            self.titles = [description[0] for description in cur.description]
            # Заполнили таблицу полученными элементами
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        except:
            self.error = 'На сегодня нет заметок'
            self.error_label.setText(str(self.error))




    def openFile(self):
        try:
            self.file_name = QFileDialog.getOpenFileName(
                self,
                'Выбрать заметку',
                '',
                'Заметка (*.txt);;Заметка (*.txt);;Все файлы (*)')[0]
            self.file_name = self.file_name.split('/')[-1]
            open_file = open(str(self.file_name), "r")
            open_file_text = open_file.read()
            self.text_edit.setReadOnly(False)
            self.text_edit.setText(open_file_text)
            self.error_label.setText('')
            self.btn_save.setEnabled(True)
        except FileNotFoundError:
            self.error = 'Выберите файл!'
            self.error_label.setText(str(self.error))

    def newFile(self):
        try:
            name, ok_pressed = QInputDialog.getText(
                self,
                "Введите имя заметки",
                "Как назовём?")
            if ok_pressed:
                if '/' in name:
                    raise nameError
                self.file_name = str(name) + '.txt'
                self.file_name = self.file_name.split('/')[-1]
                self.text_edit.setReadOnly(False)
                self.text_edit.setText('')
                self.error_label.setText('')
                self.btn_save.setEnabled(True)
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            self.error = 'Назовите файл!'
            self.error_label.setText(str(self.error))
            self.text_edit.setReadOnly(True)
        except nameError:
            self.error = 'Имя без "/"'
            self.error_label.setText(str(self.error))

    def saveFile(self):
        cur = self.con.cursor()
        file_deaddate, ok_pressed = QInputDialog.getText(
            self,
            "Когда требуется заметка?",
            "гггг-мм-дд")
        if ok_pressed:
            self.file_deaddate = file_deaddate
        texteditor_text = self.text_edit.toPlainText()
        saved_file = open(self.file_name, 'w')
        saved_file.write(texteditor_text)
        if cur.execute(f"""
        SELECT * FROM notes
        WHERE note = '{self.file_name}'
        """).fetchall():
            cur.execute(f"""
            UPDATE notes
            SET date = '{self.file_deaddate}'
            WHERE note = '{self.file_name}'""")
        else:
            cur.execute(f"""
            INSERT INTO notes
            VALUES ('{self.file_name}', '{self.file_deaddate}')
            """)
        self.con.commit()

    def dateFile(self):
        cur = self.con.cursor()
        try:
            fdate, ok_pressed = QInputDialog.getText(
                self,
                "Введите дату(гггг-мм-дд)",
                "Дата(гггг-мм-дд):")
            if ok_pressed:
                self.fdate = fdate
            else:
                raise FileNotFoundError
            # Получили результат запроса, который ввели в текстовое поле
            result = cur.execute(f"""
            SELECT * FROM notes WHERE date = '{str(self.fdate)}'""").fetchall()
            # Заполнили размеры таблицы
            self.tableWidget.setRowCount(len(result))
            # Если запись не нашлась, то не будем ничего делать
            self.tableWidget.setColumnCount(len(result[0]))
            self.titles = [description[0] for description in cur.description]
            # Заполнили таблицу полученными элементами
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
            self.error_label.setText('')
        except FileNotFoundError:
            self.error = 'Введите дату!'
            self.error_label.setText(str(self.error))

    def nameFile(self):
        cur = self.con.cursor()
        try:
            fname, ok_pressed = QInputDialog.getText(
                self,
                "Введите имя(имя.txt)",
                "Дата(имя.txt):")
            if ok_pressed:
                self.fname = fname
            else:
                raise FileNotFoundError
            # Получили результат запроса, который ввели в текстовое поле
            result = cur.execute(f"""
            SELECT * FROM notes WHERE note = '{str(self.fname)}'""").fetchall()
            # Заполнили размеры таблицы
            self.tableWidget.setRowCount(len(result))
            # Если запись не нашлась, то не будем ничего делать
            self.tableWidget.setColumnCount(len(result[0]))
            self.titles = [description[0] for description in cur.description]
            # Заполнили таблицу полученными элементами
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
            self.error_label.setText('')
        except FileNotFoundError:
            self.error = 'Введите имя!'
            self.error_label.setText(str(self.error))

    def deleteFile(self):
        cur = self.con.cursor()
        try:
            fname, ok_pressed = QInputDialog.getText(
                self,
                "Введите имя(имя.txt)",
                "Имя(имя.txt):")
            if ok_pressed:
                self.fname = fname
            else:
                raise FileNotFoundError
            fdate, ok_pressed = QInputDialog.getText(
                self,
                "Введите дату(гггг-мм-дд)",
                "Дата(гггг-мм-дд):")
            if ok_pressed:
                self.fdate = fdate
            else:
                raise FileNotFoundError
            if cur.execute(f"""
            SELECT * FROM notes
            WHERE note = '{self.fname}' and date = '{self.fdate}'
            """).fetchall():
                cur.execute(f"""
                DELETE from notes
                where note = '{self.fname}'
                and date = '{self.fdate}' """)
            self.error_label.setText('')
            self.con.commit()
        except FileNotFoundError:
            self.error = 'Введите имя и дату!'
            self.error_label.setText(str(self.error))


if __name__ == '__main__':
    # Создадим класс приложения PyQT
    app = QApplication(sys.argv)
    # А теперь создадим и покажем пользователю экземпляр
    # нашего виджета класса Example
    ex = Example()
    ex.show()
    # Будем ждать, пока пользователь не завершил исполнение QApplication,
    # а потом завершим и нашу программу
    sys.exit(app.exec())
