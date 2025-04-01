import socket
import argparse
import time
import sys
import base64
import select
import random
import queue
import threading

########################################################################
#
# Address configuration for MulticastSenderReceiverConfig.py
#
########################################################################

# Multicast configuration
MULTICAST_ADDRESS = "239.0.0.10"
MULTICAST_PORT = 2000

IFACE_ADDRESS = "192.168.56.1"  #st to latest ipv4 addr based on where u at

CMD = {"getdir": 1, "makeroom": 2, "deleteroom": 3}

MSG_ENCODING = "utf-8"

# For UDP multicast receiving
RX_IFACE_ADDRESS = IFACE_ADDRESS
RX_BIND_ADDRESS = "0.0.0.0"

########################################################################
# SERVER
########################################################################

class Server:
    HOSTNAME = "0.0.0.0"  # Listen on all interfaces
    PORT = 50000

    BACKLOG = 10
    RECV_SIZE = 256

    def __init__(self):
        self.thread_list = []

        self.directory = {}  # Stores chat room entries as {room_name: ChatRoom}

        self.create_listen_socket()
        self.process_connections_forever()

    def create_listen_socket(self):
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Get socket layer socket options.
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind socket to socket address, i.e., IP address and port.
            self.socket.bind((Server.HOSTNAME, Server.PORT))

            # Set socket to listen state.
            self.socket.listen(Server.BACKLOG)
            print("chatroom server Listening on port {} ...".format(Server.PORT))

        except Exception as err:
            print("error for making hte server socket:", err)
            sys.exit(1)

    def process_connections_forever(self):
        try:
            while True:
                new_client = self.socket.accept()

                # A new client has connected. Create a new thread and
                # have it process the client using the connection
                # handler function.
                new_thread = threading.Thread(target=self.connection_handler, 
                                              args=(new_client,))
                
                # Record the new thread.
                self.thread_list.append(new_thread)

                # Start the new thread running.
                print("Starting serving thread:", new_thread.name)
                new_thread.daemon = True
                new_thread.start()

        except Exception as err:
            print("Error:", err)
        except KeyboardInterrupt:
            print("keyboard interrupt so must be closing server socket.....")
        finally:
            print("keyboard interrupt so must be closing server socket.....")
            self.socket.close()
            sys.exit(1)

    def connection_handler(self, client):
        connection, address_port = client
        print("-" * 72)
        print("Connection received from {}.".format(address_port))

        while True:
            # Receive bytes over the TCP connection. This will block
            # until "at least 1 byte or more" is available.
            recvd_bytes = connection.recv(Server.RECV_SIZE)

            # If recv returns with zero bytes, the other end of the
            # TCP connection has closed (The other end is probably in
            # FIN WAIT 2 and we are in CLOSE WAIT.). If so, close the
            # server end of the connection and get the next client
            # connection.
            if len(recvd_bytes) == 0:
                print("Closing connection from {} ...".format(address_port))
                connection.close()
                # Break will exit the connection_handler and cause the
                # thread to finish.
                break

            # Decode the received bytes back into strings.
            recvd = recvd_bytes.decode(MSG_ENCODING).split()

            if not recvd or recvd[0] not in ["1", "2", "3"]:
                break
            cmd = int(recvd[0])
            if cmd == CMD["getdir"]:#getdir command to get the directory of rooms
                print("recieved getdir command..")
                pack = ""
                for welc in self.getting_directory():#getdirectiory
                    pack += f"{welc[0]} {welc[1]} {welc[2]}\n"#dir to send to client
                if pack == "":
                    pack = "no rooms currently avail...."#telling that there are no rooms available
                pack = pack.encode(MSG_ENCODING)
            elif cmd == CMD["makeroom"]:#new room make command
                print("received makerom cmd...")
                self.making_room(recvd[1], recvd[2], recvd[3])#making the room with the making_room function
                pack = "room created".encode(MSG_ENCODING)
            elif cmd == CMD["deleteroom"]:#delete room command
                pack = self.no_room(recvd[1]).encode(MSG_ENCODING)
            try:
                connection.sendall(pack)#command to send the data to the client
            except socket.error:
                print("Closing client conn ...")
                connection.close()
                return
            print("we received:", recvd_bytes.decode(MSG_ENCODING))#tells us what we received from the client

    def getting_directory(self):
        return [room.get_ip_port_name() for room in self.directory.values()]

    def making_room(self, name, address, port):
        self.directory[name] = ChatRoom(name, address, port)

    def no_room(self, name):#
        if name not in self.directory:
            return "the requested room dne..."
        else:
            self.directory.pop(name)
            return "room has been deleted successfully..."

