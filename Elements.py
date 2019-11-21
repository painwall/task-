from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QFileDialog
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap
import sqlite3
from database_sorting import sorting_db
import os
import shutil
import time

ID_TASK_FOR_SUBTASK = None


class Task(QWidget):
    # создает окно в котором можно добавлять задачи
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/dialog_task.ui', self)
        self.setWindowTitle('Добавление задачи')

        self.btn_SaveClose.clicked.connect(self.close_dialog)
        self.btn_enterTask.clicked.connect(self.add_task)
        self.btn_showSubtask.clicked.connect(self.showSubtask)
        self.btn_showSubtask.setEnabled(False)
        self.btn_add_tags.clicked.connect(self.show_add_tags)
        self.btn_add_tags.setEnabled(False)
        self.btn_update.clicked.connect(self.update_table)
        self.btn_add_img.clicked.connect(self.add_img)
        self.btn_add_img.setEnabled(False)

    def add_img(self):
        # диалоговое окно получает путь к файлу, переменовывает его и добавляет в папку img
        img = QFileDialog.getOpenFileName(self, 'Выбрать картинку',
                                          '', "Картинка(*.png *.jpg)")[0]

        name_img = img.split('/')[-1]
        shutil.copyfile(img, 'img/{}'.format(name_img))
        n_img = len(os.listdir('img'))

        os.rename('img/{}'.format(name_img),
                  'img/t_{}_{}.{}'.format(ID_TASK_FOR_SUBTASK, n_img, name_img.split('.')[-1]))

    def transformation(self, type, id, table):
        # получает данные из базы данных и добавляет их в соответстувующие переменные
        con = sqlite3.connect('data/data.db')
        cur = con.cursor()
        self.list_tasks = cur.execute(
            'SELECT name FROM {} WHERE type = "{}" and id = {}'.format(table, type, id)).fetchall()
        self.time = cur.execute('SELECT time FROM idTime WHERE type="{}" and id = {}'.format(type, id)).fetchall()
        self.date = cur.execute('SELECT date FROM idDate WHERE type="{}" and id = {}'.format(type, id)).fetchall()
        self.description = cur.execute('SELECT description FROM idDescription WHERE type="{}" and id = {}'
                                       .format(type, id)).fetchall()
        tags = cur.execute('SELECT tags FROM idListTags WHERE type="{}" and id = {}'.format(type, id)).fetchall()

        if self.time == []:
            self.time = '-'
        else:
            self.time = str(self.time[0])[2:-3]

        if self.date == []:
            self.date = '-'
        else:
            self.date = str(self.date[0])[2:-3]

        if self.description == []:
            self.description = '-'
        else:
            self.description = str(self.description[0])[2:-3]

        if tags == []:
            self.tags = '-'
        else:
            self.tags = '; '.join((str(tags[0])[2:-3]).split())

    def close_dialog(self):
        # закрывает окно для добавления задач
        global ID_TASK_FOR_SUBTASK
        ID_TASK_FOR_SUBTASK = None
        self.close()

    def update_table(self):
        # изменяет древо для просмотра задач и подзадач
        global ID_TASK_FOR_SUBTASK
        con = sqlite3.connect('data/data.db')
        cur = con.cursor()

        self.treeWidget.clear()
        task = QTreeWidgetItem(self.treeWidget)
        self.transformation('t', ID_TASK_FOR_SUBTASK, 'idNameTask')
        task.setText(0, "Название: {}\n[{} ; {}]\nОписание: {}\nТеги: {}".
                     format(self.list_tasks[0][0], self.time, self.date, self.description, self.tags))
        task.setFlags(task.flags() | Qt.ItemIsTristate)
        list_subtasks = cur.execute(
            'SELECT id FROM idNameSubtask WHERE type = "st" and idTask = {}'.format(ID_TASK_FOR_SUBTASK)).fetchall()

        for i in range(len(list_subtasks)):
            self.transformation('st', list_subtasks[i][0], 'idNameSubtask')
            subtask = QTreeWidgetItem(task)
            subtask.setText(0, "Название: {}\n[{} ; {}]\nОписание: {}\nТеги: {}".
                            format(self.list_tasks[0][0], self.time, self.date, self.description, self.tags))

    def add_task(self):
        # добавляет задачу в базу данных и делает так, чтобы добавлялось самое меньшее id
        global ID_TASK_FOR_SUBTASK
        con = sqlite3.connect('data/data.db')
        cur = con.cursor()

        typeStr = 't'
        table = 'idNameTask'

        if (self.textEdit_nameTask.toPlainText() == '' and self.textEdit_descriptionTask.toPlainText() != '') \
                or (self.textEdit_nameTask.toPlainText() != '' and self.textEdit_descriptionTask.toPlainText() == '') \
                or (self.textEdit_nameTask.toPlainText() != '' and self.textEdit_descriptionTask.toPlainText() != ''):

            list_id = cur.execute('SELECT id FROM {} WHERE type = "{}"'.format(table, typeStr)).fetchall()

            if list_id != []:
                list_id = [el[0] for el in list_id]
                for n in range(len(list_id)):
                    if n not in list_id:
                        self.ban()
                        cur.execute('INSERT INTO {}(type, id, name) VALUES("{}", {}, "{}")'.
                                    format(table, typeStr, n, self.textEdit_nameTask.toPlainText()))
                        if self.textEdit_descriptionTask.toPlainText() != '':
                            self.add_description(typeStr, n, cur)

                        ID_TASK_FOR_SUBTASK = int(n)

                        if self.cb_dataTask.isChecked():
                            self.add_date(typeStr, n, cur)
                            if self.cb_timeTask.isChecked():
                                self.add_time(typeStr, n, cur)
                        break
                    elif n == len(list_id) - 1:
                        n = len(list_id)
                        self.ban()
                        ID_TASK_FOR_SUBTASK = len(list_id)
                        cur.execute(
                            'INSERT INTO {}(type, id, name) VALUES("{}", {}, "{}")'.
                                format(table, typeStr, n, self.textEdit_nameTask.toPlainText()))
                        if self.textEdit_descriptionTask.toPlainText() != '':
                            self.add_description(typeStr, len(list_id), cur)

                        if self.cb_dataTask.isChecked():
                            self.add_date(typeStr, n, cur)
                            if self.cb_timeTask.isChecked():
                                self.add_time(typeStr, n, cur)
            elif list_id == []:
                self.ban()
                n = 0
                ID_TASK_FOR_SUBTASK = int(n)
                cur.execute('INSERT INTO {}(type, id, name) VALUES("{}", {}, "{}")'
                            .format(table, typeStr, n, self.textEdit_nameTask.toPlainText()))
                if self.textEdit_descriptionTask.toPlainText() != '':
                    self.add_description(typeStr, n, cur)
                if self.cb_dataTask.isChecked():
                    self.add_date(typeStr, n, cur)
                    if self.cb_timeTask.isChecked():
                        self.add_time(typeStr, n, cur)

        con.commit()
        con.close()
        if (self.textEdit_nameTask.toPlainText() == '' and self.textEdit_descriptionTask.toPlainText() != '') \
                or (self.textEdit_nameTask.toPlainText() != '' and self.textEdit_descriptionTask.toPlainText() == '') \
                or (self.textEdit_nameTask.toPlainText() != '' and self.textEdit_descriptionTask.toPlainText() != ''):
            self.update_table()

    def add_description(self, typeStr, n, cur):
        # добавляет описание задачи в базу дынных
        cur.execute('INSERT INTO idDescription(type, id, description) VALUES("{}", {}, "{}")'.
                    format(typeStr, n, self.textEdit_descriptionTask.toPlainText()))

    def add_date(self, typeStr, n, cur):
        # добавляет дату в базу дынных
        cur.execute('INSERT INTO idDate(type, id, date) VALUES("{}", {}, "{}")'.
                    format(typeStr, n, self.dateEdit_task.date().toString('dd.MM.yyyy')))

    def add_time(self, typeStr, n, cur):
        # добавляет время в базу данных
        cur.execute('INSERT INTO idTime(type, id, time) VALUES("{}", {}, "{}")'.
                    format(typeStr, n, self.timeEdit_task.time().toString('hh:mm')))

    def show_add_tags(self):
        # создает окно для добавления тегов в задачи
        self.menuTags = MenuAddTags('t', ID_TASK_FOR_SUBTASK)
        self.menuTags.show()

    def showSubtask(self):
        # создает окно для добавления подзадач
        self.subtask = Subtask()
        self.subtask.show()

    def ban(self):
        # запрещает нажимать на какие-либо кнопки
        self.btn_add_tags.setEnabled(True)
        self.btn_showSubtask.setEnabled(True)
        self.btn_enterTask.setEnabled(False)
        self.textEdit_nameTask.setReadOnly(True)
        self.textEdit_descriptionTask.setReadOnly(True)
        self.btn_add_img.setEnabled(True)


