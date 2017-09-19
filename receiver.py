#DEFINING PROPER LIBRARIES
import time
import thread
import datetime
import sys
import socket
import os

abp = 0; #Alternating Bit Protocol
k = 1;

#2 bytes checksum function
def checksum(data):
    delt = 1020 - (sys.getsizeof(data) - 37) # -37 because the getsize function add 37 bytes
    data_pad = data + ('\0' * delt)
    checksum_b = 0
    for i in range(0, 1020, 2):
        data_byte = ord(data_pad[i + 1]) + (ord(data_pad[i]) << 8)    #translates data into unicode/binary
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


def rcv_pckt(yourSocket):               #mySocket is receiving socket
    global abp
    global k
    while True:
        data_rcv, address = yourSocket.recvfrom(1024)
        if data_rcv[1] == repr(abp) and checksum(data_rcv[4:]) == data_rcv[2:4]:
            timestamp()
            sys.stderr.write(" [recv data] " + "PKT" + str(abp) + " " + str(len(data_rcv)*k) + " (" + str(len(data_rcv)) + ")" + " ACCEPTED\n")
            k += 1
            ACK = chr(4) + repr(abp) + checksum('') + '\0'*1020
            yourSocket.sendto(ACK, address)
            abp = 1 - abp                           #update value of ABP
            return data_rcv[4:].replace('\0', '')
        else:
            timestamp()
            sys.stderr.write(" [recv corrupted packet]\n")
            ACK = chr(4) + repr(1 - abp) + checksum('') + '\0'*1020
            yourSocket.sendto(ACK, address)
        return 'corrupt'



#********MAIN*********

#recv takes UDP port number of receiver
arg = sys.argv[1]
recvPort = int(arg)

recvHost = "127.0.0.1" #localhost
recvAddress = (recvHost, recvPort)

#creating Socket for receiver
recvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#binding Socket to local UDP port
recvSocket.bind(recvAddress)

#receiver ready to receive god bless
timestamp()
sys.stderr.write(" [bound] " + arg +"\n")

#receive file name from sender
filename,senderAddress = recvSocket.recvfrom(1024)
#open new file where the sent file will be copied
f = open('recv_' + filename, 'wb')
start_time = time.time()        #to calculate how long receiving lasts
data = rcv_pckt(recvSocket)
print "\n****receiving file\n"
while(data):
    if data == 'EOF':
        break
    if data != 'corrupt':       #if data corrupt skip write, rcv packet again
        f.write(data)
    data = rcv_pckt(recvSocket)
timestamp()
sys.stderr.write(" [receiver completed]\n\n")
#printing the duration from receiver's side
sys.stderr.write("****Duration of process from receiver side: " + str(time.time() - start_time) +"ms\n")
f.close()
recvSocket.close()
print "...Receiver exited gracefully\n\n\n"
