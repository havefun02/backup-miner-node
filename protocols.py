from message_type import *
from frame import *
from helper import *
from work import*
import struct
from logger import *
def convert_string_hex(hex_string):
    byte_data = bytes.fromhex(hex_string)

    reversed_byte_data = byte_data[::-1]

    reversed_hex_string = reversed_byte_data.hex()
    return reversed_hex_string
def register(username,password):
    data=(Frame.string_to_hex(username+":"+password))
    frame=Frame(open_connection,len(data),data)
    return frame.create_frame()

def open_connection_method(username,password):
    # username="username"
    # password="password"
    data=(Frame.string_to_hex(username+":"+password))
    frame=Frame(open_connection,len(data),data)
    return frame.create_frame()
def open_success_handler(data):
    # target=data[0:64].decode('utf-8')
    byte_data = bytes.fromhex(data.decode('utf-8'))
    username = byte_data.decode('utf-8')
    return write_username(username)
def open_error_handler(data):
    return ""
    #display to screen
def request_job_method(username):
    urn=(Frame.string_to_hex(username))
    # job_id=job_id.to_bytes(4,byteorder="big")
    data=urn
    frame=Frame(request_job,len(data),data)
    return frame.create_frame()
def submit_method(job_id,nonce,ntime,username):
    payload=job_id.to_bytes(4,byteorder="big").hex()+nonce.to_bytes(4,byteorder="big").hex()+ntime.to_bytes(4,byteorder="big").hex()+Frame.string_to_hex(username)
    frame=Frame(submit_job,len(payload),payload)
    return frame.create_frame()
def request_target_handler():
    #request target from server
    # write_target(data)
    username=read_username()
    frame=Frame(request_target,0,Frame.string_to_hex(username))
    return frame.create_frame()
def set_target_handler(data):
    write_target(data.decode("utf-8"))
    
def new_block_handler():
    #request new block from server
    username=read_username()
    data=request_job_method(username)
    return data
def new_job_handler(data):
    block={}
    job_id=int(data[0:8].decode('utf-8'),16)
    version= int(data[8:16].decode('utf-8'),16)
    prevhash=data[16:16+64].decode('utf-8')
    difficulty=data[16+64:16+64+8].decode('utf-8')
    time=int(data[88:96].decode('utf-8'),16)
    mintime=int(data[96:104].decode('utf-8'),16)
    merkle=data[104:104+64].decode('utf-8')
    target=data[104+64:104+64+64].decode('utf-8')
    block["job_id"]=job_id
    block["version"]=version
    block["bits"]=difficulty
    block["previousblockhash"]=prevhash
    block["merkleroot"]=merkle
    block["curtime"]=time
    block["mintime"]=mintime
    block["target"]=target
    #start mining
    return block

def submit_success_handler(data):
    logger=Logger()
    logger.log_info("Id share: "+data.decode("utf-8"))
    return ""

def submit_error_handler(data):
    logger.log_info("Submit error :"+data.decode("utf-8"))
    return ""
