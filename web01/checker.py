#!/usr/bin/env python3
import sys
import os
import hashlib
import requests
import random

from checklib import *
from time import sleep

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web01_lib import *


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
        m1 = rnd_username() + '@ahihi.com'
        self.mch.register(s1, m1, u1, n1, p1)
        self.mch.login(s1, u1, p1)
        uid1 = self.mch.get_uid(s1)
        
        self.mch.get_profile(s1, uid1, u1, "Chill Guy")

        intro1 = rnd_string(10)
        intro2 = rnd_string(10)
        self.mch.update(s1, intro1)
        self.mch.update_old(s1, intro2)

        names = ["abc", "testtest", "upload", "php", "html", "php7", "phar", "htaccess", "ini"]
        extensions = ["png", "PNG", "JPEG", "JPG", "jpg"]
        name = random.choice(names)
        extension = random.choice(extensions)
        filename = f"{name}.{extension}"
        content = rnd_string(50)
        self.mch.upload_img(s1,filename,content)
        
        name = rnd_string(10)
        self.mch.preview(s1,name)
        self.mch.flag_admin(s1)
        sleep(3)
        self.mch.destroy_session(s1)
        self.cquit(Status.OK)
    
    def put(self, flag_id: str, flag: str, vuln: str):
        s1 = self.mch.get_session()
        u1, p1, n1 = rnd_username(), rnd_password(), rnd_username()
        m1 = rnd_username() + '@ahihi.com'
        self.mch.register(s1, m1, u1, n1, p1)
        self.mch.login(s1, u1, p1)
        uid1 = self.mch.get_uid(s1)
        if random.choice([True, False]):
            self.mch.update(s1, flag)
        else:
            self.mch.update_old(s1, flag)
        self.mch.writefile(s1)
        self.mch.destroy_session(s1)

        self.cquit(Status.OK,f'{uid1}',f'{u1}:{p1}:{m1}')

    def get(self, flag_id: str, flag: str, vuln: str):
        s = self.mch.get_session()
        username, password, mail = flag_id.split(':')
        self.mch.login(s, username, password, Status.CORRUPT)
        intro = self.mch.get_flag(s, Status.CORRUPT)
        self.assert_eq(intro, flag, "Flag invalid", Status.CORRUPT)
        
        self.cquit(Status.OK)



if __name__ == '__main__':
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
