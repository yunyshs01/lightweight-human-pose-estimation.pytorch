import os
import time
import win32file as wf
import threading

class KeypointTransmitter:
    def __init__(self, pipename = 'testpipe',packet_size = 144):
        self.hFile = None
        self.pipepath = os.path.join("\\\\.\\pipe\\",pipename)
        self.packet_size = packet_size

    def connect(self, max_trials = 0):
        # 파이프서버에 연결합니다. 연결 실패시 초당 1회 재시도합니다.
        # max_trials 0이면 무한히 시도합니다.
        trials = 1
        while True:
            try:
                self.hFile = wf.CreateFile(
                    self.pipepath,
                    wf.GENERIC_WRITE,
                    0, None,
                    wf.OPEN_EXISTING,  # 파일이 존재하지 않으면 예외 발생
                    0, None
                )
                break
            except KeyboardInterrupt:
                exit(1)
            except Exception as e:
                print(f'connection fail, trial {trials}')
                if max_trials > 0 and trials > max_trials:
                    raise ConnectionError("Fail to connect to pipe")
                trials += 1
                print(e)
                time.sleep(1)
                continue

    def transmit(self, dat):
        # 바이트데이터를 전송합니다.
        assert len(dat) == self.packet_size, f"data size must be {self.packet_size}, got {len(dat)}"
        if not self.hFile:
            raise ConnectionError("pipe not connected")
 
        wf.WriteFile(self.hFile, dat)
        wf.FlushFileBuffers(self.hFile)


if __name__ == '__main__':
    tx = KeypointTransmitter()
    tx.connect()
    tx.transmit()
