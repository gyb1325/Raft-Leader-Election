import socket
import pickle
import time
import random
import threading
import kthread
from Message import *
#from Server import *

def acceptor(server, data, addr):
    Msg = pickle.loads(data)
    type = Msg.type
    sender = Msg.sender
    term = Msg.term
    if type == 1: # RequestVote
        print("Receive Request Vote Message from {}".format(sender))
        if sender not in server.peers:
            return
        msg = Msg.data
        msg = msg.split(" ")

        if term < server.cur_term:
            print("Reject vote due to old term")
            voteGranted = 0

        elif term == server.cur_term:
            if server.VoteFor == -1 or server.VoteFor == sender:
                voteGranted = 1
            else:
                voteGranted = 0
        else:
            server.cur_term = term
            server.step_down()
            voteGranted = 1
            server.VoteFor = sender
        if voteGranted == 1:
            print("Granted")
        else:
            print("Not Granted")
        reply = str(voteGranted)
        reply_msg = VoteResponseMsg(server.id, sender, server.cur_term, reply)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(pickle.dumps(reply_msg),("", server.serverlist[sender]))

    elif type == 2: #VoteResponseMsg
        print("Receive Vote Response Msg from server {}".format(sender))
        msg = Msg.data
        voteGranted = int(msg)
        if voteGranted:
            if server.role == "candidate":
                server.request_votes.remove(sender)
                server.numVotes += 1
                if server.numVotes == server.majority:
                    print("Get majority Vote, become the leader at term {}".format(server.cur_term))
                    if server.election.is_alive():
                        server.election.kill()
                    server.role = "leader"
                    server.follower_state.kill()
                    server.leader_state = kthread.KThread(target = server.leader, args = ())
                    server.leader_state.start()
        else:
            if term > server.cur_term:
                server.cur_term = term
                if server.role == "candidate":
                    server.step_down()

    elif type == 0:
        print("Receive heartbeat from {}".format(sender))
        if term >= server.cur_term:
            server.cur_term = term
            server.step_down()
            if server.role == "follower":
                server.last_update = time.time()
            success = "True"
            server.leaderID = sender
        else:
            success = "False"
        reply_msg = AppendEntryResponseMsg(server.id, sender, server.cur_term, success)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(pickle.dumps(reply_msg), ("", server.serverlist[sender]))

    elif type == 3:
        success = Msg.success
        if success == "False":
            if term > server.cur_term:
                server.step_down()
        else:
            print("Receive heartbeat response from {}".format(sender))






