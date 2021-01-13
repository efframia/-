# 文件名：tcpclient.py
import socket
MaxBytes = 1024 * 1024
#host = '127.0.0.1'
#port = 11223
host = input("请输入要连入的ip地址：");
port = input("请输入端口号：");
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(30)
client.connect((host, int(port)))
while True:
    inputData = input("请输入要发送的小写英文文本：（如需退出，请输入quit）");  # 等待输入数据
    if (inputData == "quit"):
        print("正在退出程序...")
        break
    sendBytes = client.send(inputData.encode())
    if sendBytes <= 0:
        break;
    recvData = client.recv(MaxBytes)
    if not recvData:
        print('接收数据为空，即将退出程序...')
        break
    print("接收服务器返回文本：",recvData.decode())
client.close()
print("成功退出！")
