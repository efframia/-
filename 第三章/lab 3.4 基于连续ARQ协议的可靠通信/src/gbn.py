"""
This module implements the sender and receiver of Go-Back-N Protocol.
"""
import random
import socket
import struct
import time
from config import Config


BUFFER_SIZE = 4096
TIMEOUT = 10
WINDOW_SIZE = 4
LOSS_RATE = Config.FilterLost / 100
ERROR_RATE = Config.FilterError / 100

def checkCRC(message):
    # CRC-16-CITT poly, the CRC sheme used by ymodem protocol
    poly = 0x1021
    # 16bit operation register, initialized to zeros
    reg = 0x0000
    # pad the end of the message with the size of the poly
    message += '\x00\x00'
    # for each bit in the message
    for byte in message:
        mask = 0x80
        while (mask > 0):
            # left shift by one
            reg <<= 1
            # input the next bit from the message into the right hand side of the op reg
            if ord(byte) & mask:
                reg += 1
            mask >>= 1
            # if a one popped out the left of the reg, xor reg w/poly
            if reg > 0xffff:
                # eliminate any one that popped out the left
                reg &= 0xffff
                # xor with the poly, this is the remainder
                reg ^= poly
    return reg

class GBNSender:
    def __init__(self, senderSocket, address, timeout=TIMEOUT,
                    windowSize=WINDOW_SIZE, lossRate=LOSS_RATE):
        self.sender_socket = senderSocket
        self.timeout = timeout
        self.address = address
        self.window_size = windowSize
        self.loss_rate = lossRate
        self.send_base = 0
        self.next_seq = 0
        self.packets = [None] * 256

    def udp_send(self, pkt):
        if self.loss_rate == 0 or random.randint(0, int(1 / self.loss_rate)) != 1:
            self.sender_socket.sendto(pkt, self.address)
        else:
            print('发送方帧丢失.')
        time.sleep(0.3)

    def wait_ack(self):
        self.sender_socket.settimeout(self.timeout)

        count = 0
        while True:
            if count >= 10:
                # 连续超时10次，接收方已断开，终止
                break
            try:
                data, address = self.sender_socket.recvfrom(BUFFER_SIZE)

                ack_seq, expect_seq = self.analyse_pkt(data)
                print('发送方收到ACK：' + str(ack_seq) + '，期望ACK：' + str(expect_seq))

                if (self.send_base == (ack_seq + 1) % 256):
                    # 收到重复确认, 此处应当立即重发
                    pass
                    # for i in range(self.send_base, self.next_seq):
                    #     print('Sender resend packet:', i)
                    #     self.udp_send(self.packets[i])

                self.send_base = max(self.send_base, (ack_seq + 1) % 256)
                if self.send_base == self.next_seq:  # 已发送分组确认完毕
                    self.sender_socket.settimeout(None)
                    return True

            except socket.timeout:
                # 超时，重发分组.
                print('超时，重发数据.')
                for i in range(self.send_base, self.next_seq):
                    print('发送方重发帧：', i)
                    self.udp_send(self.packets[i])
                self.sender_socket.settimeout(self.timeout)  # reset timer
                count += 1
        return False

    def make_pkt(self, seqNum, data, checkcrc, stop=False):
        """
        将数据打包
        """
        flag = 1 if stop else 0
        #print("1+",checkCRC(data.decode('unicode_escape')))
        return struct.pack('BBH', seqNum, flag, checkcrc) + data

    def analyse_pkt(self, pkt):
        """
        分析数据包
        """
        ack_seq = pkt[0]
        expect_seq = pkt[1]
        return ack_seq, expect_seq

class GBNReceiver:
    def __init__(self, receiverSocket, timeout=10, errorRate=ERROR_RATE):
        self.receiver_socket = receiverSocket
        self.timeout = timeout
        self.error_rate = errorRate
        self.expect_seq = 0
        self.target = None

    def udp_send(self, pkt):
        #if self.loss_rate == 0 or random.randint(0, 1 / self.loss_rate) != 1:
        self.receiver_socket.sendto(pkt, self.target)
        print('接收方发送ACK：'+ str(pkt[0]) + '，实际应发ACK：' + str(pkt[1]))
        #else:
            #print('接收者发送ACK:'+ str(pkt[0]) + '丢失.')

    def wait_data(self):
        """
        接收方等待接受数据包
        """
        self.receiver_socket.settimeout(self.timeout)

        while True:
            try:
                data, address = self.receiver_socket.recvfrom(BUFFER_SIZE)
                self.target = address

                seq_num, flag, checkcrc, data = self.analyse_pkt(data)
                # 收到期望数据包且未出错
                #if seq_num == self.expect_seq and getChecksum(data) == checkcrc :
                if seq_num == self.expect_seq and checkCRC(data.decode('utf-8','ignore')) == checkcrc:
                    if random.randint(0, int(1 / self.error_rate)) != 1 :
                        print('接收方接受帧：', seq_num)
                        self.expect_seq = (self.expect_seq + 1) % 256
                        ack_pkt = self.make_pkt(seq_num, seq_num)
                        self.udp_send(ack_pkt)
                        if flag:    # 最后一个数据包
                            return data, True
                        else:
                            return data, False
                    else:
                        print('发送方帧出错：', seq_num)
                        ack_pkt = self.make_pkt((self.expect_seq - 1) % 256, self.expect_seq)
                        self.udp_send(ack_pkt)
                        return bytes('', encoding='utf-8'), False
                else:
                    ack_pkt = self.make_pkt((self.expect_seq - 1) % 256, self.expect_seq)
                    self.udp_send(ack_pkt)
                    return bytes('', encoding='utf-8'), False

            except socket.timeout:
                return bytes('', encoding='utf-8'), False

    def analyse_pkt(self, pkt):
        '''
        分析数据包
        '''
        # if len(pkt) < 4:
        # print 'Invalid Packet'
        # return False
        seq_num = pkt[0]
        flag = pkt[1]
        checkcrc = struct.unpack('H',pkt[2:4])
        data = pkt[4:]
        #print(seq_num,flag,checkcrc,data)
        #print("1",checkcrc[0])
        #print("2",checkCRC(data.decode('utf-8')))
        #print(checkCRC(data.decode('utf-8')) == checkcrc[0])
        return seq_num, flag, checkcrc[0], data

    def make_pkt(self, ackSeq, expectSeq):
        """
        创建ACK确认报文
        """
        return struct.pack('BB', ackSeq, expectSeq)