class Subtask(QWidget):  # все тоже самое что и class Task
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/dialog_subtask.ui', self)

        self.setWindowTitle('Добавление подзадачи')
        self.btn_enterTask.clicked.connect(self.add_subtask)
        self.btn_add_tags.clicked.connect(self.show_add_tags)
        self.btn_exit.clicked.connect(self.close)
        self.btn_add_tags.setEnabled(False)

    def add_subtask(self):
        global ID_TASK_FOR_SUBTASK
        con = sqlite3.connect('data/data.db')
        cur = con.cursor()
        typeStr = 'st'
        table = 'idNameSubtask'

        if self.textEdit_nameTask.toPlainText() == '' and self.textEdit_descriptionTask.toPlainText() != '' \
                or self.textEdit_nameTask.toPlainText() != '' and self.textEdit_descriptionTask.toPlainText() == '' \
                or self.textEdit_nameTask.toPlainText() != '' and self.textEdit_descriptionTask.toPlainText() != '':

            list_id = cur.execute('SELECT id FROM {} WHERE type = "{}"'.format(table, typeStr)).fetchall()

            if list_id != []:
                list_id = [el[0] for el in list_id]
                for n in range(len(list_id)):
                    if n not in list_id:
                        cur.execute(
                            'INSERT INTO {}(type, id, idTask, name) VALUES("{}", {}, {}, "{}")'
                                .format(table, typeStr, n, ID_TASK_FOR_SUBTASK, self.textEdit_nameTask.toPlainText()))
                        if self.textEdit_descriptionTask.toPlainText() != '':
                            self.add_description(typeStr, n, cur)

                        if self.cb_dataTask.isChecked():
                            self.add_date(typeStr, n, cur)
                            if self.cb_timeTask.isChecked():
                                self.add_time(typeStr, n, cur)
                        break
                    elif n == len(list_id) - 1:
                        n = len(list_id)
                        cur.execute(
                            'INSERT INTO {}(type, id, idTask, name) VALUES("{}", {}, {}, "{}")'.
                                format(table, typeStr, n, ID_TASK_FOR_SUBTASK, self.textEdit_nameTask.toPlainText()))
                        if self.textEdit_descriptionTask.toPlainText() != '':
                            self.add_description(typeStr, len(list_id), cur)

                        if self.cb_dataTask.isChecked():
                            self.add_date(typeStr, n, cur)
                            if self.cb_timeTask.isChecked():
                                self.add_time(typeStr, n, cur)
            elif list_id == []:
                n = 0
                cur.execute(
                    'INSERT INTO {}(type, id, idTask, name) VALUES("{}", {}, {}, "{}")'
                        .format(table, typeStr, n, ID_TASK_FOR_SUBTASK, self.textEdit_nameTask.toPlainText()))
                if self.textEdit_descriptionTask.toPlainText() != '':
                    self.add_description(typeStr, n, cur)

                if self.cb_dataTask.isChecked():
                    self.add_date(typeStr, n, cur)
                    if self.cb_timeTask.isChecked():
                        self.add_time(typeStr, n, cur)

        self.id_subtask = n
        con.commit()
        con.close()
        self.btn_add_tags.setEnabled(True)
        self.btn_enterTask.setEnabled(False)

    def add_description(self, typeStr, n, cur):
        cur.execute('INSERT INTO idDescription(type, id, description) VALUES("{}", {}, "{}")'
                    .format(typeStr, n, self.textEdit_descriptionTask.toPlainText()))

    def add_date(self, typeStr, n, cur):
        cur.execute('INSERT INTO idDate(type, id, date) VALUES("{}", {}, "{}")'
                    .format(typeStr, n, self.dateEdit_task.date().toString('dd.MM.yyyy')))

    def add_time(self, typeStr, n, cur):
        cur.execute('INSERT INTO idTime(type, id, time) VALUES("{}", {}, "{}")'
                    .format(typeStr, n, self.timeEdit_task.time().toString('hh:mm')))

    def show_add_tags(self):
        self.menuTags = MenuAddTags('st', self.id_subtask)
        self.menuTags.show()


