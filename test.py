# import time
# start=time.time()
# nonce=0
# while(1):
#     nonce+=1
#     if (nonce%(1024*1024*1000)==0):
#         print(nonce,time.time()-start)
#         print(nonce/(time.time()-start))

t=0x0000ffff000000000000000000000000000000000000000000000000
hex_str = hex(int(t/7))[2:]

# Pad the string with leading zeros to ensure it is 32 characters long
hex_str_padded = hex_str.zfill(32)
print('0000ffff000000000000000000000000000000000000000000000000')
print(hex(int(0xffff/7)))
