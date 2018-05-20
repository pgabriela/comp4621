from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import gzip
import math


host = '127.0.0.1'
port = 80

server = socket(AF_INET, SOCK_STREAM)
server.bind((host, port))
server.listen()


def handleClient(conn, addr):

    # httpReqLen = 0
    httpReq = conn.recv(4096)
    # while(len(httpReq) - httpReqLen > 0):
    #     httpReqLen = len(httpReq)
    #     httpReq += conn.recv(4096)

    httpReq = httpReq.decode().split('\r\n')
    end_of_header = 0
    for idx, i in enumerate(httpReq):
        if(i == ''):
            end_of_header = idx
            break

    HTTPheaders = [x.split(' ') for idx, x in enumerate(httpReq) if idx <
                   end_of_header]

    try:
        reqLine = HTTPheaders[0]
        method = reqLine[0]
        URL = reqLine[1]
        # version = reqLine[2]
    except IndexError:
        return

    if(method == 'GET'):
        try:
            requestedFile = open('.'+URL, 'rb')
            respMsg = b''
            L = requestedFile.read(4096)
            while(L):
                respMsg += L
                L = requestedFile.read(4096)
            requestedFile.close()

            fileType = URL.split(".")[-1]
            contentType = ""
            if(fileType == "html"):
                contentType = "text/html"
            elif(fileType == "css"):
                contentType = "text/css"
            elif(fileType == "jpg"):
                contentType = "image/jpg"
            elif(fileType == "pdf"):
                contentType = "application/pdf"
            elif(fileType == "pptx"):
                contentType = "application/vnd.openxmlformats-" + \
                    "officedocument.presentationml.presentation"
            elif(fileType == "ppt"):
                contentType = "application/vnd.ms-powerpoint"
            elif(fileType == "ico"):
                contentType = "image/x-icon"

            respMsg = gzip.compress(respMsg)
            # send HTTP response
            rM = b'HTTP/1.1 200 OK\r\n' + \
                 b'Content-Type: ' + contentType.encode('ascii') + b'\r\n' + \
                 b'Content-Encoding: gzip\r\n' + \
                 b'Transfer-Encoding: chunked\r\n' + \
                 b'Connection: Keep-Alive\r\n' + \
                 b'Keep-Alive: timeout=5, max=100\r\n' + \
                 b'\r\n'
            chunks = []
            for i in range(10):
                chunks.append(respMsg[i*math.ceil(len(respMsg)/10):
                                      (i+1)*math.ceil(len(respMsg)/10)])
            chunks = [x for x in chunks if x != '']
            for i in chunks:
                rM += str(hex(len(i))).encode('ascii')[2:] + b'\r\n'
                rM += i + b'\r\n'
            rM += b'0\r\n\r\n'
            conn.send(rM)

        except FileNotFoundError:
            """ Send Error MSG here (404 NOT FOUND)"""
            errFile = open('./err404.html', 'rb')
            respMsg = b''
            L = errFile.read(4096)
            while(L):
                respMsg += L
                L = errFile.read(4096)
            errFile.close()

            conn.send(b'HTTP/1.1 404 Not Found\r\n' +
                      b'Connection: Closed\r\n' +
                      b'Content-Type: text/html\r\n' +
                      b'Content-Length: ' + str(len(respMsg)).encode('ascii') +
                      b'\r\n\r\n' + respMsg)

    conn.close()


while(True):
    conn, addr = server.accept()
    conn.settimeout(60)
    Thread(target=handleClient, args=(conn, addr)).start()
