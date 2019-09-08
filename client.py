import socket                   # Import socket module
import os
import time
import _thread
import logging
import zipfile
import shutil

s = socket.socket()             # Create a socket object
host = socket.gethostname()     # Get local machine name
port = 6969                    # Reserve a port for your service.
file_transfer_port = 9696

def upload_to_server(file_transfer_port,time_stamp):
    time.sleep(1)
    # firstly compress the save file.
    output_file_name = str(time_stamp)
    shutil.make_archive(output_file_name, 'zip', './save')
    FT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    FT.connect((socket.gethostname(), file_transfer_port))
    with open(str(output_file_name+'.zip'),'rb') as fs:
        while True:
            data = fs.read(1024)
            FT.send(data)
            if not data:
                break
        fs.close()
    print('Uploaded')
    
            

def download_to_client(file_transfer_port,server_time_stamp):
    time.sleep(1)
    FT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    FT.connect((socket.gethostname(), file_transfer_port))
    output_file_name = str(server_time_stamp) + '.zip'
    print('writing')
    with open(output_file_name,'wb') as fs:
        while True:
            data = FT.recv(1024)
            if not data:
                # print("no more data")
                break
            fs.write(data)
        fs.close()
    print('Received')

    # Then remove the previous save file and decompress
    shutil.rmtree('./save')
    os.mkdir('save')
    
    shutil.unpack_archive(output_file_name,extract_dir='save')
    print('Unzipped')



def check_time_stamp():
    # Firstly check if the target folder exists
    if os.path.exists("./save"):
        result = os.path.getmtime('./save')
        if len(os.listdir('./save') ) == 0:
            result = 0.0
        else:    
            pass
        return result
    else:
        raise ValueError('The save folder does not exist')

# Send data to server step by step
def verification():
    s.connect((host, port))
    string = "Hello server!" # Security header
    s.send(string.encode())
    data = s.recv(1024)
    time_stamp = check_time_stamp()
    send_data = "time_stamp" + str(time_stamp)
    print('send_data=%s' %data) # Receive header
    s.send(send_data.encode())
    data = s.recv(1024)
    print('data=%s' %data) # Receive header
    if data == b'upload':
        print("Server requests to upload")
        try:
            _thread.start_new_thread(upload_to_server, (file_transfer_port,time_stamp,))
        except Exception as e:
            logging.error(e)
    else:
        print("Server requests to download")
        try:
            server_time_stamp = data.decode('ascii')
            _thread.start_new_thread(download_to_client, (file_transfer_port,server_time_stamp,))
        except Exception as e:
            logging.error(e)
        
    print('Handle the sync request to threading.')
    s.close()
    print('connection closed')
    
verification()
