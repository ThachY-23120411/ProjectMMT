import socket
import os
import threading

HOST = "127.0.0.1"
SERVER_PORT = 65432
FORMAT = "utf8"

# Hàm xử lý từng client (Hàm thực hiện các chức năng như upload và download cho 1 client)
def handle_client(conn, addr):
    print(f"Client connected: {addr}")
    try:
        msg = None
        while msg != "end":
            msg = conn.recv(1024).decode(FORMAT)
            print(f"Client {addr} talk: {msg}")
            if msg == "upload":
                conn.sendall("Ready to receive file".encode(FORMAT))
                file_name = received_prop_filename(conn, None)
                file_size = received_prop_filesize(conn, None)
                case = check_exist_file_on_server(file_name, file_size)
                received_data_server(case, conn, file_name, file_size)
                
            elif msg == "dowload":
                dowload_path = conn.recv(1024).decode(FORMAT)
                if not os.path.exists(dowload_path):
                    conn.sendall("ERROR".encode(FORMAT))
                else:
                    conn.sendall("GOOD".encode(FORMAT))
                    file_size = os.path.getsize(dowload_path)
                    conn.sendall(str(file_size).encode(FORMAT))
                    send_data(conn, dowload_path, file_size)
    
    except Exception as e:
        print(f"Lỗi xử lý client {addr}: {e}")
    finally:
        conn.close()
        print(f"Client {addr} disconnected.")

# Hàm khởi động server (Hàm chịu trách nhiệm tạo đa luồng)
def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, SERVER_PORT))
    s.listen()
    print("SERVER SIDE")
    print(f"Server running on {HOST}:{SERVER_PORT}")
    
    while True:#vòng lặp để chấp nhận kết nối từ các client
        conn, addr = s.accept()
        print(f"Client {addr} connected.")
        
        # Tạo một luồng mới để xử lý client
        client_thread = threading.Thread(target=handle_client, args=(conn, addr)) ##Khi đã có 1 client kết nối tới thì server sẽ tạo 1 luồng mới và mỗi luồng mới sẽ gọi hàm 'handle_client' để xử lí upload/download với 2 tham số tr vào hàm 'handle_client' là args=(conn,addr) vs conn là đối tượng kết nối, addr là địa chỉ client
        client_thread.start()
        ##Tiếp tục lắng nghe các kết nối từ các client khác (Vì vòng lặp này là vô tận)

# Các hàm hỗ trợ khác
def received_prop_filename(socket, file_name):
    file_name = socket.recv(1024).decode(FORMAT)
    socket.sendall(f"Received file name: {file_name}".encode(FORMAT))
    print(f"Tên file nhận được: {file_name}")
    return file_name

def received_prop_filesize(conn, file_size):
    file_size = int(conn.recv(1024).decode(FORMAT))
    print(f"Kích thước file nhận được: {file_size} bytes")
    return file_size

def check_exist_file_on_server(file_name, file_size):
    if not os.path.exists(file_name):
        return 1
    else:
        return 2

def received_data_server(case, socket, file_name, file_size):
    if case == 1:
        socket.sendall("TH1".encode(FORMAT))
        with open(file_name, "wb") as f:
            received = 0
            while received < file_size:
                chunk = socket.recv(min(1024, file_size - received))
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)
                percent = received / file_size * 100
                print(f"Đã nhận {received}/{file_size} bytes {percent:.2f}%")
        print(f"File {file_name} đã được lưu thành công.")
    elif case == 2:
        print("Có file bị trùng lặp đang chờ phản hồi của Client")
        socket.sendall("TH2".encode(FORMAT))
        msg = socket.recv(1024).decode(FORMAT)
        print("Client phản hồi:", msg)
        if msg == "overwrite":
            with open(file_name, "wb") as f:
                received = 0
                while received < file_size:
                    chunk = socket.recv(min(1024, file_size - received))
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
                    percent = received / file_size * 100
                    print(f"Đã nhận {received}/{file_size} bytes {percent:.2f}%")
            print(f"File {file_name} đã được lưu thành công.")

def send_data(socket, file_name, file_size):
    with open(file_name, mode='rb') as f:
        sent = 0
        while chunk := f.read(1024):
            socket.sendall(chunk)
            sent += len(chunk)
            percent = sent / file_size * 100
            print(f"Đã gửi {sent}/{file_size} bytes {percent:.2f}%")
    print("Đã gửi file thành công.")

if __name__ == "__main__": # hàm start_server() sẽ được chạy khi ta chạy code (Ctrl + F5)
    start_server()
