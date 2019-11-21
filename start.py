import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from Elements import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/main.ui', self)
        self.setWindowTitle('Taskер')
        self.addTask_action.triggered.connect(self.add_task)
        self.addTag_action.triggered.connect(self.add_tag)
        self.listTags_action.triggered.connect(self.list_tags)
        self.all_settings_action.triggered.connect(self.settings_tasker)
        self.allTime_action.triggered.connect(self.show_all_time_tasks)
        self.today_action.triggered.connect(self.show_today_tasks)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.close_tab)

    def close_tab(self):
        self.tabWidget.removeTab(self.sender().currentIndex())

    def show_all_time_tasks(self):
        self.tabWidget.addTab(AllTimeViewTasks(), 'Задачи на все время')

    def add_task(self):
        self.task = Task()
        self.task.show()

    def add_tag(self):
        self.tag = Tag()
        self.tag.show()

    def list_tags(self):
        self.tabWidget.addTab(ListTags(), 'Меню тегов')

    def settings_tasker(self):
        self.tabWidget.addTab(SettingsTasker(), 'Настройки')

    def show_today_tasks(self):
        self.tabWidget.addTab(TodayViewTasks(), 'Задачи на сегодня')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
