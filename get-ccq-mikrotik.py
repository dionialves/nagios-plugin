# -*- encoding: utf-8 -*-
# !/usr/bin/python
import paramiko
import re
import json
import sys


class ConnectionSSH(object):

    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def connection(self):
        connect = paramiko.SSHClient()
        connect.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Connect to server
            connect.connect(self.host, username=self.user, password=self.password)
            return connect

        except:
            print("UKNOWN - Authentication failed")
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
    argv_host = sys.argv[1]
    argv_user = sys.argv[2]
    argv_password = sys.argv[3]
    argv_critical = sys.argv[4]
    argv_warning = sys.argv[5]

    # Start the class object
    conn = ConnectionSSH(argv_host, argv_user, argv_password)

    # Get result line
    result_list = str(conn.execute_command('/interface wireless registration-table print stats without-paging')).split(" ")

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