class Tag(QWidget):
    # создает окно для добавления тегов
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/dialog_tag.ui', self)

        self.setWindowTitle('Добавление тега')
        self.btn_enter.clicked.connect(self.append_tag)

    def append_tag(self):
        txt = open('data/tags.txt', encoding='UTF-8').read().split(' ')[1:]
        txt_edit = open('data/tags.txt', mode='a', encoding='UTF-8')

        for el in set(self.textTag.text().split()):
            if el not in txt and self.textTag.text():
                txt_edit.write(' {}'.format(el))
        txt_edit.close()

        self.close()

    def delete_all_tags(self):
        con = sqlite3.connect('data/data.db')
        cur = con.cursor()
        cur.execute('DELETE FROM idListTags')
        con.commit()

        self.listTags.clear()
        txtListTags = open('data/tags.txt', mode='w')
        txtListTags.close()

    def delete_tag(self):
        con = sqlite3.connect('data/data.db')
        cur = con.cursor()

        element = self.listTags.selectedItems()[0].text()

        for el in cur.execute('SELECT * FROM idListTags').fetchall():
            edit = el[2].split()
            if element in edit:
                edit.remove(element)
                cur.execute('DELETE FROM idListTags')
                if edit != []:
                    cur.execute('INSERT INTO idListTags(type, id, tags) VALUES("{}", {},  "{}")'
                                .format(el[0], el[1], ' '.join(edit)))
        con.commit()

        txt = open('data/tags.txt', encoding='UTF-8').read().split(' ')
        txt_edit = open('data/tags.txt', mode='w', encoding='UTF-8')
        txt.remove(element)
        for el in set(txt):
            if el != ' ':
                txt_edit.write(' {}'.format(el))
        txt_edit.close()

        self.add_tag_in_list()

        # self.listTags.itemClicked()


