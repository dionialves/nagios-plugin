# -*- encoding: utf-8 -*-
# !/usr/bin/python
import paramiko
import re
import json
import sys
from optparse import OptionParser


class ConnectionSSH(object):

    def __init__(self, host, user, password, port):
        self.host = host
        self.user = user
        self.password = password
        self.port = port

    def connection(self):
        connect = paramiko.SSHClient()
        connect.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Connect to server
            connect.connect(hostname=self.host, port=self.port, username=self.user, password=self.password)
            return connect

        except:
            print("UKNOWN - Authentication failed or inaccessible host")
            sys.exit(3)

    def execute_command(self, command):

        connect = self.connection()

        # Run command line
        stdin, stdout, stderr = connect.exec_command(command)
        result = stdout.readlines()
        connect.close()

        return result

if __name__ == '__main__':

    # Variables received via the command line
    parser = OptionParser()
    parser.add_option("-H", "--host", dest="argv_host", type="string", help="Specify hostname to run")
    parser.add_option("-u", "--user", dest="argv_user", type="string", help="Specify username for connect")
    parser.add_option("-p", "--pass", dest="argv_password", type="string", help="Specify password for connect")
    parser.add_option("-c", "--critical", dest="argv_critical", type="string", help="Specify the value of critical")
    parser.add_option("-w", "--warning", dest="argv_warning", type="string", help="Specify the value of critical")
    parser.add_option("-P",
                      "--port",
                      dest="argv_port",
                      default="22",
                      type="int",
                      help="Specify the SSH connection port. If not specified we will use the default port 22")

    # Receive as variables in command line
    (options, args) = parser.parse_args()

    argv_host = options.argv_host
    argv_user = options.argv_user
    argv_password = options.argv_password
    argv_critical = options.argv_critical
    argv_warning = options.argv_warning
    argv_port = options.argv_port

    # Checks whether the required variables have been entered
    for option in ('argv_host', 'argv_user', 'argv_password', 'argv_critical', 'argv_warning'):
        if not getattr(options, option):
            print('UKNOWN - Option %s not specified' % option.capitalize())
            sys.exit(3)

    # Start the class object
    conn = ConnectionSSH(argv_host, argv_user, argv_password, argv_port)

    # Get result line
    result_list = str(conn.execute_command('/interface wireless registration-table '
                                           'print stats without-paging')).split(" ")

    # In the code below, we extract the values ​​of tx and rx and put them in a dictionary.
    try:
        new_list = []
        for x in result_list:
            if (re.search("tx-ccq", x) is not None) or (re.search("rx-ccq", x) is not None):
                new_element = x.replace("=", '":"').replace("tx", '"tx').replace("rx", '"rx').replace("%", '%"')
                new_list.append(new_element)

        to_string = ",".join(str(x) for x in new_list)
        to_string = "{" + to_string + "}"
        to_dict = json.loads(to_string)

        # To validate the CCQ status, we remove the '%'.
        tx = to_dict['tx-ccq'].replace('%', '')
        rx = to_dict['rx-ccq'].replace('%', '')

    except:
        print("UKNOWN - Incompatible equipment")
        sys.exit(3)

    # Returns result to nagios
    if (int(tx) >= int(argv_warning)) and (int(rx) >= int(argv_warning)):
        print("OK - Client Connection Quality (CCQ) = %s/%s" % (to_dict['tx-ccq'], to_dict['rx-ccq']))
        sys.exit(0)
    elif (int(tx) >= int(argv_critical)) and (int(tx) < int(argv_warning)) or \
         (int(rx) >= int(argv_critical)) and (int(rx) < int(argv_warning)):
        print("WARNING - Client Connection Quality (CCQ) = %s/%s" % (to_dict['tx-ccq'], to_dict['rx-ccq']))
        sys.exit(1)
    elif (int(tx) < int(argv_critical)) or (int(rx) < int(argv_critical)):
        print("CRITICAL - Client Connection Quality (CCQ) = %s/%s" % (to_dict['tx-ccq'], to_dict['rx-ccq']))
        sys.exit(2)
    else:
        print("UKNOWN - Unavailable data")
        sys.exit(3)
