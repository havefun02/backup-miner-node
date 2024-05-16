import urllib.request
import urllib.error
import urllib.parse
import base64
import json
import hashlib
import struct
import random
import time
import os
import sys

def int2varinthex(value):
    """
    Convert an unsigned integer to little endian varint ASCII hex string.

    Args:
        value (int): value

    Returns:
        string: ASCII hex string
    """

    if value < 0xfd:
        return int2lehex(value, 1)
    elif value <= 0xffff:
        return "fd" + int2lehex(value, 2)
    elif value <= 0xffffffff:
        return "fe" + int2lehex(value, 4)
    else:
        return "ff" + int2lehex(value, 8)

def tx_compute_hash(tx):
    """
    Compute the SHA256 double hash of a transaction.

    Arguments:
        tx (string): transaction data as an ASCII hex string

    Return:
        string: transaction hash as an ASCII hex string
    """

    return hashlib.sha256(hashlib.sha256(bytes.fromhex(tx)).digest()).digest()[::-1].hex()



def block_make_header(block):
    """
    Make the block header.

    Arguments:
        block (dict): block template

    Returns:
        bytes: block header
    """

    header = b""

    # Version
    header += struct.pack("<L", block['version'])
    # Previous Block Hash
    header += bytes.fromhex(block['previousblockhash'])[::-1]
    # Merkle Root Hash
    header += bytes.fromhex(block['merkleroot'])[::-1]
    # Time
    header += struct.pack("<L", block['curtime'])
    # Target Bits
    header += bytes.fromhex(block['bits'])[::-1]
    # Nonce
    header += struct.pack("<L", block['nonce'])

    return header


def block_compute_raw_hash(header):
    """
    Compute the raw SHA256 double hash of a block header.

    Arguments:
        header (bytes): block header

    Returns:
        bytes: block hash
    """

    return hashlib.sha256(hashlib.sha256(header).digest()).digest()[::-1]


def block_bits2target(bits):
    """
    Convert compressed target (block bits) encoding to target value.

    Arguments:
        bits (string): compressed target as an ASCII hex string

    Returns:
        bytes: big endian target
    """

    # Bits: 1b0404cb
    #       1b          left shift of (0x1b - 3) bytes
    #         0404cb    value
    bits = bytes.fromhex(bits)
    shift = bits[0] - 3
    value = bits[1:]

    # Shift value to the left by shift
    target = value + b"\x00" * shift
    # Add leading zeros
    target = b"\x00" * (32 - len(target)) + target

    return target


def block_make_submit(block):
    """
    Format a solved block into the ASCII hex submit format.

    Arguments:
        block (dict): block template with 'nonce' and 'hash' populated

    Returns:
        string: block submission as an ASCII hex string
    """

    submission = ""

    # Block header
    submission += block_make_header(block).hex()
    # Number of transactions as a varint
    submission += int2varinthex(len(block['transactions']))
    # Concatenated transactions data
    for tx in block['transactions']:
        submission += tx['data']

    return submission



def block_mine(block_template,stop_event, timeout=None, debugnonce_start=False):
    time_start=time.time()
    hashrate,hash_count=0.0,0

    nonce=0
    if (block_template['nonce'] is None):
        block_template['nonce'] = 0
    else:
        nonce=block_template['nonce']+1
    target_hash = block_bits2target(block_template['bits'])
    target_share_hash = bytes.fromhex(block_template["target"])

    block_header = block_make_header(block_template)

    while nonce <= 0xffffffff:
        if (stop_event.is_set()):
            return (3,None)
        # Update the block header with the new 32-bit nonce
        block_header = block_header[0:76] + nonce.to_bytes(4, byteorder='little')

        # Recompute the block hash
        block_hash = block_compute_raw_hash(block_header)

        # Check if it the block meets the target hash
        if block_hash < target_hash:
            hashrate=hash_count/(time.time()-time_start)
            block_template['nonce'] = nonce
            block_template['hash'] = block_hash.hex()
            block_template['hashrate']=hashrate
            return (1,block_template)
        elif block_hash<target_share_hash:
            hashrate=hash_count/(time.time()-time_start)
            block_template['nonce'] = nonce
            block_template['hash'] = block_hash.hex()
            block_template['hashrate']=hashrate
            print(hash_count,time.time()-time_start)
            return (2,block_template)
        hash_count+=1
        nonce += 1
    # print("run out of nonce")
    return (None,None)
    
