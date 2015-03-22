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

    def exec_command(self, command):
        return self.ssh.exec_command(command)

    def exec_sudo_command(self, command):
        chan=self.ssh.get_transport().open_session()
        chan.get_pty()
        f = chan.makefile()
        chan.exec_command(command)
        chan.send('%s\n' % self.password)
        return f.read()

class Tasks3(Tasks):
    def task1(self):
        stdin, stdout, stderr = self.exec_command('dpkg -s apache2 | grep Status')
        out = stdout.read()

        if re.search(r'Status: install ok installed', out):
            return True, u'Apache zainstalowany'
        else:
            return False, u'Apache nie zainstalowany'

    def task2(self):
        out = self.exec_sudo_command('sudo service apache2 status')
        #print out
        if re.search(r'Status: install ok installed', out):
            return True, u'Apache zainstalowany'
        else:
            return False, u'Apache nie zainstalowany'



# task = Tasks3('192.168.2.3', 'kwrobel', 'password')
# print task.perform_tasks()
