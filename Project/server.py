from bluetooth import *
from gyroOrAccl import GyroOrAccel
import time

uuid = "54c7001e-263c-4fb6-bfa7-2dfe5fba0f5b"

def flatten_list(arr):
    full_str = ""
    for string in arr:
        full_str += string
    return full_str

def analyse_string(data):
    accl = GyroOrAccel("Accelerometer", data)
    accl.plotSingluarPeaks(1.5, 25)

def run_server():
    epoch = time.time()
    curr_data = []
    curr_str = ""

    is_first = True

    server_sock=BluetoothSocket(RFCOMM)
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
    if time.time() - epoch > 30:
        return 0

    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)

    try:
        start_time = time.time()
        while True:
            data = client_sock.recv(1024)
            if len(data) == 0: break
            data = data.decode("utf-8") + "\n"
            if time.time() - start_time > 1:
                if len(curr_data) < 5:
                    curr_data.append(curr_str + data)
                    start_time = time.time()
                else:
                    curr_data = curr_data[1:]
                    curr_data.append(curr_str + data)
                    print("[" + flatten_list(curr_data) + "]\n")
                    analyse_string(flatten_list(curr_data))
                    start_time = time.time()
                curr_str = ""
            else:
                curr_str += data
    except IOError:
        return 1

    print("disconnected")

    client_sock.close()
    server_sock.close()
    print("run_server done")

    return 0


def run_server_instance_to_file(filename):
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
                f.write(data.decode("utf-8") + "\n")
    except IOError:
        pass

    print("disconnected")

    client_sock.close()
    server_sock.close()
    print("run_server_instance_to_file " + filename + " done")

if __name__ == "__main__":
    # run_server_instance_to_file("./data/real-fall.txt")
    while True:
        run_server()
        raw_in = input("Press enter to continue or type exit: ")
        if raw_in == "exit": break
