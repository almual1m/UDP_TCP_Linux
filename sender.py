#DEFINING PROPER LIBRARIES
import time
import thread
import datetime
import sys
import socket
import os

abp = 0; #Alternating Bit Protocol
k = 1; #counting offset

#2 bytes checksum function
def checksum(data):
    delt = 1020 - (sys.getsizeof(data) - 37) # -37 because the getsize function adds 37 bytes
    data_pad = data + ('\0' * delt)               #padding
    checksum_b = 0
    for i in range(0, 1020, 2):
        data_byte = ord(data_pad[i + 1]) + (ord(data_pad[i]) << 8)    #translates data into udata_padode/binary
        checksum_b += data_byte
        if checksum_b >> 16:         #if checksum overflows, add the carry
            checksum_b &= 0xffff
            checksum_b += 0x1
    checksum_b = (~checksum_b) & 0xffff   #1s complement
    checksum_str = chr(checksum_b & 0xff) + chr((checksum_b & 0xff00) >> 8)  #store in string
    return checksum_str

#function to print timestamp
def timestamp():
	sys.stderr.write(datetime.datetime.now().strftime("<%H:%M:%S.%f>"))


#Packet size is 1024B for convenience
#because if size>1500B ethernet will fragment it
#2B sequence number
#1B flag kept for consistency for checksum (even data length)
#2B for checksum
#1000B for data to send
def send_pckt(mySocket, dest_address, flag, data):      #mySocket is sending socket
    global abp
    global k

    diff = 1020 - (sys.getsizeof(data) - 37)
    if diff > 0:
        data = data + '\0' * diff #if packet size <1024, use padding with nulls
    pckt = chr(flag) + repr(abp) + checksum(data) + data
    timestamp()
    sys.stderr.write(" [sending] " + "PKT" + str(abp) + " " + str(len(pckt)*k) + " (" + str(len(pckt)) + ")" + "\n")
    mySocket.sendto(pckt, dest_address)
    #<timestamp> [sending]
    mySocket.settimeout(4)
    while True:
        try:
            ack_rcv, address = mySocket.recvfrom(1024)
            if ack_rcv[0] == chr(4) and ack_rcv[1] == repr(abp):
                timestamp()
                sys.stderr.write(" [recv ack] " + "ACK" + str(abp) + " " + str(len(pckt)*k)+ "\n")
                k += 1
                mySocket.settimeout(None)
                break
            else:
                mySocket.sendto(pckt, dest_address)
                continue
        except socket.timeout:
            mySocket.sendto(pckt, dest_address)
            continue
    abp = 1 - abp;


#***************MAIN******************
#getting arguments from command
#sender takes IP address of receiver
arg = sys.argv[1]
recvHost = str(arg)

#UDP port number of receiver
arg = sys.argv[2]
recvPort = int(arg)
if any([recvPort < 1024, recvPort > 60000]):
    sys.exit("Port must be between 1024 and 60000. Exiting...")

#file we want to transmit
arg = sys.argv[3]
file_name = str(arg)
if not os.path.exists(file_name):
    sys.exit("File not available in the directory. Exiting...")

#recvAddress
recvAddress = (recvHost, recvPort)

#first send the name of the file
print "\n****sending file name & extension to receiver\n"
senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
senderSocket.sendto(file_name,recvAddress)

while True:
    start_time = time.time() #start point to calcualte duration of process
    #open the file requested
#    send_pckt(senderSocket, recvAddress, 1, 'begin')
    f = open(file_name,"rb")
    #read 1020B of data (without the header obv.)
    data = f.read(1020)

    while data != '':
        send_pckt(senderSocket, recvAddress, 2, data)
        data = f.read(1020)
    print "\n****end of file has been reached, sending EOF packet\n"
    send_pckt(senderSocket, recvAddress, 3, 'EOF')  #this is the last packet with EOF
    break
timestamp()
sys.stderr.write(" [sender completed]\n\n")
sys.stderr.write("****Duration of process from sender side: " + str(time.time() - start_time) +"ms\n")
senderSocket.close()
f.close()
print "...Sender exited gracefully\n\n\n"
