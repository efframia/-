import socket
import json
from Config import config

def sim_cong():
    mss = config.MSS
    threshold = config.Threshold
    tri_ack_round = config.TriACKRound
    timeout_round = config.TimeoutRound
    end_round = config.EndRound

    message = []

    cwnd = 1
    ssthresh = int(threshold / mss)
    print("MSS: {}, initial ssthresh: {}".format(mss, ssthresh))

    for i in range(1, end_round + 1):
        print("Round: {}, cwnd: {}.".format(i, cwnd))
        if i == tri_ack_round:
            ssthresh = int(cwnd / 2)
            cwnd = ssthresh
            message.append("3 duplicate ACK at Round %d:begin to Fast Recovery..."%i)
        elif i == timeout_round:
            ssthresh = int(cwnd / 2)
            cwnd = 1
            message.append("Timeout at Round %d:begin to Slow Start..."%i)
        else:
            if cwnd < ssthresh:
                cwnd *= 2
                message.append("Slow Start at Round %d."%i)
            else:
                cwnd += 1
                message.append("Additive Increase at Round %d."%i)
    return message

address = ('127.0.0.1', 31500)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mylist = sim_cong()
json_string = json.dumps(mylist)
s.sendto(json_string.encode(), address)
s.shutdown(socket.SHUT_RDWR)
s.close()
