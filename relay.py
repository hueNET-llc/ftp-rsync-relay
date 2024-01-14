import colorlog
import logging
import os
import queue
import subprocess
import sys
import time
import threading

from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer
from pyftpdlib.authorizers import DummyAuthorizer

file_queue = queue.Queue()
log = logging.getLogger('Relay')

class Handler(FTPHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_file_received(self, file):
        # Insert the file path into the file queue
        file_queue.put(file)

def _setup_logging():
    """
        Sets up logging colors and formatting
    """
    # Create a new handler with colors and formatting
    shandler = logging.StreamHandler(stream=sys.stdout)
    shandler.setFormatter(colorlog.LevelFormatter(
        fmt={
            'DEBUG': '{log_color}{asctime} [{levelname}] {message}',
            'INFO': '{log_color}{asctime} [{levelname}] {message}',
            'WARNING': '{log_color}{asctime} [{levelname}] {message}',
            'ERROR': '{log_color}{asctime} [{levelname}] {message}',
            'CRITICAL': '{log_color}{asctime} [{levelname}] {message}',
        },
        log_colors={
            'DEBUG': 'blue',
            'INFO': 'white',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bg_red',
        },
        style='{',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    # Add the new handler
    logging.getLogger('Relay').addHandler(shandler)
    logging.root.setLevel(int(os.environ.get('LOG_LEVEL', 20)))
    log.debug('Finished setting up logging')

def rsync_send(host: str, port: int, username: str, file_path: str, destination_path: str) -> int:
    """
    Send a file to a remote host using rsync.

    Args:
        host (str): hostname or IP address of the remote host
        port (int): port number of the remote rsync daemon
        username (str): username to use for the rsync connection
        file_path (str): full path to the file to send
        destination_path (str): destination path on the remote host

    Returns:
        int: process return code
    """
    # os.system(f'rsync -avR --mkpath {file} rsync://{self.rsync_user}@{self.rsync_destination_ssh}:{self.rsync_rsh_port}{self.rsync_destination}/{file2}')
    log.debug(f'Sending file {file_path} to {host}:{port}{destination_path}')
    log.debug(f'Full rsync URI is rsync://{username}@{host}:{port}/{destination_path}')
    result = subprocess.run([
        'rsync',
        '-a',
        '--mkpath',
        file_path,
        f'rsync://{username}@{host}:{port}/{destination_path}'
    ])
    return result.returncode

def process_queue():
    while True:
        file_path: str = file_queue.get()
        log.info(f'Processing queue file: {file_path}')
        # Strip the FTP_HOME from the file path
        destination_path: str = file_path.removeprefix(os.environ['FTP_HOME'])
        while True:
            try:
                result = rsync_send(
                    host=os.environ['RSYNC_HOST'],
                    port=int(os.environ['RSYNC_PORT']),
                    username=os.environ['RSYNC_USER'],
                    file_path=file_path,
                    destination_path=f'{os.environ["RSYNC_DESTINATION"]}{destination_path}'
                )
                if result == 0:
                    # rsync succeeded, delete the local file
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        log.warning(f'rsync succeeded without file deletion: {file_path}: {e}')
                    else:
                        log.info(f'rsync succeeded: {file_path}')
                    break
                else:
                    log.error(f'rsync failed: {file_path}')
            except Exception as e:
                log.exception(f'rsync failed: {file_path}')
            finally:
                # If we got here, rsync failed. Wait 5 seconds and try again.
                time.sleep(5)

def process_existing_files():
    """
    Process all existing files in the FTP_HOME directory
    """
    for root, _, files in os.walk(os.environ.get('FTP_HOME', '/')):
        for file in files:
            file_path = os.path.join(root, file)
            log.info(f'Adding existing file to queue: {file_path}')
            file_queue.put(file_path)

def main():
    # Setup logging
    _setup_logging()
    # Process existing files
    process_existing_files()
    authorizer = DummyAuthorizer()
    authorizer.add_user(
        username=os.environ['FTP_USER'],
        password=os.environ['FTP_PASSWORD'],
        homedir=os.environ.get('FTP_HOME', '/'),
        perm='elradfmw'
    )
    handler = Handler
    handler.authorizer = authorizer
    server = ThreadedFTPServer(('', 21), handler)

    # Start the file processing threads
    for _ in range(int(os.environ.get('RELAY_THREADS', 4))):
        thread = threading.Thread(target=process_queue)
        # Make the thread a daemon so it will exit when the main thread exits
        thread.daemon = True
        thread.start()

    server.serve_forever()

if __name__ == '__main__':
    main()
