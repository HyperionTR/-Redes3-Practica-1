import configparser as cfp
from shutil import ExecError
import subprocess
from snmp import *
from typing import Dict, List
import os

# Directorio pare de los archivos guardados
scriptParentDir = os.path.dirname( os.path.abspath(__file__) )

# INI config parser
cfgParser = cfp.ConfigParser()
# Leer por primera vez los host
cfgParser.read(f"{scriptParentDir}/hosts.ini")

def nuevoHost( comunidad: str, ip: str, puerto: int, version: int ):
	
	# Verificamos que el host no esté ya registrado
	regHosts = cfgParser.sections()
	for h in regHosts:
		if ip == cfgParser[h]["ip"]:
			print(f"\n\x1b[1;93mEl host {h} ya está registrado!\x1b[0m")
			return
	del regHosts

	# Registramos un nuevo host
	try:
		host = consultaSNMP( comunidad, ip, *SYS_NAME )

		if host in cfgParser.sections():
			print(f"\n\x1b[1;93mEl host {host} ya está registrado!\x1b[0m")
			return

		print(f"\n\x1b[1;32m{host} encontrado con éxito!\x1b[0m")
		cfgParser[host] = {
			"Comunidad": comunidad,
			"IP": ip,
			"Puerto": puerto,
			"Version": version
		}

		# Creamos el archivo de configuración si no existe
		try:
			hosts = open(f"{scriptParentDir}/hosts.ini", "w")
		except:
			hosts = open(f"{scriptParentDir}/hosts.ini", "x")
		# Y guardamos elhost neuvo
		cfgParser.write(hosts)
		hosts.close()
	except Exception as e:
		print(f"\n\x1b[91;1mProblema de conexión con el host...\n└─ {e}\x1b[0m")

# Retorna la lista de hosts registrados
def leerHosts() -> List[str]:
	cfgParser.read(f"{scriptParentDir}/hosts.ini")
	return cfgParser.sections()

def obtenerDatosHost( hostname: str ) -> Dict[str, str]:
	"""Devuelve un diccionario con los datos del host"""
	return {
		"nombre": hostname,
		"comunidad": cfgParser[hostname]["comunidad"],
		"ip": cfgParser[hostname]["ip"],
		"puerto": cfgParser[hostname]["puerto"],
		"version": cfgParser[hostname]["version"]
	}

# Elimina un solo host registrado
def eliminarHost( hostname: str ):
	cfgParser.remove_section(hostname)
	with open(f"{scriptParentDir}/hosts.ini", "w") as h:
		cfgParser.write(h)

# Recibe la cadena sysDescr de una consula SNMP y retorna una cadena indicando el SO
def soHost( sysDescr: str ) -> str:
	lowerDesc = sysDescr.lower()
	if "ubuntu" in lowerDesc:
		os = "Ubuntu"
	elif "windows" in lowerDesc:
		if "version 6.1" in lowerDesc:
			os = "Windows7"
		else:
			os = "Windows10"
	else:
		os = "Linux"
	return os

# Usamos neofeth para obtener un logo en ASCII-art
def logoHost( osName: str ) -> str:
	return subprocess.run( ["neofetch", "-L", "--ascii_distro", osName], stdout=subprocess.PIPE ).stdout.decode("ASCII")

def numeroInterfaces( hostname: str ) -> int:
	"""Devuelve la cantidad de interfaces que tiene un determinado host"""
	return int( consultaSNMP( cfgParser[hostname]["comunidad"], cfgParser[hostname]["ip"], IF_NUMBER_OID ) )

# Retorna el nombre de cada interfáz, junto a su estado administrativo
def interfacesHost( hostname: str, ifNumber: int ) -> Dict[str, str]:
	leerHosts()
	comunidad = cfgParser[hostname]["comunidad"]
	ip = cfgParser[hostname]["ip"]
	interfaces = {}

	# Version final
	for i in range( 1, int(ifNumber) + 1 ):
		# Si no podemos encontrar el objeto, continuamos al siguiente
		try:
			# Buscamos el nombre de la interfáz
			cons = consultaSNMP( comunidad, ip, IF_DESCR_OID+f".{i}")
		except:
			continue
		
		# Si está en hex, viene de windows, codificado con "windows-1252"
		if cons.startswith("0x"):
			ifName = bytes.fromhex(cons[2:]).decode("windows-1252")
		else:
			ifName = cons

		try:
			# Aquí uso la morsa := para crear y usar adm al mismo tiempo
			# y no consultar 2 veces el estado de la interfáz
			interfaces[ifName] = "Up (1)" if (adm := consultaSNMP( comunidad, ip, IF_ADMSTAT_OID+f".{i}")) == '1' else\
								 "Down (2)" if adm == '2' else\
								 "Testing (3)"
			# Ya luego no te necesito, gracias
			del adm
		except:
			continue;
		
	return interfaces;

# Muestra y retorna la lista de hosts
def mostrarHosts() -> List[str]:
	
	hosts = leerHosts()

	if len(hosts) == 0:
		return hosts
	else:	
		print(f"\x1b[1mHosts actualmente registrados: \x1b[0m")
		for i, h in enumerate(hosts):
			print(f"{i} -> {h}")
	
	return hosts

def ordenarInterfacesPorValor( hostname: str, ifNumber: int, valueOID ):
	"""Ordena las interfaces obtenidas según el valor que su respectica OID tenga, como por ejemplo la OID de 'InOctets' """
	comunidad = cfgParser[hostname]["comunidad"]
	ip = cfgParser[hostname]["ip"]
	interfaces = {}
	ordered_dict = {}
	# Version final
	for i in range( 1, int(ifNumber) + 1 ):
		# Si no podemos encontrar el objeto, continuamos al siguiente
		try:
			# Buscamos el nombre de la interfáz concatenando el numero i al OID
			cons = consultaSNMP( comunidad, ip, IF_DESCR_OID+f".{i}")
		except:
			continue
		
		# Si está en hex, viene de windows, codificado con "windows-1252"
		if cons.startswith("0x"):
			ifName = bytes.fromhex(cons[2:]).decode("windows-1252")
		else:
			ifName = cons

		try:
			# Creamos un diccionario a ordenar con el nombre de la interfaz y el valor de la OID respectivo
			# formato:  ifNumber:ifDescr
			interfaces[f"{i}:{ifName}"] = int(consultaSNMP( comunidad, ip, f"{valueOID}.{i}" ))
		except:
			print("xC")
			continue;

	# Usamos una lambda para ordenar el diccionario
	# Ya que items() retorna una lista de tuplas con las llaves en el indice 0 y los valores en el indice 1
	# obtenemos los valores para ordenarlos. Por eso el índice 1
	ordered_dict = dict( sorted( interfaces.items(), key=lambda x: x[1], reverse=True ))
	return ordered_dict;