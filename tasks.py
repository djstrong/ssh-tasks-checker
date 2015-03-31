# -*- coding: utf-8 -*-

import paramiko
import re
import urllib2
import traceback
import base64

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
                traceback.print_exc()
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
    def task01(self):
        stdin, stdout, stderr = self.exec_command('dpkg -s apache2 | grep Status')
        out = stdout.read()

        if re.search(r'Status: install ok installed', out):
            return True, u'Apache zainstalowany'
        else:
            return False, u'Apache nie zainstalowany'

    def task02(self):
        out = self.exec_sudo_command('sudo service apache2 status')

        if re.search(r'is not running', out):
            return False, u'Apache nie uruchomiony'
        if re.search(r'is running', out):
            return True, u'Apache uruchomiony'
        else:
            return False, u'Apache nie uruchomiony'

    def task03(self):
        response = urllib2.urlopen('http://%s'%self.ip)
        try:
            html = response.read()
        except urllib2.URLError:
            return False, u'Strona WWW jest niedostępna'
        return True, u'Strona WWW jest dostępna'

    def task04(self):
        response = urllib2.urlopen('http://%s'%self.ip)
        html = response.read()

        if re.search(r'Witaj na stronie EPI', html):
            return True, u'Komunikat "Witaj..."'
        else:
            return False, u'Brak komunikatu "Witaj.." na stronie'

    def task05(self):

        try:
            response = urllib2.urlopen('http://%s/~%s'%(self.ip,self.user))
            html = response.read()
        except urllib2.HTTPError as e:
            if re.search(r'401: Unauthorized', str(e)):
                return True, u'Strona domowa użytkownika jest dostępna'
            else:
                return False, u'Strona domowa użytkownika jest niedostępna: %s'%e
 
        except urllib2.URLError as e:
            return False, u'Strona domowa użytkownika jest niedostępna: %s'%e
        return True, u'Strona domowa użytkownika jest dostępna'

    def task06(self):
        stdin, stdout, stderr = self.exec_command('a2query -m userdir')
        out = stdout.read()

        if re.search(r'enabled', out):
            return True, u'Moduł userdir włączony'
        else:
            return False, u'Moduł userdir wyłączony'



    def task08(self):
        stdin, stdout, stderr = self.exec_command('find public_html/ -name ".git"')
        out = stdout.read()

        if re.search(r'\.git', out):
            return True, u'Repozytorium Git w public_html'
        else:
            return False, u'Brak repozytorium w public_html'


    def task09(self):
        try:
            response = urllib2.urlopen('http://%s/~%s/projekt'%(self.ip,self.user))
            html = response.read()

        except urllib2.HTTPError as e:
            if re.search(r'401: Unauthorized', str(e)):
                return True, u'Projekt wymaga logowania'
            else:
                return False, u'Błąd dostępu do projektu'
        return False, u'Projekt nie wymaga logowania'

    def task10(self):
        request = urllib2.Request('http://%s/~%s/projekt'%(self.ip,self.user))
        base64string = base64.encodestring('%s:%s' % ('student', 'password')).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        response = urllib2.urlopen(request)

        try:
            html = response.read()
            #print html
        except urllib2.URLError:
            return False, u'Projekt jest niedostępny przy podaniu danych logowania'
        return True, u'Projekt jest dostępny przy podaniu danych logowania'


    def task11(self):
        for function in [self.helper11a, self.helper11b]:
            v,d = function()
            if v:
                return v,d
        return v,d

    def helper11a(self):
        try:
            response = urllib2.urlopen('http://%s/~%s/projekt/.git'%(self.ip,self.user))
            html = response.read()

        #TODO gdy public_html nie utworzony jest true
        except urllib2.HTTPError as e:
            if re.search(r'Forbidden', str(e)):
                return True, u'Repozytorium Git jest niedostępne'
            else:
                return False, u'Błąd dostępu do repozytorium Git'
        return False, u'Repozytorium git jest dostępne'

    def helper11b(self):
        try:
            response = urllib2.urlopen('http://%s/~%s/.git'%(self.ip,self.user))
            html = response.read()

        #TODO gdy public_html nie utworzony jest true
        except urllib2.HTTPError as e:
            if re.search(r'Forbidden', str(e)):
                return True, u'Repozytorium Git jest niedostępne'
            else:
                return False, u'Błąd dostępu do repozytorium Git'
        return False, u'Repozytorium git jest dostępne'
