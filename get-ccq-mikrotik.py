#!/usr/bin/python
# -*- encoding: utf-8 -*-
import paramiko
import sys


class ConexaoSSH(object):

    def __init__(self, host, usuario, senha):
        self.host = host
        self.usuario = usuario
        self.senha = senha

    def conectar(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Conecta ao servidor
            ssh.connect(self.host, username=self.usuario, password=self.senha)
            return ssh

        except ValueError:
            return "Problemas com a conexão"

    def executarComando(self, comando):

        ssh = self.conectar()

        # Executa linha de comando
        stdin, stdout, stderr = ssh.exec_command(comando)
        resultado = stdout.readlines()
        ssh.close()

        return resultado

if __name__ == '__main__':
    # Variaveis passadas na chamado do script
    host = sys.argv[1]
    usuario = sys.argv[2]
    senha = sys.argv[3]
    critical = sys.argv[4]
    warning = sys.argv[5]

    # Inicia objeto da classe
    ssh = ConexaoSSH(host, usuario, senha)
    # Pega resultado da linha
    string = ssh.executarComando('/interface wireless registration-table print stats without-paging')

    # Trata string para obter os resultados de CCQ, tx e rx
    string = str(string)
    if string:
        tx = string.find('tx-ccq')
        rx = string.find('rx-ccq')

        tx=string[tx+7:tx+10]
        rx=string[rx+7:rx+10]

        if tx[2] == '%':
            tx = tx[0:2]

        if rx[2] == '%':
            rx = rx[0:2]

    else:
        print "UKNOWN - Dados indisponiveis"
        sys.exit(3)


    # Devolve resultado ao nagios
    if (int(tx) >= int(warning)) and (int(rx)>= int(warning)):
        print "OK - Qualidade de CCQ = %s/%s" % (tx, rx)
        sys.exit(0)
    elif (int(tx) >= int(critical)) and (int(tx) < int(warning)) or \
         (int(rx) >= int(critical)) and (int(rx) < int(warning)):
        print "WARNING - Qualidade de CCQ = %s/%s" % (tx, rx)
        sys.exit(1)
    elif (int(tx) < int(critical)) or (int(rx) < int(critical)):
        print "CRITICAL - Qualidade de CCQ = %s/%s" % (tx, rx)
        sys.exit(2)
    else:
        print "UKNOWN - Dados indisponiveis"
        sys.exit(3)
