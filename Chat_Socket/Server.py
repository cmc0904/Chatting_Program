import socket
import threading
import json
connList = []
nameList = list()

def worker(conn):
    while True:
        header = conn.recv(4)
        body = conn.recv(int(header.decode()))
        datas = json.loads(body.decode())

        if datas['type'] == "Join":
            nameList.append(datas['name'])
            datas["message"] = json.dumps(nameList)
        if datas['type'] == "Leave":
            del nameList[nameList.index(datas["name"])]
            datas["message"] = json.dumps(nameList)
        if datas['type'] == "SendMSg":
            datas["message"] = "[ %s ] : %s" % (datas["name"], datas["message"])

        data = json.dumps(datas)
        for b in connList:
            try:
                b.send((str(len(data.encode())).zfill(4) + data).encode())  # 메세지를 연결된 클라이언트에게 전달
            except BrokenPipeError:
                pass
    conn.close()


def run_server(port=4000):
    host = ''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()

        while True:
            conn, addr = s.accept()
            print("서버 소켓정보 : ", conn)
            print("연결된 클라이언트 정보 : ", addr)

            connList.append(conn)
            th = threading.Thread(target=worker, name="[스레드 이름 {}]".format(conn), args=(conn,))
            th.start()  # 생성한 스레드를 시작한다


if __name__ == '__main__':
    run_server()