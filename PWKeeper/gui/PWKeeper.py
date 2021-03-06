# -*- coding: utf-8 -×-

from PyQt4 import QtGui
import sqlite3
import os

class PWKeeper(QtGui.QMainWindow):

    def __init__(self):
        super(PWKeeper, self).__init__()
        self.initToolBar()
        self.initGrid()
        self.initDB()

        # self.current_row = 0
        self.setGeometry(300, 300, 650, 300)
        self.setWindowTitle('PWKeeper')
        self.setWindowIcon(QtGui.QIcon('images/icon.png'))

    def initToolBar(self):
        newAction = QtGui.QAction(QtGui.QIcon('images/new.png'), 'new', self)
        editAction = QtGui.QAction(QtGui.QIcon('images/edit.png'), 'edit', self)
        delAction = QtGui.QAction(QtGui.QIcon('images/del.png'), 'del', self)

        newAction.setShortcut('Ctrl+N')
        editAction.setShortcut('Ctrl_E')
        delAction.setShortcut('Delete')

        # 事件绑定
        newAction.triggered.connect(self.newAction_def)
        editAction.triggered.connect(self.editAction_def)
        delAction.triggered.connect(self.delAction_def)

        self.tb_new = self.addToolBar('New')
        self.tb_edit = self.addToolBar('Edit')
        self.tb_del = self.addToolBar('Del')

        self.tb_new.addAction(newAction)
        self.tb_edit.addAction(editAction)
        self.tb_del.addAction(delAction)

    def initDB(self):
        if os.path.exists('DB/info.db'):
            self.conn = sqlite3.connect('DB/info.db')
            self.conn.isolation_level = None
        else:
            self.conn = sqlite3.connect('DB/info.db')
            self.conn.isolation_level = None
            self.conn.execute('''CREATE TABLE INFO
            (ID INT PRIMARY KEY NOT NULL,
            WEBSITE CHAR(255),
            USERNAME CHAR(255),
            PASSWORD CHAR(255),
            URL CHAR(255))''')
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM INFO')
        self.displayData = cursor.fetchall()
        cursor.close()
        self.current_row = len(self.displayData)
        for row in range(self.current_row):
            self.grid.insertRow(self.displayData[row][0] - 1)
            for i in range(4):
                new_item = QtGui.QTableWidgetItem(self.displayData[row][i + 1])
                self.grid.setItem(self.displayData[row][0] - 1, i, new_item)


    def initGrid(self):
        self.grid = QtGui.QTableWidget()
        self.setCentralWidget(self.grid)
        # set cols=4, row=0
        self.grid.setColumnCount(4)
        self.grid.setRowCount(0)
        column_width = [75, 150, 270, 150]
        for colunm in range(4):
            self.grid.setColumnWidth(colunm, column_width[colunm])
        headerlabels = ['WebSite', 'Username', 'Password', 'Url']
        self.grid.setHorizontalHeaderLabels(headerlabels)
        self.grid.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.grid.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        # self.setFixedSize(self.sizeHint())
        self.show()

    def newAction_def(self):
        data = self.showDialog()
        if data[0]:
            self.current_row += 1
            self.grid.insertRow(self.current_row - 1)
            for i in range(4):
                new_item = QtGui.QTableWidgetItem(data[i+1])
                self.grid.setItem(self.current_row - 1, i, new_item)
            # save to database
            self.conn.execute("INSERT INTO INFO VALUES(%d, '%s', '%s', '%s', '%s')"
                              % (self.current_row, data[1], data[2], data[3], data[4]))
            # self.conn.commit()

    def editAction_def(self):
        selected_row = self.grid.selectedItems()
        if selected_row:
            edit_row = self.grid.row(selected_row[0])
            old_data = []
            for i in range(4):
                old_data.append(self.grid.item(edit_row, i).text())
            new_data = self.showDialog(*old_data)
            if new_data[0]:
                for i in range(4):
                    new_item = QtGui.QTableWidgetItem(new_data[i+1])
                    self.grid.setItem(edit_row, i, new_item)
                    self.conn.execute('''UPDATE INFO SET
                                             WEBSITE = '%s', USERNAME = '%s',
                                             PASSWORD = '%s', URL = '%s'
                                             WHERE ID = '%d' '''
                                      % (new_data[1], new_data[2], new_data[3], new_data[4], edit_row + 1))
                    # self.conn.commit()
        else:
            self.showHint()

    def delAction_def(self):
        selected_row = self.grid.selectedItems()
        if selected_row:
            del_row = self.grid.row(selected_row[0])
            self.conn.execute('DELETE FROM INFO WHERE ID=%d' % (del_row + 1))
            self.grid.removeRow(del_row)
            for index in range(del_row + 2, self.current_row + 1):
                self.conn.execute('UPDATE INFO SET ID=%d WHERE ID=%d' % ((index-1), index))
            # self.conn.commit()
            self.current_row -= 1
        else:
            self.showHint()

    def showDialog(self, ws='', un='', pw='', url=''):

        edit_dialog = QtGui.QDialog(self)
        group = QtGui.QGroupBox('Edit Info', edit_dialog)

        lbl_website = QtGui.QLabel('Website:', group)
        le_website = QtGui.QLineEdit(group)
        le_website.setText(ws)

        lbl_username = QtGui.QLabel('Username:', group)
        le_username = QtGui.QLineEdit(group)
        le_username.setText(un)

        lbl_password = QtGui.QLabel('Password:', group)
        le_password = QtGui.QLineEdit(group)
        le_password.setText(pw)

        lbl_url = QtGui.QLabel('Url:', group)
        le_url = QtGui.QLineEdit(group)
        le_url.setText(url)

        ok_btn = QtGui.QPushButton('OK', edit_dialog)
        cancel_btn = QtGui.QPushButton('Cancel', edit_dialog)

        ok_btn.clicked.connect(edit_dialog.accept)
        ok_btn.setDefault(True)
        cancel_btn.clicked.connect(edit_dialog.reject)

        group_layout = QtGui.QVBoxLayout()
        group_item = [lbl_website, le_website,
                      lbl_username, le_username,
                      lbl_password, le_password,
                      lbl_url, le_url]
        for item in group_item:
            group_layout.addWidget(item)
        group.setLayout(group_layout)
        group.setFixedSize(group.sizeHint())

        btn_layout = QtGui.QHBoxLayout()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        dialog_layout = QtGui.QVBoxLayout()
        dialog_layout.addWidget(group)
        dialog_layout.addLayout(btn_layout)
        edit_dialog.setLayout(dialog_layout)
        edit_dialog.setFixedSize(edit_dialog.sizeHint())

        if edit_dialog.exec_():
            website = le_website.text()
            username = le_username.text()
            password = le_password.text()
            url = le_url.text()
            return True, website, username, password, url
        return False, None, None, None, None, None

    def showHint(self):
        hint_msg = QtGui.QMessageBox()
        hint_msg.setText('No selected row!')
        hint_msg.addButton(QtGui.QMessageBox.Ok)
        hint_msg.exec_()


