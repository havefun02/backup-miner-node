class Frame:
    def __init__(self, frame_type, frame_length, frame_payload):
        self.type = frame_type
        self.length = frame_length
        self.payload = frame_payload
    @classmethod
    def string_to_hex(cls,str):
        res=bytes(str, 'utf-8').hex()
        return res

    def create_frame(self):
        #create frame with little endian format
        # Convert type, length, and payload to hex strings
        type_hex = format(self.type, '02X')
        length_hex = format(self.length, '06X')
        # Concatenate hex strings
        hex_string = type_hex + length_hex + self.string_to_hex(self.payload)

        # Convert hex string to bytes with little-endian format
        res = bytes.fromhex(hex_string)
        return res
    @classmethod
    def extract_frame(cls, frame_bytes):

        frame_type = frame_bytes[0:1]
        frame_length = int.from_bytes(frame_bytes[1:4],byteorder="big")
        payload = frame_bytes[4:4+frame_length]
        return cls(frame_type, frame_length, payload)
