#!/usr/bin/python3.7 -W ignore::DeprecationWarning
# ADRIEN MONTIGNEAUX B3
import string
import sys
import subprocess
import urllib.parse
from random import *
from pymongo import MongoClient
from collections import OrderedDict

database_admin["host"] = sys.argv[0]
database_projet["host"] = sys.argv[0]
database_projet_service["host"] = sys.argv[0]

# On définit ici un dictionnaire pour chaque compte utilisateur qui va être créer

database_admin = {
    "host": "",
    "login": "administrateur",
    "password": "",
    "port": "10000",
    "db_name": "admin",
}

database_projet = {
	"host": "",
    "login": "adminprojet",
    "password": "",
    "port": "10000",
    "db_name": "projet",
}

database_projet_service = {
	"host": "",
    "login": "service",
    "password": "",
    "port": "10000",
    "db_name": "projet",
}

# Fonction de génération de mots de passe qui respecte les recommandations ANSI

def generate_password():
	valid_punctuation = "#([-|_^@)=}{]%$*!:/;.,?&<>"
	min_char = 12
	max_char = 20
	allchar = string.ascii_letters + valid_punctuation + string.digits
	password = "".join(choice(allchar) for x in range(randint(min_char, max_char)))
	return password

password = generate_password()
print("##############################################################################################################")
print("Base : admin | utilisateur : admin | mot de passe : ",password," | role : dbOwner\n")
database_admin["password"] = password
subprocess.call(["echo", password ," >> mongo_password.txt"], shell=True)


password_admin_projet = generate_password()
print("Base : projet | utilisateur : adminprojet | mot de passe : ",password_admin_projet," | role : dbAdmin\n")
database_projet["password"] = password_admin_projet
subprocess.call(["echo", password_admin_projet ," >> mongo_password.txt"], shell=True)

password_service_projet = generate_password()
print("Base : projet | utilisateur : service | mot de passe : ",password_service_projet," | role : read")
print("#############################################################################################################")
database_projet_service["password"] = password_service_projet
subprocess.call(["echo", password_service_projet ," >> mongo_password.txt"], shell=True)


###### Connexion à la base Admin et ajout de l'utilisateur administrateur

connection = MongoClient(f'mongodb://{database_admin["host"]}:{database_admin["port"]}/{database_admin["db_name"]}')
db_admin = connection[database_admin["db_name"]]
db_admin.add_user(database_admin["login"], database_admin["password"], roles=[{'role':'dbOwner','db':'admin'}])
connection.close()


###### Tests de connexions avec l'utilisateur administrateur sur la base admin
print("\n")
print(f'Test de connexion à la base de admin avec le compte administrateur et le mot de passe : {database_admin["password"]}')
try:
	connection_admin_password = urllib.parse.quote_plus(database_admin["password"])
	connection = MongoClient(f'mongodb://{database_admin["login"]}:%s@{database_admin["host"]}:{database_admin["port"]}/{database_admin["db_name"]}' % connection_admin_password)
	connection.server_info()
	print("Résultat du test : Succès\n")
	connection.close()
except:
	print("Résultat du test : Erreur\n")

###### ajout des utilisateurs adminprojet et service à la base projet

connection_projet = MongoClient(f'mongodb://{database_projet["host"]}:{database_projet["port"]}/{database_projet["db_name"]}')
db_projet = connection_projet[database_projet["db_name"]]
db_projet.add_user(database_projet["login"], database_projet["password"], roles=[{'role':'dbAdmin','db':'projet'}])
db_projet.add_user(database_projet_service["login"], database_projet_service["password"], roles=[{'role':'read','db':'projet'}])
connection_projet.close()


###### Tests de connexions avec les utilisateurs adminprojet et service à la base projet

print("\n")
print(f'Test de connexion à la base de projet avec le compte adminprojet et le mot de passe : {database_projet["password"]}')
try:
	connection_projet_password = urllib.parse.quote_plus(database_projet["password"])
	connection_projet = MongoClient(f'mongodb://{database_projet["login"]}:%s@{database_projet["host"]}:{database_projet["port"]}/{database_projet["db_name"]}' % connection_projet_password)
	connection_projet.server_info()
	print("Résultat du test : Succès\n")
	connection_projet.close()
except:
	print("Résultat du test : Erreur\n")