class ListTags(Tag):
    # создает вкладу меню тегов для их удаления и добавления
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/list_tag.ui', self)
        self.add_tag_in_list()
        self.btn_addTag.clicked.connect(self.show_addTag)
        self.btn_delAll.clicked.connect(self.delete_all_tags)
        self.btn_del.clicked.connect(self.delete_tag)
        self.btn_refresh.clicked.connect(self.add_tag_in_list)
        self.btn_enter.clicked.connect(self.addTag)
        self.show()
        self.flag = False
        self.label.hide()
        self.textTag.hide()
        self.btn_enter.hide()

    def show_addTag(self):
        if self.flag:
            self.label.hide()
            self.textTag.hide()
            self.btn_enter.hide()

            self.flag = False
        else:
            self.label.show()
            self.textTag.show()
            self.btn_enter.show()

            self.flag = True

    def addTag(self):
        txt = open('data/tags.txt', encoding='UTF-8').read().split(' ')[1:]
        txt_edit = open('data/tags.txt', mode='a', encoding='UTF-8')

        for el in set(self.textTag.text().split()):
            if el not in txt and self.textTag.text():
                txt_edit.write(' {}'.format(el))
        txt_edit.close()

        self.add_tag_in_list()

    def add_tag_in_list(self):
        self.listTags.clear()
        txtListTags = sorted(open('data/tags.txt', encoding='UTF-8').read().split())
        for tag in txtListTags:
            self.listTags.addItem(tag)


