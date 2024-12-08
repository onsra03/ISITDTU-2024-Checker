import requests
import re
import os
from checklib import *

PORT = 1337

class CheckMachine:
    @property
    def url(self):
        return f'http://{self.c.host}:{self.port}'

    def __init__(self, checker):
        self.c = checker
        self.port = PORT

    def get_session(self):
        url = f'{self.url}'
        s = requests.Session()
        s.get(url,timeout=5)
        return s

    def destroy_session(self, s):
        url = f'{self.url}'
        s.get(f'{url}/index.php?page=logout')

    def register(self, s, m, u, n, p, status=Status.MUMBLE):
        url = f'{self.url}/index.php?page=register'

        data = {
            "email": m,
            "username": u,
            "name": n,
            "password": p
        }

        response = s.post(url, data=data, timeout=5)
        self.c.assert_in("Register success", response.text, "Can't register", status=status)

    def login(self, s, u, p, status=Status.MUMBLE):
        url = f'{self.url}/index.php?page=login'

        r = s.post(url, data={
            'username': u,
            'password': p
        },timeout=5)
        
        d = r.text
        # self.c.assert_eq(type(d), type(""), "Can't login", status=status)
        self.c.assert_in("{\"success\":true}", d, "Can't login", status=status)


    def get_flag(self, s, status=Status.MUMBLE):
        url = f'{self.url}/index.php?page=user'

        r = s.get(url)
        d = r.text
        match = re.search(r'<input[^>]*id="intro"[^>]*value="([^"]+)"', d)
        if match:
            intro_value = match.group(1)
            return intro_value
        else:
            self.cquit(Status.MUMBLE)

    def update_old(self, s, d, status=Status.MUMBLE):
        url = f'{self.url}/index.php?page=user'

        data = {"xml":f"<user><intro>{d}</intro></user>"}
        r = s.post(url,data=data)
        
        self.c.assert_in(f'Update success', r.text, "Can't update via XML", status=status)
    
    def update(self, s, d, status=Status.MUMBLE):
        url = f'{self.url}/index.php?page=user'

        json = [{"name": "intro", "value": f"{d}"}]
        r = s.post(url,json=json)
        
        self.c.assert_in(f'Update success', r.text, "Can't update via JSON", status=status)

    def get_uid(self, s, status=Status.MUMBLE):
        url = f'{self.url}/index.php?page=user'
        r = s.get(url)
        d = r.text
        match = re.search(r'<input[^>]*id="uid"[^>]*value="(\d+)"', d)
        if match:
            uid = match.group(1)
            return uid

    def get_profile(self, s, uid, u, intro, status=Status.MUMBLE):
        url = f'{self.url}/index.php?page=user'
        r = s.get(url)
        self.c.assert_in(f'<input id="intro" type="text" class="form-control" name="intro" value="{intro}"', r.text, 
                     "Can't get intro profile", status=status)
    
    def upload_img(self, s, filename, content, status=Status.MUMBLE):
        url = f'{self.url}/index.php?page=user'
        file_content = content.encode('utf-8')
        files = {"avatar": (f"{filename}", file_content, "image/jpeg"),}
        r = s.post(url, files=files)
        d = r.text
        self.c.assert_in('Avatar uploaded successfully', r.text, "Can't upload avatar", status=status)
    
    def writefile(self, s, status=Status.MUMBLE):
        url = f'{self.url}/index.php?page=writefile'
        r = s.get(url)
        if r.status_code == 200:
            content = r.text
            words = content.split()
            word_count = len(words)
        self.c.assert_eq(184,word_count,"Edited source write flag", status=status)
    def preview(self, s, name, status=Status.MUMBLE):
        url = f'{self.url}/index.php?page=user'

        data = {"name":f"{name}","preview":"123"}
        r = s.post(url,data=data)
        
        self.c.assert_in('Forbidden. Only admin can preview.', r.text, "Can't preview name", status=status)
    
    def flag_admin(self, s, status=Status.MUMBLE):
        url = f'{self.url}/index.php?page=admin'
        r = s.get(url)
        self.c.assert_in('Hi', r.text, "Function admin has problem", status=status)