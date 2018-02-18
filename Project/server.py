from bluetooth import *

uuid = "54c7001e-263c-4fb6-bfa7-2dfe5fba0f5b"

def runServer():
    server_sock=BluetoothSocket( RFCOMM )
    server_sock.bind(("",PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]
    port = PORT_ANY

    advertise_service(server_sock, "TPServer",
                      service_id = uuid,
                      service_classes = [ uuid, SERIAL_PORT_CLASS ],
                      profiles = [ SERIAL_PORT_PROFILE ]
    )

    print("Waiting for connection on RFCOMM channel %d" % port)

    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)

    try:
        while True:
            data = client_sock.recv(1024)
            if len(data) == 0: break
            print(data)
    except IOError:
        pass

    print("disconnected")

    client_sock.close()
    server_sock.close()
    print("runServer done")

def print_from_server(filename):
    server_sock=BluetoothSocket( RFCOMM )
    server_sock.bind(("",PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]
    port = PORT_ANY

    advertise_service(server_sock, "TPServer",
                      service_id = uuid,
                      service_classes = [ uuid, SERIAL_PORT_CLASS ],
                      profiles = [ SERIAL_PORT_PROFILE ]
    )

    print("Waiting for connection on RFCOMM channel %d" % port)

    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)

    try:
        with open(filename, 'a') as f:
            while True:
                data = client_sock.recv(1024)
                if len(data) == 0: break
                f.write(data + "\n")
    except IOError:
        pass

    print("disconnected")

    client_sock.close()
    server_sock.close()
    print("runServer done")

if __name__ == "__main__":
    # while True:
    #     runServer()
    print_from_server("./data/long3.txt")
