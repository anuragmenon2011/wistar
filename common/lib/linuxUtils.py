import re

import paramiko
from paramiko.ssh_exception import SSHException
from common.lib.WistarException import WistarException


# simple method to execute a cli on a remote host
# fixme - improve error handling
def execute_cli(host, username, password, cli):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password)
        stdin, stdout, stderr = client.exec_command(cli)
        err = stderr.read()
        if err != "":
            return err
        else:
            return stdout.read()
    except SSHException as se:
        raise WistarException(str(se))


# set an IP on an interface and return to user
def set_interface_ip_address(ip, username, pw, interface, interface_ip):
    flush_cmd = "ip addr flush dev " + interface
    execute_cli(ip, username, pw, flush_cmd)

    # did the user include a subnet?
    if not re.match('\d+\.\d+\.\d+\.\d+/\d+', interface_ip):
        # no, let's add a default /24 then
        interface_ip += "/24"

    cmd = "ip addr add " + interface_ip + " dev " + interface
    cmd = cmd + " && ip link set dev " + interface + " up"
    # fixme - there needs to be a better way to inform of failure
    # always returning a string isn't the best...
    print execute_cli(ip, username, pw, cmd)
    return True


def push_remote_script(ip, username, pw, script_text, script_destination):

    try:
        # remove last thing after last "/"
        # results in only the path we care about
        script_path = "/".join(script_destination.split('/')[:-1])
        transport = paramiko.Transport((ip, 22))
        transport.connect(username=username, password=pw)

        client = paramiko.SFTPClient.from_transport(transport)
    except SSHException as se:
        print "Caught SSHException"
        print str(se)
        raise WistarException(str(se))

    try:
        print "Creating directory: " + script_path
        rstats = client.stat(script_path)
        print rstats
    except IOError:
        print "creating non-existant path"
        client.mkdir(script_path)

    try:
        print "Writing file"
        f = client.file(script_destination, 'w')
        f.write(script_text)
        f.close()
        print "setting execute permissions"
        client.chmod(script_destination, 0744)
        client.close()
    except Exception as e:
        print "Caught error!"
        print str(e)
        raise WistarException(str(e))
