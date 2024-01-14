# ftp-rsync-relay
A simple FTP to rsync relay

## Features
- Receives and stores incoming files over FTP
- Forwards received files over rsync to a remote host
- Concurrent forwarding
- Automatic retry when remote host is unreachable

## Requirements
Python requirements are listed in `requirements.txt`.

The only system requirement is `rsync`.

## Environment Variables ##
Configuration is done via environment variables. Any values with "N/A" default are required.

|  Name  | Description | Type | Default | Example |
| ------ | ----------- | ---- | ------- | ------- |
| RSYNC_HOST | Remote rsync host address | str | N/A | server.example.com |
| RSYNC_PORT | Remote rsync host port | int | N/A | 873 |
| RSYNC_USER | Remote rsync user | str | N/A | rsync_user |
| RSYNC_PASSWORD | Remote rsync password | str | N/A | hunter2
| RSYNC_DESTINATION | Remote rsync destination path/module | str | N/A | data/ |
| RSYNC_RETRY_INTERVAL | Failed rsync retry interval (seconds) | int | 5 | 10 |
| FTP_USER | Local FTP username | str | N/A | ftp_user |
| FTP_PASSWORD | Local FTP password | str | N/A | hunter3 |
| FTP_HOME | Local FTP home path | str | / | /home/ftp |
| RELAY_THREADS | Number of concurrent relay threads | int | 4 | 4 |
| PROCESS_EXISTING_FILES | Relay any existing files in FTP_HOME | bool | True | True |
| DELETE_AFTER_RSYNC | Delete local files after successful rsync | bool | True | True
