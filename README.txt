1. First execute receiver.py in Python as follows:
python receiver.py portNumber

2. Then, execute sender.py in Python as follows:
python sender.py 127.0.0.1 portNumber sendingfile.txt


sendingfile.txt is the file you wish to send
portNumber must be the same for both 1. and 2.

The received file will be saved in the same directory as recv_sending.txt
The code supports any file extension
