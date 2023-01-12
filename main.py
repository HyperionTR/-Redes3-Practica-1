from host_control import *
from snmp import *
from pdf_gen import *
from rrd_tools import *
from rcp import *

"""Hola desde mi compu remota! :D
"""

inputStr = \
"""
¿Qué deseas hacer?
0 -> Mostrar los hosts registrados
1 -> Registrar un nuevo Host
2 -> Eliminar un host registrado
3 -> Generar un reporte
4 -> Reporte de red RRD
5 -> \033[93;1;7mMonitoreo de rendimiento de host\033[0m
6 -> \033[93;1;7mHerramientas de RCP-Live\033[0m
7 -> Salir
			
> """

def main():
	print("\033[1m-*-*-*-*-*- Py Network Admin System -*-*-*-*-*-\033[0m")
	act = 0
	while int(act) < 7 and int(act) >= 0:

		act = input(inputStr)

		print("-*-*-*-*-*- -*-*-*-*-*-*-*-+-+- -*-*-*-*-*-\n")

		if act == '0':
			if len(mostrarHosts()) == 0:
				print("\x1b[93;1m¡No hay hosts registrados!\x1b[0m")
		elif act == '1':
			print("Ingresa los datos del host... ")
			try:
				com = input("Comunidad\n> ")
				ip = input("IP Local\n> ")
				pu = input("Puerto\n> ")
				ver = input("Version\n> ")
				nuevoHost( com, ip, int(pu), int(ver) )
			except:
				print("\n\x1b[93;1mUno de los datos ingresados, es inválido\x1b[0m")
		elif act == '2':
			hosts = mostrarHosts()	
			
			if len(hosts) != 0 :
				el = input("\nEscribe el indice del host a eliminar\n> ")
				try:
					eliminarHost(hosts[int(el)])
				except IndexError:
					print(f"\n\x1b[91;1mEl host {el} no existe\x1b[0m")
			else :
				print("\x1b[93;1m¡No hay hosts registrados!\x1b[0m")
		elif act == '3':
			hosts = mostrarHosts()	
			
			if len(hosts) != 0 :
				el = input("\nEscribe el índice del host para generar su reporte\n> ")
				try:
					pdf = ReportGenerator()
					pdf.reporteSNMP( hosts[int(el)] )
				except IndexError:
					print(f"\n\x1b[91;1mEl host {el} no existe\x1b[0m")
				finally:
					del pdf
			else :
				print("\x1b[93;1m¡No hay hosts registrados!\x1b[0m")
		elif act == '4':
			hosts = mostrarHosts()	
			
			if len(hosts) != 0:
				try:
					pdf = ReportGenerator()
					rrd = RRDTools()
					el = input("\nEscribe el índice del host para generar su reporte RRD\n> ")
					tiempo_inicial = float(input("¿Desde que momento quieres los datos graficados? (en minutos dese ahora)\n> "))
					tiempo_final = float(input("¿Hasta que momento quieres los datos graficados? (en minutos dese ahora)\n> "))
					rrd.createNetworkRRD(hosts[int(el)])
					rrd.updateNetworkRRD(hosts[int(el)], tiempo_inicial, tiempo_final)
					rrd.graphNetworkRRD(hosts[int(el)], tiempo_inicial, tiempo_final)
					# Generando reporte con las graficas creadas
					print("Generando reporte...")
					pdf.reporteRedRRD( hosts[int(el)] )
				except IndexError as ie:
					print(f"\n\x1b[91;1mEl host {el} no existe\x1b[0m")
				except Exception as ex:
					print(f"Por favor, ingresa datos válidos... Error: {ex}")
				finally:
					del pdf
					del rrd
		elif act == '5':
			hosts = mostrarHosts()
			rrd = RRDTools()

			# try:
			if len(hosts) != 0:
				el = input("\nEscribe el índice del host para monitorear su rendimiento\n> ")
				rrd.createPerfRRD(hosts[int(el)])
				rrd.monitorAndGraphPerf(hosts[int(el)])
			else:
				print("\x1b[93;1m¡No hay hosts registrados!\x1b[0m")
			# except Exception as ex:
			# 	print(f"Hubo algún error ... {ex}")
			# finally:
			# 	del rrd
		elif act == '6':
			
			rcp_obj = None

			gateway = input("¿A que router desear conectarte? (Enter para ninguno)\nGateway IP> ")

			if gateway == "":
				rcp_obj = RCP()
			else:
				login = input("Login > ")
				password = input("Contraseña > ")
				rcp_obj = RCP(gateway, login, password)

			rcp_obj.menu()

		else:
			print("\x1b[94;1;7m¡Hasta luego!\x1b[0m")
		print("\n-*-*-*-*-*- -*-*-*-*-*-*-*-+-+- -*-*-*-*-*-")

if __name__ == "__main__":
	main();
