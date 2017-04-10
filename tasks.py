# -*- coding: utf-8 -*-

import paramiko
import re
import urllib2
import traceback
import base64

class Tasks:
    def __init__(self, ip, user, password,port_ssh, port_www):
        self.ip = ip
        self.user = user
        self.password = password
        self.port_ssh=port_ssh
        self.port_www=port_www

    def connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(self.ip, username=self.user, password=self.password, port=self.port_ssh)
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

class Tasks2(Tasks):
    def task01(self):
        stdin, stdout, stderr = self.exec_command('dpkg -s git | grep Status')
        out = stdout.read()

        if re.search(r'Status: install ok installed', out):
            return True, u'Git zainstalowany'
        else:
            return False, u'Git nie zainstalowany'  
        
    def task02(self):
        stdin, stdout, stderr = self.exec_command('ls ~/project2/')
        out = stdout.read()

        if len(out)>1:
            return True, u'Katalog project2 istnieje'
        else:
            return False, u'Katalog project2 nie istnieje'  
     
    def task03(self):
        stdin, stdout, stderr = self.exec_command('ls ~/repos/project2.git')
        out = stdout.read()

        if len(out)>1:
            return True, u'Katalog repos/project2.git istnieje'
        else:
            return False, u'Katalog repos/project2.git nie istnieje'
     
        
class Tasks3(Tasks):
    def task01(self):
        stdin, stdout, stderr = self.exec_command('dpkg -s apache2 | grep Status')
        out = stdout.read()
        if re.search(r'Status: install ok installed', out):
            return True, u'Apache zainstalowany'
        else:
            return False, u'Apache nie zainstalowany'

    def task02(self):
        out = self.exec_sudo_command('sudo service apache2 status | cat')
        if re.search(r'is not running', out):
            return False, u'Apache nie uruchomiony'
        if re.search(r'is running', out):
            return True, u'Apache uruchomiony'
        else:
            return False, u'Apache nie uruchomiony'

    def task03(self):
        print 'http://%s:%s' % (self.ip, self.port_www)
        response = urllib2.urlopen('http://%s:%s' % (self.ip, self.port_www))
        try:
            html = response.read()
        except urllib2.URLError:
            return False, u'Strona WWW jest niedostępna'
        return True, u'Strona WWW jest dostępna'

    def task04(self):
        response = urllib2.urlopen('http://%s:%s' % (self.ip, self.port_www))
        html = response.read()

        if re.search(r'Witaj na stronie EPI', html):
            return True, u'Komunikat "Witaj..."'
        else:
            return False, u'Brak komunikatu "Witaj.." na stronie'

    def task05(self):

        try:
            response = urllib2.urlopen('http://%s:%s/~%s'%(self.ip,self.port_www,self.user))
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
            response = urllib2.urlopen('http://%s:%s/~%s/projekt'%(self.ip,self.port_www,self.user))
            html = response.read()

        except urllib2.HTTPError as e:
            if re.search(r'401: Unauthorized', str(e)):
                return True, u'Projekt wymaga logowania'
            else:
                return False, u'Błąd dostępu do projektu'
        return False, u'Projekt nie wymaga logowania'

    def task10(self):
        request = urllib2.Request('http://%s:%s/~%s/projekt'%(self.ip,self.port_www,self.user))
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
            response = urllib2.urlopen('http://%s:%s/~%s/projekt/.git'%(self.ip,self.port_www,self.user))
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
            response = urllib2.urlopen('http://%s:%s/~%s/.git'%(self.ip,self.port_www,self.user))
            html = response.read()

        #TODO gdy public_html nie utworzony jest true
        except urllib2.HTTPError as e:
            if re.search(r'Forbidden', str(e)):
                return True, u'Repozytorium Git jest niedostępne'
            else:
                return False, u'Błąd dostępu do repozytorium Git'
        return False, u'Repozytorium git jest dostępne'

