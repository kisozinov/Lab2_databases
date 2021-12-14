import traceback
import design
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from database import Database
import config as log
import design


class connectWin(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self, app):
        super().__init__()
        self.setupUi(self)
        self.app = app

    def connect_to_database(self):
        try:
            self.app.connect(self.database_name.text())
            self.close()
        except Exception as ex:
            print(traceback.format_exc())
            self.message("Такой базы нет!", traceback.format_exc())


class App(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database(log.name_db)
        self.setupUi(self)
        self.connectionWindow = connectWin(self)
        self.add_to_lab_work_button.clicked.connect(self.add_book_record)
        self.add_to_student_button.clicked.connect(self.add_publisher_record)
        self.clear_lab_work_button.clicked.connect(self.clear_book)
        self.clear_student_button.clicked.connect(self.clear_publisher)
        self.delete_button.clicked.connect(self.delete_by_author)
        self.delete_database_button.clicked.connect(self.delete_database)
        self.search_button.clicked.connect(self.search_by_author)
        self.actionOpen.triggered.connect(self.connectionWindow.show)
        self.actionDelete.triggered.connect(self.delete_record)
        self.columns_publisher = ['name', 'studentID', 'lastUpdate']
        self.columns_books = ['id', 'title', 'discipline', 'student']
        self.lab_work_table.itemChanged.connect(self.update_books)
        self.student_table.itemChanged.connect(self.update_publishers)
        self.lab_work_table.setColumnCount(4)
        self.student_table.setColumnCount(3)
        self.lab_work_table.setHorizontalHeaderLabels(self.columns_books)
        self.student_table.setHorizontalHeaderLabels(self.columns_publisher)
        self.edit_flag = False

    def connect(self, dbname):
        self.db = Database(dbname)
        try:
            self.data_lab_workss = self.db.get_books()
            self.data_students = self.db.get_publishers()
            self.set_data(self.lab_work_table, self.columns_books, self.data_lab_workss)
            self.set_data(self.student_table, self.columns_publisher, self.data_students)
        except Exception as ex:
            print(traceback.format_exc())
            self.message("Ошибка при подключении!", traceback.format_exc())

    def set_data(self, table, columns, data):
        self.edit_flag = True
        try:
            if data is not None:
                table.setRowCount(len(data))
                for i, row in enumerate(data):
                    for j, col in enumerate(columns):
                        table.setItem(i, j, QTableWidgetItem(str(row[col])))

            else:
                table.setRowCount(0)
        except Exception as ex:
            self.message("Ошибка при установке данных!", traceback.format_exc())
        self.edit_flag = False

    def message(self, error, detailed_error="Непредвиденная ошибка", icon=QMessageBox.Warning):
        msg = QMessageBox()
        msg.setWindowTitle("Отчёт")
        msg.setIcon(icon)
        msg.setText(f"{error}")
        msg.setDetailedText(detailed_error)
        msg.addButton(QMessageBox.Ok)
        msg.exec()

    def add_book_record(self):
        try:
            title = self.lab_work_title.text()
            discipline = self.lab_work_discipline.text()
            student = self.lab_work_student.text()
            if title != "" and discipline != "" and student != "" and self.db is not None:
                self.db.add_to_book(title, discipline, student)
                self.data_lab_work = self.db.get_books()
                self.set_data(self.lab_work_table, self.columns_books, self.data_lab_work)
                self.lab_work_title.clear()
                self.lab_work_discipline.clear()
                self.lab_work_student.clear()
            else:
                self.message(
                    "Проверьте, все ли поля заполнены или подключились ли вы к базе данных")
        except Exception as ex:
            self.message("Ошибка при добавлении данных!", traceback.format_exc())

    def add_publisher_record(self):
        try:
            name = self.student_name.text()
            studentID = self.student_studentID.text()
            if name != "" and studentID != "" and self.db is not None:
                self.db.add_to_publisher(name, studentID)
                self.data_students = self.db.get_publishers()
                self.set_data(self.student_table, self.columns_publisher, self.data_students)
                self.student_name.clear()
                self.student_studentID.clear()
            else:
                self.message("Проверьте, все ли поля заполнены или подключились ли вы к БД")

        except Exception as ex:
            print(traceback.format_exc())
            self.message("Ошибка при добавлении данных!", str(ex))

    def clear_book(self):
        try:
            self.db.clear_books()
            self.data_lab_work = self.db.get_books()
            self.set_data(self.lab_work_table, self.columns_books, self.data_lab_work)
        except Exception as ex:
            self.message("Ошибка при очистке данных!", traceback.format_exc())

    def clear_publisher(self):
        try:
            self.db.clear_students()
            self.data_students = self.db.get_publishers()
            self.set_data(self.student_table, self.columns_publisher, self.data_students)
        except Exception as ex:
            self.message("Ошибка при очистке данных!", traceback.format_exc())

    def delete_database(self):
        try:
            if self.db is not None:
                self.db.delete_database()
                self.data_students = []
                self.data_lab_work = []
                self.set_data(self.student_table, self.columns_publisher, self.data_students)
                self.set_data(self.lab_work_table, self.columns_books, self.data_lab_work)
                self.db = None
                self.connectionWindow = None
                self.connectionWindow = connectWin(self)
            else:
                self.message("Проверьте, подключились ли вы к БД")
        except Exception as ex:
            self.message("Ошибка при удалении базы данных!", traceback.format_exc())

    def delete_by_author(self):
        try:
            author = self.data_to_delete.text()
            if author != "" and self.db is not None:
                self.db.delete_book_by_author(author)
                self.data_lab_work = self.db.get_books()
                self.set_data(self.lab_work_table, self.columns_books, self.data_lab_work)
                self.data_to_delete.clear()
            else:
                self.message("Проверьте, все ли поля (автор) заполнены или подключились ли вы к БД")
        except Exception as ex:
            self.message("Ошибка при удалении данных!", traceback.format_exc())

    def find_by_author(self):
        try:
            student = self.data_to_delete.text()
            if student != "" and self.db is not None:
                self.set_data(self.lab_work_table, self.columns_books, self.db.find_book_by_author(student))
                self.set_data(self.student_table, self.columns_publisher, self.db.find_publisher(student))
                self.data_to_delete.clear()
            if student == "":
                self.set_data(self.lab_work_table, self.columns_books, self.data_lab_work)
                self.set_data(self.student_table, self.columns_publisher, self.data_students)
            else:
                self.message("Проверьте, подключились ли вы к БД")
        except Exception as ex:
            self.message("Ошибка при поиске данных!", traceback.format_exc())

    def update_books(self, item):
        if not self.edit_flag:
            try:
                if item.column() == 1:
                    self.db.update_book_by_title(item.text(), self.lab_work_table.item(item.row(), 0).text())
                elif item.column() == 2:
                    self.db.update_book_by_student(item.text(), self.lab_work_table.item(item.row(), 0).text())
                elif item.column() == 3:
                    self.db.update_book_by_publisher(item.text(), self.lab_work_table.item(item.row(), 0).text())
                self.data_lab_work = self.db.get_books()
                self.set_data(self.lab_work_table, self.columns_books, self.data_lab_work)
            except Exception:
                self.message("Ошибка при обновлении данных!", traceback.format_exc())

    def update_publishers(self, item):
        if not self.edit_flag:
            try:
                if item.column() == 0:
                    self.db.update_publisher_by_name(item.text(), self.data_students[item.row()]['name'])
                elif item.column() == 1:
                    self.db.update_publisher_by_tel(item.text(), self.student_table.item(item.row(), 0).text())
                self.data_students = self.db.get_publishers()
                self.set_data(self.student_table, self.columns_publisher, self.data_students)
            except Exception:
                print(traceback.format_exc())
                self.message("Ошибка при обновлении данных!", traceback.format_exc())

    def search_by_author(self):
        try:
            author = self.data_to_delete.text()
            if author != "" and self.db is not None:
                self.set_data(self.lab_work_table, self.columns_books, self.db.find_book_by_author(author))
                self.set_data(self.student_table, self.columns_publisher, self.db.find_publisher(author))
                self.data_to_delete.clear()
                self.data_to_delete.clear()
            else:
                self.set_data(self.lab_work_table, self.columns_books, self.data_lab_work)
                self.set_data(self.student_table, self.columns_publisher, self.data_students)
        except Exception:
            self.message("Ошибка при поиске данных!", traceback.format_exc())

    def delete_record(self):
        if len(self.student_table.selectedIndexes()):
            try:
                for i in self.student_table.selectedIndexes():
                    self.db.delete_publisher_record(self.data_students[i.row()]['name'])
                    self.data_students = self.db.get_publishers()
                    self.set_data(self.student_table, self.columns_publisher, self.data_students)
            except Exception:
                self.message("Ошибка при удалении данных!", traceback.format_exc())
        else:
            try:
                for i in self.lab_work_table.selectedIndexes():
                    self.db.delete_book_record(self.data_lab_work[i.row()]['id'])
                    self.data_lab_work = self.db.get_books()
                    self.set_data(self.lab_work_table, self.columns_books, self.data_lab_work)
            except Exception:
                self.message("Ошибка при удалении данных!", traceback.format_exc())