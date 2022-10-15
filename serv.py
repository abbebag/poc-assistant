import socket

HOST = "0.0.0.0"
PORT = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print("Connected by", addr)

receiving = True

while True:
    if receiving:
        data = conn.recv(1024)
        data = data.decode()
        # split on newline
        lines = data.split("\n")
        for line in lines:
            if line == "command":
                receiving = False
            else:
                print(line)
    else:
        command = input("Enter command: ")
        conn.send(command.encode())
        receiving = True
