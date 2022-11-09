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
UNICAST_RECEIVED_OID = "1.3.6.1.2.1.2.2.1.11.1" # Tabular
# IP Receuved datagrams
IP_IF_RECV_OID = "1.3.6.1.2.1.4.31.3.1.3.2.1" # Tabular
# ICMP Echo messages
ICMP_OUT_ECHOS_OID = "1.3.6.1.2.1.5.21.0"
# TCP input segments
TCP_IN_SEGS_OID = "1.3.6.1.2.1.6.10.0"
# UDP Sent datagrams
UDP_OUT_DATAGRAMS_OID = "1.3.6.1.2.1.7.4.0"
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
