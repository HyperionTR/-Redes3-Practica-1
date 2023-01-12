import ftplib as ftp
import telnetlib as tn
from host_control import scriptParentDir

rcpmenu = """
	1. Crear archivo de configuración inicial
	2. Obtener archivo de configuración inicial
	3. Enviar archivo de configuración inicial
	4. Mostrar lista de archivos
	5. Cambiar router actual
	6. Regresar al menú principal
"""

class RCP:

	current_router = "No router selected"
	user = ""
	password = ""

	def __init__(self, host=current_router,  user="", password=""):
		self.current_router = host
		self.user = user
		self.password = password

	def menu(self):
		print("\n\033[1m-*-*-*-*-*- RCPLive Admin Tools -*-*-*-*-*-\033[0m")
		print("Gateway actual:", self.current_router)

		opt = 0

		while opt != "6":
			print(rcpmenu)
			opt = input("> ")

			if opt == "1":
				confirm = input("Esto copiará la configuración en ejecución, al archivo \033[1;4mstartup-config\033[0m\n¿Deseas continuar? (S/N)\n> ")
				if confirm.lower() == "s":
					# Mandamos los comandos telnet desde enable, hasta copy running-config startup-config
					with tn.Telnet(self.current_router) as tn_con:
						try:
							# Nos logeamos por telnet al router
							tn_con.read_until(b"User:")
							tn_con.write(self.user.encode("ascii") + b"\n")
							tn_con.read_until(b"Password:")
							tn_con.write(self.password.encode("ascii") + b"\n")

							print("\n\033[92;1mConectado exitosamente!\033[0m")

							# Comandos para crear el archivo startup-config
							tn_con.read_until(b">")
							tn_con.write(b"enable\n")
							tn_con.read_until(b"#")
							tn_con.write(b"configure\n")
							tn_con.write(b"copy running-config startup-config\n")
							print(tn_con.read_very_eager().decode("ascii"))

							print("\n\033[92;1mArchivo startup-config creado con éxito!\033[0m")

						except Exception as ex:
							print("\033[91;1mHubo un error durante la conexión...", ex, "\033[0m")
							continue
			elif opt == "2":
				self.get_config()
			elif opt == "3":
				self.send_config()
			elif opt == "4":
				try:
					with ftp.FTP(self.current_router, self.user, self.password) as ftp_con:
						ftp_con.cwd("/")
						ftp_con.dir()
				except Exception as ex:
					print("\033[31;1mHubo un error durante la conexión...", ex, "\033[0m")
			elif opt == "5":
				new_router = ""
				while new_router == "":
					new_router = input("Gateway IP > ")

					if new_router == "":
						print("Por favor, ingresa una IP válida")
						continue
				
					new_login = input("Login > ")
					new_pass = input("Contraseña > ")
					
				self.current_router = new_router
				self.user = new_login
				self.password = new_pass

		return

	def get_config(self):
		"""Obtiene el archivo startup config mediante FTP del router actual"""
		try:
			with ftp.FTP(self.current_router, self.user, self.password) as ftp_con:
				with open(f"{scriptParentDir}/rcp_files/{self.current_router}_startup-config", "wb") as f:
					try:
						ftp_con.cwd("/")
						ftp_con.retrbinary("RETR startup-config", f.write)
					except Exception as ex:
						print("\033[31;1mHubo un error durante la transferencia...", ex, "\033[0m")
		except Exception as ex:
			print("\033[31;1mHubo un error durante la conexión...", ex, "\033[0m")
	
	def send_config(self):
		"""Envía el archivo startup config mediante FTP al router actual"""
		try:
			with ftp.FTP(self.current_router, self.user, self.password) as ftp_con:
				with open(f"{scriptParentDir}/rcp_files/{self.current_router}_startup-config", "rb") as f:
					try:
						ftp_con.cwd("/")
						ftp_con.storbinary("STOR startup-config", f)
					except Exception as ex:
						print("\033[31;1mHubo un error durante la transferencia...", ex, "\033[0m")
		except Exception as ex:
			print("\033[31;1mHubo un error durante la conexión...", ex, "\033[0m")

		
