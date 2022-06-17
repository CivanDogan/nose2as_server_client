import os
import sys


#Common settings
PACKET_SIZE = 1024
SEP = chr(0x1C)
ENCODER = "utf-8"

#Error codes and their meanings.
RESPONSE = {"OK":"202","DENIED":"400",
            "SIZE":"300",
            "FILE_NOT_FOUND":"404",
            "METHOD_NOT_ALLOWED":"405",
            "FILE_EXISTS":"406"}

def send_file(socket,filename,size=-1):
    sent_data= 0
    # Progress tracker
    progress = 0
    last_progress = -1
    with open(filename,"rb") as f:
        print(f"Sending {filename}(size)")
        while(sent_data<size):
            try:
                #Reads and sends data
                packet = f.read(PACKET_SIZE)
                socket.sendall(packet)
            except OSError as e:
                #Incase of connection lost
                print("Connection lost...")
                return

            except Exception as e:
                print("Unknown error occured while sending the file")
                socket.close()
                return

            #Update progress
            sent_data += len(packet)
            progress = int((sent_data/size)*100)
            if last_progress != progress:
                print(f"Sending...{progress}/100")
                last_progress = progress

    print("Sent")

def recv_file(socket,filename,size):
    #Creating file.
    try:
        print(f"Creating file : {filename} size :{size}")
        f = open(filename,"xb")
    except FileExistsError:
        print("File already exist.")
        return
    except IOError:
        print("IO error occured.")
        return

    #Receiving loop
    print(f"Receiving {filename}(size)")
    written_data = 0
    progress = 0 #Progress tracker
    last_progress = -1
    while(written_data<size):
        if last_progress != progress:
            print(f"Receiving...{progress}/100")
            last_progress = progress
        try:
            #Recieve packet
            packet = socket.recv(PACKET_SIZE)
        except OSError as e:
            #Incase of connection drop
            print("Can't reach server...")
            ans = input("Do you want to keep the file ? (Y/N)")
            if ans == "Y":
                return
            elif ans == "N":
                f.close()
                try:
                    os.remove(filename)
                    print("File removed")
                except Exception as e:
                    print("File cannot be removed.")
                return
            else:
                print("Unknown answer file kept.")
            return
        #Write packet to file.
        f.write(packet)
        written_data += len(packet)
        #Update progress
        progress = int((written_data / size) * 100)



    print("Received")
    f.close()


def sendList(socket,list):
    l = str(list)
    #print("List : "+"\n".join(list))
    l = l.encode()
    socket.sendall(l)

def recieveList(socket):
    data = socket.recv(PACKET_SIZE*4)
    data = eval(data)

    if type(data) == type([]):
        return data
    else:
        print("Error occured while receiving list")
        sys.exit(0)





def sendReq(socket,cmd,filename="",size=0):
    print("Sending a request")
    req = SEP.join([cmd,filename,str(size)])
    #Sends request as a speacial seperated string
    socket.sendall(req.encode("utf-8"))
    #Listens for Response
    response = socket.recv(3).decode("utf-8")

    #Takes action according to response
    if response == RESPONSE["OK"]:
        print("Request accepted")
        return
    if response == RESPONSE["SIZE"]:
        print("Request accepted")
        print("Receiving size information...")
        size = int(socket.recv(PACKET_SIZE).decode(ENCODER))
        print(f"Size {size}")
        socket.sendall("OK".encode(ENCODER))
        return size
    if response == RESPONSE["DENIED"]:
        print("Request denied")
        socket.close()
        sys.exit(0)
    if response == RESPONSE["FILE_NOT_FOUND"]:
        print("File not found")
        socket.close()
        sys.exit(0)
    if response == RESPONSE["METHOD_NOT_ALLOWED"]:
        print("Method not allowed")
        socket.close()
        sys.exit(0)
    if response == RESPONSE["FILE_EXISTS"]:
        print("A File with the same name exists.")
        socket.close()
        sys.exit(0)

    #If response doesn't match returns Unknown Response.
    print("Unknown response")
    socket.close()
    sys.exit(0)

def recvReq(socket,filelist):
    #Listens socket for a request.
    response = socket.recv(1024).decode("utf-8")
    #print(response.split(SEP))

    #Splits received request.
    try:
        cmd,filename,size = response.split(SEP)
    except Exception:
    #If request has an unexpected style returns Request Denied message.
        print("Exception")
        socket.sendall(RESPONSE["DENIED"].encode(ENCODER))
        return "Request denied"

    # Takes action according to response
    # Sends back a confirmation or denial after checking requirements of the request.
    if not cmd in ["get","put","list"]:
        socket.sendall(RESPONSE["METHOD_NOT_ALLOWED"].encode(ENCODER))
        return "Method not allowed"

    if cmd == "put" and filename in filelist:
        socket.sendall(RESPONSE["FILE_EXISTS"].encode(ENCODER))
        return "A File with the same name exists."

    if cmd == "get" and filename not in filelist:
        socket.sendall(RESPONSE["FILE_NOT_FOUND"].encode(ENCODER))
        return "File not found"

    if cmd == "get" and filename in filelist:
        socket.sendall(RESPONSE["SIZE"].encode(ENCODER))
        file_size = os.path.getsize( f"{filename}")
        socket.sendall(str(file_size).encode(ENCODER))
        ans = socket.recv(PACKET_SIZE).decode(ENCODER)
        if ans == "OK":
            pass
        else:
            print("Error")
            return
        return {"cmd":cmd,"file":filename,"size":int(size)}

    if cmd == "put" and  filename not in filelist:
        socket.sendall(RESPONSE["OK"].encode(ENCODER))
        return {"cmd":cmd,"file":filename,"size":int(size)}

    if cmd == "list" and filename == "" and size == "0":
        socket.sendall(RESPONSE["OK"].encode(ENCODER))
        return {"cmd":cmd}

    print("unknown")
    socket.sendall(RESPONSE["DENIED"].encode())
    return None
