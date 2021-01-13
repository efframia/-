# 文件名：tcpserver.py
import socket
MaxBytes = 1024 * 1024
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.settimeout(60)
host = '127.0.0.1'
# host = socket.gethostname()
port = 11223
server.bind((host, port))  # 绑定端口
server.listen(1)  # 监听
try:
    client, addr = server.accept()  # 等待客户端连接
    print(addr, "已成功连接！")
    while True:
        data = client.recv(MaxBytes)
        if not data:
            print('接收数据为空，即将退出程序...')
            break
        print("接收来自客户端的数据：",data.decode())
        print("发送数据：",data.decode().upper())
        client.send(data.upper())
except BaseException as e:
    print("出现异常：")
    print(repr(e))
finally:
    server.close()  # 关闭连接
    print("成功退出！")
