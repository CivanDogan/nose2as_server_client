import socket
import os as o
from helper import *

def parseArg(arg):
    """" Parsing func for arguments. Returns a dictionary"""
    if len(arg) != 2:
        print("Wrong arguments.")
        sys.exit(1)

    temp = {"port":int(arg[1])}

    return temp


if __name__ == '__main__':
    arg = parseArg(sys.argv)

    #Sets the server socket.
    srv_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    srv_socket.bind(("0.0.0.0",arg["port"]))
    print(f"Server started on port : {arg['port']}")
    srv_socket.listen(5)


    while True:
        #Waiting requests.
        print("Waiting for request.")
        cli_sock, cli_addr = srv_socket.accept()
        cli_ip,cli_port=cli_addr[0],cli_addr[1]
        req = recvReq(cli_sock,os.listdir())
        #Display result of the request.
        if type(req) == type(" "):
            print(f"Invalid request from {cli_ip}(port:{cli_port}) : ")
            print(req)
            continue
        #Takes action according to request.
        if req["cmd"] == "put":
            print(f"Receiving {req['file']} from {cli_ip}(port:{cli_port})")
            recv_file(cli_sock,req["file"],req["size"])

        if req["cmd"] == "get":
            print(f"Sending {req['file']} to {cli_ip}(port:{cli_port})")
            file_size = os.path.getsize( f"{req['file']}")
            send_file(cli_sock,req["file"],file_size)

        if req["cmd"] == "list":
            print(f"Listing files for {cli_ip}(port:{cli_port})")
            sendList(cli_sock,os.listdir())



        print("---------")

    sys.exit()




