import cv2
import socket
import threading
import numpy as np
import time
import io

class SocketHandler(socket.socket):
    def __init__(self, ip,port,shape = (640,640,3)):
        self.ip = ip
        self.port = port
        self.shape = shape
        super().__init__(socket.AF_INET,socket.SOCK_STREAM)
        self.bind((self.ip,self.port))
        self.listen()
        self.th = threading.Thread(target = self.accept_and_receive)

        self.cs = None      # client socket
        self.addr = None    # client address

        self.img = None
        self.jpeg = None
        self.th_recv = None

    def accept_and_receive(self):
        self.cs, self.addr =  self.accept()
        return

    
    def recv_forever(self):
        def recv():

            WHOLESIZE = 65535
            BUFSIZ = 4096
            while True:
                num = self.cs.recv(4)
                if len(num) == 0:
                    return
                # print(num, end = ' ')
                num = int(np.frombuffer(num[::-1],np.int32))
                # print(num)
                if(num == 0) :  continue
                dat = b''
                while len(dat) < num:
                    dat+=self.cs.recv(min(BUFSIZ,num - len(dat)))
                
                self.jpeg = np.frombuffer(dat,dtype=np.uint8)
                if modify():
                    return
                
        def forever():
            while True:
                recv()
                self._reconnect()
        def modify():
            try:
                self.img = cv2.imdecode(self.jpeg,1)
                return 0
            except cv2.error:
                return 1
        
        self.th.join()
        self.th_recv = threading.Thread(target = forever)
        self.th_recv.start()
        

        
class SocketReader(object):
    def __init__(self, sock : SocketHandler):
        self.sock = sock
        if  not self.sock.th_recv.is_alive():
            raise socket.SO_ERROR("error on socket")

    def __iter__(self):
        return self

    def __next__(self):
        img = self.sock.img
        if img is None:
            return np.zeros(self.sock.shape,dtype=np.float32)
        if img.size == 0:
            raise IOError('Image {} cannot be read'.format(self.file_names[self.idx]))
        # assert img.shape == self.sock.shape,f"error on image shape : {img.shape}"
        img = img.astype(np.float32)/255.0

        return img
    


        

if __name__ == '__main__':
    PORT = 17171
    ip_addr = socket.gethostbyname(socket.gethostname())
    print(ip_addr, PORT)
    IP = ip_addr
    sock = SocketHandler(IP,PORT,(640,480,3))
    sock.th.start()
    sock.recv_forever()

    for img in SocketReader(sock):
        cv2.imshow('dfs',img)
        cv2.waitKey(1)

        
    
    
        
        