connection_projet_service_password = urllib.parse.quote_plus(database_projet_service["password"])
connection_projet_service = MongoClient(f'mongodb://{database_projet_service["login"]}:%s@{database_projet_service["host"]}:{database_projet_service["port"]}/{database_projet_service["db_name"]}' % connection_projet_service_password )
print("\n")
print(f'Test de connexion à la base de projet avec le compte service et le mot de passe : {database_projet_service["password"]}')
try:
	connection_projet_service.server_info()
	print("Résultat du test : Succès\n")
	connection_projet_service.close()
except:
	print("Résultat du test : Erreur\n")

# Modification de la configuration de MongoDB afin d'interdire la connexion à un utilisateur non authentifié

subprocess.call("docker exec -it $(docker ps -qf label=com.docker.swarm.service.name=overlay_mongo1) bash -c \"sed -i -r 's/#auth = true/auth = true/' /etc/mongodb.conf\"", shell=True)
subprocess.call("docker exec -it $(docker ps -qf label=com.docker.swarm.service.name=overlay_mongo1) bash -c \"systemctl restart mongodb\"", shell=True)

# Ici le validateur est défini, il sera ajouter à la collection lors de sa création

validator = {"jsonSchema":{
			"bsonType":"object",
			"required":["label","brand","price","stock"],
			"properties":{
				"label":{
					"bsonType":"string",
					"descripion":"must be a string and is required"
				},
				"brand":{
					"enum":["AMD","Intel","Ballistix","Corsair","Crucial","G.Skill","Gigabyte","HyperX","ASUS","MSI","EVGA","Inno 3D","NVIDIA","PNY","SAPPHIRE","ZOTAC","Seagate Technology","Toshiba","Western Digital","AORUS","Kingston","Samsung","Abkoncore","Be Quiet !","Fractal Design"],
					"description":"must be a brand"
				},
				"price":{
                    "bsonType":"float",
                    "minimum":0,
                    "description":"must be a float and is required"
                },
                "stock":{
                    "bsonType":["double"],
                    "minimum":0,
                    "description":"must be a double and is required"
				},
				"typeSocketCPU":{
					"enum":["AMD AM4","AMD sTR4","Intel 1151","Intel 2011-v3","Intel 2066"],
					"description":"must be a valid type"
				},
				"frequencyCPU":{
					"bsonType":"float",
					"minimum":2.0,
					"maximum":5.0,
					"description":"must be a float between 2.0 and 5.0"
				},
				"busFrequencyCPU":{
					"enum":["DMI 5.0 GT/s","DMI 8.0 GT/s"],
					"description":"must be a valid frequency"
				},
				"coreCPU":{
					"bsonType":"int",
					"minimum":2,
					"maximum":32,
					"description":"must be an int between 2 and 32"
				},
				"capacityRAM":{
					"enum":["0","2","4","8","16","32","64","128"],
					"description":"must be a valid capacity"
				},
				"typeRAM":{
					"enum":["DDR2","DDR3","DDR4"],
					"description":"must be a valid type"
				},
				"frequencyRAM":{
					"enum":["800","1066","1333","1600","1866","2133","2400","2666","2800","3000","3300","3333"],
					"description":"must be a valid frequency"
				},
				"numberBarsRAM":{
					"bsonType":"int",
					"minimum":1,
					"maximum":8
				},
				"chipsetGPU":{
					"enum":["AMD Radeon HD6450","AMD Radeon R5 230","AMD Radeon R7 240","AMD Radeon RX 550","AMD Radeon RX 560","AMD Radeon RX 570","AMD Radeon RX 580","AMD Radeon RX 590","AMD Radeon RX VEGA 56","AMD Radeon RX VEGA 64","AMD Radeon VII","NVIDIA GeForce GT710","NVIDIA GeForce GT730","NVIDIA GeForce GTX 1050","NVIDIA GeForce GTX 1060","NVIDIA GeForce GTX 1070","NVIDIA GeForce GTX 1650","NVIDIA GeForce GTX 1660","NVIDIA GeForce RTX 2060","NVIDIA GeForce RTX 2070","NVIDIA GeForce RTX 2080","NVIDIA GeForce RTX TITAN"],
					"description":"must be a valid chipset"
				},
				"videoMemoryGPU":{
					"enum":["2","1024","2048","3072","4096","6144","8192","11264","16384","24576"],
					"description":"must be a valid quantity in Mb"
				},
				"busGPU":{
					"enum":["PCI Express 2.0 16x","PCI Express 2.0 16x (8x)","PCI Express 2.0 8x","PCI Express 3.0 16x","PCI Express 3.0 1x"],
					"description":"must be a valid bus"
				},
				"videoOutputGPU":{
					"enum":["VGA","DVI","HDMI","DisplayPort"],
					"description":"must be a valid output type"
				},
				"typeHousin":{
					"enum":["Low","Medium","High"],
					"description":"must be a valid type"
				},
				"motherboardSupportHousin":{
					"enum":["ATX","DTX","E-ATX","Micro ATX","Mini DTX"],
					"description":"must be a valid format"
				},
				"materialHousin":{
					"enum":["steel","aluminum","steel/aluminum","plastic"],
					"description":"must be a valid material"
				},
				"connectorsHousin1":{
					"enum":["USB 3.1 x2","USB 3.0 x2", "USB 2.0 x2", "Jack 3,5mm Micro","Jack 3,5mm Stereo","None"],
					"description":"must be a valid connector or nothing"
				},
				"connectorsHousin2":{
					"enum":["USB 3.1 x2","USB 3.0 x2", "USB 2.0 x2", "Jack 3,5mm Micro","Jack 3,5mm Stereo","None"],
					"description":"must be a valid connector or nothing"
				},
				"powerSupply":{
					"bsonType":"int",
					"minimum":270,
					"maximum":1800
				},
				"typeSupply":{
					"enum":["ATX/EPS","Flex ATX","SFX","SFX-L","TFX"],
					"description":"must be a valid type"
				},
				"modularPowerSupply":{
					"enum":["Yes","No"],
					"description":"A supply is modular or not"
				},
				"quietSupply":{
					"enum":["Yes","No"],
					"description":"A supply can be quiet or not"
				},
				"socketCpuMotherboard":{
					"enum":["AMD AM3","AMD AM3+","AMD AM4","AMD sTR4","Intel 1151","Intel 2066"],
					"description":"must be a valid socket"
				},
				"typeMotherboard":{
					"enum":["ATX","E-ATX","Micro ATX","Mini ITX","Mini STX","SSI CEB"],
					"description":"must be a valid type"
				},
				"typeRamMotherboard":{
					"enum":["DDR3","DDR4"],
					"description":"must be a valid type"
				},
				"graphicOutputMotherboard":{
					"enum":["None","PCI Express 2.0 16x","PCI Express 2.0 16x (x4)","PCI Express 3.0 16x","PCI Express 3.0 16x (2x)","PCI Express 3.0 16x (4x)","PCI Express 3.0 16x (8x)"],
					"description":"must be a valid connector"
				},
				"diskOutputMotherboard":{
					"enum":["SATA II","SATA III","M.2 PCI-E","M.2 PCI-E 2.0","M.2 PCI-E 3.0"],
					"description":"must be a valid connector"
				},
				"frequencyRamMotherboard":{
					"enum":["DDR3 1066","DDR3 1333","DDR3 1600","DDR4 1866","DDR4 2133","DDR4 2400","DDR4 2666","DDR4 2800","DDR4 3000","DDR4 3300","DDR4 3333"],
					"description":"must be a valid frequency"
				},
				"capacitySSD":{
					"bsonType":"int",
					"minimum":120,
					"maximum":4096
				},
				"typeSSD":{
					"enum":["2' 1/2","M.2","mSATA"],
					"description":"must be a valid type"
				},
				"outputSSD":{
					"enum":["M.2 PCI-E 2.0 4x","M.2 PCI-E 3.0 2x","M.2 PCI-E 3.0 4x","M.2 SATA 6GB/s","Serial ATA 6GB/s (SATA3)","mSATA 6GB/s (mini-SATA)"],
					"description":"must be a valid connector"
				},
				"capacityHDD":{
					"enum":["1","2","3","4","5","6","8","10","12","14","16"],
					"description":"must be a valid capacity"
				},
				"typeHDD":{
					"enum":["2'1/2","3' 1/2","M.2",],
					"description":"must be a valid type"
				},
				"outputHDD":{
					"enum":["M.2 PCI-E 3.0 4x","SATA 2","SATA 3"],
					"description":"must be a valid connector"
				},
				"speedHDD":{
					"enum":["5400","5700","5900","5940","7200"],
					"description":"must be a valid speed"
				}}}}

# Connexion à la base projet, ajout de la collection products avec le validateur

connection_projet_password = urllib.parse.quote_plus(database_projet["password"])
connection_projet = MongoClient(f'mongodb://{database_projet["login"]}:%s@{database_projet["host"]}:{database_projet["port"]}/{database_projet["db_name"]}' % connection_projet_password)
db_projet = connection_projet[database_projet["db_name"]]
collection = db_projet.create_collection("products")

query =[('collMod','products'),
        ('validator', validator),
        ('validationLevel','moderate')]

query = OrderedDict(query)
db_projet.command(query)
