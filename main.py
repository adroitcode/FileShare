from Tkinter import *
from socket import *
import shutil
import os
import thread


import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

splitter = '<splitter>'
host = False
connections = []


#takes in list if msg parts
def send(msg_parts):
    global splitter
    #formatted_msg = ''
    formatted_msg = splitter.join(msg_parts)
    #for x in xrange(0,len(msg_parts)):
    #    formatted_msg += msg_parts[x]
    #    if x != len(msg_parts) - 1:
    #        formatted_msg += splitter.encode('UTF-8')
    formatted_msg += '</msgend>'.encode('UTF-8')

    #print "Sending msg: " + formatted_msg
    if host:
        for connection in connections:
            connection.sendall(formatted_msg)
    else:
        global sock
        global splitter
        sock.sendall(formatted_msg)



def host_click():
    global host_port
    def host():
        port_num = int(host_port.get())
        server_address = ('', port_num)
        print >>sys.stderr, 'starting up on %s port %s' % server_address
        global sock
        sock.bind(server_address)
        sock.listen(1)
        global host
        host = True

        show("Hosting at localhost:" + str(port_num) + " \nWaiting for connection...")
        toggle_ui()



        while True:
            print >>sys.stderr, 'waiting for a connection'
            connection, client_address = sock.accept()
            global connections
            connections.append(connection)
            try:
                print >>sys.stderr, 'client connected:', client_address
                show("client connected: " + str(client_address))
                msg = ''
                while 1:
                    try:
                        connection.settimeout(5)
                        #12582912
                        #131072
                        buf = connection.recv(12582912)
                        #print >>sys.stderr, 'received "%s"' % buf
                        #print "Recieving data"
                        #print buf[0:10]
                        #print msg
                        msg += buf
                        #print msg

                        #print msg
                        if '</msgend>' in msg:
                            msg = msg.replace('</msgend>','')
                            print "MESSAGE IS COMPLETE"
                            #print msg

                            process_msg(msg)
                            msg = ''

                    except socket.timeout:
                        #print traceback.print_exc()
                        print "recv timeout, repeat"
                        pass
                    except:
                        sock.close()
                        connections = []
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        print "Socket disconnected"

                        toggle_ui()

                        return


            finally:
                connection.close()


    thread.start_new_thread(host, ())



def connect_click():
    #disable buttons
    #button.config(state='normal')
    #else:
    #    button.config(state='disabled')
    global connect_button, connect_ip, connect_port

    server_address = (connect_ip.get(), int(connect_port.get()))

    def connect():

        global sock
        # Create a TCP/IP socket
        try:
            sock.connect(server_address)
            show("Connected to server!")
            toggle_ui()
            global host
            host = False
        except:
            print traceback.print_exc()
            show("Error connecting to server " + str(server_address))

        try:

            msg = ''
            while 1:
                print "LOL"
                try:
                    sock.settimeout(5)
                    #12582912
                    #131072
                    buf = sock.recv(12582912)
                    #print >>sys.stderr, 'received "%s"' % buf
                    #print "Recieving data"
                    #print buf[0:10]
                    #print msg
                    msg += buf

                    #print msg

                    #print msg
                    if '</msgend>' in msg:
                        msg = msg.replace('</msgend>','')
                        print "MESSAGE IS COMPLETE"
                        #print msg

                        process_msg(msg)
                        msg = ''
                    #echo back to client
                    #connection.sendall(("l" * 5000) + "\r\n")
                    #time.sleep(3)
                except socket.timeout:
                    #print traceback.print_exc()
                    print "recv timeout, repeat"
                    pass
                except:
                    sock.close()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    toggle_ui()
                    return
        finally:
            sock.close()

    thread.start_new_thread(connect, ())


def toggle_ui():
    if send_file_button['state'] == 'disabled':
        host_button.config(state='disabled')
        connect_button.config(state='disabled')
        entry_field.config(state='normal')
        send_file_button.config(state='normal')
    else:
        host_button.config(state='normal')
        connect_button.config(state='normal')
        entry_field.config(state='disabled')
        send_file_button.config(state='disabled')


def show(msg):
    global messaging_field
    messaging_field.insert(END, msg + "\n")