class MenuAddTags(QWidget):
    # создает окно для добавления тегов в задачи и подзадачи
    def __init__(self, type, id):
        super().__init__()
        self.type = type
        self.id = id
        self.list_tags = []
        uic.loadUi('ui/dialog_addTag_in_task_or_subtask.ui', self)
        self.setWindowTitle('Меню добавления тегов')
        txt_tags = open('data/tags.txt', encoding='UTF-8').read().split(' ')[1:]
        self.btn_addTag.clicked.connect(self.close_menu)
        self.listWidget_tags.itemDoubleClicked.connect(self.addTag_in_task)
        self.listWidget_addTags.itemDoubleClicked.connect(self.delete_tag_in_listWidget_addTags)
        if txt_tags != []:
            for tag in txt_tags:
                self.listWidget_tags.addItem(tag)

    def addTag_in_task(self):  # добавление тегов в виджет
        if self.listWidget_tags.selectedItems()[0].text() not in self.list_tags:
            self.list_tags.append(self.listWidget_tags.selectedItems()[0].text())
            self.listWidget_addTags.addItem(self.listWidget_tags.selectedItems()[0].text())

    def delete_tag_in_listWidget_addTags(self):  # удаление тегов из виджета
        self.list_tags.remove(self.listWidget_addTags.selectedItems()[0].text())
        self.listWidget_addTags.clear()
        for tag in self.list_tags:
            self.listWidget_addTags.addItem(tag)

    def close_menu(self):  # закрытие окна
        con = sqlite3.connect('data/data.db')
        cur = con.cursor()
        cur.execute('DELETE FROM idListTags WHERE type = "{}" and id = {}'.format(self.type, self.id))
        if self.list_tags != []:
            cur.execute('INSERT INTO idListTags(type, id, tags) VALUES("{}", {},  "{}")'
                        .format(self.type, self.id, ' '.join(self.list_tags)))
        con.commit()
        con.close()
        self.close()


class SettingsTasker(QWidget):  # создает вкладу с настройками
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/settings.ui', self)
        self.btn_delete_all_data.clicked.connect(self.delete_all_data)
        self.btn_delete_all_task_or_subtask.clicked.connect(self.delete_data_in_db)
        self.btn_delete_all_tags.clicked.connect(self.delete_all_tags)
        self.btn_delete_all_img.clicked.connect(self.delete_all_img)

    def delete_data_in_db(self):  # удаление задач и подзадач из базы данных
        con = sqlite3.connect('data/data.db')
        cur = con.cursor()
        cur.execute('DELETE from idNameTask')
        cur.execute('DELETE from idNameSubtask')
        cur.execute('DELETE from idDescription')
        cur.execute('DELETE from idDate')
        cur.execute('DELETE from idTime')
        cur.execute('DELETE from idListTags')
        self.delete_all_img()
        con.commit()

    def delete_all_tags(self):  # удаление тегов из базы данных
        txt = open('data/tags.txt', mode='w')
        txt.close()

    def delete_all_img(self):  # удаление картинок из папки img
        for img in os.listdir('img'):
            os.remove('img/{}'.format(img))

    def delete_all_data(self):  # очистка базы данных и папки img
        self.delete_data_in_db()
        self.delete_all_tags()
        self.delete_all_img()


