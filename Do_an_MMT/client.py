
import socket
import os
import threading
def received_prop_filename(socket, file_name):
    file_name = socket.recv(1024).decode(FORMAT)
    socket.sendall(f"Received file name: {file_name}".encode(FORMAT))
    print(f"Tên file nhận được: {file_name}")
    return file_name
def received_prop_filesize(socket, file_size):
    # Nhận kích thước file
    file_size = int(socket.recv(1024).decode(FORMAT))
    print(f"Kích thước file nhận được: {file_size} bytes")
    return file_size


def check_exist_file_on_server(file_name, file_size):
    #check file da ton tai tren server chua
    if not os.path.exists(file_name):
        return 1
    else:
        return 2
          
                    
def received_data_client( socket, file_name, file_size):

        # # Lưu file với tên gốc
        with open(file_name, "wb") as f:
            received = 0
            while received < file_size:
                chunk = socket.recv(min(1024, file_size - received))  # Đọc khối dữ liệu
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)
                percent=received/file_size*100
                print(f"Đã nhận {received}/{file_size} bytes {percent}%")
        print(f"File {file_name} đã được lưu thành công.")
        f.close()
                    
def send_prop(socket, file_name, file_size):
        print(f"Tên file: {file_name}, Kích thước: {file_size} bytes")
        # Gửi tên file trước
        client.sendall(file_name.encode(FORMAT))
        server_msg = socket.recv(1024).decode(FORMAT)  # Nhận phản hồi
        print("SERVER TRA LOI:", server_msg)
        # Gửi kích thước file
        client.sendall(str(file_size).encode(FORMAT)) #ép kiểu kích thước file thành chuỗi str để gửi
def send_data(socket, file_name, file_size):
    with open(file_path, mode='rb') as f:
        send=0
        while True:  # Vòng lặp vô hạn
            # Đọc tối đa 1024 byte dữ liệu từ file (trong 1 vòng lặp)
            chunk = f.read(1024)
                        
            # Nếu chunk rỗng (tức đã đọc hết file), thoát khỏi vòng lặp
            if not chunk:
                break
                    
             #Nếu chunk không rỗng -> Gửi khối dữ liệu hiện tại qua socket
            socket.sendall(chunk)
            send+=len(chunk)
            percent=send/file_size*100
            print(f"Đã tải {send}/{file_size} bytes {percent}%")
                # In thông báo sau khi toàn bộ file đã được gửi
    print("Đã gửi file thành công.")
    f.close()
    


HOST = "127.0.0.1"
SERVER_PORT = 65432
FORMAT = "utf8"

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("CLIENT SIDE")
    client.connect((HOST, SERVER_PORT))
    print("client address:", client.getsockname())
    msg = None
    luachon=None
    while msg != "end":
        msg = input("talk: ")
        client.sendall(msg.encode(FORMAT))

        if msg == "upload":
            
            # Nhận phản hồi từ server
            server_msg = client.recv(1024).decode(FORMAT)
            print("SERVER TRA LOI:", server_msg)
            # Nhập đường dẫn file và kiểm tra tồn tại
            file_path = input("Nhap file path: ")
            if not os.path.exists(file_path):
                print("File không tồn tại.")
            else:
                file_name = os.path.basename(file_path)  # Lấy tên file (vì sử dụng hàm basename--> sẽ tự động lấy tên file từ file path)
                file_size = os.path.getsize(file_path)    
                send_prop(client,file_name, file_size)
            #nhan truong hop
            server_msg=client.recv(1024).decode(FORMAT)
            if server_msg=="TH1":
                # Mở file ở chế độ nhị phân (rb - read binary)
                send_data(client, file_name, file_size)
                continue
            
            elif  server_msg=="TH2":
                
                print("ten file da ton tai, ban co muon overwrite khong: ")
                print("1) Overwrite ")
                print("2) Cancel")
                
                luachon= input("lua chon")
                
                if luachon=="1":
                    client.sendall("overwrite".encode(FORMAT))
                    send_data(client, file_name, file_size)
                else :
                    client.sendall("Cancel".encode(FORMAT))
                    continue
                
        elif  msg=="dowload":
            dowload_path=input("nhap ten file muon dowload trên máy chủ: ")
            client.sendall(dowload_path.encode(FORMAT))
            server_msg=client.recv(1024).decode(FORMAT)
            if server_msg=="GOOD":
                file_size = int(client.recv(1024).decode(FORMAT))
                received_data_client(client,dowload_path,file_size)
            elif server_msg=="ERROR":
                print("FILE không tồn tại trên server")

                
                

except Exception as e:
    print("Lỗi client:", e)
finally:
    client.close()
