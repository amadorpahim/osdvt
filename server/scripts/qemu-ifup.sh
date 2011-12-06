#!/bin/bash

BRCTL="/usr/sbin/brctl"
IFCONFIG="/sbin/ifconfig"

DBHost=$(grep DBHost /usr/local/osdvt/server/config/osdvt.conf | cut -d " " -f 3)
DBName=$(grep DBName /usr/local/osdvt/server/config/osdvt.conf | cut -d " " -f 3)
DBUser=$(grep DBUser /usr/local/osdvt/server/config/osdvt.conf | cut -d " " -f 3)
DBPassword=$(grep DBPassword /usr/local/osdvt/server/config/osdvt.conf | cut -d " " -f 3)

VmID=$(echo $1 | sed "s/tap//g")
BRIDGE=$(mysql -s --host=$DBHost --user=$DBUser --password=$DBPassword -e "select osdvtadmin_bridge.Name from osdvtadmin_vm,osdvtadmin_bridge where osdvtadmin_vm.id = $VmID and osdvtadmin_vm.Bridge_id = osdvtadmin_bridge.id" $DBName)

echo "Adding $1 to $BRIDGE..."
$BRCTL addif $BRIDGE $1
echo "Bringing up $1 for bridged mode..."
$IFCONFIG $1 0.0.0.0 promisc up
