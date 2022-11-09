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

# Para evitar tener que re-ordenar, y re-obtener los mismos datos entre distintas funciones
# creamos estar variables globales que guardan las ultimas interfaces ordenadas
last_ordered_unicast_ints = {}
last_ordered_ip_ints = {}

last_active_unicast_int_1 = ""
last_active_unicast_int_2 = ""
last_active_unicast_int_3 = ""

last_active_ip_int_1 = ""
last_active_ip_int_2 = ""
last_active_ip_int_3 = ""

def createRRD( hostname: str ):
	"""Función que crea un nuevo RRD para el hostname especificado, guardando las 3 interfaces con mayor índice de actividad"""
	print("Creando RRD...")
	# Se creara una RRD para cada hostname

	# Se crearan 3 DS para cada mejor interfaz de este tipo
	# -------------------------------------------------------
	# 1. Paquetes unicast que ha recibido una interfaz de red
	# 2. Paquetes recibidos a protocolos IP

	# Solo se hará 1 DS para estos
	# -------------------------------------------------------
	# 3. Mensajes ICMP echo
	# 4. Segmentos recibidos
	# 5. Datagramas entregados a usuarios UDP

	ret = rrdtool.create(f"{scriptParentDir}/database/{hostname}_packets.rrd",
	                     "--start",'N',
	                    #  "--step",'60',
						 "--step", "5",
						 # Data source con HB de 120 sin maximo ni minimo
						 # Data source de paquetes unicast
	                     "DS:int_1_unicast:COUNTER:120:U:U",
	                     "DS:int_2_unicast:COUNTER:120:U:U",
	                     "DS:int_3_unicast:COUNTER:120:U:U",
	                     # Data source de paquetes IP
						 "DS:int_1_ip:COUNTER:120:U:U",
	                     "DS:int_2_ip:COUNTER:120:U:U",
	                     "DS:int_3_ip:COUNTER:120:U:U",
	                     # Data source de mensajes ICMP
						 "DS:icmp:COUNTER:120:U:U",
						 # Data source de segmentos TCP recibidos
						 "DS:segmentos:COUNTER:120:U:U",
						 # Data source de datagramas UDP entregados
						 "DS:datagramas:COUNTER:120:U:U",
	                     # RRA para unicast
						 "RRA:AVERAGE:0.4:10:100",
						 "RRA:AVERAGE:0.4:10:100",
						 "RRA:AVERAGE:0.4:10:100",
						 # RRA para ip 
						 "RRA:AVERAGE:0.4:10:100",
						 "RRA:AVERAGE:0.4:10:100",
						 "RRA:AVERAGE:0.4:10:100",
						 # RRA para icmp
						 "RRA:AVERAGE:0.4:10:100",
						 # RRA para segmentos
						 "RRA:AVERAGE:0.4:10:100",
						 # RRA para datagramas
						 "RRA:AVERAGE:0.4:10:100",)

	if ret:
		print (rrdtool.error())

