from bluetooth import *
from gyroOrAccl1 import GyroOrAccel
import time
import datetime
import os

uuid = "54c7001e-263c-4fb6-bfa7-2dfe5fba0f5b"

def make_sound():
    duration = 0.1  # second
    freq = 440  # Hz
    os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq))
    return 0

def flatten_list(arrs):
    full_list = []
    for arr in arrs:
        full_list += arr
    return full_list

def analyse_string(data):
    abso = GyroOrAccel("Absolute", data, "fake")
    res = abso.is_fall([False, True], 0.05, 0.01, 25, 25, 41, 12, 0.8)
    print(res)
    # abso.plotFinalAlgoPeaks([False, True], 0.05, 0.01, 25, 25, 41, 12, 0.8)
    if len(res) != 0:
        return True
    else:
        return False

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

    is_fall = False
    prev = False
    curr = False

    # try:
    with open("./fall_detection_data_0.txt", "w") as f:
        start_time = time.time()
        while True:
            data = client_sock.recv(1024)
            if len(data) == 0: break
            data = data.decode("utf-8")
            f.write(data + "\n")
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
                    curr = analyse_string(send_data)
                    if prev and curr:
                        is_fall = True
                        make_sound()
                    #f.write(data + "\n")#'\n'.join(send_data))
                    print("%s\t%s\t%s\tis_fall: %s" % (value.strftime('%Y-%m-%d %H:%M:%S.%f'), \
                                                       len(send_data), curr, is_fall))
                    client_sock.send(str(is_fall))
                    start_time = time.time()
                    is_fall = False
                    prev = curr
                curr_strs = []
            else:
                curr_strs.append(data)
    # except IOError:
    #     return 1

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
