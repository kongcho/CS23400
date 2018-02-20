from bluetooth import *
from gyroOrAccl import GyroOrAccel
import time
import datetime

uuid = "54c7001e-263c-4fb6-bfa7-2dfe5fba0f5b"

def flatten_list(arrs):
    full_list = []
    for arr in arrs:
        full_list += arr
    return full_list

def analyse_string(data):
    accl = GyroOrAccel("Accelerometer", data)
    return accl.hasPeak()

def run_server(second=1):
    epoch = time.time()
    curr_data = []
    curr_strs = []

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
            data = data.decode("utf-8")
            if time.time() - start_time > second:
                if len(curr_data) < 5:
                    curr_strs.append(data)
                    curr_data.append(curr_strs)
                    start_time = time.time()
                else:
                    curr_strs.append(data)
                    curr_data = curr_data[1:]
                    curr_data.append(curr_strs)
                    send_data = flatten_list(curr_data)
                    timestamp = time.time()
                    value = datetime.datetime.fromtimestamp(timestamp)
                    is_single_peak = analyse_string(send_data)
                    print("%s\t%s\t%s" % (value.strftime('%Y-%m-%d %H:%M:%S.%f'), \
                                          len(send_data), is_single_peak))
                    client_sock.send(str(is_single_peak))
                    start_time = time.time()
                curr_strs = []
            else:
                curr_strs.append(data)
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
