import json
import kthread
import socket
import time
import random
import pickle
from Message import *
from Functions import *


class Server:
    def __init__(self, id):
        self.id = id
        self.role = "follower"
        self.leaderID = 0
        address = json.load(open("config.json"))
        port_list = address["port"]
        running = address["running"]
        self.serverlist = {}
        for running_id in running:
            self.serverlist[running_id] =  port_list[running_id-1]

        initial_running = [1,2,3,4,5]
        self.cur_term = 0
        self.VoteFor = -1
        self.log = []
        self.peers = [i for i in initial_running if i != self.id]
        self.majority = 3

        self.request_votes = self.peers.copy()
        self.port = self.serverlist[self.id]
        self.lastLogIndex = 0
        self.lastLogTerm = 0

        self.listener = kthread.KThread(target = self.listen, args = (acceptor,))
        self.listener.start()

    def listen(self, accept):
        srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        srv.bind(("",self.port))
        print("start Listening")
        while True:
            data, addr = srv.recvfrom(1024)
            new_thread = kthread.KThread(target = accept, args = (self, data, addr))
            new_thread.start()
        srv.close()

    def follow(self):
        print("The current state is a follower"+ " Time Stamp: " + time.asctime())
        self.role = "follower"
        self.last_update = time.time()
        time_out = 5 + random.random() * 5
        # The following starts the election from the beginning
        while time.time() - self.last_update < time_out:
            pass
        self.start_election()
        # The Following monitor if the follower can get heartbeat from the leader
        while True:
            self.last_update = time.time()
            time_out = 5 + random.random() * 5
            while time.time() - self.last_update < time_out:
                pass
            if self.election.is_alive():
                self.election.kill()
            self.start_election()

    def start_election(self):
        self.role = "cadidate"
        print("The current state is a candidate"+ " Time Stamp: " + time.asctime())
        self.election = kthread.KThread(target = self.thread_election, args =())
        if len(self.peers) != 0:
            self.cur_term += 1
            self.votefor = self.id
            # self.log()
            self.numVotes = 1
            self.election.start()


    def thread_election(self):
        print("Timeout, a new election process is started at term {}, the id is {}".format( self.cur_term, self.id) + " Time Stamp: " + time.asctime())
        self.role = "candidate"
        self.request_votes =self.peers.copy()
        requestor = self.id
        while True:
            for peer in self.peers:
                if peer in self.request_votes:
                    Msg = str(self.lastLogTerm) + " " + str(self.lastLogIndex)
                    msg = RequestVoteMsg(requestor, peer, self.cur_term, Msg)
                    data = pickle.dumps(msg)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(data,("", self.serverlist[peer]))
            time.sleep(1)
    def leader(self):
        print("The current state is a leader"+ " Time Stamp: " + time.asctime())
        self.role = "leader"
        self.send_heartbeats()

    def send_heartbeats(self):
        while True:
            receipts = self.peers[:]
            for peer in receipts:
                Msg = AppendEntryMsg(self.id, peer, self.cur_term)
                data = pickle.dumps(Msg)
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(data, ("", self.serverlist[peer]))
            time.sleep(0.5)

    def step_down(self):
        if self.role == "candidate":
            self.election.kill()
            self.last_update = time.time()
            self.role = "follower"
        elif self.role == "leader":
            self.leader_state.kill()
            self.follower_state = kthread.KThread(target=self.follow, args= ())
            self.follower_state.start()


    def run(self):
        time.sleep(1)
        self.follower_state = kthread.KThread(target = self.follow, args= ())
        self.follower_state.start()









