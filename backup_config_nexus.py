import csv
import os,sys
import paramiko
from datetime import datetime, timedelta

def server_tftp():

    ip_server = "10.64.129.7/SW_NEXUS_LCS/NEXUS"
    return ip_server

def get_ymd_currently():

    ymd = datetime.now()
    Ymd = ymd.strftime("%Y%m%d")
    return Ymd

def get_hms_currently():

    hms = datetime.now()
    HMS = hms.strftime("%H%M%S")
    return HMS

def rename_folder_include_config_currently():

    year_month_day = get_ymd_currently()
    hour_munites_second = get_hms_currently()

    folder_source = "/tftpboot/SW_NEXUS_LCS/NEXUS"
    folder_destination = "/tftpboot/SW_NEXUS_LCS/NEXUS_"+year_month_day+'_'+hour_munites_second

    if (os.path.exists(folder_source)):
        os.system("mv "+folder_source+" "+folder_destination)
        print('Move folder '+folder_source+' to '+folder_destination+' complete....')
    else:
        print('[ERROR] Not exists folder '+folder_source)
        create_folder_include_backup_config()

def create_folder_include_backup_config():
    
    folder_mkdir = "/tftpboot/SW_NEXUS_LCS/NEXUS"
    os.system("mkdir -p "+folder_mkdir)
    print('Create mkdir folder '+folder_mkdir+' complete....')

def chmod_folder_include_backup_config():

    folder_chmod = "/tftpboot/SW_NEXUS_LCS"
    os.system("chmod -R 777 "+folder_chmod)
    print('Permissions chmod -R 777 '+folder_chmod+' complete....')

def remove_folder_include_backup_config():

    for ago_days in range(30,60):
        date_days_ago = (datetime.now() - timedelta(days=ago_days)).strftime("%Y%m%d")
        get_date_time_ago = "/tftpboot/SW_NEXUS_LCS/NEXUS_"+date_days_ago
        os.system("rm -rf "+get_date_time_ago+"_*")
        print('Running cmd rm -rf '+get_date_time_ago+'_*')

def copy_running_config(name_switch, vrf_context):

    return ('copy running-config ' + 'tftp://'+server_tftp()+'/'+name_switch+'-running-config vrf '+ vrf_context)

def copy_startup_config(name_switch,vrf_context):

     return ('copy startup-config ' + 'tftp://'+server_tftp()+'/'+name_switch+'-startup-config vrf '+ vrf_context)

def ssh_connect_backup_config_via_paramiko(ip_switch, port, user, password, name_switch, vrf_context):

    try:
    # Doi ten thu muc chua nhung file config cua tat ca NEXUS hien tai
        rename_folder_include_config_currently()
    # Tao thu muc de thuc hien backup config NEXUS
        create_folder_include_backup_config()

        chmod_folder_include_backup_config()

        ssh = paramiko.SSHClient()
        print('Start connect ssh to client')
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip_switch, port=port, username=user, password=password)

    # Backup running config

        copy_running_config_tftp = copy_running_config(name_switch,vrf_context)
        print("Backup startup config to tftp server "+server_tftp()+" is starting ......")
        stidin,stdout,stderr = ssh.exec_command(copy_running_config_tftp)
    # In ra log vua thuc thi duoc tu cau lenh khi goi ham exec_command
        for line in iter(stdout.readline, ""):
            print(line, end="")

    # Backup startup config

        copy_startup_config_tftp = copy_startup_config(name_switch,vrf_context)
        print("Backup running config to tftp server "+server_tftp()+" is starting ......")
        stidin,stdout,stderr = ssh.exec_command(copy_startup_config_tftp)
    # In ra log vua thuc thi duoc tu cau lenh khi goi ham exec_command
        for line in iter(stdout.readline, ""):
            print(line, end="")

        stidin.close()
        ssh.close()

    except Exception as e:
        print('Establish connection SSH to client failed !!!')
        print(e)

if __name__ == '__main__':

    get_path_current_execute_directory = os.path.dirname(os.path.realpath(sys.argv[0]))
    get_directory_path_file_csv = (get_path_current_execute_directory + '/server.csv')

    if os.path.isfile(get_directory_path_file_csv):

        with open(get_directory_path_file_csv, 'r') as open_file_csv:

            read_file_csv = csv.reader(open_file_csv, delimiter=',')

            next(open_file_csv)  # skip row header csv

            for row in read_file_csv:
                print('===================================================================================')
                ip_switch = row[0]
                print('Ip Switch:', ip_switch)
                port = row[3]
                print('Port Connect:', port)
                user = row[1]
                print('Username:', user)
                password = row[2]
                print('Password: **********')
                name_switch = row[4]
                print('Name Device: ', name_switch)
                vrf_context = row[5]
                print('VRF Context:', vrf_context)

                ssh_connect_backup_config_via_paramiko(ip_switch,port,user,password,name_switch,vrf_context)
        open_file_csv.close()
    else:
        print('File '+get_directory_path_file_csv+' not exists !!! ')
    remove_folder_include_backup_config()