import base64,zlib
def process_msg(msg):
    try:
        print "PROCESS MSG"
        #splitter = '<commandblock>'

        parts = msg.split(splitter)
        data_type = parts[0]
        print "DATATYPE: " + data_type

        if data_type == 'file':
            print "Processing zip"
            file_name = parts[1]
            show("Downloading " + file_name + '...')
            print "Decompressing file data"
            try:
                file_data = base64.b64decode(zlib.decompress(parts[2]))
                print "Len of decompressed file data is " + str(len(file_data))

                current_path =  os.path.dirname(os.path.abspath(__file__))
                writefile = open(current_path + "/files/" + file_name, 'wb')
                print "Writing zip file"
                for data in file_data:
                    writefile.write(data)

                show(file_name + ' is finished downloading to your /files/ folder.')
                send(['msg','User is finished downloading ' + file_name])
            except:
                print traceback.print_exc()
        elif data_type == 'msg':
            print "MSG: "
            msg = parts[1]
            show("other: " + msg)
        elif data_type == 'error':
            msg = parts[1]
            print "Error msg: " + msg
            show("error: " + msg)
        print "Message has been completely processed"
    except:
        print traceback.print_exec()



def send_file():
    global splitter
    file_path = choose_file()

    def async_send():
        try:
            sendfile = open(file_path, 'rb')
            file_name = sendfile.name.split('/')[-1]

            send(['msg','Sending file ' + file_name + ' data...'])
            data = sendfile.read()
            data = base64.b64encode(data)
            data = zlib.compress(data,9)

            #send("file" + splitter + sendfile.name.split('/')[-1] + ":::" + data)

            send(['file'.encode('UTF-8'),file_name.encode('UTF-8'),data])
            show('You sent file ' + file_name)
        except:
            print traceback.print_exc()
            send(['error',"Error sending file " + file_path])


    thread.start_new_thread(async_send, ())


#http://synack.me/blog/using-python-tcp-sockets
import traceback

#http://code.activestate.com/recipes/408859/



def callback(event):
    global root
    message = entry_field.get()
    messaging_field.insert(END, "you: " + message + "\n")
    entry_field.delete(0, END)
    send(['msg',message])

root = Tk()
root.title("FileShare")
root.geometry("500x300")

messaging_field = Text(root, wrap = WORD)
messaging_field.pack()
messaging_field.place(x=101,y=0,height=300,width=400)
#
#
entry_field = Entry(root)
#self.entry_field.grid(row = 1, column = 1, columnspan = 2,sticky = W)
entry_field.pack()
entry_field.place(x=101,y=280,height=20,width=400)
entry_field.bind('<Return>', callback)
entry_field.config(state='disabled')
#
#        #startBtn = Button(root, text = "Start",command = buttonDown)
#        #startBtn.pack()
#        #startBtn.place(x=50,y=50,height=50,width=100)
#        #buttons.append(startBtn)

#HOST
host_port = Entry(root)
host_port.pack()
host_port.place(x=0,y=0,height=20,width=100)
host_port.insert(0, "10000")



host_button = Button(root,text="host",command=host_click)
host_button.pack()
host_button.place(x=0,y=21,height=40,width=100)


#CLIENT
connect_ip = Entry(root)
connect_ip.pack()
connect_ip.place(x=0,y=62,height=20,width=100)
connect_ip.insert(0, "ip")

connect_port = Entry(root)
connect_port.pack()
connect_port.place(x=0,y=83,height=20,width=100)
connect_port.insert(0, "10000")

connect_button = Button(root,text="connect",command=connect_click)
connect_button.pack()
connect_button.place(x=0,y=104,height=40,width=100)

send_file_button = Button(root,text="send file",command=send_file)
send_file_button.pack()
send_file_button.place(x=0,y=260,height=40,width=100)
send_file_button.config(state='disabled')

from tkFileDialog import askopenfilename
def choose_file():
    # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file

    print(filename)
    return filename


def main():
    current_path =  os.path.dirname(os.path.abspath(__file__))
    print
    if os.path.isdir(current_path + '/files/') is False:
        os.makedirs(current_path + '/files/')

    root.mainloop()


main()