class ViewTasks(QWidget):  # создает в кладку для просмотра задач
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/view_tasks.ui', self)
        self.btn_update.clicked.connect(self.update_table)
        self.treeWidget.itemDoubleClicked.connect(self.detail_view)

    def detail_view(self):
        if self.treeWidget.indexFromItem(self.treeWidget.selectedItems()[0]).parent().row() == -1:
            type = 't'
            list_t_or_st = self.list_tasks_for_table
        else:
            type = 'st'
            list_t_or_st = self.list_subtasks

        row = self.treeWidget.indexFromItem(self.treeWidget.selectedItems()[0]).row()
        self.detailed_view = DetailedView(type, list_t_or_st, row)
        self.detailed_view.show()

    def transformation(self, type, id, table):
        con = sqlite3.connect('data/data.db')
        cur = con.cursor()
        self.list_tasks = cur.execute(
            'SELECT name FROM {} WHERE type = "{}" and id = {}'.format(table, type, id)).fetchall()
        self.time = cur.execute('SELECT time FROM idTime WHERE type="{}" and id = {}'.format(type, id)).fetchall()
        self.date = cur.execute('SELECT date FROM idDate WHERE type="{}" and id = {}'.format(type, id)).fetchall()
        self.description = cur.execute('SELECT description FROM idDescription WHERE type="{}" and id = {}'
                                       .format(type, id)).fetchall()
        tags = cur.execute('SELECT tags FROM idListTags WHERE type="{}" and id = {}'.format(type, id)).fetchall()

        if self.time == []:
            self.time = '-'
        else:
            self.time = str(self.time[0])[2:-3]

        if self.date == []:
            self.date = '-'
        else:
            self.date = str(self.date[0])[2:-3]

        if self.description == []:
            self.description = '-'
        else:
            self.description = str(self.description[0])[2:-3]

        if tags == []:
            self.tags = '-'
        else:
            self.tags = '; '.join((str(tags[0])[2:-3]).split())


class AllTimeViewTasks(ViewTasks):
    # создает в кладку для просмотра задач за все время
    def __init__(self):
        super().__init__()
        self.update_table()

    def update_table(self):
        self.treeWidget.clear()
        sorting_db()
        con = sqlite3.connect('data/data.db')
        cur = con.cursor()

        self.list_tasks_for_table = cur.execute('SELECT id, name FROM idNameTask').fetchall()
        self.list_subtasks = cur.execute('SELECT id, idTask, name FROM idNameSubtask').fetchall()

        for task in self.list_tasks_for_table:
            self.transformation('t', task[0], 'idNameTask')
            parent = QTreeWidgetItem(self.treeWidget)
            parent.setText(0, "Название: {}\n[{} ; {}]\nОписание: {}\nТеги: {}".
                           format(task[1], self.time, self.date, self.description, self.tags))
            parent.setFlags(parent.flags() | Qt.ItemIsTristate)
            for subtask in self.list_subtasks:
                if task[0] == subtask[1]:
                    self.transformation('st', subtask[0], 'idNameSubtask')
                    child = QTreeWidgetItem(parent)
                    child.setText(0, "Название: {}\n[{} ; {}]\nОписание: {}\nТеги: {}".
                                  format(subtask[2], self.time, self.date, self.description, self.tags))
        con.close()


class TodayViewTasks(ViewTasks):
    # создает в кладку для просмотра задач за сегодня время
    def __init__(self):
        super().__init__()
        self.update_table()

    def update_table(self):
        self.treeWidget.clear()
        sorting_db()
        con = sqlite3.connect('data/data.db')
        cur = con.cursor()

        self.list_tasks_for_table = cur.execute('SELECT id, name FROM idNameTask').fetchall()
        self.list_subtasks = cur.execute('SELECT id, idTask, name FROM idNameSubtask').fetchall()

        datenow = time.strftime("%d.%m.%Y", time.localtime())
        date = cur.execute(
            'SELECT type, id, date FROM idDate WHERE type = "t" and date = "{}"'.format(datenow)).fetchall()

        for task in self.list_tasks_for_table:
            if cur.execute('SELECT type, id, date FROM idDate WHERE type = "t" and id = {} and date = "{}"'.
                                   format(task[0], datenow)).fetchall() != []:
                self.transformation('t', task[0], 'idNameTask')
                parent = QTreeWidgetItem(self.treeWidget)
                parent.setText(0, "Название: {}\n[{} ; {}]\nОписание: {}\nТеги: {}".
                               format(task[1], self.time, self.date, self.description, self.tags))
                parent.setFlags(parent.flags() | Qt.ItemIsTristate)
                for subtask in self.list_subtasks:
                    if task[0] == subtask[1]:
                        self.transformation('st', subtask[0], 'idNameSubtask')
                        child = QTreeWidgetItem(parent)
                        child.setText(0, "Название: {}\n[{} ; {}]\nОписание: {}\nТеги: {}".
                                      format(subtask[2], self.time, self.date, self.description, self.tags))
        con.close()


