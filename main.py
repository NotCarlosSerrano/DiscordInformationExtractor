import json
import os
import shutil
import csv
import sys
from PIL import Image
import requests
from datetime import datetime

FOLDER_NAME = 'test3'
PACKAGE_PATH = ''


# Clase gestionar la lista
class user:
    def __init__(self, name, guid):
        self.name = name
        self.guid = guid

def createDir(directoryName):
    dir_name = FOLDER_NAME + '/' + directoryName
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

def deleteDir():
    if os.path.isdir(FOLDER_NAME):
        shutil.rmtree(FOLDER_NAME)

def createUserNameDirs():
    for u in listaNombresIds:
        createDir(u.name)

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 90, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def copyCsvFromUsers():
    iteration = 1
    for u in listaNombresIds:
        directoryName = f'{PACKAGE_PATH}\messages\c' + u.guid
        if os.path.isdir(directoryName):
            # print('Existe la carpeta para el usuario: ' + u.name)
            folderDes = FOLDER_NAME + '/' + u.name + '/messages.csv'
            directoryName = directoryName + '\messages.csv'
            shutil.copyfile(directoryName, folderDes)
            # print('Copiado en: ' + folderDes)
        printProgressBar(iteration, len(listaNombresIds), suffix = 'Saving CSV\'s')
        iteration += 1
    
def getImagesFromUsers():
    test = 1
    for u in listaNombresIds:
        directoryName = f'{PACKAGE_PATH}\messages\c' + u.guid + '\messages.csv'
        with open(directoryName, encoding="utf8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            numberCounter = 0
            for row in csv_reader:
                # Attachments
                attachmentName = row[3]
                if attachmentName != "":
                    if ".png" in attachmentName:
                        try:
                            im = Image.open(requests.get(attachmentName, stream=True).raw)
                            im.save(FOLDER_NAME + '/' + u.name + '/imagen' + str(numberCounter) + '.png', 'PNG')
                            # print(f'Imagen {numberCounter} guardada')
                            numberCounter += 1
                        except:
                            continue
                # Mensajes
                message = str(row[2]).encode(encoding='UTF-8',errors='strict')
                time = str(row[1])
                # Creamos el fichero de los mensajes
                message = message.decode('utf-8', 'strict')
                if message != "" and not message.isspace() and time != "Timestamp":
                    time = time.split(".")[0].replace("+00:00", "")
                    time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                    time = time.strftime("%d/%m/%Y %H:%M:%S")
                    f = open(FOLDER_NAME + '/' + u.name + '/mensajes.txt', "a", encoding='UTF-8')
                    f.write(f"{str(time)}: {str(message)}\n")
                    f.close()
        printProgressBar(test, len(listaNombresIds), suffix = f'Downloading images')
        test += 1

def deleteCsvFromUsers(): 
    for u in listaNombresIds:
        directoryName = FOLDER_NAME + '/' + u.name + '/messages.csv'
        if os.path.isfile(directoryName):
            os.remove(FOLDER_NAME)

def selectPackagePath():
    global PACKAGE_PATH
    print('Insert the path to the package folder: ')
    is_valid_path = False
    # Mientras no nos dé un path correcto no lo validamos
    while not is_valid_path:
        selected_path = input()

        # Si la ruta proporcionada no tiene el package incluído se añade
        if not 'package' in selected_path and len(selected_path) > 0:
            if not selected_path[-1] in ['\\', '/']:
                selected_path += '\\' + 'package\\'
            else:
                selected_path += 'package'
            
        if os.path.isdir(selected_path):
            PACKAGE_PATH = selected_path
            is_valid_path = True
        else:
            print('The path is invalid')

if __name__ == '__main__':

    # Primero necesitamos el path de la carpeta package
    selectPackagePath()
    
    # Cargamos el fichero index.json
    jsonFile = open(f"{PACKAGE_PATH}\\messages\\index.json",)

    # Lo convertimos a JSON
    dataJsonFile = json.load(jsonFile)

    listaNombresIds = []

    ################################################################################################

    # Eliminamos todo lo de la carpeta
    # deleteDir() # TODO MIRAR ESTO ANTES

    # Metemos todos los usuarios en una lista del json
    contadorNombresRepes = 0
    for i in dataJsonFile:
        if "Direct Message with" in str(dataJsonFile[i]):
            alphanumeric = ""
            userName = dataJsonFile[i].split("Direct Message with ")[1]
            for character in userName.split('#')[0]:
                if character.isalnum():
                    alphanumeric += character
            userName = alphanumeric
            newUser = user(str(userName), str(i))
            listaNombresIds.append(newUser)
        else:
            if dataJsonFile[i] != None:
                alphanumeric = ""
                userName = str(dataJsonFile[i])
                userName += str(contadorNombresRepes)
                for character in userName:
                    if character.isalnum():
                        alphanumeric += character           
                userName = alphanumeric
                newUser = user(str(userName), str(i))
                listaNombresIds.append(newUser)
        contadorNombresRepes += 1


    # Creamos las carpetas de los usuarios
    createUserNameDirs()

    # Copiar archivo CSV en cada carpeta
    copyCsvFromUsers()

    # Guardamos las imagenes de los chats en sus carpetas
    downloadImages = input('Do you want to download the imges (Y/N)')
    if any(ele in downloadImages for ele in ['Y', 'y', 'yes']):
        getImagesFromUsers()

    # TODO NO FUNCIONA
    # deleteCsvFromUsers()

    jsonFile.close()