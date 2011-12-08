#!/usr/bin/python
#
# This program is a VDI solution using the SPICE Protocol
# Copyright (C) 2011  Universidade de Caxias do Sul
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# long with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import MySQLdb
import sys
import os
import socket
import ldap
import ssl
import ldap
import random
import commands                
import time
import signal
import fcntl
import syslog
import subprocess
from ConfigParser import ConfigParser
from threading import Thread

# Config file
filename = '/usr/local/osdvt/server/config/osdvt.conf'
config = ConfigParser()
config.read([filename])

# Config Main
port 			= int(config.get('Main','Port') )
root_dir 		= config.get('Main','MainDir')

# Config Database
dbhost = config.get('Database','DBHost')
dbname = config.get('Database','DBName')
dbuser = config.get('Database','DBUser')
dbpass = config.get('Database','DBPassword')

# Config SSL
certfile = config.get('SSL','CertFile')
keyfile = config.get('SSL','KeyFile')
sslversion = config.get('SSL','Version')

# Config LDAP
LDAPEnabled = config.get('LDAP','Enabled')
ldaphost = "ldap://"+config.get('LDAP','Host')
baseDN = config.get('LDAP','BaseDN')
LdapFilter = config.get('LDAP','Filter')

# Finding KVM binary. RHEL6 puts in "libexec" without $PATH.
if os.path.exists('/usr/bin/qemu-kvm'):
	KVM="/usr/bin/qemu-kvm"
elif os.path.exists('/usr/libexec/qemu-kvm'):
	KVM="/usr/libexec/qemu-kvm"
else:
	syslog.syslog(syslog.LOG_ERR, "OSDVT: qemu-kvm not found. Maybe, you've to install it.")
	signal.signal(signal.SIGTERM, minhas_vms.sigterm_handler, Socket)
	signal.signal(signal.SIGINT, minhas_vms.sigint_handler, Socket)

syslog.syslog("OSDVT: using "+KVM)

