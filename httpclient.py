#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
import urllib.parse as urlparse


def help():
    print ("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    #def get_host_port(self,url):
    GET_REQUEST_TEMPLATE = "GET {path} HTTP/1.1\r\n" + \
        "Host:{host}:{port}\r\n" + "Content-Length:0\r\n" + "\r\n"
    POST_REQUEST_TEMPLATE = "POST {path} HTTP/1.1\r\n" + "Host:{host}:{port}\r\n" + \
        "Content-Length:{content_length}\r\n" + \
        "Content-Type:{content_type}\r\n" + "\r\n" + "{body}" + "\r\n"
    ENCODING = "utf-8"

    def connect(self, host, port):
        # use sockets
        self.sock = socket.socket()
        self.sock.connect((host, port))

    def get_code(self, data):
        return data.split("\r\n")[0].split(" ")[1]

    def get_headers(self, data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[-1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer, self.ENCODING)

    def GET(self, url, args=None):

        host = urlparse.urlparse(url).hostname
        port = urlparse.urlparse(url).port
        path = urlparse.urlparse(url).path

        if not port:
            port = 80

        if not path:
            path = "/"

        self.connect(host, port)

        self.sock.sendall(
            bytearray(self.generateGETRequest(path, host, port), self.ENCODING))
        data = self.recvall(self.sock)

        code = int(self.get_code(data))
        body = str(self.get_body(data))

        self.sock.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):

        host = urlparse.urlparse(url).hostname
        port = urlparse.urlparse(url).port
        path = urlparse.urlparse(url).path

        if not port:
            port = 80

        if not path:
            path = "/"

        self.connect(host, port)

        if args:
            body = urlparse.urlencode(args, encoding="utf-8")
            content_length = len(body)
            content_type = "application/x-www-form-urlencoded"

        else:
            body = ""
            content_length = 0
            content_type = "application/x-www-form-urlencoded"

        self.sock.sendall(bytearray(self.generatePOSTRequest(
            path, host, port, content_length, content_type, body), self.ENCODING))
     
     
        data = self.recvall(self.sock)

        code = int(self.get_code(data))
        body = str(self.get_body(data))

        self.sock.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

    def generateGETRequest(self, path, host, port):
        return self.GET_REQUEST_TEMPLATE.format(path=path, host=host, port=port)

    def generatePOSTRequest(self, path, host, port, content_length, content_type, body):
        return self.POST_REQUEST_TEMPLATE.format(path=path, host=host, port=port, content_length=content_length, content_type=content_type, body=body)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print( client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
