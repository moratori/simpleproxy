#!/usr/bin/env python
#coding:utf-8

import socket
import sys
import time
import threading

def initServer(myport):
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind(("",myport))
    server.listen(5)
    return server

def readRR(sock,wait):
    sock.setblocking(0)
    whole = ""
    time.sleep(wait)
    try:
        while True: 
            data = sock.recv(8192)
            if data == "": break
            else: whole += data
    except socket.error:pass
    sock.setblocking(1)
    return whole

def parseRaw(rawreq):
    meta = {}
    data = ""
    n = -1
    tmp = rawreq.split("\r\n")
    for i,v in enumerate(tmp):
        if v == "": 
            n = i
            break
    meti = tmp[1:n]
    for kv in meti:
        index = kv.index(":")
        k,v = kv[0:index],kv[index+1:]
        meta[k.strip()] = v.strip()
    data = "\r\n".join(tmp[n+1:])
    return tmp[0],meta,data

def rewriteHeader(rawreq,rule):
    result = ""
    status,meta,data = parseRaw(rawreq)

    for k in rule.keys():
        meta[k] = rule[k]

    for k,v in meta.items():
        result += "%s: %s\r\n" %(k,v)

    result = status + "\r\n" + result + "\r\n" + data
    return result

def initQuery(host,port):
    addr = socket.gethostbyname(host)
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((addr,port))
    return s




def controller(client,info):

    rawreq = readRR(client,0.1)
    req    = rewriteHeader(rawreq,rewriterule)

    s = initQuery(upper_proxy,upper_proxy_port)
    s.sendall(req)
    response = readRR(s,0.7)
    s.close()

    client.sendall(response)
    client.close()

    return



def main(myport,rewriterule,upper_proxy,upper_proxy_port):
    server = initServer(myport)
    try:
        while True:
            client , info = server.accept()

            th_controller = threading.Thread(target=controller,args=(client,info))
            th_controller.start()

    except KeyboardInterrupt:
        server.close()
    return


if __name__ == "__main__":
    rewriterule = {"Host": "hogehoge.jp"}
    myport = 12345
    upper_proxy = "proxy.exmaple.jp"
    upper_proxy_port = 8080
    main(myport,rewriterule,upper_proxy,upper_proxy_port)

