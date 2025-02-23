from ast import parse
from socket import *
import sys

import select


def get_host_and_path(request):
    try:
        first_line = request.split("\n")[0] #Get first line from request. this contains the URL
        parts = first_line.split(" ") #Split line into parts to get URL.
        url = parts[1]
        print("URL:", url)

        if url.startswith("/"):     #Get rid of the leading / that happens as a result of the request being localhost/page-to-visit.com
            url = url[1:]
        if "/" in url:
            host, path = url.split("/", 1)              #get any path that is included in the URL as well as the host
            path = "/" + path
        else:
            host = url
            path = "/"
        return host, path

    except Exception as e:
        print("Error:", e)          #Return nothing if an error occurs anywhere, this will be dealt with in subsequent code
        return None, None


def send_new_request(host, path):
    try:
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.connect((host, 80))

        request_line = f"GET {path} HTTP/1.0\r\nHost: {host}\r\n\r\n"
        server_socket.send(request_line.encode())

        response = b""
        while True:
            part_res = server_socket.recv(4096)             #keep requesting while there are objects that are part of the request
            if not part_res:
                break
            response += part_res                #append all objects for teh request that will be sent back to the browser

        server_socket.close()
        return response

    except Exception as e:
        print("Error making request:", e)
        return b"HTTP/1.0 500 Internal Server Error\r\n"

def handle_connection(client_socket):
    message = client_socket.recv(1024).decode()
    print(message)
    host, path = get_host_and_path(message)
    if not host:                                        #If get_host_and_path returns none, send back an error code
        client_socket.send(b"HTTP/1.0 400 Bad Request\r\n\r\n")
        client_socket.close()
    response = send_new_request(host, path)
    print(response)

    client_socket.send(response)
    client_socket.close()

if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
    sys.exit(2)

# The proxy server is listening at 8888
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind((sys.argv[1], 8888))
tcpSerSock.listen(100)
tcpSerSock.setblocking(False)

# Strat receiving data from the client
print('Ready to serve...')

connections = [tcpSerSock]
while True:
    readable, writable, exceptional = select.select(connections, [], []) #list of connections
    for sock in readable:
        if sock == tcpSerSock:
            client_socket, client_address = tcpSerSock.accept()
            print('Received a connection from:', client_address)
            connections.append(client_socket)                       #add connection to list
        else:
            handle_connection(sock)
            connections.remove(sock)

    ## FILL IN HERE...

    # filetouse = ## FILL IN HERE...

    # try:
    # 	# Check wether the file exist in the cache
    #
    # 	## FILL IN HERE...
    #
    # 	fileExist = "true"
    # 	# ProxyServer finds a cache hit and generates a response message
    # 	tcpCliSock.send("HTTP/1.0 200 OK\r\n")
    # 	tcpCliSock.send("Content-Type:text/html\r\n")


        ## FILL IN HERE...


    # Error handling for file not found in cache, need to talk to origin server and get the file
    # except IOError:
    # 	if fileExist == "false":
    #
    # 		## FILL IN HERE...
    # 		except:
    # 			print("Illegal request")
    # 	else:
    # 		# HTTP response message for file not found
    # 		tcpCliSock.send("HTTP/1.0 404 sendErrorErrorError\r\n")
    # 		tcpCliSock.send("Content-Type:text/html\r\n")
    # 		tcpCliSock.send("\r\n")
    #
    # # Close the client and the server sockets
    # tcpCliSock.close()
tcpSerSock.close()


