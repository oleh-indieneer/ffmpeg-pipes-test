import asyncio
import win32pipe, win32file

class PipeServer:
    __name: str
    __pipe: int
    
    @property
    def name(self):
        return self.__name
    
    @property
    def path(self):
        return '\\\\.\\pipe\\' + self.__name

    def __init__(self, name: str):
        self.__name = name
        self.__pipe = win32pipe.CreateNamedPipe(
            self.path,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_READMODE_BYTE | win32pipe.PIPE_WAIT,
            1, 65536, 65536,
            0,
            None
        )
        print(f'[pipe][{name}] created')

    def write(self, bytes: bytes):
        return win32file.WriteFile(self.__pipe, bytes)
    
    async def write_async(self, bytes: bytes):
        return win32file.WriteFile(self.__pipe, bytes)

    def wait(self):
        print(f'[pipe][{self.__name}] waiting for connections...')
        win32pipe.ConnectNamedPipe(self.__pipe, None)
        print(f'[pipe][{self.__name}] client connected!')

    async def wait_async(self):
        self.wait()

    def close(self):
        win32file.CloseHandle(self.__pipe)
        print(f'[pipe][{self.__name}] closed')