# Modulo que tendrá las funciones de Creaar, actualizar y graficar los siguientes datos obtenidos mediante SNMP, usando RRDTools
# 1. Paquetes unicast que ha recibio una interfaz de red
# 2. Paquetes recxibios a protocolos IP
# 3. Mensajes ICMP echo
# 4. Segmentos recibidos
# 5. Datagramas entegaos a usuarios UDP

import rrdtool
from snmp import *
from host_control import *
import time

def createRRD( hostname: str ):
	"""Función que crea un nuevo RRD para el hostname especificado"""
	print("Creando RRD...")
	# Se creara una RRD para cada hostname
	# 1. Paquetes unicast que ha recibido una interfaz de red
	# 2. Paquetes recibidos a protocolos IP
	# 3. Mensajes ICMP echo
	# 4. Segmentos recibidos
	# 5. Datagramas entregados a usuarios UDP

	ret = rrdtool.create(f"{scriptParentDir}/database/{hostname}_packets.rrd",
	                     "--start",'N',
	                    #  "--step",'60',
						 "--step", "5",
						 # Data source con HB de 120 sin maximo ni minimo
	                     "DS:unicast:COUNTER:120:U:U",
	                     "DS:ip:COUNTER:120:U:U",
	                     "DS:icmp:COUNTER:120:U:U",
	                     "DS:segmentos:COUNTER:120:U:U",
	                     "DS:datagramas:COUNTER:120:U:U",
	                     # RRA para unicast
						 "RRA:AVERAGE:0.4:10:100",
						 # RRA para ip 
						 "RRA:AVERAGE:0.4:10:100",
						 # RRA para icmp
						 "RRA:AVERAGE:0.4:10:100",
						 # RRA para segmentos
						 "RRA:AVERAGE:0.4:10:100",
						 # RRA para datagramas
						 "RRA:AVERAGE:0.4:10:100")

	if ret:
		print (rrdtool.error())

def updateRRD( hostname: str ):
	"""Función continua que obtendrá los datos el host mediante SNMP para actualizar su respectiva RRD"""
	print("Obteniendo datos durante 2 minutos...")
	seconds = 120
	hosts = leerHosts()
	while( seconds > 0 ):
		# Mostrando el tiempo transtuccurrido cada 10 segundos
		if (seconds % 10 == 0):
			print(f"Tiempo restante: {seconds} segundos")
		# Recibimos los datos mediante SNMP
		unicast_total = consultaSNMP( cfgParser[hostname]["comunidad"], cfgParser[hostname]["ip"], UNICAST_RECEIVED_OID )
		ip_total = consultaSNMP( cfgParser[hostname]["comunidad"], cfgParser[hostname]["ip"],  IP_IF_RECV_OID)
		icmp_total = consultaSNMP( cfgParser[hostname]["comunidad"], cfgParser[hostname]["ip"], ICMP_OUT_ECHOS_OID )
		segmentos_total = consultaSNMP( cfgParser[hostname]["comunidad"], cfgParser[hostname]["ip"], TCP_IN_SEGS_OID )
		datagramas_total = consultaSNMP( cfgParser[hostname]["comunidad"], cfgParser[hostname]["ip"], UDP_OUT_DATAGRAMS_OID )
		# Actualizamos la RRD
		ret = rrdtool.update(f"{scriptParentDir}/database/{hostname}_packets.rrd",
							"--template", "unicast:ip:icmp:segmentos:datagramas",
							f"N:{unicast_total}:{ip_total}:{icmp_total}:{segmentos_total}:{datagramas_total}")
		if ret:
			print (rrdtool.error())

		seconds -= 1
		time.sleep(1)

def graphRRD( hostname: str, tiempo_inicial: int, tiempo_final: int ):
	print("Las gráficas serán creadas..")
	tiempo_inicial = (time.time()) - tiempo_inicial * 60
	tiempo_final = (time.time()) - tiempo_final * 60
	ret = rrdtool.graph(
		f"{scriptParentDir}/images/{hostname}_unicast.png",
		"--start", str(int(tiempo_inicial)),
		"--end", str(int(tiempo_final)),
		# Reosolución de los datos de la gráfica
		"--step", "10",
		# Dimensiones de la gráfica
		"--width", "800",
		"--height", "200",
		# Titulo de la gráfica
		"--title", "Paquetes Unicast recividos por las diferentes interfaces",
		"--vertical-label", "Paquetes/s",
		# Definimos los datos que se graficaran
		f"DEF:Paquetes={scriptParentDir}/database/{hostname}_packets.rrd:unicast:AVERAGE",
		"LINE3:Paquetes#00BBAA:Interfaz_1"
	)

	ret = rrdtool.graph(
		f"{scriptParentDir}/images/{hostname}_ip.png",
		"--start", str(int(tiempo_inicial)),
		"--end", str(int(tiempo_final)),
		# Reosolución de los datos de la gráfica
		"--step", "10",
		# Dimensiones de la gráfica
		"--width", "800",
		"--height", "200",
		# Titulo de la gráfica
		"--title", "Paquetes recibidos a protocolos IP",
		"--vertical-label", "Paquetes/s",
		# Definimos los datos que se graficaran
		f"DEF:Paquetes={scriptParentDir}/database/{hostname}_packets.rrd:ip:AVERAGE",
		"LINE3:Paquetes#00BBAA:Paquetes"

	)
	
	ret = rrdtool.graph(
		f"{scriptParentDir}/images/{hostname}_icmp.png",
		"--start", str(int(tiempo_inicial)),
		"--end", str(int(tiempo_final)),
		# Reosolución de los datos de la gráfica
		"--step", "10",
		# Dimensiones de la gráfica
		"--width", "800",
		"--height", "200",
		# Titulo de la gráfica
		"--title", "Mensajes ICMP echo",
		"--vertical-label", "Paquetes/s",
		# Definimos los datos que se graficaran
		f"DEF:Paquetes={scriptParentDir}/database/{hostname}_packets.rrd:icmp:AVERAGE",
		"LINE3:Paquetes#00BBAA:Paquetes"

	)

	ret = rrdtool.graph(
		f"{scriptParentDir}/images/{hostname}_segmentos.png",
		"--start", str(int(tiempo_inicial)),
		"--end", str(int(tiempo_final)),
		# Reosolución de los datos de la gráfica
		"--step", "10",
		# Dimensiones de la gráfica
		"--width", "800",
		"--height", "200",
		# Titulo de la gráfica
		"--title", "Segmentos TCP recibidos",
		"--vertical-label", "Paquetes/s",
		# Definimos los datos que se graficaran
		f"DEF:Paquetes={scriptParentDir}/database/{hostname}_packets.rrd:segmentos:AVERAGE",
		"LINE3:Paquetes#00BBAA:Paquetes"

	)

	ret = rrdtool.graph(
		f"{scriptParentDir}/images/{hostname}_datagramas.png",
		"--start", str(int(tiempo_inicial)),
		"--end", str(int(tiempo_final)),
		# Reosolución de los datos de la gráfica
		"--step", "10",
		# Dimensiones de la gráfica
		"--width", "800",
		"--height", "200",
		# Titulo de la gráfica
		"--title", "Segmentos TCP recibidos",
		"--vertical-label", "Segmentos/s",
		# Definimos los datos que se graficaran
		f"DEF:Paquetes={scriptParentDir}/database/{hostname}_packets.rrd:datagramas:AVERAGE",
		"LINE3:Paquetes#00BBAA:Paquetes"

	)
	print(f"Gráfica creada... {ret}")