class DetailedView(QWidget):
    def __init__(self, type, list_t_or_st, row):
        super().__init__()
        uic.loadUi('ui/detailed_view.ui', self)
        self.setWindowTitle('Подробный просмотр')

        con = sqlite3.connect('data/data.db')
        cur = con.cursor()

        if type == 't':
            self.name = list_t_or_st[row][1]
        elif type == 'st':
            self.name = list_t_or_st[row][2]
            self.idTask = list_t_or_st[row][1]

        self.type = type
        self.id = list_t_or_st[row][0]

        self.textEdit_name.append(self.name)
        if cur.execute('SELECT description FROM idDescription WHERE type = "{}" and id = {}'
                               .format(self.type, self.id)).fetchall() != []:
            self.textEdit_description.append(
                cur.execute('SELECT description FROM idDescription WHERE type = "{}" and id = {}'
                            .format(self.type, self.id)).fetchall()[0][0])

        self.ban()

        self.btn_edit.clicked.connect(self.edit)
        self.btn_delete.clicked.connect(self.delete)
        self.btn_edit_tags.clicked.connect(self.edit_tags)
        self.btn_save.clicked.connect(self.save_st_or_t)
        self.btn_edit_date.clicked.connect(self.edit_date)
        self.btn_edit_time.clicked.connect(self.edit_time)
        self.listWidget_img.itemDoubleClicked.connect(self.delete_img)
        self.listWidget_img.itemClicked.connect(self.view_img)
        self.btn_add_img.clicked.connect(self.add_img)

        self.update_list_img()

    def edit_date(self):
        self.e_d = EditDate(self.type, self.id)
        self.e_d.show()

    def edit_time(self):
        self.e_t = EditTime(self.type, self.id)
        self.e_t.show()

    def edit_tags(self):
        self.dialog_edit_tags = MenuAddTags(self.type, self.id)
        self.dialog_edit_tags.show()

    def edit(self):
        self.textEdit_name.setReadOnly(False)
        self.textEdit_description.setReadOnly(False)
        self.btn_edit.setEnabled(False)
        self.btn_save.show()

    def save_st_or_t(self):
        con = sqlite3.connect('data/data.db')
        cur = con.cursor()

        if self.type == 't':
            cur.execute('DELETE FROM idNameTask WHERE type = "{}" and id = {}'.format(self.type, self.id))
            cur.execute('INSERT INTO idNameTask(type, id, name) VALUES("{}", {},  "{}")'
                        .format(self.type, self.id, self.textEdit_name.toPlainText()))
        elif self.type == 'st':
            cur.execute('DELETE FROM idNameSubtask WHERE id = {}'.format(self.id))
            cur.execute('INSERT INTO idNameSubtask(type, id, idTask, name) VALUES("{}", {}, {}, "{}")'
                        .format(self.type, self.id, self.idTask, self.textEdit_name.toPlainText()))

        cur.execute('DELETE FROM idDescription WHERE type = "{}" and id = {}'.format(self.type, self.id))
        cur.execute('INSERT INTO idDescription(type, id, description) VALUES("{}", {},  "{}")'
                    .format(self.type, self.id, self.textEdit_description.toPlainText()))

        self.ban()

        con.commit()

    def ban(self):
        self.textEdit_name.setReadOnly(True)
        self.textEdit_description.setReadOnly(True)
        self.btn_save.hide()
        self.btn_edit.setEnabled(True)

        if self.type != 't':
            self.btn_add_img.hide()
            self.label_img.hide()
            self.listWidget_img.hide()
            self.label_3.hide()

    def delete(self):
        con = sqlite3.connect('data/data.db')
        cur = con.cursor()

        if self.type == 't':
            cur.execute('DELETE FROM idNameTask WHERE type = "{}" and id = {}'.format(self.type, self.id))

            for subtask in cur.execute('SELECT id FROM idNameSubtask WHERE idTask = {}'.format(self.id)):
                cur.execute('DELETE FROM idNameSubtask WHERE id = {}'.format(subtask[0]))
                cur.execute('DELETE FROM idDate WHERE type = "st" and id = {}'.format(subtask[0]))
                cur.execute('DELETE FROM idTime WHERE type = "st" and id = {}'.format(subtask[0]))
                cur.execute('DELETE FROM idDescription WHERE type = "st" and id = {}'.format(subtask[0]))
                cur.execute('DELETE FROM idListTags WHERE type = "st" and id = {}'.format(subtask[0]))
        elif self.type == 'st':
            cur.execute('DELETE FROM idNameSubtask WHERE type = "{}" and id = {}'.format(self.type, self.id))

        cur.execute('DELETE FROM idDate WHERE type = "{}" and id = {}'.format(self.type, self.id))
        cur.execute('DELETE FROM idTime WHERE type = "{}" and id = {}'.format(self.type, self.id))
        cur.execute('DELETE FROM idDescription WHERE type = "{}" and id = {}'.format(self.type, self.id))
        cur.execute('DELETE FROM idListTags WHERE type = "{}" and id = {}'.format(self.type, self.id))
        con.commit()

        if self.sender() == self.btn_delete:
            self.close()

    def update_list_img(self):
        if self.type == 't':
            self.list_img = os.listdir('img')
            self.listWidget_img.clear()

            for image in self.list_img:
                edit_name = image.split('.')[0]
                edit_name = edit_name.split('_')
                if edit_name[0] == self.type and int(edit_name[1]) == self.id:
                    self.listWidget_img.addItem(image)

    def delete_img(self):
        os.remove('img/{}'.format(self.listWidget_img.selectedItems()[0].text()))
        self.list_img.remove(self.listWidget_img.selectedItems()[0].text())
        self.update_list_img()

    def add_img(self):
        img = QFileDialog.getOpenFileName(self, 'Выбрать картинку',
                                          '', "Картинка(*.png *.jpg)")[0]

        name_img = img.split('/')[-1]
        print(name_img)
        shutil.copyfile(img, 'img/{}'.format(name_img))
        n_img = len(os.listdir('img'))
        os.rename('img/{}'.format(name_img), 'img/t_{}_{}.{}'.format(self.id, n_img, name_img.split('.')[-1]))

        self.update_list_img()

    def view_img(self):
        pixmap = QPixmap('img/{}'.format(self.listWidget_img.selectedItems()[0].text()))
        pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio)
        self.label_img.setPixmap(pixmap)


