import requests
import re
import os
from checklib import *

PORT = 8080

class CheckMachine:
    @property
    def url(self):
        return f'http://{self.c.host}:{self.port}'

    def __init__(self, checker):
        self.c = checker
        self.port = PORT

    def get_session(self):
        url = f'{self.url}/employees/index'
        s = requests.Session()
        s.get(url,timeout=5)
        return s

    def destroy_session(self, s):
        url = f'{self.url}'
        s.get(f'{url}/logout')

    def register(self, s, u, n, e, p, status=Status.MUMBLE):
        url = f'{self.url}/register'

        data = {
            "username": u,
            "name": n,
            "email": e,
            "password": p
        }

        response = s.post(url, data=data, timeout=5)
        self.c.assert_nin("Username already exists", response.text, "Can't register", status=status)

    def login(self, s, u, p, status=Status.MUMBLE):
        url = f'{self.url}/login'

        r = s.post(url, data={
            'username': u,
            'password': p
        },timeout=5,allow_redirects=False)
        
        if r.status_code == 200 and r.headers['Location'] != '/employees/index':
            self.cquit(Status.MUMBLE)

    def searchByName(self, s, name, status=Status.MUMBLE):
        url = f'{self.url}/employees/searchByName?searchName=' + name + "''"
        r = s.get(url)
        self.c.assert_in('Sorry!! Search not found.', r.text, "Function searchByName has problem", status=status)

    def get_flag(self, s, status=Status.MUMBLE):
        url = f'{self.url}/employees/feedback'

        r = s.get(url)
        d = r.text
        match = re.search(r'<div class="name-display">\s*<span>(.*?)</span>', d)
        if match:
            flag = match.group(1)
            return flag
        self.cquit(Status.MUMBLE)
    def write_flag(self,s,name,status=Status.MUMBLE):
        url = f'{self.url}/api/writeflag/'+name
        r = s.get(url)
        

        
    def upload(self, s, filename, content, status=Status.MUMBLE):
        url = f'{self.url}/upload'
        file_content = content.encode('utf-8')
        files = {"file": (f"{filename}", file_content, "image/jpeg"),}
        r = s.post(url, files=files)
        d = r.text
        self.c.assert_in('File uploaded successfully!', r.text, "Can't Upload", status=status)
