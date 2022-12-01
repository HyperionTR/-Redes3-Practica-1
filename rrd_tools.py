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

class RRDTools:
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

	def createNetworkRRD( self, hostname: str ):
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
							"RRA:AVERAGE:0.4:10:500",
							"RRA:AVERAGE:0.4:10:500",
							"RRA:AVERAGE:0.4:10:500",
							# RRA para ip 
							"RRA:AVERAGE:0.4:10:500",
							"RRA:AVERAGE:0.4:10:500",
							"RRA:AVERAGE:0.4:10:500",
							# RRA para icmp
							"RRA:AVERAGE:0.4:10:500",
							# RRA para segmentos
							"RRA:AVERAGE:0.4:10:500",
							# RRA para datagramas
							"RRA:AVERAGE:0.4:10:500",)

		if ret:
			print (rrdtool.error())

	def updateNetworkRRD( self, hostname: str, tiempo_inicial: int, tiempo_final: int ):
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
		self.last_active_unicast_int_1 = unicast_active_ints[0]
		self.last_active_unicast_int_2 = unicast_active_ints[1]
		self.last_active_unicast_int_3 = unicast_active_ints[2]

		self.last_active_ip_int_1 = ip_active_ints[0]
		self.last_active_ip_int_2 = ip_active_ints[1]
		self.last_active_ip_int_3 = ip_active_ints[2]

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
								"--template", "int_1_unicast:int_2_unicast:int_3_unicast:int_1_ip:int_2_ip:int_3_ip:icmp:segmentos:datagramas",
								f"N:{unicast_total[0]}:{unicast_total[1]}:{unicast_total[2]}"+
								f":{ip_total[0]}:{ip_total[1]}:{ip_total[2]}"+
								f":{icmp_total}:{segmentos_total}:{datagramas_total}"
			)
			# rrdtool.dump(f"{scriptParentDir}/database/{hostname}_packets.rrd", f"{scriptParentDir}/database/{hostname}_packets.xml")
			if ret:
				print (rrdtool.error())

			seconds -= 1
			time.sleep(1)


	def graphNetworkRRD( self, hostname: str, tiempo_inicial: int, tiempo_final: int ):
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
			f"LINE2:paq_int_1#00BBAA:{self.last_active_unicast_int_1.replace(':','-')}",
			f"LINE2:paq_int_2#bb5a00:{self.last_active_unicast_int_2.replace(':','-')}",
			f"LINE2:paq_int_3#bb0009:{self.last_active_unicast_int_3.replace(':','-')}"
		)

		ret = rrdtool.graph(
			f"{scriptParentDir}/images/{hostname}_ip.png",
			"--start", str(int(tiempo_inicial)),
			"--end", str(int(tiempo_final)),
			# Reosolución de los datos de la gráfica
			"--step", "5",
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
			f"LINE2:paq_int_1#00AABB:{self.last_active_ip_int_1.replace(':','-')}",
			f"LINE2:paq_int_2#bb8f00:{self.last_active_ip_int_2.replace(':','-')}",
			f"LINE2:paq_int_3#bb0054:{self.last_active_ip_int_3.replace(':','-')}"
		)
		
		ret = rrdtool.graph(
			f"{scriptParentDir}/images/{hostname}_icmp.png",
			"--start", str(int(tiempo_inicial)),
			"--end", str(int(tiempo_final)),
			# Reosolución de los datos de la gráfica
			"--step", "5",
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
			"--step", "5",
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
			"--step", "5",
			# Dimensiones de la gráfica
			"--width", "800",
			"--height", "200",
			# Titulo de la gráfica
			"--title", "Datagramas UDP recibidos",
			"--vertical-label", "Paquetes/s",
			# Definimos los datos que se graficaran
			f"DEF:Paquetes={scriptParentDir}/database/{hostname}_packets.rrd:datagramas:AVERAGE",
			"LINE3:Paquetes#ff3c1e:Paquetes"
		)

		### Calculadora para colores complementarios :D https://www.sessions.edu/color-calculator/ ###

		print(f"Todas las gráficas ha sido creadas :D!!")

	##########################################################################
	# Adminstración de rendimiento
	##########################################################################
	
	def createPerfRRD( self, hostname: str, ):
		# Creamos una RRD para al menos 4 nucleos del procesador
		err = rrdtool.create(
			f"{scriptParentDir}/database/rrd_perf_{hostname}.rrd",
			"--start",'N',
			"--step",'5',
			# Creamos los Datasource como GAUGE para almacenar el dato sin procesar
			"DS:CPUcore1:GAUGE:120:0:100",
			"DS:CPUcore2:GAUGE:120:0:100",
			"DS:CPUcore3:GAUGE:120:0:100",
			"DS:CPUcore4:GAUGE:120:0:100",
			"DS:RAMusage:GAUGE:120:0:U",
			"DS:NETusage:COUNTER:120:U:U",
			# Y almacenamos unicamente el último dato obtenido
			# que se almacena cada "step" (5 segundos)
			"RRA:AVERAGE:0.5:1:100",
			"RRA:AVERAGE:0.5:1:100",
			"RRA:AVERAGE:0.5:1:100",
			"RRA:AVERAGE:0.5:1:100",
			"RRA:AVERAGE:0.5:1:100",
			"RRA:AVERAGE:0.5:1:100"
		)

		if (err):
			print("Error al crear la RRD de rendimiento: ", err)

	def updatePerfRRD( self, hostname: str ):
		"Función que actualiza constantemente la RRd. Se ejecutará en un Thread diferente"
		datosHost = obtenerDatosHost(hostname)
		carga_CPU = [0,0,0,0]
		# Obtenemos el uso de CPU
		# en caso de error, simplemente ponemos 0
		for i in range( 0, 3 ):
			try:
				carga_CPU[i] = int(consultaSNMP(datosHost["comunidad"], datosHost["ip"], f'1.3.6.1.2.1.25.3.3.1.2.{int(INTEL_CPU_CORE_START) + i}'))
			except Exception as ex:
				print("Error al obtener el uso de CPU: ", ex)
				carga_CPU[i] = 0

		# Obtenemos el uso de RAM
		carga_RAM = int(consultaSNMP(datosHost["comunidad"], datosHost["ip"], f"{HR_STORAGE_USAGE_OID}.{HR_PHYS_RAM_INDEX}"))
		# Obtenemos la memoria SWAP y CAche para no tomarla en cuenta al momento de actualizar la RAM
		carga_RAM_Cache = int(consultaSNMP(datosHost["comunidad"], datosHost["ip"], f"{HR_STORAGE_USAGE_OID}.{HR_CACHED_RAM_INDEX}"))
		carga_RAM_Swap = int(consultaSNMP(datosHost["comunidad"], datosHost["ip"], f"{HR_STORAGE_USAGE_OID}.{HR_SWAP_RAM_INDEX}"))
		# Hacemos la resta
		carga_RAM = carga_RAM - carga_RAM_Cache - carga_RAM_Swap

		# Actualizamos la RRD con los datos obtenidos
		err = rrdtool.update(
			f"{scriptParentDir}/database/rrd_perf_{hostname}.rrd",
			"--template", "CPUcore1:CPUcore2:CPUcore3:CPUcore4:RAMusage",
			f"N:{carga_CPU[0]}:{carga_CPU[1]}:{carga_CPU[2]}:{carga_CPU[3]}:{carga_RAM}"
		)

		rrdtool.dump( f"{scriptParentDir}/database/rrd_perf_{hostname}.rrd", f"{scriptParentDir}/database/rrd_perf_{hostname}.xml" )

		if (err):
			raise Exception("Error al actualizar la RRD de rendimiento: ", err)

	def monitorAndGraphPerf( self, hostname: str ):
		"""Actualiza la RRD en un thread diferente y envía un correo de alerta
		en caso de que el uso de CPU o RAM supere algun umbral"""
		
		# Importamos las librerias utilizadas unicamente por esta función
		import threading
		import smtplib
		from email.mime.text import MIMEText
		from email.mime.image import MIMEImage
		from email.mime.multipart import MIMEMultipart

		# Guardamos el tiempo desde que se envió el ultimo correo
		ultimo_correo = 0;

		def generarGrafica(ultima_lectura: int, total_ram: int):
			tiempo_final = int(ultima_lectura)
			tiempo_inicial = tiempo_final - 60 * 3

			ret_ram = rrdtool.graph(
				f"{scriptParentDir}/images/{hostname}_ram.png",
				"--start", str(int(tiempo_inicial)),
				"--end", str(int(tiempo_final)),
				"--lower-limit", "0",
				"--upper-limit", "100",
				"--vertical-label", "Porcentaje de uso de RAM",
				"--title", "Uso de RAM",
				f"DEF:RAM={scriptParentDir}/database/rrd_perf_{hostname}.rrd:RAMusage:LAST",
				f"CDEF:RAMporc=RAM,{total_ram},/,100,*",
				# Obtenemos los datos mayores al 70% de uso de RAM
				f"CDEF:UmbralRAMporc=RAMporc,70,GT,RAMporc,0,IF",
				"HRULE:70#ff0000:Umbral de alerta",
				"AREA:RAMporc#00ff00:Memoria RAM",
				"AREA:UmbralRAMporc#cfbb11:RAM Mayor al 70%",
			)

			ret = rrdtool.graphv(
				f"{scriptParentDir}/images/{hostname}_perf.png",
				"--start",str(tiempo_inicial),
				"--end",str(tiempo_final),
				"--vertical-label=Cpu load",
				'--lower-limit', '0',
				'--upper-limit', '100',
				"--title=Carga del CPU del agente Usando SNMP y RRDtools \n Detección de umbrales",
				f"DEF:cargaCPU1={scriptParentDir}/database/rrd_perf_{hostname}.rrd:CPUcore1:LAST",
				f"DEF:cargaCPU2={scriptParentDir}/database/rrd_perf_{hostname}.rrd:CPUcore2:LAST",
				f"DEF:cargaCPU3={scriptParentDir}/database/rrd_perf_{hostname}.rrd:CPUcore3:LAST",
				f"DEF:cargaCPU4={scriptParentDir}/database/rrd_perf_{hostname}.rrd:CPUcore4:LAST",
					
				"VDEF:cargaMAX1=cargaCPU1,MAXIMUM",
				"VDEF:cargaMAX2=cargaCPU2,MAXIMUM",
				"VDEF:cargaMAX3=cargaCPU3,MAXIMUM",
				"VDEF:cargaMAX4=cargaCPU4,MAXIMUM",

				"VDEF:cargaMIN1=cargaCPU1,MINIMUM",
				"VDEF:cargaMIN2=cargaCPU2,MINIMUM",
				"VDEF:cargaMIN3=cargaCPU3,MINIMUM",
				"VDEF:cargaMIN4=cargaCPU4,MINIMUM",

				"CDEF:umbral85_c1=cargaCPU1,85,LT,0,cargaCPU1,IF",
				"CDEF:umbral85_c2=cargaCPU2,85,LT,0,cargaCPU2,IF",
				"CDEF:umbral85_c3=cargaCPU3,85,LT,0,cargaCPU3,IF",
				"CDEF:umbral85_c4=cargaCPU4,85,LT,0,cargaCPU4,IF",
				
				"LINE2:cargaCPU1#00FF00:Carga del Core 1",
				"LINE2:cargaCPU2#00CC00:Carga del Core 2",
				"LINE2:cargaCPU3#009900:Carga del Core 3",
				"LINE2:cargaCPU4#007700:Carga del Core 4",

				"LINE2:umbral85_c1#FF9F00:Carga Core 1 mayor de 85",
				"LINE2:umbral85_c2#CC9F00:Carga Core 2 mayor de 85",
				"LINE2:umbral85_c3#999F00:Carga Core 3 mayor de 85",
				"LINE2:umbral85_c4#779F00:Carga Core 4 mayor de 85",

				"HRULE:85#FF0000:Umbral  85%",

				"GPRINT:cargaMIN1:%6.2lf %SMIN",
				"GPRINT:cargaMIN2:%6.2lf %SMIN",
				"GPRINT:cargaMIN3:%6.2lf %SMIN",
				"GPRINT:cargaMIN4:%6.2lf %SMIN")
			return ret

		def enviarCorreo( hostname: str, cuerpo: str, remitente: str, destino: str, servidorSMTP: str ):
			"""Envía un correo de alerta al administrador"""
			# Creamos el objeto mensaje
			mensaje = MIMEMultipart()
			texto = MIMEText(cuerpo)
			mensaje['From'] = remitente
			mensaje['To'] = destino
			mensaje['Subject'] = f"Alerta de rendimiento en {hostname}"
			# Adjuntamos la imagen
			imagen = MIMEImage(open(f"{scriptParentDir}/images/{hostname}_perf.png", 'rb').read())
			mensaje.attach(texto)
			mensaje.attach(imagen)
			# Enviamos el correo
			s = smtplib.SMTP(servidorSMTP)
			s.sendmail(remitente, destino, mensaje.as_string())
			s.quit()

		while (1):
			# Actualizamos la RRD
			self.updatePerfRRD( hostname )

			# Definimos los datos para el envío de notificaciones por correo
			remitente = "testSender@example.com"
			destino = "testRecv@example.com"
			servidorSMTP = 'mail.smtpbucket.com:8025'

			# Obtenemos la cantidad total de RAM del host actual
			datosHost = obtenerDatosHost(hostname)
			total_RAM = int(consultaSNMP(datosHost["comunidad"], datosHost["ip"], f"{HR_STORAGE_TOTAL_SIZE_OID}.{HR_PHYS_RAM_INDEX}"))
			
			# Obtenemos los ultimos datos dentro de la RRD
			ultima_actualizacion = rrdtool.lastupdate(f"{scriptParentDir}/database/rrd_perf_{hostname}.rrd")
			timestamp=ultima_actualizacion['date'].timestamp()
			
			dato_CPU=ultima_actualizacion['ds']["CPUcore1"]
			dato_RAM=ultima_actualizacion['ds']["RAMusage"]
			
			print("Ultima acctualizacion de...\n\t> Core 1: ", dato_CPU, "%")
			print("\t> RAM: ", (dato_RAM/total_RAM)*100, "%")
			
			generarGrafica(int(timestamp), total_RAM)
			
			if dato_CPU > 85 or (dato_RAM / total_RAM) * 100 > 80:
				cuerpo_correo = ""
				if ( dato_CPU > 85):
					cuerpo_correo += f"El Core 1 de {hostname} ha superado el umbral de 85% de carga. Actualmente tiene un {dato_CPU}% de carga.\n"
				if ( (dato_RAM / total_RAM) * 100 > 80 ):
					cuerpo_correo += f"La memoria RAM de {hostname} ha superado el umbral del 80% de uso. Actualmente tiene un {(dato_RAM / total_RAM) * 100}% de uso.\n"
				
				print(f"\033[91;1m{cuerpo_correo}\033[0m")

				# Enviamos un correo cada minuto
				if ( ultimo_correo <= 0 ):
					print( "Enviando correo..." )
					enviarCorreo( hostname, cuerpo_correo, remitente, destino, servidorSMTP )
					ultimo_correo = 60

			ultimo_correo = ultimo_correo - 1 if ultimo_correo > 0 else 0

			time.sleep(1)