class Tasks4(Tasks):
    def task01(self):
        stdin, stdout, stderr = self.exec_command('ping -c 1 virtual')
        out = stdout.read()

        if re.search(r'1 received', out):
            return True, u'Alias virtual ustawiony'
        else:
            return False, u'Alias virtual nie ustawiony'

    def task02(self):
        stdin, stdout, stderr = self.exec_command('dpkg -s mysql-server | grep Status')
        out = stdout.read()

        if re.search(r'Status: install ok installed', out):
            return True, u'Serwer MySQL zainstalowany'
        else:
            return False, u'Serwer MySQL nie zainstalowany'

    def task03(self):
        out = self.exec_sudo_command('sudo service mysql status | cat')

        if re.search(r'waiting', out):
            return False, u'MySQL nie uruchomiony'
        if re.search(r'running', out):
            return True, u'MySQL uruchomiony'
        else:
            return False, u'MySQL nie uruchomiony'

    def task04(self):
        stdin, stdout, stderr = self.exec_command('mysql -u root --password=secret -e "show databases;"')
        out = stdout.read()

        if re.search(r'Database', out):
            return True, u'Zalogowano do bazy MySQL jako root'
        else:
            return False, u'Brak możliwości zalogowania się do bazy MySQL jako użytkownik root z hasłem secret'

    def task05(self):
        stdin, stdout, stderr = self.exec_command('mysql -u root --password=secret -e "show databases;"')
        out = stdout.read()

        if re.search(r'epi', out):
            return True, u'Utworzona baza "epi"'
        else:
            return False, u'Brak bazy "epi"'

    def task06(self):
        stdin, stdout, stderr = self.exec_command('mysql -u user1 --password=user1 -e "show databases;"')
        out = stdout.read()

        if re.search(r'Database', out):
            return True, u'Zalogowano do bazy MySQL jako user1'
        else:
            return False, u'Brak możliwości zalogowania się do bazy MySQL jako użytkownik user1 z hasłem user1'

    def task07(self):
        stdin, stdout, stderr = self.exec_command('mysql -u user1 --password=user1 -e "SHOW GRANTS FOR CURRENT_USER"')
        out = stdout.read()

        if re.search(r'ON .epi.\.\* TO \'user1', out):
            return True, u'Prawa przyznane do bazy epi'
        else:
            stdin, stdout, stderr = self.exec_command('mysql -u user1 --password=user1 -e "SHOW GRANTS FOR \'user1\'@\'%\'"')
            out = stdout.read()

            if re.search(r'ON .epi.\.\* TO \'user1', out):
                return True, u'Prawa przyznane do bazy epi'
            else:
                return False, u'Nieprzyznane prawa do bazy epi'

class Tasks5(Tasks):
    def task01(self):
        stdin, stdout, stderr = self.exec_command('dpkg -s libapache2-mod-php5 | grep Status')
        out = stdout.read()

        if re.search(r'Status: install ok installed', out):
            return True, u'Moduł Apache do obsługi PHP zainstalowany'
        else:
            return False, u'Moduł Apache do obsługi PHP nie zainstalowany'

    # def task02(self):
    #     stdin, stdout, stderr = self.exec_command('dpkg -s php5 | grep Status')
    #     out = stdout.read()
    #
    #     if re.search(r'Status: install ok installed', out):
    #         return True, u'PHP zainstalowane'
    #     else:
    #         return False, u'PHP nie zainstalowane'

    def task03(self):
        stdin, stdout, stderr = self.exec_command('dpkg -s php5-mysql | grep Status')
        out = stdout.read()

        if re.search(r'Status: install ok installed', out):
            return True, u'Moduł MySQL dla PHP zainstalowany'
        else:
            return False, u'Moduł MySQL dla PHP nie zainstalowany'

    def task04(self):

        try:
            response = urllib2.urlopen('http://%s:%s/~%s/test.php'%(self.ip,self.port_www,self.user))
            html = response.read()
        except urllib2.HTTPError as e:
            return False, u'Strona test.php jest niedostępna: %s'%e

        if re.search(r'PHP Version 5', html):
            return True, u'Strona test.php wykonała kod PHP'
        elif re.search(r'phpinfo\(\)', html):
            return False, u'Strona test.php nie wykonała kodu PHP'
        else:
            return False, u'Strona test.php nie wykonała phpinfo()'

    def task05(self):
        stdin, stdout, stderr = self.exec_command('mysql -u root --password=secret -e "show databases;"')
        out = stdout.read()

        if re.search(r'phpbb', out):
            return True, u'Utworzona baza "phpBB"'
        else:
            return False, u'Brak bazy "phpBB"'

    def task06(self):
        stdin, stdout, stderr = self.exec_command('mysql -u user1 --password=user1 -e "SHOW GRANTS FOR CURRENT_USER"')
        out = stdout.read()

        if re.search(r'ON .phpbb.\.\* TO \'user1', out):
            return True, u'Prawa przyznane do bazy phpbb'
        else:
            stdin, stdout, stderr = self.exec_command('mysql -u user1 --password=user1 -e "SHOW GRANTS FOR \'user1\'@\'%\'"')
            out = stdout.read()

            if re.search(r'ON .phpbb.\.\* TO \'user1', out):
                return True, u'Prawa przyznane do bazy phpbb'
            else:
                return False, u'Nieprzyznane prawa do bazy phpbb'

    def task07(self):
        link = 'http://%s:%s/~user/phpBB3/'% (self.ip,self.port_www)
        try:
            response = urllib2.urlopen(link)
            html = response.read()
        except urllib2.URLError as e:
            return False, u'Forum phpBB jest niedostępne pod adresem %s: %s' % (link,e)
        return True, u'Forum phpBB jest dostępne'

    def task08(self):
        response = urllib2.urlopen('http://%s:%s/~user/phpBB3/'% (self.ip,self.port_www))
        html = response.read()

        if re.search(r'Board index', html) or re.search(r'Wykaz for', html):
            return True, u'Forum zostało zainstalowane'
        else:
            return False, u'Forum nie zostało zainstalowane'
