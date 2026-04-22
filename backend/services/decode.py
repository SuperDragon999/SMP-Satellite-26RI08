import io
from kaitaistruct import KaitaiStream
from services.sys_kaitai.norby import Norby #Auto created by kaitai struct compiler

def fdecode_satellite_packet(file_path):
    '''
    Decodes data from a packet file that is already saved
    '''
    with open(file_path, "rb") as f:
        # Read the raw binary data
        raw_data = f.read()
        stream = KaitaiStream(io.BytesIO(raw_data)) #creates an object from kaitai stream for easy byte manipulation
        
        # Create the Norby object
        packet = Norby(stream)

        #Packet debug code below:
        # header = vars(packet.Header)
        # payload = vars(packet.payload)
        # for x,y in header.items():
        #     if x[0] == "_":
        #         pass
        #     else:
        #         print(x + ":", y)
        # for x,y in payload.items():
        #     if x[0] == "_":
        #         pass
        #     else:
        #         print(x + ":", y)        

        # Return packet
        return packet

def rdecode_satellite_packet(raw_data):
    '''
    Decodes data from a raw data packet (Must be in hexadecimal, not raw text)
    '''
    packet_start = 0
    stream = KaitaiStream(io.BytesIO(raw_data[packet_start:]))
    
    # Create the Norby object
    packet = Norby(stream)

    # Return packet
    return packet