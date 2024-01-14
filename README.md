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

|  Name  | Description | Type | Default |
| ------ | ----------- | ---- | ------- |
| RSYNC_HOST | Remote rsync host address | str | N/A |
| RSYNC_PORT | Remote rsync host port | int | N/A |
| RSYNC_USER | Remote rsync user | str | N/A |
| RSYNC_DESTINATION | Remote rsync destination path/module | str | N/A |
| FTP_USER | Local FTP username | str | N/A |
| FTP_PASSWORD | Local FTP password | str | N/A |
| FTP_HOME | Local FTP home path | str | / |
| RELAY_THREADS | Number of concurrent relay threads | int | 4 |

