import json
import subprocess
import sys
import socket
from termcolor import colored
import threading
import time
import select

newMessages = []
allMessages = []

getLocalIp = str(subprocess.check_output(["ipconfig", "getifaddr", "en0"]))

localIp = getLocalIp.split("\\")[0].split("'")[1]

localNetwork = localIp.split(
    ".")[0] + "." + localIp.split(".")[1] + "." + localIp.split(".")[2] + ".1/24"

onlineUsers = {}
discoveredIds = []

HOST = localIp
PORT = 12345


def currentMillisecond():
    return round(time.time() * 1000)


def sendDiscoverResponse(receivedStr):
    global userName
    global discoveredIds
    onlineUsers[receivedStr['name']] = receivedStr['IP']
    discoveredIds.append(receivedStr['ID'])
    package = {}
    package['type'] = 2
    package['name'] = userName
    package['IP'] = localIp
    result = json.dumps(package)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(1)
                s.connect((receivedStr['IP'], PORT))
                s.sendall(result.encode('utf-8'))
                s.close()
            except:
                pass
    except:
        pass


def discoverBroadcasts():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', PORT))
    s.setblocking(0)
    while True:
        result = select.select([s], [], [])
        if not result:
            break
        msg = result[0][0].recv(10240)
        if not msg:
            break

        receivedJson = msg
        try:
            receivedStr = json.loads(receivedJson)
            if receivedStr['type'] == 1 and not receivedStr['IP'] == localIp and not receivedStr['ID'] in discoveredIds:
                userName = colored(receivedStr['name'], 'blue')
                sendDiscoverResponse(receivedStr)
                print(colored(f'User {userName} is online now.','cyan'))
        except:
            print(colored('There is a not valid broadcast message at the port: {PORT}','red'))


def discoverUsers():
    global userName
    id = str(currentMillisecond())
    for i in range(10):
        discoverMessage = '{ \"type\":1, \"name\":\"' + userName + '\", \"IP\":\"' + \
            localIp + '\" , \"ID\":' + id + ' }'
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(discoverMessage.encode('utf-8'), ('<broadcast>', PORT))


def receiver():
    global newMessages
    global allMessages
    while True:
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
                newMessages.append(receivedStr)
                allMessages.append(receivedStr)
                print(colored(
                    f"You have a new message from {colored(receivedStr['name'],'blue')}", 'green'))
            else:
                print(colored('One user sent a wrong message type','red'))
        except:
            print(colored("A user sent a package which is not Json format",'red'))


def sendMessage(user, message):
    global userName
    userIp = onlineUsers[user]
    package = {}
    package['type'] = 3
    package['name'] = userName
    messageBody = message[0]
    for word in message[1:]:
        messageBody += ' ' + word
    allMessages.append(user + '>>' + messageBody)
    package['body'] = messageBody
    result = json.dumps(package)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(0.3)
            s.connect((userIp, PORT))
            s.sendall(result.encode('utf-8'))
            s.close()
            print(colored('Message sent successfully','green'))
        except:
            print(colored('Message can not be sent. The user is not available','red'))
            onlineUsers.pop(user)


def showOnlineUsers():
    if onlineUsers:
        for key in onlineUsers:
            print(key)
        runChat()
    else:
        print(colored('There is not any available user.','red'))


def runChat():
    print(colored('Command(-h for help): ','cyan'))
    for line in sys.stdin:
        cmd = line[:-1].replace(' ', '.').split('.')[0]
        if cmd == 'send':
            if line[:-1].replace(' ', '.').split('.')[1] in onlineUsers:
                sendMessage(line[:-1].replace(' ', '.').split('.')
                            [1], line[:-1].replace(' ', '.').split('.')[2:])
            else:
                print(colored('There is no such user.','red'))
        elif cmd == 'users':
            showOnlineUsers()
        elif cmd == 'inbox':
            displayNewMessages()
        elif cmd == 'history':
            displayMessageHistory()
        elif cmd == '-h':
            print(colored(
                "users\t\t=> shows online users\ninbox\t\t=> shows unread messages\nhistory\t\t=> shows message history\nsend\t\t=> send messages as: send [user] [message]"
                , 'cyan'))
            print(colored('New command: ', 'cyan'))
        else:
            print(colored(f'{cmd} is not a valid command (write -h for help) : ','cyan'))


def displayNewMessages():
    global newMessages

    if newMessages:
        for message in newMessages:
            listToStr = ''.join([str(elem) for elem in message['body']])
            print(colored(message['name'], 'blue') + ': \n' + listToStr)
        newMessages.clear()
    else:
        print(colored('There is not any new message.','cyan'))


def displayMessageHistory():
    global allMessages

    if allMessages:
        for message in allMessages:
            if "type" in message:
                listToStr = ''.join([str(elem) for elem in message['body']])
                print(colored(message['name'], 'blue') + ': \n' + listToStr)
            else:
                me = colored('Me', 'yellow')
                user = colored(message.split('>>')[0], 'blue')
                print(
                    f"{me} to {user}" + ': \n' + message.split('>>')[1])
    else:
        print(colored('There is not any message history.', 'cyan'))


if __name__ == '__main__':
    print(colored('Zeroconf Chat','green','on_grey',attrs = ['bold']))
    userName = 'a b'
    while not len(userName.split(' ')) == 1 :
        userName = input(colored('Please enter your username: ', 'cyan'))
        if not len(userName.split(' ')) == 1 :
         print(colored('User name should be one one word!','red'))
    

    receiverThread = threading.Thread(target=receiver)
    receiverThread.start()
    broadcastReceiverThread = threading.Thread(target=discoverBroadcasts)
    broadcastReceiverThread.start()
    discoverUsers()
    while True:
        runChat()
