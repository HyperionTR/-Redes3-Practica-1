import imghdr
from fpdf import *
from host_control import *
import os

UBUNTU_ORANGE = (210, 68, 19)
WINDOWS10_BLUE = (18, 176, 233)
WINDOWS7_GREEN = (138, 185, 0)
LINUX_YELLOW = (222, 178, 2)

class ReportGenerator(FPDF):
	def reporte( self, hostname: str ):
		# Hacemos una prueba de crear PDF's
		# Default A4 con unidades mm
		# Actualizamos la lista de host
		leerHosts()
		# Obtenemos los datos básicos del host
		try:
			host = multiConsultaSNMP ( 
				cfgParser[hostname]["comunidad"], 
				cfgParser[hostname]["ip"],
				SYS_CONTACT,
				SYS_LOCATION,
				SYS_DESCRIPTION,
				IF_NUMBER_OID
			)
		except Exception as e:
			print("Error en la generación del reporte: " + e)
			return

		# Obtenemos los datos de las interfaces y OS
		hostIf = interfacesHost( hostname, 7 )
		hostOS = soHost( host[2] )

		# Definimos el color del texto
		txtColor =  UBUNTU_ORANGE if hostOS == "Ubuntu" else\
					WINDOWS10_BLUE if hostOS == "Windows10" else\
					WINDOWS7_GREEN if hostOS == "Windows7" else\
					LINUX_YELLOW

		self.add_page()
		self.set_font( "Courier", size = 12 )

		self.set_line_width(3)
		self.set_fill_color(0, 0, 0)

		folder = os.path.dirname(os.path.abspath(__file__))
		self.image(f"{folder}/images/{hostOS.lower()}.png", 20, 15, 70)

		self.text( 95, 20+5, "Sistema operativo")
		
		self.set_font( "Courier", style="B", size = 12 )
		self.set_text_color(*txtColor)
		
		self.text( 95, 25+5, f"---> {hostOS}")


		self.set_text_color(0, 0, 0)
		self.set_font( "Courier", size = 12)
		
		self.text( 95, 35+5, "Nombre de Host")
		self.set_font( "Courier", style="B", size = 12 )
		
		self.set_text_color(*txtColor)
		self.text( 95, 40+5, f"---> {hostname}")


		self.set_text_color(0, 0, 0)
		self.set_font( "Courier", size = 12)
		
		self.text( 95, 50+5, "Ubicación del host")
		self.set_font( "Courier", style="B", size = 12 )
		
		self.set_text_color(*txtColor)
		self.text( 95, 55+5, f"---> {host[1]}")
		

		self.set_text_color(0, 0, 0)
		self.set_font( "Courier", size = 12)
		
		self.text( 95, 65+5, "Contacto")
		self.set_font( "Courier", style="B", size = 12 )
		
		self.set_text_color(*txtColor)
		self.text( 95, 70+5, f"---> {host[0]}")
		
		self.line(20, 95, 190, 95)

		self.set_text_color(0, 0, 0)
		self.set_font( "Courier", size = 12)
		self.text( 30, 105, f"Mostrando { 7 if int(host[3]) > 7 else host[3] } de {host[3]} interfaces...")

		self.set_line_width(1)
		ifline = 130
		self.line( 30, ifline - 10, 175,ifline - 10)
		# Mostrando unicamente las primer 5 interfaces
		for k, v in list(hostIf.items())[:7]:
			self.set_text_color(0,0,0)
			self.text( 30+10, ifline, f"{ k[:30] }" + ("..." if len(k) > 20 else ""))
			if '1' in v:
				self.set_text_color(3, 140, 69)
			elif '2' in v:
				self.set_text_color(140, 3, 12)
			else:
				self.set_text_color(163, 137, 3)
			self.text( 95+50, ifline, v)
			self.line( 30, ifline + 8, 175,ifline + 8)
			ifline += 20

		self.output(f"{folder}/report/reporte_{hostname}.pdf")