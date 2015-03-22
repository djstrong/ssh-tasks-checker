# -*- coding: utf-8 -*-

import paramiko
import re


class Tasks:
    def __init__(self, ip, user, password):
        self.ip = ip
        self.user = user
        self.password = password

    def connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(self.ip, username=self.user, password=self.password)
            return True, u'Zalogowano przez SSH'
        except Exception as e:
            return False, u'Brak możliwości zalogowania przez SSH: %s' % e

    def perform_tasks(self):
        tasks = [self.connect]
        tasks += [getattr(self, method) for method in dir(self) if
                  callable(getattr(self, method)) and re.match(r'task', method)]
        tasks_results = []
        for task in tasks:
            try:
                result, description = task()
                #print result, description
            except Exception as e:
                result = False
                description = e
            tasks_results.append((result, description))
        return tasks_results


class Tasks3(Tasks):
    def task1(self):
        stdin, stdout, stderr = self.ssh.exec_command('dpkg -s apache | grep Status')
        out = stdout.read()

        if re.search(r'Status: install ok installed', out):
            return True, u'Apache zainstalowany'
        else:
            return False, u'Apache nie zainstalowany'

# tdin, stdout, stderr = ssh.exec_command(
#     "sudo dmesg")
# stdin.write('lol\n')
# stdin.flush()
# data = stdout.read.splitlines()

#task = Tasks3('192.168.2.32', 'kwrobel', 'password')
#print task.perform_tasks()