class EditDate(QWidget):
    def __init__(self, type, id):
        super().__init__()
        uic.loadUi('ui/dialog_date.ui', self)
        self.setWindowTitle('Изменение даты')
        self.btn_enter.clicked.connect(self.enter)

        self.type = type
        self.id = id

    def enter(self):
        con = sqlite3.connect('data/data.db')
        cur = con.cursor()
        cur.execute('DELETE FROM idDate WHERE type = "{}" and id = {}'
                    .format(self.type, self.id))
        cur.execute('INSERT INTO idDate(type, id, date) VALUES("{}", {}, "{}")'.
                    format(self.type, self.id, self.calendar.selectedDate().toString('dd.MM.yyyy')))
        con.commit()
        self.close()


class EditTime(QWidget):
    def __init__(self, type, id):
        super().__init__()
        uic.loadUi('ui/dialog_time.ui', self)
        self.setWindowTitle('Изменение времени')
        self.btn_enter.clicked.connect(self.enter)

        self.type = type
        self.id = id

    def enter(self):
        con = sqlite3.connect('data/data.db')
        cur = con.cursor()
        if cur.execute('SELECT * FROM idDate WHERE type = "{}" and id = {}'
                               .format(self.type, self.id)).fetchall() != []:
            cur.execute('DELETE FROM idTime WHERE type = "{}" and id = {}'
                        .format(self.type, self.id))
            cur.execute('INSERT INTO idTime(type, id, time) VALUES("{}", {}, "{}")'.
                        format(self.type, self.id, self.timeEdit.time().toString('hh:mm')))
        con.commit()
        self.close()
