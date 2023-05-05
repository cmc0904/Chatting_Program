import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import socket, threading, json
form = uic.loadUiType("chat.ui")[0]

class Chat(QWidget, form):


    def __init__(self, name):
        super().__init__()
        self.setupUi(self)
        # self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle(name)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.plainTextEdit.setReadOnly(True)
        self.send.clicked.connect(self.sendMsg)

        self.id = name
        self.dict = {'name' : self.id,  'message' : None , 'type' : "Join"}

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('127.0.0.1', 4000))

        print("클라이언트 소켓정보 : ", self.client_socket)
        th = threading.Thread(target=self.worker, name="[스레드 이름 {}]".format(self.client_socket), args=(self.client_socket,))
        th.start()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return:
            self.sendMsg()

    def sendMsg(self):
        self.dict['type'] = 'SendMsg'
        self.dict['message'] = self.lineEdit.text()
        data = json.dumps(self.dict)
        self.client_socket.send((str(len(data.encode())).zfill(4) + str(data)).encode())
        self.lineEdit.clear()

    def worker(self, conn):
        data = json.dumps(self.dict)
        self.client_socket.send((str(len(data.encode())).zfill(4) + str(data)).encode())
        while True:
            header = conn.recv(4)
            body = conn.recv(int(header.decode()))
            datas = json.loads(body.decode())

            if datas["type"] == 'SendMsg':
                self.plainTextEdit.insertPlainText("[ %s ] : %s\n" % (datas['name'], datas['message']))
            elif datas["type"] == "Leave":
                self.plainTextEdit.insertPlainText("[ %s 님이 퇴장 하였습니다. ]\n" % datas['name'])
                model = QStandardItemModel()
                for x in json.loads(datas['message']):
                    model.appendRow(QStandardItem(x))
                self.listView.setModel(model)
            elif datas["type"] == "Join":
                self.plainTextEdit.insertPlainText("[ %s 님이 참여 하였습니다. ]\n" % datas['name'])
                model = QStandardItemModel()
                for x in json.loads(datas['message']):
                    model.appendRow(QStandardItem(x))
                self.listView.setModel(model)

        conn.close()

    def closeEvent(self, event):
        self.dict["type"] = "Leave"
        data = json.dumps(self.dict)
        self.client_socket.send((str(len(data.encode())).zfill(4) + data).encode())

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('SWH Academy Window.')

        centerGeometry = QDesktopWidget().availableGeometry().center()
        self.resize(300, 100)
        frameGeometry = self.frameGeometry()
        frameGeometry.moveCenter(centerGeometry)

        self.idLabel = QLabel("아이디 : ")
        self.idLineEdit = QLineEdit()
        self.loginButton = QPushButton("로그인")
        self.loginButton.clicked.connect(self.buttonClicked)
        layout = QGridLayout()

        layout.addWidget(self.idLabel, 0, 0)
        layout.addWidget(self.idLineEdit, 0, 1)

        layout.addWidget(self.loginButton, 1, 1)

        self.setLayout(layout)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return:
            self.buttonClicked()

    def buttonClicked(self):
        if len(self.idLineEdit.text()) == 0:
            return
        self.chatting = Chat(self.idLineEdit.text())
        self.chatting.show()
        window.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())