import socket                   # Import socket module
import time
import os
import logging
import _thread
import zipfile

port = 6969                     # Reserve a port for the server.
file_transfer_port = 9696       # Reserve a port for file upload/download
s = socket.socket()             # Create a socket object
host = socket.gethostname()     # Get local machine name
s.bind((host, port))            # Bind to the port
s.listen(5)                     # Now wait for client connection.
FTs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
FTs.bind((socket.gethostname(), file_transfer_port))
FTs.listen(1)
save_file_dir = "./save/"

print('Server listening....')

def check_time_stamp():
    # Firstly check if the target folder exists
    if os.path.exists(save_file_dir):
        if len(os.listdir(save_file_dir) ) == 0:
            result = 0.0
        else:    
            filenames = (os.listdir(save_file_dir) )
            name_list = [i.replace('.zip','') for i in filenames]
            final_list = [float(i.replace('.zip','')) for i in filenames]
            max_name = max(final_list)
            max_index = final_list.index(max_name)
            result = name_list[max_index]
        return result
    else:
        raise ValueError('The save folder does not exist')

def server_data_handler(FTs, client_request):
    response = "test"
    if 'time_stamp' in client_request:
        time_stamp = check_time_stamp()
        client_stamp = float(client_request.replace('time_stamp',''))
        print("server: ", time_stamp, "\nclient: ", client_stamp)
        if client_stamp > float(time_stamp):
            response = "upload"
            '''
            try:
                _thread.start_new_thread(file_receiving, (FTs, file_transfer_port,client_stamp,))
            except Exception as e:
                logging.error(e)
            '''
            _thread.start_new_thread(file_receiving, (FTs, file_transfer_port,client_stamp,))
        else:
            response = str(time_stamp)
            '''
            try:
                print('serving time stamp ',str(time_stamp))
                _thread.start_new_thread(file_serving, (FTs, file_transfer_port,str(time_stamp),))
            except Exception as e:
                logging.error(e)
            '''
            _thread.start_new_thread(file_serving, (FTs, file_transfer_port,str(time_stamp),))
    else:
        pass
    
    return response

def security_check(magic_word):
    # work on this later
    return None
    return output

    

def file_receiving(FTs, file_transfer_port,client_time_stamp):
    print("start to receive file")
    # One thing you may want to notice is that the server will store all the history data in zip format
    # For now, you may prefer to clear the past data manually. However, I believe it is good to keep those files
    # Some day you may want to play them so you can just go and download. Who knows?
    file_name = save_file_dir + str(client_time_stamp) + '.zip'
    while True:
        conn,addr = FTs.accept()
        with open(file_name,'wb') as fw:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                fw.write(data)
            fw.close()
        conn.close()
        break
    print('File received')
    
def file_serving(FTs, file_transfer_port,time_stamp):
    print("start to serve file")
    file_name = save_file_dir + str(time_stamp) + '.zip'
    while True:
        conn,addr = FTs.accept()
        print("serving file")
        with open(file_name,'rb') as fr:
            while True:
                data = fr.read(1024)
                #print(data)
                if not data:
                    break
                conn.send(data)
                #print('sent')
            fr.close()
        break
    print('File served')
    conn.close()
# Start the listener loop
while True:
    try:
        conn, addr = s.accept()     # Establish connection with client.
        print('Got connection from', addr)
        while True:
            data = conn.recv(1024)
            print('Server received data: ', repr(data))
            response = server_data_handler(FTs, data.decode())
            conn.send(response.encode())
            # conn.close()  # It should not be the server side to close the connection

    except Exception as e:
        # Connection closed by server will be recorded in Exceptions.
        # It is possible to put a separate Exception handler for connection close, but I'm a bit lazy lol.
        # can write to a file later
        logging.error(e)
    
    