def updateRRD( hostname: str, tiempo_inicial: int, tiempo_final: int ):
	"""Función continua que obtendrá los datos el host mediante SNMP para actualizar su respectiva RRD"""
	if ( tiempo_inicial <= tiempo_final ):
		raise Exception(f"El tiempo que se graficará no debe ser negativo o cero\n( el rango especificado fué de {tiempo_inicial - tiempo_final = } )")
	
	seconds = (tiempo_inicial - tiempo_final) * 60
	print(f"Obteniendo datos durante {tiempo_inicial - tiempo_final} minutos...")
	hosts = leerHosts()
	
	# Obtenemos los números de las interfaces con mayor actividad, para monitorear el rendimiento de ellas
	ints_unicast = ordenarInterfacesPorValor( hostname, numeroInterfaces(hostname), UNICAST_IF_RECEIVED_OID )
	ints_ip = ordenarInterfacesPorValor( hostname, numeroInterfaces(hostname), IP_IF_RECV_OID )
	
	# Obtenemos solo las primeras 3 interfaces más activas
	unicast_active_ints = list(ints_unicast.keys())[:3]
	ip_active_ints = list(ints_ip.keys())[:3]

	# Obtenemos las OID para adquirir datos de las primeras 3 interfaces con mayor actividad
	# Obtenemos el numero de la interfaz, pues la llave de los diccionarios tiene el formato "ifNum:ifDescr"
	unicast_active_int_1 = f"{UNICAST_IF_RECEIVED_OID}.{unicast_active_ints[0].split(':')[0]}"
	unicast_active_int_2 = f"{UNICAST_IF_RECEIVED_OID}.{unicast_active_ints[1].split(':')[0]}"
	unicast_active_int_3 = f"{UNICAST_IF_RECEIVED_OID}.{unicast_active_ints[2].split(':')[0]}"

	ip_active_int_1 = f"{IP_IF_RECV_OID}.{ip_active_ints[0].split(':')[0]}"
	ip_active_int_2 = f"{IP_IF_RECV_OID}.{ip_active_ints[1].split(':')[0]}"
	ip_active_int_3 = f"{IP_IF_RECV_OID}.{ip_active_ints[2].split(':')[0]}"

	# Guardamos los nombres de las ultimas interfaces más activas
	last_active_unicast_int_1 = unicast_active_ints[0]
	last_active_unicast_int_1 = unicast_active_ints[1]
	last_active_unicast_int_1 = unicast_active_ints[2]

	last_active_ip_int_1 = ip_active_ints[0]
	last_active_ip_int_2 = ip_active_ints[1]
	last_active_ip_int_3 = ip_active_ints[2]

	while( seconds > 0 ):
		# Mostrando el tiempo transtuccurrido cada 10 segundos
		if (seconds % 10 == 0):
			print(f"Tiempo restante: {seconds} segundos")
		# Recibimos los datos mediante SNMP
		unicast_total = multiConsultaSNMP( cfgParser[hostname]["comunidad"], cfgParser[hostname]["ip"], 
			unicast_active_int_1,
			unicast_active_int_2,
			unicast_active_int_3,
		)
		ip_total = multiConsultaSNMP( cfgParser[hostname]["comunidad"], cfgParser[hostname]["ip"], 
			ip_active_int_1,
			ip_active_int_2,
			ip_active_int_3
		)
		icmp_total = consultaSNMP( cfgParser[hostname]["comunidad"], cfgParser[hostname]["ip"], ICMP_OUT_ECHOS_OID )
		segmentos_total = consultaSNMP( cfgParser[hostname]["comunidad"], cfgParser[hostname]["ip"], TCP_IN_SEGS_OID )
		datagramas_total = consultaSNMP( cfgParser[hostname]["comunidad"], cfgParser[hostname]["ip"], UDP_OUT_DATAGRAMS_OID )
		
		# Actualizamos unicamente las interfaces unicast
		ret = rrdtool.update(f"{scriptParentDir}/database/{hostname}_packets.rrd",
							"--template", "int_1_unicast:int_2_unicast:int_3_unicast",
							f"N:{unicast_total[0]}:{unicast_total[1]}:{unicast_total[2]}")
		# Luego, solamente las interfaces IP
		ret = rrdtool.update(f"{scriptParentDir}/database/{hostname}_packets.rrd",
							"--template", "int_1_ip:int_2_ip:int_3_ip",
							f"N:{ip_total[0]}:{ip_total[1]}:{ip_total[2]}")
		# Ahora actualizamos el resto de datos de la RRD
		ret = rrdtool.update(f"{scriptParentDir}/database/{hostname}_packets.rrd",
							"--template", "icmp:segmentos:datagramas",
							f"N:{icmp_total}:{segmentos_total}:{datagramas_total}")
		if ret:
			print (rrdtool.error())

		seconds -= 1
		time.sleep(1)

def graphRRD( hostname: str, tiempo_inicial: int, tiempo_final: int ):
	print("Las gráficas serán creadas..")
	tiempo_inicial = (time.time()) - tiempo_inicial * 60
	tiempo_final = (time.time()) - tiempo_final * 60
	# Obteniendo los nombres de las interfaces graficadas
	unic_if_names = list()
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
		f"DEF:paq_int_1={scriptParentDir}/database/{hostname}_packets.rrd:int_1_unicast:AVERAGE",
		f"DEF:paq_int_2={scriptParentDir}/database/{hostname}_packets.rrd:int_2_unicast:AVERAGE",
		f"DEF:paq_int_3={scriptParentDir}/database/{hostname}_packets.rrd:int_3_unicast:AVERAGE",
		f"LINE2:Paquetes#00BBAA:{last_active_unicast_int_1}"
		f"LINE2:Paquetes#bb5a00:{last_active_unicast_int_2}"
		f"LINE2:Paquetes#bb0009:{last_active_unicast_int_3}"
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
		f"DEF:paq_int_1={scriptParentDir}/database/{hostname}_packets.rrd:int_1_ip:AVERAGE",
		f"DEF:paq_int_2={scriptParentDir}/database/{hostname}_packets.rrd:int_2_ip:AVERAGE",
		f"DEF:paq_int_3={scriptParentDir}/database/{hostname}_packets.rrd:int_3_ip:AVERAGE",
		f"LINE2:Paquetes#00AABB:{last_active_ip_int_1}"
		f"LINE2:Paquetes#bb8f00:{last_active_ip_int_2}"
		f"LINE2:Paquetes#bb0054:{last_active_ip_int_3}"

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
		"LINE3:Paquetes#ff1ebf:Paquetes"

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
		"LINE3:Paquetes#4fff1e:Paquetes"

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
		"LINE3:Paquetes#ff3c1e:Paquetes"
	)

	### Calculadora para colores complementarios :D https://www.sessions.edu/color-calculator/ ###

	print(f"Todas las gráficas ha sido creadas :D!!")


