# lockpicker
Lockpicker is a multithreaded brute force login tool, supporting various protocols to attack. This tool is dedicated to security researchers and pentesters to perform brute force attacks in controlled and safe environemnts.

Currently supported modules:    telnet, ssh, ftp, smb, smtp, pop3, mysql, postgresql
(some modules may be slow, due to protocol's implementation)
## Requirements
* Several python libraries are required for this script to run. To install them, in terminal run:
```bash
pip install -r requirements.txt
```
## Usage
usage: lockpicker.py USERNAME@IP [-h] -p PASSWORDLIST [-n NUMPORT] [-t THREADS] -s SERVICE

options:
  -h, --help            show this help message and exit
  -p, --passwordlist PASSWORDLIST
                        passwordlist to iterate through
  -n, --numport NUMPORT
                        custom port number for selected service
  -t, --threads THREADS
                        threads used to attack (default=8)
  -s, --service SERVICE
                        target service to attack

## Examples
examples:
```bash
         python3 lockpicker.py user@127.0.0.1 -p passwords.txt -s telnet
         python3 lockpicker.py postgres@127.0.0.1 -p passwords.txt -s postgresql -n 5555 -t 12
```
## Example Output
```python
      _               _          _      _
     | |    ___   ___| | ___ __ (_) ___| | _____ _ __       _ __  _   _
     | |   / _ \ / __| |/ / '_ \| |/ __| |/ / _ \ '__|     | '_ \| | | |
     | |__| (_) | (__|   <| |_) | | (__|   <  __/ |     _  | |_) | |_| |
     |_____\___/ \___|_|\_\ .__/|_|\___|_|\_\___|_|    (_) | .__/ \__, |
                          |_|                              |_|    |___/

[*] Starting lockpicker on 127.0.0.1, user lockpicked: ftpuser
[*] Attacking FTP on port 21...

[+] SUCCESS | The FTP password is: test
 89%|█████████████████████████████████████████████████████████████████████████▏        | 91/102 [00:30<00:03,  2.98it/s]
```
---
## Disclaimer
Any illegal use of this tool could be met with consequences.
