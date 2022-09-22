from host_control import *
from snmp import *
from pdf_gen import *

inputStr = \
"""
¿Qué deseas hacer?
0 -> Mostrar los hosts registrados
1 -> Registrar un nuevo Host
2 -> Eliminar un host registrado
3 -> Generar un reporte
4 -> Salir
			
> """

def main():
	print("-*-*-*-*-*- Py Report Generator -*-*-*-*-*-")
	act = 0
	while int(act) < 4 and int(act) >= 0:

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
					pdf.reporte( hosts[int(el)] )
				except IndexError:
					print(f"\n\x1b[91;1mEl host {el} no existe\x1b[0m")
				finally:
					del pdf
			else :
				print("\x1b[93;1m¡No hay hosts registrados!\x1b[0m")
		else:
			print("\x1b[94;1;7m¡Hasta luego!\x1b[0m")
		print("\n-*-*-*-*-*- -*-*-*-*-*-*-*-+-+- -*-*-*-*-*-")

if __name__ == "__main__":
	main();