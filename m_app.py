import os
import sys
import strictyaml
import yaml
import time
import datetime
import socket
import re
import paramiko
import shutil
import getpass
import colorama
from getpass import getpass
from io import StringIO
from paramiko import SSHClient
from paramiko import AutoAddPolicy
from yaml import CLoader as Loader, CDumper as Dumper
from pythonping import ping

os.system('cls')

script_start_time = datetime.datetime.now()
system_name = os.getenv('HOSTNAME')
print ("Script run at:", datetime.datetime.now())

#print text color
class print_color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

print("""
  MMM      MMM       KKK                          TTTTTTTTTTT      KKK
  MMMM    MMMM       KKK                          TTTTTTTTTTT      KKK
  MMM MMMM MMM  III  KKK  KKK  RRRRRR     OOOOOO      TTT     III  KKK  KKK
  MMM  MM  MMM  III  KKKKK     RRR  RRR  OOO  OOO     TTT     III  KKKKK
  MMM      MMM  III  KKK KKK   RRRRRR    OOO  OOO     TTT     III  KKK KKK
  MMM      MMM  III  KKK  KKK  RRR  RRR   OOOOOO      TTT     III  KKK  KKK
------------------------------------------------------------------------------
 script by slogangray     ver 1.0 beta
""")

#get addresses and ports from a file ip_list.txt
routers_list = []
try:    
    with open("ip_list.txt") as f:
        for line in f:
            try:
                ip_and_port = re.findall(r'(^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{2,5})', line)
                if socket.inet_aton(ip_and_port[0][0]) and int(ip_and_port[0][1]) <= 65535:
                    routers_list.append(ip_and_port)
            except socket.error: pass
            except IndexError: pass
except IOError:
    print (print_color.RED + 'Can`t read ip_list.txt!' + print_color.END)
    sys.exit()

#get config data
try:
    config = yaml.safe_load(open('config.conf')) 
except IOError:
    print (print_color.RED + "ERROR: can't read config.conf!" + print_color.END)
    sys.exit()

#generate a private key and save
def generate_keys():
    try:
        gen_passwd = getpass(prompt='Please input password for generte KEY: ')
        file_obj = StringIO()
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(config["save_private_key_file"], gen_passwd)
        key.write_private_key(file_obj)
        public = key.get_base64()
        private = file_obj.getvalue()
        file_obj.close()
        return {'private': private,'public': public}
    except IOError:
        print (print_color.RED + "ERROR: can't write private key file!" + print_color.END)    
	
#generate a public key and save
def save_keys(keys):
    with open (config["save_public_key_file"], 'w') as fd:
        shutil.copyfileobj (StringIO(keys['public']), fd)

#open SSH key
def open_ssh_key():
    try:       
        print("--->>> Try to open key file", config["private_key_file"])
        sslpasswd = getpass(prompt='Please input password for SSL connection: ')
        with open(config["private_key_file"]) as f:
            ssh_key = paramiko.RSAKey.from_private_key_file(config["private_key_file"], password=sslpasswd)
        print("--->>> ssh-key loaded")
        return ssh_key
    except IOError:
        print(print_color.RED + "ERROR!: can't read private_key_file:", config["private_key_file"]+ print_color.END)
        sys.exit()
    except IndexError:
        print(print_color.RED + "ERROR: not corrent private_key_file:", config["private_key_file"]+ print_color.END)
        sys.exit()
    except paramiko.ssh_exception.SSHException as err:
        print(print_color.RED + "ERROR:" + print_color.END, err)
        sys.exit()

#connect SSH
def connect_ssh(hostname_id,port_id,username_id,pkey_id):
    try:
        ssh=SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(hostname=hostname_id, port=port_id, username=username_id, pkey=pkey_id)
        print(print_color.GREEN + "--->>> connected" + print_color.END)
        print ("--->>> run script")
        cmd0 ="system routerboard settings set auto-upgrade=yes"
        cmd1 ="system package update check-for-updates"
        cmd2 ="system package update download"
        cmd3 ="system reboot"
        stdin,stdout,stderr = ssh.exec_command(cmd0)
        print (stdout.read().decode('utf-8'))
        time.sleep(2)
        stdin,stdout,stderr = ssh.exec_command(cmd1)
        print (stdout.read().decode('utf-8'))
        time.sleep(2)
        stdin,stdout,stderr = ssh.exec_command(cmd2)
        print (stdout.read().decode('utf-8'))
        time.sleep(60)
        stdin,stdout,stderr = ssh.exec_command(cmd3) #reboot to upgrade ROS
        print (stdout.read().decode('utf-8'))
        time.sleep(60)
        stdin,stdout,stderr = ssh.exec_command(cmd3) #reboot to upgrade firmware
        print (stdout.read().decode('utf-8'))
#        print (stdout.read().decode('utf-8').strip().replace('\r\n', ''))
        time.sleep(1)
        ssh.close()
        time.sleep(1)
        return True
    except Exception:
        return False 

#availability check procedure
def port_available (ip):
    try:
        res = False
        ping_param = "-n 1" #if system_name.lower() == "windows" else "-c 1"
        resultado = os.popen("ping " + ping_param + " " + ip).read()
        if "TTL=" in resultado:
            res = True
        if res == True:
            print("--->>> router reachable")
        else:
            print(print_color.RED + '--->>> router unreachable!' + print_color.END)
        return res
    except Exception:
        print(print_color.RED + "Ping ERROR!" + print_color.END)

#portknocking
def port_knock (ip):
    try: 
        ping(ip, count=1, size=878)
        time.sleep(2)
        ping(ip, count=1, size=327)
        time.sleep(2)
        ping(ip, count=1, size=701)
    except Exception:
        print(print_color.RED + "Knock ERROR!" + print_color.END)

#check for an argument "g" to generate a new key   
def main():
    try:
        if len(sys.argv) == 2 and "g" == sys.argv[1]:
            save_keys(generate_keys())
            print("Generate keys complete")
            sys.exit()
        elif config['auth_method'] == "key":

#connecting to routers from the address list
            print ("-------------------------------------------------------------------------------")
            config['pkey'] = open_ssh_key()
            for ip in routers_list:
                print ("--->>> Check ping to router:", (ip[0][0]),"wait")           
                if port_available (ip=ip[0][0]) == True:
                    print ("--->>> connect to:",(ip[0][0]),"> wait")
                    if config['portknoking'] == "YES":
                        port_knock (ip=ip[0][0])
                        print ("--->>> knocking to:",(ip[0][0]),"> wait")
                    else:
                        if connect_ssh (hostname_id=ip[0][0], port_id=ip[0][1], username_id=config['Login'], pkey_id = config['pkey']) == False:
                            print (print_color.RED + '--->>> SSH connect failed!' + print_color.END)
                        else:
                            print ("-------------------------------------------------------------------------------")
                            print ("--->>> Check ping to router:", (ip[0][0]),"wait")
                            time.sleep(60) #time wait after run CMDs          
                            if port_available (ip=ip[0][0]) == True:
                                print ("--->>> connect to:",(ip[0][0]),"> wait")
                                if config['portknoking'] == "YES":
                                    port_knock (ip=ip[0][0])
                                    print ("--->>> knocking to:",(ip[0][0]),"> wait")
                            else:
                                raise Exception("Ping failed!")      
            
    except Exception as ex:
        print(ex)

    sctipt_duration = datetime.datetime.now() - script_start_time
    print("Script run time: {0} seconds".format(int(sctipt_duration.total_seconds())))

if __name__ == "__main__":
    main()