class Vms:
	def sigint_handler(self, signal, frame, Socket):

        	self._VarSaida=False
        	sys.exit()

	def sigterm_handler(self, signal, frame, Socket):
        	self._VarSaida=False
        	sys.exit()

	def Monitor(self):
                while self._VarSaida:
			time.sleep(1)
                        for i in commands.getoutput('ls '+root_dir+'/socket').split('\n'):
        			if i:                  
                			if os.system('ps -p $(cat '+root_dir+'/socket/'+i+') -o comm= > /dev/null 2> /dev/null') != 0:
                        			os.system('rm -rf '+root_dir+'/socket/'+i)

	def AuthToken(self, dbhost, dbname, dbuser, dbpass, user, token):
		con = MySQLdb.connect(dbhost, dbuser, dbpass) 
		con.select_db(dbname)
		cursor = con.cursor() 
		cursor.execute("select * from osdvtadmin_user where Name = '" + user + "' and Token = '"+token+"'") 
		rs = cursor.fetchall()
		cursor.close ()
		con.close ()
		if rs:
			return "OK"
		else:
			return "ERR"

	def AuthTokenIp(self, dbhost, dbname, dbuser, dbpass, ip, token):
		con = MySQLdb.connect(dbhost, dbuser, dbpass) 
		con.select_db(dbname)
		cursor = con.cursor() 
		cursor.execute("select * from osdvtadmin_ip where IP = '" + ip + "' and Token = '"+token+"'") 
		rs = cursor.fetchall()
		cursor.close ()
		con.close ()
		if rs:
			return "OK"
		else:
			return "ERR"

	def SetTokenSpice(self, dbhost, dbname, dbuser, dbpass, vmname):
		con = MySQLdb.connect(dbhost, dbuser, dbpass)
                con.select_db(dbname)
                cursor = con.cursor()
		token = hex(random.getrandbits(64))[2:-1]
                sql = "update osdvtadmin_vm,osdvtadmin_spice set osdvtadmin_spice.Token = '"+str(token)+"' where osdvtadmin_spice.id = osdvtadmin_vm.SpicePort_id and osdvtadmin_vm.Name = '" + vmname +"'" 
		try:
			cursor.execute(sql)
		except:
			cursor.close ()
			con.close ()
			return "ERR"

		con.commit() 
		cursor.close ()
		con.close ()
		return str(token)

	def SetTokenAuth(self, dbhost, dbname, dbuser, dbpass, user):
		con = MySQLdb.connect(dbhost, dbuser, dbpass)
                con.select_db(dbname)
                cursor = con.cursor()
		token = hex(random.getrandbits(64))[2:-1]
                sql = "update osdvtadmin_user set Token = '"+str(token)+"' where Name = '" + user +"'" 
		try:
			cursor.execute(sql)
		except:
			cursor.close ()
			con.close ()
			return "ERR"

		con.commit() 
		cursor.close ()
		con.close ()
		return str(token)

	def SetTokenAuthIp(self, dbhost, dbname, dbuser, dbpass, ip):
		con = MySQLdb.connect(dbhost, dbuser, dbpass)
                con.select_db(dbname)
                cursor = con.cursor()
		token = hex(random.getrandbits(64))[2:-1]
                sql = "update osdvtadmin_ip set Token = '"+str(token)+"' where IP = '" + ip +"'" 
		try:
			cursor.execute(sql)
		except:
			cursor.close ()
			con.close ()
			return "ERR"

		con.commit() 
		cursor.close ()
		con.close ()
		return str(token)

	def Auth(self, ldaphost, user, password, baseDN):
		l = ldap.initialize(ldaphost)
		searchScope = ldap.SCOPE_SUBTREE
		retrieveAttributes = ['dn']
		searchFilter = LdapFilter + "=" + user
		if LDAPEnabled == "True":
			try:
				dn = l.search_s(baseDN, searchScope, searchFilter, retrieveAttributes)[0][0]
			except:
				print sys.exc_info()
				return "ERR: Invalid credentials"
	
			try:
				l.simple_bind_s(dn,password)
			except ldap.INVALID_CREDENTIALS:
				return "ERR: Invalid credentials"
		
		return "OK: Auth successful"

	def Kill(self, dbhost, dbname, dbuser, dbpass, vmname):
		if minhas_vms.Status(dbhost, dbname, dbuser, dbpass, vmname):
			con = MySQLdb.connect(dbhost, dbuser, dbpass) 
			con.select_db(dbname)
			cursor = con.cursor() 
			cursor.execute("SELECT osdvtadmin_vm.Name FROM osdvtadmin_vm WHERE Name = '" + vmname + "'")
			rs = cursor.fetchall()
			cursor.close ()
			con.close ()
			if rs:
				pidfile = root_dir + "/socket/" + rs[0][0] + ".pid"
				cmnd = "kill $(cat "+pidfile+")"
				if os.system(cmnd) == 0:
	                        	return "OK: Killed"
	                       	else:  
	                        	return "ERR: Can not kill VM"

	def Status(self, dbhost, dbname, dbuser, dbpass, vmname):
		con = MySQLdb.connect(dbhost, dbuser, dbpass) 
		con.select_db(dbname)
		cursor = con.cursor() 
		cursor.execute("SELECT osdvtadmin_vm.Name FROM osdvtadmin_vm WHERE Name = '" + vmname + "'")
		rs = cursor.fetchall()
		cursor.close ()
		con.close ()
		if rs:
			pidfile = root_dir + "/socket/" + rs[0][0] + ".pid"
			if os.path.isfile(pidfile):
				return "True" 
			else:
				return "False"

	def StatusIp(self, dbhost, dbname, dbuser, dbpass, vmname):
		con = MySQLdb.connect(dbhost, dbuser, dbpass) 
		con.select_db(dbname)
		cursor = con.cursor() 
		cursor.execute("SELECT osdvtadmin_vm.Name FROM osdvtadmin_vm WHERE Name = '" + vmname + "'")
		rs = cursor.fetchall()
		cursor.close ()
		con.close ()
		if rs:
			pidfile = root_dir + "/socket/" + rs[0][0] + ".pid"
			if os.path.isfile(pidfile):
				return "True" 
			else:
				return "False"

	def Connect(self, dbhost, dbname, dbuser, dbpass, vmname):
		con = MySQLdb.connect(dbhost, dbuser, dbpass) 
		con.select_db(dbname)
		cursor = con.cursor() 
		cursor.execute("select osdvtadmin_spice.SpicePort,osdvtadmin_spice.Token from osdvtadmin_spice,osdvtadmin_vm where osdvtadmin_spice.id = osdvtadmin_vm.SpicePort_id and osdvtadmin_vm.Name = '" + vmname +"'")
		rs = cursor.fetchall()
		cursor.close ()
		con.close ()
		return rs

	def Search(self, dbhost, dbname, dbuser, dbpass, user):
		con = MySQLdb.connect(dbhost, dbuser, dbpass) 
		con.select_db(dbname)
		cursor = con.cursor() 

		cursor.execute("SELECT osdvtadmin_vm.Name FROM osdvtadmin_vm_Users, osdvtadmin_vm, osdvtadmin_user WHERE osdvtadmin_vm.id = osdvtadmin_vm_Users.vm_id and osdvtadmin_user.id = osdvtadmin_vm_Users.user_id and osdvtadmin_user.Name = '" + user + "'")


		rs = cursor.fetchall()
		cursor.close ()
		con.close ()
		listavms = "" 
		for i in range(rs.__len__()):
			listavms = rs[i][0] + " " + listavms

		return listavms

	def SearchIp(self, dbhost, dbname, dbuser, dbpass, ip):
		con = MySQLdb.connect(dbhost, dbuser, dbpass) 
		con.select_db(dbname)
		cursor = con.cursor() 

		cursor.execute("SELECT osdvtadmin_vm.Name FROM osdvtadmin_vm_Ips, osdvtadmin_vm, osdvtadmin_ip WHERE osdvtadmin_vm.id = osdvtadmin_vm_Ips.vm_id and osdvtadmin_ip.id = osdvtadmin_vm_Ips.ip_id and osdvtadmin_ip.IP = '" + ip + "'")


		rs = cursor.fetchall()
		cursor.close ()
		con.close ()
		listavms = "" 
		for i in range(rs.__len__()):
			listavms = rs[i][0] + " " + listavms

		return listavms

			
	
	def Start(self, dbhost, dbname, dbuser, dbpass, vmname):
		def AddQemuArgs(key, value):
			qemuargs.append("-"+key)
			if value:	
				qemuargs.append(value)

		def GetVideoPort():
			video_start_port = 5900
			video_end_port = 5999
			findport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			video_port = video_start_port

			while video_port <= video_end_port:
				try:   
					findport.bind(('localhost', video_port))
				except socket.error as e:
					if e.errno == 98:
						if video_port == video_end_port:
							return "ERR",""
						else:  
							video_port = video_port+1
					else:  
						raise
				else:  
					break

                	video_token = hex(random.getrandbits(64))[2:-1]

			con = MySQLdb.connect(dbhost, dbuser, dbpass)
	                con.select_db(dbname)
	                cursor = con.cursor()
	                sql_video_port = "update osdvtadmin_vm set VideoPort = '"+str(video_port)+"' where Name = '" + vmname +"'" 
	                sql_video_token = "update osdvtadmin_vm set VideoToken= '"+str(video_token)+"' where Name = '" + vmname +"'" 
			try:
				cursor.execute(sql_video_port)
				cursor.execute(sql_video_token)
			except:
				cursor.close ()
				con.close ()
				return "ERR",""
	
			con.commit() 
			cursor.close ()

			findport.close()
			return video_port,video_token

		if minhas_vms.Status(dbhost, dbname, dbuser, dbpass, vmname):
			minhas_vms.SetTokenSpice(dbhost, dbname, dbuser, dbpass, vmname)
			con = MySQLdb.connect(dbhost, dbuser, dbpass) 
			con.select_db(dbname)
			cursor = con.cursor() 
			cursor.execute("select * from osdvtadmin_vm where Name = '" + vmname + "'") 
			rs = cursor.fetchall()
			if rs:
				StartId 		= rs[0][0]
				StartName 		= rs[0][1]
				StartDescription 	= rs[0][2]
				StartCore 		= rs[0][3]
				StartSocket 		= rs[0][4]
				StartMemory 		= rs[0][5]
				StartImmutable 		= rs[0][6]
				StartUcsRedirect 	= rs[0][7]
				StartMac 		= rs[0][8]
				StartBridge 		= rs[0][9] 
				StartVideo 		= rs[0][10] 
				StartOsVariant 		= rs[0][11] 
				StartBits 		= rs[0][12] 

				Smp			= int(StartCore)*int(StartSocket)
				qemuargs		= []

				AddQemuArgs("M"		, "pc")
				AddQemuArgs("device"	, "virtio-balloon-pci,id=balloon0,bus=pci.0")
				AddQemuArgs("name"	, StartName)
				AddQemuArgs("smp"	, str(Smp)+",sockets="+str(StartSocket)+",cores="+str(StartCore)+",threads=1")
				AddQemuArgs("m"		, StartMemory)
				AddQemuArgs("net"	, "nic,macaddr="+StartMac+",model=rtl8139")
				AddQemuArgs("net"	, "tap,ifname=tap"+str(StartId)+",script="+root_dir+"/scripts/qemu-ifup.sh,downscript="+root_dir+"/scripts/qemu-ifdown.sh")
				AddQemuArgs("soundhw"	, "ac97")
				AddQemuArgs("monitor"	, "stdio")
				AddQemuArgs("localtime"	, "")
				AddQemuArgs("daemonize"	, "")
				AddQemuArgs("pidfile"	, root_dir + "/socket/" + StartName + ".pid")

				if StartImmutable == 1:
					AddQemuArgs("snapshot", "")

				cursor.execute("select osdvtadmin_vmdisk.Virtio,osdvtadmin_vmdisk.Cdrom,osdvtadmin_vmdisk.boot,osdvtadmin_disk.Path from osdvtadmin_vm, osdvtadmin_disk, osdvtadmin_vmdisk  where osdvtadmin_vm.id= '" + str(StartId) + "' and osdvtadmin_vm.id = osdvtadmin_vmdisk.Vm_id and osdvtadmin_vmdisk.Disk_id = osdvtadmin_disk.id") 
				rs = cursor.fetchall()
				for i in range(rs.__len__()):
					options = "file="+rs[i][3]
					if rs[i][0] == 1: 
						options = options+",if=virtio"
						if rs[i][2] == 1:
							options = options+",boot=on"
					else:
						if rs[i][1] == 1: 
							options = options+",media=cdrom"
							if rs[i][2] == 1:
								AddQemuArgs("boot", "d")

					AddQemuArgs("drive",options)
				
				video_port,video_token = GetVideoPort()

				if video_port == "ERR":
					return "ERR: Can not start VM"
				else:
					print "Port ok %s" % video_port

				
				if StartVideo == 0:
					AddQemuArgs("vga", "qxl")
					AddQemuArgs("spice", "port=%(video_port)s,password=%(video_token)s" % {'video_port': video_port, 'video_token': video_token})

				if StartVideo == 1:
					AddQemuArgs("vga", "cirrus")
					AddQemuArgs("vnc", ":%(video_port)s" % {'video_port': video_port%5900})
		
				print qemuargs

				if subprocess.call([KVM] + qemuargs) == 0:
					return "OK: Started"
				else:
					return "ERR: Can not start VM"

			else:
				return "ERR: Can not find VM"

			cursor.close ()
			con.close ()
		
		

