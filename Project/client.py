from bluetooth import *
import sys

if sys.version < '3':
    input = raw_input

addr = None

if len(sys.argv) < 2:
    print("no device specified.  Searching all nearby bluetooth devices for")
    print("the SampleServer service")
else:
    addr = sys.argv[1]
    print("Searching for SampleServer on %s" % addr)

addr = "7C:E9:D3:E7:5A:AE"

# search for the SampleServer service
uuid = "54c7001e-263c-4fb6-bfa7-2dfe5fba0f5b"
service_matches = find_service( uuid = uuid, address = addr )

if len(service_matches) == 0:
    print("couldn't find the SampleServer service =(")
    sys.exit(0)

first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

print("connecting to \"%s\" on %s" % (name, host))

# Create the client socket
sock=BluetoothSocket( RFCOMM )
sock.connect((host, port))

sock.listen(1)

print("connected.")
while True:
    data = "[CLIENT DATA]"
    if len(data) == 0: break
    sock.send(data)

    data_get = sock.recv(1024)
    data_get = data_get.decode("utf-8")
    print(data_get)

sock.close()
