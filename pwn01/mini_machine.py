from pwn import *
from checklib import *

context.log_level = 'CRITICAL'
#context.log_level = 'debug'

PORT = 50001
DEFAULT_RECV_SIZE = 4096
TCP_CONNECTION_TIMEOUT = 5
TCP_OPERATIONS_TIMEOUT = 7

class CheckMachine:

    def __init__(self, checker: BaseChecker):
        self.c = checker
        self.port = PORT

    def connection(self) -> remote:
        io = remote(self.c.host, self.port, timeout=TCP_CONNECTION_TIMEOUT)
        io.settimeout(TCP_OPERATIONS_TIMEOUT)
        return io

    def register(self, io: remote, username: str, password: str, description: str, status: Status) -> None:
        io.sendlineafter(b'> ', b'1')
        io.sendlineafter(b'Username: ', username.encode())
        io.sendlineafter(b'Password: ', password.encode())
        io.sendlineafter(b'Description: ', description.encode())
        resp = io.recvline()[:-1]
        self.c.assert_eq(resp, b'Success!', 'Invalid response on register', status)

    def login(self, io: remote, username: str, password: str, status: Status) -> None:
        io.sendlineafter(b'> ', b'2')
        io.sendlineafter(b': ', username.encode())
        io.sendlineafter(b': ', password.encode())
        resp = io.recvline()[:-1]
        self.c.assert_eq(resp, b'Login successful.', 'Invalid response on login', status)

    # 0. Exit 1
    def exit1(self, io: remote, status: Status) -> None:
        io.recvuntil(b"> ")
        io.sendline(b'0')
        resp = io.recvline()[:-1]
        self.c.assert_in(resp, b"Exiting program.", 'Invalid response on Exit', status)

    # 1. Calculate mathematical expression
    def calculate(self, io: remote, status: Status) -> None:
        #login first
        io.sendline(b'1')
        
        io.recvuntil(b"Enter a mathematical expression: ")
        io.sendline(b"10+1*(123+8/7)-1092.192")
        io.recvuntil(b"Result: ")
        resp = io.recvline()[:-1]
        self.c.assert_in(resp, b"-958.05", 'Invalid response on calculate', status)

    # 2. Check network connection (ping)
    def ping(self, io: remote, status: Status) -> None:
        #login first
        io.sendlineafter(b"choice: ", b'2')
        # ping fail
        io.recvuntil(b"Enter server to ping (e.g., google.com): ")
        io.sendline(b"id")
        resp = io.recvline()[:-1]
        self.c.assert_in(resp, b"-ping: id: Temporary failure in name resolution", 'Invalid response on Check network connection', status)
       
        io.sendlineafter(b"choice: ", b'2')
        # ping true
        io.recvuntil(b"Enter server to ping (e.g., google.com): ")
        io.sendline(b"github.com")
        resp = io.recvline()[:-1]
        self.c.assert_in(resp, b"PING github.com", 'Invalid response on Check network connection', status)
    
    # 3. Check disk usage
    def checkdir(self, io: remote, status: Status) -> None:
        #login first
        io.sendlineafter(b"choice: ", b'3')
        resp = io.recv()[:-1]
        self.c.assert_in(b"Use%", resp,  'Invalid response on Check disk usage', status)

    # 4. List files in directory
    def checkls(self, io: remote, status: Status) -> None:
        #login first
        io.sendlineafter(b"choice: ", b'4')
        io.recvuntil(b"Enter directory path: ")
        io.sendline(b"/")
        resp = io.recv(200)
        self.c.assert_in( b"bin", resp, 'Invalid response on Check network connection', status)

    # 5. Get current system time (don't need)

    # 6. Admin shell
    def adminsh(self, io: remote, status: Status) -> None:
        #login first
        io.sendlineafter(b"choice: ", b'6')
        resp = io.recvline()[:-1]
        self.c.assert_in(resp, b"Function is locked", 'Invalid response on Admin shell', status)

    # 7. User info
    def userinfo(self, io: remote, username: str, password: str, description: str, status: Status) -> None:
        io.sendlineafter(b'> ', b'7')
        io.recvuntil(b"Password: ")
        Password = io.recvline()[:-1]
        self.c.assert_eq(Password, password.encode() , 'Invalid response on User info', status)

        io.recvuntil(b"Description: ")
        resp = io.recvline()[:-1]
        self.c.assert_eq(resp, description.encode() , 'Invalid response on User info', status)
        return description.encode()
    
    # 8. Logout
    def logout(self, io: remote, status: Status) -> None:
        #login first
        io.sendline(b'8')
        io.recvuntil(b"Say good bye!~~~ ")
        io.sendline(b"byebyebyebyebye~~~")
        resp = io.recvline()[:-1]
        self.c.assert_in(resp, b"byebyebyebyebye~~~", 'Invalid response on Logout', status)

    # 0. Exit 2
    def exit2(self, io: remote, status: Status) -> None:
        #login first
        io.recvuntil(b"Enter your choice: ")
        io.sendline(b'0')
        resp = io.recvline()[:-1]
        self.c.assert_eq(resp, b"Exiting...", 'Invalid response on Exit2', status)
