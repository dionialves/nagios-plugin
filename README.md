# Nagios Plugins

PLugin para nagios, com o objetivo de retornar qualidade de conexão (TX e RX) de um enlace utilizando equipamentos mikrotik.

# Requisitos
- python 2.7
- paramiko
- Nagios 
- RouterOS v6.37 (Implementada nessa versão, pode funcionar em outras)

# Instalação
Para realizar a instalção de desse plugin, entendo que o nagios ja deve estar instalado e configurado.

- Coloque o arquivo dentro da pastar /usr/local/nagios/libexec
- Dê permisão para execução com o comando chmod +x get-ccq-mikrotik.py




# Exemplo de uso

- Configure o arquivo commands.cfg adicionando as intrução do comando a ser executado

vim /usr/local/nagios/etc/objects/commands.cfg
define command{
        command_name    check_mikrotik_ccq
        command_line    $USER1$/get-ccq-mikrotik.py $HOSTADDRESS$ $USER8$ $USER9$ $ARG1$ $ARG2$
        }

- Configure o arquivo resource.cfg adicionando as variáveis de usuario e senha
vim /usr/local/nagios/etc/resource.cfg
$USER2$=USUARIO
$USER3$=SENHA

- Configure o arquivo com a descrição do serviço a ser monitorado
vim /usr/local/nagios/etc/objects/ptp_mikrotik.cfg
define service{
        use                             generic-service
        service_description             Qualidade CCQ
        check_command                   check_mikrotik_ccq!80!90
        }



