import json
import subprocess
import sys
import re
import socket

getLocalIp = str(subprocess.check_output(["ipconfig", "getifaddr", "en0"]))

localIp = getLocalIp.split("\\")[0].split("'")[1]

localNetwork = localIp.split(
    ".")[0] + "." + localIp.split(".")[1] + "." + localIp.split(".")[2] + ".1/24"

discoverMessage = '{ \"type\":1, \"name\":\"Ozan\", \"IP\":\"' + localIp + '\" }'

onlineUsers = {}

HOST = localIp
PORT = 12345

def discoverUsers():
    out = subprocess.check_output(["nmap", "-sn", localNetwork])
    allHosts = re.findall(localIp.split(".")[
                          0] + "." + localIp.split(".")[1] + "." + localIp.split(".")[2]+".\d+", str(out))
    for host in allHosts:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.settimeout(0.03)
                    s.connect((host, PORT))
                    s.sendall(discoverMessage.encode('utf-8'))
                    s.close()

                except:
                    pass
        except:
            pass
    receiver()

        
def receiver():
    print("You are now available for other users")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        input = True
        while input:
            conn, addr = s.accept()

            data = conn.recv(10240)
            if not data:
                break
            input = False
            message_packet = str(data.decode('utf-8'))
            conn.close()
        s.close()
    
        receivedJson = message_packet
    try:
        receivedStr = json.loads(receivedJson)
        if receivedStr['type'] == 1:
            sendDiscoverResponse(receivedStr)
        elif receivedStr['type'] == 2:
            onlineUsers[receivedStr['name']] = receivedStr['IP']
        elif receivedStr['type'] == 3:
            inputList = []
            if(type(receivedStr['body']) == str):
                inputList.append(receivedStr['body'])
            else:
                inputList = receivedStr['body']
            displayMessage(inputList,receivedStr['name'])
            
        else:
            print('Wrong message type')
    except:
        print("Not a valid input. Send a Json format input")

    runChat()


def sendDiscoverResponse(receivedStr):
    onlineUsers[receivedStr['name']] = receivedStr['IP']
    package = {}
    package['type'] = 2
    package['name'] = "Ozan"
    package['IP'] = localIp
    result = json.dumps(package)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(0.004)
                s.connect((receivedStr['IP'], PORT))
                s.sendall(result.encode('utf-8'))
                s.close()
            except:
                pass
    except:
        pass

    
def sendMessage(user, message):
    userIp = onlineUsers[user]
    package = {}
    package['type'] = 3
    package['name'] = "Ozan"
    package['body'] = message
    result = json.dumps(package)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(0.3)
            s.connect((userIp, PORT))
            s.sendall(result.encode('utf-8'))
            s.close()
        except:
            pass

def showOnlineUsers():
    for key in onlineUsers:
        print(key)
    runChat()

def runChat():
    print('Command(-h for help): ')
    for line in sys.stdin:
        cmd = line[:-1].replace(' ','.').split('.')[0]
        if cmd == 'send':
            sendMessage(line[:-1].replace(' ','.').split('.')[1], line[:-1].replace(' ','.').split('.')[2:])
            print('Message is sent. New command: ')
        elif cmd == 'available':
            receiver()
        elif cmd == 'users':
            showOnlineUsers()
        elif cmd == '-h':
            print("users\t\t=> shows online users\navailable\t=> makes you available to get messages\nsend\t\t=> send messages as: send [user] [message]")
            print('New command: ')
        else:
            print(cmd + " is not a valid command (write -h for help) : ")


def displayMessage(receivedMessage, userName):
    listToStr = ' '.join([str(elem) for elem in receivedMessage])
    print(userName + ': \n' + listToStr)


if __name__ == '__main__':
    discoverUsers()
    while True:
        runChat()

