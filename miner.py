import socket
import threading
import time
from frame import *
from protocols import *
from helper import *
from work import block_mine
from logger import *
from datetime import datetime
from config import *
class MiningClient:
    _instance = None

    def __new__(cls, host, port):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.host = host
            cls._instance.port = port
            cls._instance.client_socket = None
            cls._instance.mining_thread = None
            cls._instance.logger = Logger()
            cls._instance.state = False
            cls._instance.stop_flag = threading.Event()
        return cls._instance


    def perform_handshake(self):
        handshake_message = self.client_socket.recv(1024)
        if int.from_bytes(Frame.extract_frame(handshake_message).type, byteorder="little") == hello:
            response_message = Frame(ack_hello, 0, "")
            self.client_socket.sendall(response_message.create_frame())
        else:
            # self.logger.log_info('Handshake failed')
            # print("Handshake failed")
            return 0
        handshake_message = self.client_socket.recv(1024)
        if int.from_bytes(Frame.extract_frame(handshake_message).type, byteorder="little") == hello_ok:
            # self.logger.log_info('Handshake success')
            # print("Handshake success")
            return 1
        else:
            # self.logger.log_info('Handshake failed')
            # print("Handshake failed")
            return 0

    def receive_data(self):
        while (1):
            data = self.client_socket.recv(1024)
            if not data:
                self.logger.log_warning("Server down")
                return sys.exit()
            frame_extraction = Frame.extract_frame(data)
            # print(f"Received from server: {data}")
            self.forward_request(frame_extraction.type, frame_extraction.payload)

    def forward_request(self, type_method, data):
        
        if int.from_bytes(type_method, 'little') == notify_job:
            self.logger.log_info("Receive job from pool")
            res = new_job_handler(data)
            # if (self.mining_thread is not None and self.mining_thread.is_alive()):
                # self.mining_thread.join()
            # self.logger.log_info("Start mining")
            self.mining_thread=None
            self.mining_thread = threading.Thread(target=self.mining, args=(res,))
            self.mining_thread.start()
            self.stop_flag=threading.Event()
            return ""
        elif int.from_bytes(type_method, 'little') == submit_success:
            # self.logger.log_info("Submit job success")
            submit_success_handler(data)
            return ""
        elif int.from_bytes(type_method, 'little') == submit_error:
            self.logger.log_info("Submit job error")
            # print("--log-- submit error")
            username=read_username()
            res = request_job_method(username)
            self.client_socket.sendall(res)
            return ""
        elif int.from_bytes(type_method, 'little') == job_not_found:
            # print("--log-- job not found error")
            self.logger.log_info("Job not found")
            return ""
        # elif int.from_bytes(type_method, 'little') == set_target:
        #     self.logger.log_info("Request new target from pool")
        #     print("--log-- request target")
        #     res = request_target_handler()
        #     self.client_socket.sendall(res)
        #     return ""
        # elif int.from_bytes(type_method, 'little') == notify_target:
        #     self.logger.log_info("Receive new target from pool")
        #     print("--log-- set target")
        #     res = set_target_handler(data)
        #     self.client_socket.sendall(res)
        #     return ""
        elif int.from_bytes(type_method, 'little') == set_block:
            self.logger.log_info("Request new job from pool")
            # print("--log-- new block")
            res = new_block_handler()
            self.client_socket.sendall(res)

    def open_connection(self,username,password):
        data = open_connection_method(username,password)
        self.client_socket.sendall(data)
        receive_data=self.client_socket.recv(1024)
        frame=Frame.extract_frame(receive_data)
        if int.from_bytes(frame.type, 'little') == open_success:
            self.logger.log_info("Authorize success")
            byte_data = bytes.fromhex(frame.payload.decode('utf-8'))
            result_string = byte_data.decode('utf-8')
            write_target(result_string[0:64])
            write_username(result_string[64:])
            # print("Authorize success")
            return 1
        elif int.from_bytes(frame.type, 'little') == open_error:
            self.logger.log_info("Authorize error")
            # print("Authorize error")
            return 0

    def start_client(self,username,password):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host, self.port))

            if (self.perform_handshake()==0):
                self.logger.log_warning("Please reconnect")
                return None
            self.logger.log_info(f"Connected to {self.host}:{self.port}")
            if (self.open_connection(username,password)==0):
                self.logger.log_warning("Please try again")
                return None
            input_thread = threading.Thread(target=self.handleIO)
            input_thread.start()

            while(1):
                self.receive_data()

        except ConnectionRefusedError:
            self.logger.log_info("Fail authorize")
            return None

        finally:
            self.client_socket.close()

    def mining(self, block):
        # print("new block mined----------s")
        self.logger.log_info("Start new block")
        block["nonce"]=None
        username = read_username()
        # print(block["curtime"],block["mintime"])
        while(1):            
            status,res = block_mine(block,self.stop_flag)
            if status==1:
                data = submit_method(res["job_id"], res["nonce"], res["curtime"],res["hashrate"],username)
                try:
                    time.sleep(0.1)
                    self.client_socket.sendall(data)
                    self.logger.log_info(f"Submit block network: NONCE:{res['nonce']}, Curtime: {res['curtime']}, Hash: {res['hash']}, Hashrate: {res['hashrate']}")
                except socket.error as e:
                    self.log_critical(f"Fail to submit block {e}")
                break
            elif status==2:
                data = submit_method(res["job_id"], res["nonce"], res["curtime"],res["hashrate"],username)
                self.client_socket.sendall(data)
                self.logger.log_info(f"Submit share: NONCE:{res['nonce']}, Curtime: {res['curtime']}, Hash: {res['hash']}, Hashrate: {res['hashrate']}")
            elif status==3:
                self.logger.log_info("Stop mining")
                return None
            else:
                t = request_job_method(username)
                self.client_socket.sendall(t)
                self.logger.log_info("Run out of nonce")
                return None
            block=res
        

    def handleIO(self):
        while(1):
            i=input()
            if (i=='b'):
                self.state=False
                self.stop_flag.set()
            elif (i=='s'):
                self.state=True
                res = new_block_handler()
                self.client_socket.sendall(res)




if __name__ == "__main__":
    mining_client = MiningClient('127.0.0.1', 3002)
    mining_client.start_client(USERNAME,PASSWORD)