if __name__ == "__main__":
	minhas_vms = Vms()
	minhas_vms._VarSaida=True
	t = Thread(target=minhas_vms.Monitor, kwargs=dict())
	t.start()
	
	Socket = socket.socket ()
	Socket.bind ( ( '', port ) )
	Socket.listen(5)
	if sslversion == 'SSLv1': 
		ssl_type=ssl.PROTOCOL_SSLv1
	elif sslversion == 'SSLv2': 
		ssl_type=ssl.PROTOCOL_SSLv2
	elif sslversion == 'SSLv23': 
		ssl_type=ssl.PROTOCOL_SSLv23
	elif sslversion == 'TLSv1': 
		ssl_type=ssl.PROTOCOL_TLSv1
	

	file_descriptor = Socket.fileno()
	flags = fcntl.fcntl(file_descriptor, fcntl.F_GETFD)
	fcntl.fcntl(file_descriptor, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)
	
	while True:
		newsocket, client = Socket.accept()
		try:
			connstream = ssl.wrap_socket(newsocket,
				server_side=True,
				certfile=certfile,
				keyfile=keyfile,
				ssl_version=ssl_type
				)
			data = connstream.read()	
			if len(data.split()) > 2:
				if data.split()[0] == "AUTH":
					if data.split()[1] == "IP":
						ip = data.split()[2]
						result = minhas_vms.SetTokenAuthIp(dbhost, dbname, dbuser, dbpass, ip)
						if result != "ERR":
							connstream.write("OK: "+result)
						else:
							connstream.write("ERR: Can not set IP token")
					else:
						user = data.split()[1]	
						password = data.split()[2]	
						result = minhas_vms.Auth(ldaphost, user, password, baseDN)
						if result == "OK: Auth successful":
							result = minhas_vms.SetTokenAuth(dbhost, dbname, dbuser, dbpass, user)
							if result != "ERR":
								connstream.write("OK: "+result)
							else:
								connstream.write('ERR: Can not set token')
				        	else:
				                	connstream.write(result)
			
			
				if data.split()[0] == "SEARCH":
					if data.split()[1] == "IP":
	                                        ip = data.split()[2]
	                                        token = data.split()[3]
						result = minhas_vms.AuthTokenIp(dbhost, dbname, dbuser, dbpass, ip, token) 
						if result != "ERR":
							result = minhas_vms.SearchIp(dbhost, dbname, dbuser, dbpass, ip)
	                                                if result:
	                                                        connstream.write(result)
	                                                else:
	                                                        connstream.write('ERR: Can not search')
	                                        else:
	                                                connstream.write('ERR: Can not token')
					else:
						user = data.split()[1]	
						token = data.split()[2]	
						result = minhas_vms.AuthToken(dbhost, dbname, dbuser, dbpass, user, token)
						if result != "ERR":  
							result = minhas_vms.Search(dbhost, dbname, dbuser, dbpass, user)
							if result:
				                		connstream.write(result)
				        		else:
				                		connstream.write('ERR: Can not search')
						else:
							connstream.write('ERR: Can not token')
			
				elif data.split()[0] == "KILL":
	                                if data.split()[1] == "IP":
	                                        vmname = data.split()[2]
	                                        token = data.split()[3]
						result = minhas_vms.AuthTokenIp(dbhost, dbname, dbuser, dbpass, ip, token)
						if result != "ERR":  
							result = minhas_vms.Kill(dbhost, dbname, dbuser, dbpass, vmname)
							if result:
				                		connstream.write(result)
				        		else:
				                		connstream.write('ERR: Can not start')
						else:
							connstream.write('ERR: Can not token')
	
					else:
						vmname = data.split()[1]	
						token = data.split()[2]	
						result = minhas_vms.AuthToken(dbhost, dbname, dbuser, dbpass, user, token)
						if result != "ERR":  
							result = minhas_vms.Kill(dbhost, dbname, dbuser, dbpass, vmname)
							if result:
				                		connstream.write(result)
				        		else:
				                		connstream.write('ERR: Can not start')
						else:
							connstream.write('ERR: Can not token')
			
				elif data.split()[0] == "START":
	                                if data.split()[1] == "IP":
	                                        vmname = data.split()[2]
	                                        token = data.split()[3]
						result = minhas_vms.AuthTokenIp(dbhost, dbname, dbuser, dbpass, ip, token)
						if result != "ERR":  
							#result = minhas_vms.Start(dbhost, dbname, dbuser, dbpass, vmname, video_start_port, video_end_port)
							result = minhas_vms.Start(dbhost, dbname, dbuser, dbpass, vmname)
							if result:
				                		connstream.write(result)
				        		else:
				                		connstream.write('ERR: Can not start')
						else:
							connstream.write('ERR: Can not token')
	
					else:
						vmname = data.split()[1]	
						token = data.split()[2]	
						result = minhas_vms.AuthToken(dbhost, dbname, dbuser, dbpass, user, token)
						if result != "ERR":  
							#result = minhas_vms.Start(dbhost, dbname, dbuser, dbpass, vmname, video_start_port, video_end_port)
							result = minhas_vms.Start(dbhost, dbname, dbuser, dbpass, vmname)
							if result:
				                		connstream.write(result)
				        		else:
				                		connstream.write('ERR: Can not start')
						else:
							connstream.write('ERR: Can not token')
			
				elif data.split()[0] == "STATUS":
					try:
						if data.split()[1] == "IP":
		                                        vmname = data.split()[2]
		                                        token = data.split()[3]
		                                        result = minhas_vms.AuthTokenIp(dbhost, dbname, dbuser, dbpass, ip, token)
							if result != "ERR":
								result = minhas_vms.StatusIp(dbhost, dbname, dbuser, dbpass,  vmname)
		                                                if result:
		                                                        connstream.write(result)
		                                                else:
		                                                        connstream.write('ERR: Can not get status')
							else:
								connstream.write('ERR: Can not token')
		
						else:
							vmname = data.split()[1]	
							token = data.split()[2]	
							result = minhas_vms.AuthToken(dbhost, dbname, dbuser, dbpass, user, token)
							if result != "ERR":  
								result = minhas_vms.Status(dbhost, dbname, dbuser, dbpass, vmname)
								if result:
					                		connstream.write(result)
					        		else:
					                		connstream.write('ERR: Can not get status')
							else:
								connstream.write('ERR: Can not token')
					except:
						connstream.write('ERR: Lost session')
			
				elif data.split()[0] == "CONNECT":
					if data.split()[1] == "IP":
	                                        vmname = data.split()[2]
	                                        token = data.split()[3]
	                                        result = minhas_vms.AuthTokenIp(dbhost, dbname, dbuser, dbpass, ip, token)
	                                        if result != "ERR":
							result = minhas_vms.Connect(dbhost, dbname, dbuser, dbpass, vmname)
	                                                if result:
	                                                        connstream.write(result[0][0]+" "+result[0][1])
	                                                else:
	                                                        Socket.sendto ( 'ERR: Can not connect' )
						else:
							connstream.write('ERR: Can not token')
					else:
						vmname = data.split()[1]	
						token = data.split()[2]	
						result = minhas_vms.AuthToken(dbhost, dbname, dbuser, dbpass, user, token)
						if result != "ERR":  
							result = minhas_vms.Connect(dbhost, dbname, dbuser, dbpass, vmname)
							if result:
				                		connstream.write(result[0][0]+" "+result[0][1])
				        		else:
				                		Socket.sendto ( 'ERR: Can not connect' )
						else:
							connstream.write('ERR: Can not token')
			else:
				connstream.write('ERR: Not enough parameters')	

			connstream.close() 

		except:
			print sys.exc_info()


	signal.signal(signal.SIGTERM, minhas_vms.sigterm_handler, Socket)
	signal.signal(signal.SIGINT, minhas_vms.sigint_handler, Socket)
