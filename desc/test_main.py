from multiprocessing.resource_sharer import stop
from re import T
from host_control import *
from snmp import *
from pdf_gen import *
import subprocess

def main():
	# Creamos una entrada de usuario para consultar
	# com = input("Comunidad\n> ")
	# ip = input("IP o hostname\n> ")
	# puerto, version = 161, 1
	# nuevoHost( "comunidadSNMPWin", "192.168.1.73", 161, 1 )
	# nuevoHost( "comunidadSNMP", "localhost", 161, 1 )
	# print( leerHosts() )
	# eliminarHost("einhander")
	# print( leerHosts() )

	# print( ein := multiConsultaSNMP( "comunidadSNMP", "localhost", SYS_CONTACT, SYS_DESCRIPTION, IF_NUMBER_OID, SYS_LOCATION, SYS_NAME) )
	# # print( nani := multiConsultaSNMP( "comunidadSNMPWin", "192.168.1.73", SYS_CONTACT, SYS_DESCRIPTION, IF_NUMBER_OID) )

	# # Obteniendo los logos y sistemas operativos
	# einOs = soHost( ein[1] )
	# einLogo = logoHost( einOs )

	# # naniOs = soHost( nani[1] )
	# # naniLogo = logoHost( naniOs )

	# print(einOs)
	# print(einLogo)
	# # print(naniOs)
	# # print(naniLogo)

	# # Obteniendo el nombre y estado de las interfaces
	# einIf = interfacesHost( "einhander", 5 )
	# # naniIf = interfacesHost( "Nani-PC", nani[2] )
	# for k, v in einIf.items():
	# 	print( f"\x1b[0mIf: {k}" )
	# 	if '1' in v:
	# 		color = "\x1b[92;1m"
	# 	elif '2' in v:
	# 		color = "\x1b[91;1m"
	# 	else:
	# 		color = "\x1b[93;1m"

	# 	print( f"└─ {color}{v}\x1b[0m")

	# print("\n\n")

	pdfgen = ReportGenerator()
	pdfgen.reporteSNMP("einhander")

	# for k, v in naniIf.items():
	# 	print( f"\x1b[0mIf: {k}" )
	# 	if '1' in v:
	# 		color = "\x1b[92;1m"
	# 	elif '2' in v:
	# 		color = "\x1b[91;1m"
	# 	else:
	# 		color = "\x1b[93;1m"

	# 	print( f"└─ {color}{v}\x1b[0m")

if __name__ == "__main__":
	main()


