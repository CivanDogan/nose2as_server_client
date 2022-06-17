import os
import socket
import sys
from helper import *


def parseArg(arg):
    """" Parsing func for arguments. Returns a dictionary"""
    if len(arg) > 5:
        print("Too many arguments.")
        sys.exit(1)
    if len(arg) < 4:
        print("Not enough arguments.")
        sys.exit(1)

    temp = {"ip":arg[1],"port":int(arg[2]),"cmd":arg[3]}
    if len(arg) == 5:
        if(len(arg[4])) > 190:
            print("Very long file name. Please shorten it.")
            sys.exit(1)


        temp["file"] = arg[4]
        return temp
    else:
        return temp


if __name__ == '__main__':
    arg = parseArg(sys.argv)
    if arg["cmd"] == "get" and os.path.isfile(arg["file"]):
        print("File with same name exists")
        sys.exit(0)
    if arg["cmd"] == "put" and (False == os.path.isfile(arg["file"])):
        print("File not exists")
        sys.exit(0)

    cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Trying to connect to {arg['ip']}")
    try:
        cli_sock.connect((arg['ip'], arg['port']))
    except OSError:
        print("Server not found.")
        sys.exit(0)
    if arg["cmd"] == "put":
        print(f"Sending {arg['file']} to {arg['ip']} (port: {arg['port']})")
        file_size = os.path.getsize(os.path.dirname(__file__) + f"\\{arg['file']}")
        sendReq(cli_sock, arg["cmd"], arg["file"], file_size)
        send_file(cli_sock, arg["file"], size = file_size)
    if arg["cmd"] == "get":
        print(f"Getting {arg['file']} from {arg['ip']} (port: {arg['port']})")
        size = sendReq(cli_sock,arg["cmd"],arg["file"])
        recv_file(cli_sock,arg["file"],size)
    if arg["cmd"] == "list":
        print(f"Listing files from {arg['ip']} (port: {arg['port']})2")
        sendReq(cli_sock,arg["cmd"])
        print("Available files:")
        print("\n".join(recieveList(cli_sock)))

    try:
        cli_sock.close()
    except Exception:
        pass
