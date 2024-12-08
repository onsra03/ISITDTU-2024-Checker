#!/usr/bin/env python3
import sys
import os
import hashlib
import requests
import random

from checklib import *
from time import sleep

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web02_lib import *


class Checker(BaseChecker):
    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.mch = CheckMachine(self)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            self.cquit(Status.DOWN, 'Connection error', 'Got requests connection error')

    def check(self):
        sleep(5)
        s1 = self.mch.get_session()
        u1, p1, n1 = rnd_username(), rnd_password(), rnd_username()
        m1 = rnd_username() + '@ahihi.lol'
        self.mch.register(s1, u1, n1, m1, p1)
        self.mch.login(s1, u1, p1)

        namesearch = rnd_string(10)
        self.mch.searchByName(s1, namesearch)

        names = ["abc", "testtest", "upload", "jsp", "JSP", "jspx", "xhtml", "java"]
        extensions = ["png", "PNG", "JPEG", "JPG", "jpg", "txt", "md", "javaa"]
        name = random.choice(names)
        extension = random.choice(extensions)
        filename = f"{name}.{extension}"
        content = rnd_string(100)
        self.mch.upload(s1,filename,content)
        
        sleep(3)
        self.mch.destroy_session(s1)
        self.cquit(Status.OK)
    
    def put(self, flag_id: str, flag: str, vuln: str):
        s1 = self.mch.get_session()
        u1, p1, n1 = rnd_username(), rnd_password(), flag
        m1 = rnd_username() + '@ahihi.lol'
        self.mch.register(s1, u1, n1, m1, p1)
        self.mch.login(s1, u1, p1)
        self.mch.destroy_session(s1)
        self.mch.write_flag(s1,u1)
        self.cquit(Status.OK,f'{u1}:{m1}',f'{u1}:{p1}:{m1}')

    def get(self, flag_id: str, flag: str, vuln: str):
        s = self.mch.get_session()
        username, password, mail = flag_id.split(':')
        self.mch.login(s, username, password, Status.CORRUPT)
        flag_check = self.mch.get_flag(s, Status.CORRUPT)
        self.assert_eq(flag_check, flag, "Flag invalid", Status.CORRUPT)
        
        self.cquit(Status.OK)



if __name__ == '__main__':
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
