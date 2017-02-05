#!/usr/bin/python
import paramiko
import os, sys

# Variavel passada na chamado so script
host=sys.argv[1]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Conecta ao servidor
ssh.connect(host, username='USUARIO', password='SENHA')

# Executa linha de comando
stdin, stdout, stderr = ssh.exec_command('/interface wireless registration-table print stats without-paging')

# Pega resultado da linha
string = stdout.readlines()

# Trata string para obter os resultados de CCQ, tx e rx
string=str(string)
tx = string.find('tx-ccq')
rx = string.find('rx-ccq')

tx=string[tx+7:tx+10]
rx=string[rx+7:rx+10]

if tx[2] == '%':
    tx = tx[0:2]

if rx[2] == '%':
    rx = rx[0:2]

# Fecha conexao com servidor
ssh.close()

# Devolve resultado ao nagios
if (int(tx) >= 90) and (int(rx)>= 90):
    print "OK - Qualidade de CCQ = %s/%s" % (tx, rx)
    sys.exit(0)
elif (int(tx) >= 80) and (int(tx) < 90) or (int(rx) >= 80) and (int(rx) < 90):
    print "WARNING - Qualidade de CCQ = %s/%s" % (tx, rx)
    sys.exit(1)
elif (int(tx) < 80) or (int(rx) < 80):
    print "CRITICAL - Qualidade de CCQ = %s/%s" % (tx, rx)
    sys.exit(2)
else:
    print "UKNOWN - Dados indisponiveis"
    sys.exit(3)