# -*- coding: utf-8 -*-
import os
import re
import shutil
import statistics
from statistics import mode

from PyPDF2 import PdfFileReader, PdfFileWriter
from pdf2image import convert_from_path

import yolo
import pytesseract
import cv2

textBlocks = []
dictImages = {}
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


# roi = [(0, 0), (2500, 854)]


def findBlockAndLot(path):
    global tesData1

    image = cv2.imread(path)
    tesData = f"{pytesseract.image_to_string(image, config=r'--oem 3 --psm 6')}"
    tesData = tesData.upper()

    image1 = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    cv2.imwrite("111.png", image1)
    tesData1 = f"{pytesseract.image_to_string(image1, config=r'--oem 3 --psm 6')}"
    tesData1 = tesData1.upper()

    print(tesData1)
    lot = ''
    block = ''
    lotFound = False
    blockFound = False

    if (tesData1.__contains__("LOT")):

        if (tesData1.__contains__("LOTS")):
            findBlocks = re.split('LOTS', tesData1)
        else:
            findBlocks = re.split('LOT', tesData1)

        for i in range(1, len(findBlocks)):
            splitData = re.split(',| |:', findBlocks[i])
            for j in range(len(splitData)):
                if (splitData[j] != ''):
                    lot = splitData[j]
                    break

            lot.upper()
            lot = lot.replace("I", "1")
            lot = lot.replace("!", "1")
            lot = lot.replace("S", "5")
            lot = lot.replace("O", "0")
            if (lot.isdigit() == True):
                lotFound = True
                break

    if (lotFound == False and tesData.__contains__("LOT")):

        if (tesData.__contains__("LOTS")):
            findBlocks = re.split('LOTS', tesData)
        else:
            findBlocks = re.split('LOT', tesData)

        for i in range(1, len(findBlocks)):
            splitData = re.split(',| |:', findBlocks[i])
            for j in range(len(splitData)):
                if (splitData[j] != ''):
                    lot = splitData[j]
                    break

            lot.upper()
            lot = lot.replace("I", "1")
            lot = lot.replace("!", "1")
            lot = lot.replace("S", "5")
            lot = lot.replace("O", "0")
            if (lot.isdigit() == True):
                lotFound = True
                break

    if (tesData1.__contains__("BLOCK") or tesData1.__contains__("BLK")):

        if (tesData1.__contains__("BLOCK")):
            findBlocks = re.split('BLOCK', tesData1)
        elif (tesData1.__contains__("BLK")):
            findBlocks = re.split('BLK', tesData1)

        for i in range(1, len(findBlocks)):
            splitData = re.split(',| |:', findBlocks[i])
            for j in range(len(splitData)):
                if (splitData[j] != ''):
                    block = splitData[j]
                    break

            block.upper()
            block = block.replace("I", "1")
            block = block.replace("!", "1")
            block = block.replace("S", "5")
            block = block.replace("O", "0")
            if (block.isdigit() == True):
                blockFound = True
                break

    if (blockFound == False and tesData.__contains__("BLOCK") or tesData.__contains__("BLK")):

        if (tesData.__contains__("BLOCK")):
            findBlocks = re.split('BLOCK', tesData)
        elif (tesData.__contains__("BLK")):
            findBlocks = re.split('BLK', tesData)

        for i in range(1, len(findBlocks)):
            splitData = re.split(',| |:', findBlocks[i])
            for j in range(len(splitData)):
                if (splitData[j] != ''):
                    block = splitData[j]
                    break

            block.upper()
            block = block.replace("I", "1")
            block = block.replace("!", "1")
            block = block.replace("S", "5")
            block = block.replace("O", "0")
            if (block.isdigit() == True):
                blockFound = True
                break

    disallowed_characters = "._!"
    for character in disallowed_characters:
        lot = lot.replace(character, "")
        block = block.replace(character, "")

    # if lot != "":
    #     lotFound = True
    # if block != "":
    #     blockFound = True

    json = {"lot": lot, "lotFound": lotFound, "block": block, "blockFound": blockFound, }
    print(json)

    return json


# directory = "Siteplan images/Pdf2Img"
# for filename in os.listdir(directory):
#     f = os.path.join(directory, filename)
#     if os.path.isfile(f):

#         findBlockAndLot(f)

# findBlockAndLot("Images/SitePlan\sp1.jpg")

def pdf2img(pdfpath):
    save_path = r'SitePlanImages'
    if os.path.exists(save_path):
        shutil.rmtree(save_path)
    os.mkdir(save_path)

    inputpdf = PdfFileReader(open(pdfpath, "rb"))
    output = PdfFileWriter()
    output.addPage(inputpdf.getPage(0))
    with open(save_path + "/firstPage.pdf", "wb") as outputStream:
        output.write(outputStream)

    pages = convert_from_path(save_path + "/firstPage.pdf", 800,
                              poppler_path=r"C:\Users\VRA Laptop 7\Documents\AI_WORKSPACE\poppler-22.04.0\Library\bin",
                              size=7680)
    pages[0].save(save_path + '\\' + str(0) + '.jpg', 'JPEG')
    os.remove(save_path + "/firstPage.pdf")

    findBlockAndLot(save_path + '\\' + str(0) + '.jpg')


pdfPath = "LennarSitePlans/Keesee.pdf"
print(pdfPath)
pdf2img(pdfPath)