class ChatRoom:
    def __init__(self, name, ip, port):
        self.name =name

        self.ip=ip
        self.port=int(port)

    def get_ip_port_name(self):
        return (self.name, self.ip, self.port)

########################################################################
# CLIENT
########################################################################

class Client:
    SERVER_HOSTNAME = "localhost"
    RECV_SIZE = 256
    RECV_BUFFER_SIZE = 1024
    

    def __init__(self):
        self.roomdir = {}#this is the room directory we are going to use to store the rooms
        self.TCP_conn = False#settinh the tcp connection to false as default

        self.name="Username"

        self.process_in_forever()#to cont checking for input forever

    def process_in_forever(self):
        while True:
            try:
                self.recv_input()#this is client waits for user input

            except Exception as err:
                print("Error:",err)#print error msg
                continue

            except KeyboardInterrupt:
                sys.exit(0)#exiting thre progrm

    def recv_input(self):
        in_vals = input("Enter your input cmd: ")#user inp for what they wanna di
        in_str = in_vals.split()#for splitting input into a list of strings

        if not in_str:#if the input is empty, we just return for new line
            return
        
        cmd = in_str[0]#frst string in the list is the command

        if cmd == "connect":#checking if the user wants to connect to the server
            self.TCP_recv()#this is the function that creates the tcp socket
            self.TCP_server()#this is the function that connects to the server

        elif cmd =="name":
            if len(in_str) > 1:#if user has the name then we change the name
                self.name = in_str[1]#changing the name to the new name
                print("your username has been changed to:",self.name)#printing the new name

            else:
                print("Please input as such: name <your_name>")##asking the user to input their name

        elif cmd=="chat":
            if len(in_str)> 1:#checkign if room name exists alreadt
                self.chat_handler(in_str[1])

            else:
                print("Please inpuit as such: chat <room_name>")#incorrect command input handle

        elif cmd == "makeroom":#command to make a new room
            if not self.TCP_conn:#check if already in server or not to see if can connect 
                print("you're not connected." )
                return
            
            if len(in_str) < 4:#checking if the user has given all the required inputs
                print("Please input as suhc: makeroom <room_name> <multicast_ip> <port>")##incorrect command input handle
                return
            
            self.TCP_rx_tx("2 " + in_str[1] + " " + in_str[2] + " " + in_str[3])##sending the command to the server to create a new room

        elif cmd =="getdir":#command to get the directory of rooms
            if not self.TCP_conn:#need to be connected to the server to get the directory of rooms and req to run this so don't try to enter non existant rom
                print("you're not connected.")
                return
            
            dir_inf = self.TCP_rx_tx("1")##sending the command to the server to get the directory of rooms
            self.getdir_handler(dir_inf)

        elif cmd =="deleteroom":#if we want to delete a room

            if not self.TCP_conn:#must be in the room and server cannto delete from outside
                print("you're not connected.")
                return
            
            if len(in_str)<2:#checking if the user has given all the required inputs
                print("Please input as such: deleteroom <room_name>")
                return
            
            self.TCP_rx_tx("3 "+ in_str[1])#ssending the command to the server to delete a room

        elif cmd=="bye":#if we want disconnect so we don't do any other commands 
            if not self.TCP_conn:
                print("you're not connected...")
                return
            
            self.TCPsocket.close()
            self.TCP_conn =False 

        else:
            print("the command you have entered is not possible. sorry...")#not good command 

    def chat_handler(self, room_num):#function handles the chat room creation and joining
        if room_num not in self.roomdir:
            print("Please rerun getdir to see if the room exists...")#checking if the room exists or not
            return
        
        addr_prt=self.roomdir[room_num]#address and port of the room we are going to joi
        self.chat_addr =addr_prt
        self.udp_socket_recv(addr_prt)#create the udp socket for theroom

        print("You've entered chat for room#:",room_num)
        print("Pls type in ther terminal '/exit' so you can leave the chat.")

        message_mixer=self.name +" joined your chat."#telling that you (name) have joined the chat
        self.udp_socket.sendto(message_mixer.encode(MSG_ENCODING), self.chat_addr)##sending the message to the room so that the other people in the room can see it
        event_thrd =threading.Event()#event thread to see if in chat or exited
        event_thrd.set()
        rx_thrd=threading.Thread(target=self.recv_udp, args=(event_thrd,))#thread to receive the messages from the room
        rx_thrd.daemon= True
        rx_thrd.start()

        try:
            while True:
                msg_tx=input(self.name + ": ")

                if msg_tx.strip()=="/exit":
                    print("you are now exiting the chat")#tell the user that htey are exiting when they do /exit
                    event_thrd.clear()
                    rx_thrd.join()
                    break

                mixed_msg=self.name + ": " +msg_tx
                self.udp_socket.sendto(mixed_msg.encode(MSG_ENCODING),self.chat_addr)

        except KeyboardInterrupt:
            print("chat exiting through keyboard cmd")#ctrl +C
            event_thrd.clear()#clear the thread and then hoin so it exits again
            rx_thrd.join()

    def udp_socket_recv(self, addr_prt):

        try:
            self.udp_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)# Create a UDP socket.
            self.udp_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            self.udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
            bind_address = (RX_BIND_ADDRESS, addr_prt[1])#Bind to the multicast port on all interfaces.

            # Bind to an address/port. In multicast, this is viewed as
            # a "filter" that determines what packets make it to the
            # UDP app.
            self.udp_socket.bind(bind_address)

            ############################################################
            # The multicast_request must contain a bytes object
            # consisting of 8 bytes. The first 4 bytes are the
            # multicast group address. The second 4 bytes are the
            # interface address to be used. An all zeros I/F address
            # means all network interfaces.
            ############################################################
            
            multicast_group_bytes = socket.inet_aton(addr_prt[0])#multicast to bytes
            multicast_if_bytes = socket.inet_aton(RX_IFACE_ADDRESS)
            multicast_request = multicast_group_bytes + multicast_if_bytes

            # You can use struct.pack to create the request, but it is more complicated, e.g.,
            # 'struct.pack("<4sl", multicast_group_bytes,
            # int.from_bytes(multicast_if_bytes, byteorder='little'))'
            # or 'struct.pack("<4sl", multicast_group_bytes, socket.INADDR_ANY)'

            self.udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_request)
            self.udp_socket.settimeout( 0.5)#timeout

        except Exception as err:
            print("there was an error making the udp socket, sorry", err)

    def recv_udp(self, event_thrd):#function to recevive messages from udp server
        while event_thrd.is_set():
            try:
                # Receive bytes over the TCP connection. This will block
                # until "at least 1 byte or more" is available.
                recvd_bytes,address=self.udp_socket.recvfrom(Client.RECV_SIZE)

                # Decode the received bytes back into strings. Then output
                # them.
                recvd_str=recvd_bytes.decode(MSG_ENCODING)
                print("\n" +recvd_str)#this is the message we are going to print out

            except socket.timeout:
                continue

            except Exception as err:
                print("error in recving with udp server:", err)
                return

    def getdir_handler(self, dir_inf):#handle the directory of rooms
        if dir_inf.strip()=="sorry but you need to make a room fistr.":
            print(dir_inf)
            return
        
        self.roomdir.clear()
        results =dir_inf.splitlines()#list of rooms we are getting from the server

        for result in results:
            sec=result.split()#splitting the string into a list of strings

            if len(sec) == 3:
                self.roomdir[sec[0]] =(sec[1], int(sec[2]))##adding the room to the directory of rooms

        print("here is the latest dir for rooms avail.",self.roomdir)

    def TCP_recv(self):
        try:
            self.TCPsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)#creating the tcp socket

        except Exception as err:
            print("there was an error in making the tcp socket, sorry pls restart", err)#counlt make the sockert
            sys.exit(1)

    def TCP_server(self):
        try:
            self.TCPsocket.connect((Client.SERVER_HOSTNAME, Server.PORT))#connecting to the server
            print("you are connected to {} on proit num {}".format(Client.SERVER_HOSTNAME, Server.PORT))
            self.TCP_conn=True

        except Exception as err:
            print("error in  connecting to the req server:",err)
            sys.exit(1)

    def TCP_rx_tx(self, message):

        self.TCPsocket.sendall(message.encode(MSG_ENCODING))#sending msg to server

        try:
            recvd_bytes = self.TCPsocket.recv(Client.RECV_BUFFER_SIZE)#receiving the msg from the server

            if len(recvd_bytes)==0:
                print("server closed your connections.")
                self.TCPsocket.close()
                return ""
            
            recvd_str= recvd_bytes.decode(MSG_ENCODING)#decoding msg from server
            print("received frm server:", recvd_str)
            return recvd_str
        
        except Exception as err:
            print("sorry there was an error with the tcp server pls restart:", err)
            sys.exit(1)

########################################################################
# Process command line arguments if this module is run directly.
########################################################################

# When the python interpreter runs this module directly (rather than
# importing it into another file) it sets the __name__ variable to a
# value of "__main__". If this file is imported from another module,
# then __name__ will be set to that module's name.

if __name__ == '__main__':
    roles = {'client': Client,'server': Server}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='server or client role',
                        required=True, type=str)

    args = parser.parse_args()
    roles[args.role]()

########################################################################