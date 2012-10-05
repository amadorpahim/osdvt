#!/bin/bash
# OSDVT Install Script
# Be careful: This script may not check the system before making changes.
#             It's just the automation of Full Install Guide 
# Supported Systems:
# - Red Hat Enterprise Linux 6.3

install_packets()
{
    echo "OSDVT SERVER - Installing Packets"
    [ $1 -eq 1 ] && {
        rpm -Uvh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-7.noarch.rpm
        yum -y install qemu-kvm qemu-img spice-server \
            mysql-server MySQL-python python-ldap \
            bridge-utils tunctl Django httpd \
            mod_ssl mod_python wget
    }
}

os_probe()
{
    echo "OSDVT SERVER - Probing Linux Distro"
    osVersion=$(</etc/system-release)
    if [[ $osVersion =~ "Red Hat" ]]
    then
        [[ $osVersion =~ "6.3" ]] && {
            echo Red Hat 6.3
            return 1
        }
    else
        echo "System not supported. Please install manually."
	exit 1
    fi
}


config_network()
{
    echo "OSDVT SERVER - Bridge Configuration"
    read -p "Please enter the interface to be bridged: [eth0] " iface
    read -p "Please enter the bridge name: [br0] " bridge
    iface=${iface:-eth0}
    bridge=${bridge:-br0}
    [ $1 -eq 1 ] && {
	[ -a /etc/sysconfig/network-scripts/ifcfg-$bridge ] && {
		echo "File /etc/sysconfig/network-scripts/ifcfg-$bridge found. Skiping bridge creation."
	} 
	grep -i "BRIDGE=" /etc/sysconfig/network-scripts/ifcfg-$iface > /dev/null 2> /dev/null && {
		echo "$iface is already configured to a bridge. Skipping bridge and interface configuration."
	} || {
       		cat /etc/sysconfig/network-scripts/ifcfg-$iface | grep -v -e DEVICE -e NAME -e UUID -e MAC -e TYPE -e ONBOOT > /etc/sysconfig/network-scripts/ifcfg-$bridge
		echo -e "DEVICE=$bridge\nONBOOT=yes\nTYPE=Bridge\nNAME=$bridge" >> /etc/sysconfig/network-scripts/ifcfg-$bridge
       		echo -e "DEVICE=$iface\nONBOOT=yes\nBRIDGE=$bridge"  > /etc/sysconfig/network-scripts/ifcfg-$iface
       		service network restart
	}
        chkconfig network on
    }
}

config_mysql()
{
    echo "OSDVT SERVER - MySQL Configuration"
    read -p "Please enter MySQL password: " mysqlpwd
    [ $1 -eq 1 ] && {
        service mysqld restart
        mysqladmin -u root password "${mysqlpwd}"
        chkconfig mysqld on
        mysql --user=root --password="${mysqlpwd}" -e "create database db_osdvt" 
    }
}

config_django()
{
    [ $1 -eq 1 ] && {
	[ -a /usr/local/osdvt/osdvtweb/settings.py ] || {
        	cp /usr/local/osdvt/server/packaging/rhel63/django-settings.py /usr/local/osdvt/osdvtweb/settings.py
	}
	sed -i "s/PASSWORD':\t''/PASSWORD':\t'${mysqlpwd}'/" /usr/local/osdvt/osdvtweb/settings.py
        cd /usr/local/osdvt/osdvtweb/
        python manage.py syncdb
    }
}

config_init()
{
    [ $1 -eq 1 ] && {
        cp /usr/local/osdvt/server/packaging/rhel63/sysv-osdvtd /etc/init.d/osdvtd
        chkconfig osdvtd on
    }
}

config_httpd()
{
    [ $1 -eq 1 ] && {
        cp /usr/local/osdvt/server/packaging/rhel63/httpd-osdvt.conf /etc/httpd/conf.d/osdvt.conf
        chkconfig httpd on
        service httpd restart
        echo "Got to https://$(hostname)/osdvtweb/admin"
    }
}

start_osdvtd()
{
    [ $1 -eq 1 ] && {
        service osdvtd start
    }
}

main()
{
    os_probe
    distro=$?

    install_packets $distro
    config_mysql $distro    
    config_django $distro
    config_init $distro
    config_network $distro    
    start_osdvtd $distro
    config_httpd $distro
    
}

main
