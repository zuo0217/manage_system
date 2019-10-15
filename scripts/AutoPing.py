#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# author: saseny_zhou
# Create On 20191015

import requests
import time
import os

try:
    import urlparse
except:
    from urllib import parse as urlparse
finally:
    pass


class AutoPing():
    """
        用于程序员客栈自动ping
    """

    host = "https://www.proginn.com"
    loginUrl = "/api/passport/login"
    pingUrl = "/api/remote/ping"
    header = {
        "User-Agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
    }

    def __init__(self, username, password, DEBUG=False, filePath="/tmp/auto_ping.log"):
        self.username = username
        self.password = password
        self.filePath = filePath
        self.debug = DEBUG

        self.status = False
        self.s = requests.session()

    def logDebug(self, message):
        if self.debug: print("{} --> {}".format(time.strftime("%Y-%m-%d %H:%M:%S"), message))

    def login(self):
        try:
            response = self.s.post(url=urlparse.urljoin(self.host, self.loginUrl),
                                   data={"login_name": self.username, "password": self.password},
                                   headers=self.header)
            if response.status_code == 200:
                self.status = True
            else:
                self.logDebug("{} - {}".format(response.status_code, response.text))
        except Exception as e:
            self.logDebug("Login Error: " + str(e))
        finally:
            pass

    def ping(self):
        if self.status:
            try:
                response = self.s.post(url=urlparse.urljoin(self.host, self.pingUrl),
                                       headers=self.header)
                if response.status_code == 200:
                    self.logDebug(response.json())
                    self.writeFile(response.json())
                else:
                    self.logDebug("{} - {}".format(response.status_code, response.text))
            except Exception as e:
                self.logDebug("Ping Error: " + str(e))
            finally:
                pass

    def readFile(self):
        try:
            current = time.strftime("%Y-%m-%d")
            f = open(self.filePath, "r")
            f_obj = f.read()
            f.close()
            if current in f_obj:
                return True
        except Exception as e:
            self.logDebug("Read File Error: " + str(e))
        finally:
            pass
        return False

    def writeFile(self, message):
        try:
            current = time.strftime("%Y-%m-%d")
            f = open(self.filePath, "a")
            f.write(str(current) + "\t" + str(message) + "\n")
            f.close()
        except Exception as e:
            self.logDebug("Read File Error: " + str(e))
        finally:
            pass

    def checkFile(self):
        if not os.path.isfile(self.filePath):
            f = open(self.filePath, "w")
            f.close()

    def run(self):
        self.checkFile()
        if not self.readFile():
            self.login()
            self.ping()


if __name__ == "__main__":
    AutoPing(username="******", password="*****", DEBUG=True).run()
