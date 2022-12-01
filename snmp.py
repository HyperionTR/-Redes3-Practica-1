from typing import List
from pysnmp.hlapi import *

# Definiendo algunos campos por comodidad
SYS_LOCATION = ('SNMPv2-MIB', 'sysLocation', 0)
SYS_DESCRIPTION = ('SNMPv2-MIB', 'sysDescr', 0)
SYS_NAME = ('SNMPv2-MIB', 'sysName', 0)
SYS_CONTACT = ('SNMPv2-MIB', 'sysContact', 0)
IF_NUMBER_OID = "1.3.6.1.2.1.2.1.0"
IF_ENTRY_OID = "1.3.6.1.2.1.2.2.1"
# Tabular OID's
IF_INDEX_OID = "1.3.6.1.2.1.2.2.1.1"
IF_DESCR_OID = "1.3.6.1.2.1.2.2.1.2"
IF_ADMSTAT_OID = "1.3.6.1.2.1.2.2.1.7"

# Accounting Management OID's
# Unicast recieved PACKETS
UNICAST_IF_RECEIVED_OID = "1.3.6.1.2.1.2.2.1.11" # Tabular
# IP Receuved datagrams
IP_IF_RECV_OID = "1.3.6.1.2.1.4.31.3.1.3.2" # Tabular
# ICMP Echo messages
ICMP_OUT_ECHOS_OID = "1.3.6.1.2.1.5.21.0"
# TCP input segments
TCP_IN_SEGS_OID = "1.3.6.1.2.1.6.10.0"
# UDP Sent datagrams
UDP_OUT_DATAGRAMS_OID = "1.3.6.1.2.1.7.4.0"

# Performance Management OID's
# CPU Usage OID
CPU_USAGE_OID = "1.3.6.1.2.1.25.3.3.1.2"
# Los núcleos del procesador están numerados del 1966_08 al 1966_15 (al menos para los Intel Core i-7)
INTEL_CPU_CORE_START = "196608"
# General Storage OID : 1.3.6.1.2.1.25.2.3
# Table Storage Entry : 1.3.6.1.2.1.25.2.3.1.3
# HR_STORAGE_TYPE_OID : 1.3.6.1.2.1.25.2.3.1.2
# HR_ALLOCATION_UNITS_OID : 1.3.6.1.2.1.25.2.3.1.4
# HR_STORAGE_SIZE_OID : 1.3.6.1.2.1.25.2.3.1.5

# ON LINUX
HR_STORAGE_DESCR_OID = "1.3.6.1.2.1.25.2.3.1.3" # Description of this Index
HR_STORAGE_ALLOC_UNITS_OID = "1.3.6.1.2.1.25.2.3.1.4" # Numbres of bytes considered a unit by SNMP
HR_STORAGE_TOTAL_SIZE_OID = "1.3.6.1.2.1.25.2.3.1.5" # Total size of memory in STORAGE_UNITS
HR_STORAGE_USAGE_OID = "1.3.6.1.2.1.25.2.3.1.6"
HR_PHYS_RAM_INDEX = "1"
HR_SWAP_RAM_INDEX = "10"
HR_CACHED_RAM_INDEX = "7"
HR_BUFFERED_RAM_INDEX = "6"
HR_AVAIL_RAM_INDEX = "11"



# Inicilaizamos el unico motor SNMPv3
engine = SnmpEngine()

# Funcion que regresa unicamente el valor de la consulta SNMP v1
def consultaSNMP( communityName:str, ip:str, *oid ) -> str:
	getIterator = getCmd(
		engine,
		# Comunidad SNMP v1
		CommunityData( communityName, mpModel=0),
		# SNMP over UDP-IPv4
		UdpTransportTarget( (ip, 161) ),
		# MIB Context
		ContextData(),
		# Mira! :D, la destructuración (*) existe!
		ObjectType( ObjectIdentity(*oid) )
	)

	# Destructuramos la tupla retornada
	errorIndication, errorStatus, errorIndex, conResult = next(getIterator)

	if errorIndication != None:
		# print( f"\x1b[91;1mError en la consulta: {errorIndication}\x1b[0m")
		raise Exception(errorIndication)
	elif errorStatus != 0:
		statusString = '\x1b[91;1mError status: %d \n   └─ %s \x1b[0m' % (errorStatus,
		errorIndex and conResult[int(errorIndex) - 1][0] or '?')
		raise Exception(statusString)
	else:
		# Obtenemos el resto de la respuesta desde al signo '='
		# Dividimos la cadena
		replyList = str(conResult[0]).split()
		# Obtenemos el indice del igual
		equalIndex = replyList.index('=')
		# Unimos la cadena restante mediante espacios
		replyStr = " ".join(replyList[equalIndex+1:])
		return replyStr

def multiConsultaSNMP( communityName: str, ip: str, *identidades ) -> List[str]:
	oids = []
	for id in identidades:
		if type(id) is tuple:
			oids.append( ObjectType( ObjectIdentity(*id) ) )
		else:
			oids.append( ObjectType( ObjectIdentity(id) ) )

	getIterator = getCmd(
		engine,
		# Comunidad SNMP v1
		CommunityData( communityName, mpModel=0),
		# SNMP over UDP-IPv4
		UdpTransportTarget( (ip, 161) ),
		# MIB Context
		ContextData(),
		# Destructuramos todas las identidades
		*oids
	)

	replyList = []
	# Destructuramos la tupla retornada
	errorIndication, errorStatus, errorIndex, conResult = next(getIterator)
	for res in conResult:
		if errorIndication != None:
			# print( f"\x1b[91;1mError en la consulta: {errorIndication}\x1b[0m")
			raise Exception(errorIndication)
		elif errorStatus != 0:
			statusString = '\x1b[91;1mError status: %d \n   └─ %s \x1b[0m' % (errorStatus,
			errorIndex and res[int(errorIndex) - 1][0] or '?')
			raise Exception(statusString)
		else:
			# Obtenemos el resto de la respuesta desde al signo '='
			# Dividimos la cadena
			replyStrList = str(res).split()
			# Obtenemos el indice del igual
			equalIndex = replyStrList.index('=')
			# Unimos la cadena restante mediante espacios
			replyStr = " ".join(replyStrList[equalIndex+1:])
			replyList.append(replyStr)
	return replyList
