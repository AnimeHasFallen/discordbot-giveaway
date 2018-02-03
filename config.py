import configparser

config = configparser.ConfigParser()

config.read('config.ini')

token = config['SETTINGS']['token'].strip()
modrole = config['SETTINGS']['modrole'].strip()
prefix = config['SETTINGS']['prefix'].strip()
riggers = config['SETTINGS']['riggers'].split(",")
dmAllowed = config['SETTINGS']['dmAllowed'].split(",")

try:
	riggers.remove("")
except:
	pass
	
try:
	dmAllowed.remove("")
except:
	pass
