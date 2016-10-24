#!/usr/bin/env python
#coding:utf-8

import socket
import sys
import time
import threading
import logging


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

def rewriteStatus(status):
    method,res,ty = status.split(" ")
    res_result = "/"
    try:
        tmp1 = res[res.index("//")+2:]
        res_result = tmp1[tmp1.index("/"):]
    except ValueError:pass
    return "%s %s %s" %(method,res_result,ty)

def rewriteHeader(rawreq,rule):
    result = ""
    status,meta,data = parseRaw(rawreq)
    status = rewriteStatus(status)

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

def controller(client,info,addr,port):

    rawreq = readRR(client,0.1)
    try:
        req    = rewriteHeader(rawreq,rewriterule)
    except:
        client.close()
        return

    s = initQuery(addr,port)
    s.sendall(req)
    response = readRR(s,0.7)
    s.close()

    client.sendall(response)
    client.close()

    return

def main(myport,rewriterule,addr,port):
    server = initServer(myport)
    try:
        while True:
            client , info = server.accept()
            th_controller = threading.Thread(target=controller,args=(client,info,addr,port))
            th_controller.start()
    except KeyboardInterrupt:
        server.close()
    return


if __name__ == "__main__":
    rewriterule = {"User-Agent": "Chrome"}
    myport = 12345

    addr = "www.sie.dendai.ac.jp"
    port = 80

    main(myport,rewriterule,addr,port)

