# -*- coding: utf-8 -*-
import os
import re
import shutil
import statistics
from statistics import mode

from pdf2image import convert_from_path
import xlwt
from xlwt import Workbook
import yolo
import pytesseract
import cv2

textBlocks = []
dictImages = {}
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

roi = [(0, 0), (2500, 854)]


def findBlockAndLot(path):
    image = cv2.imread(path)
    x, y = roi[0]
    w, h = roi[1]
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 9)
    imageCrop = image[x:x + h, y:y + w]

    tesData = f"{pytesseract.image_to_string(imageCrop)}"
    lot = ''
    block = ''

    if (tesData.__contains__("BLOCK")):
        findBlocks = re.split('BLOCK', tesData)
        splitData = re.split(',| |\n', findBlocks[1])
        if (splitData[0] == ''):
            block = splitData[1]
        else:
            block = splitData[0]
    else:
        tesData1 = f"{pytesseract.image_to_string(image)}"

        if (tesData1.__contains__("BLOCK")):
            findBlocks = re.split('BLOCK', tesData1)

            bno = []

            for i in range(1, len(findBlocks)):
                splitData = re.split(',| |\n', findBlocks[i])
                if (splitData[0] == ''):
                    lot = splitData[1]
                else:
                    lot = splitData[0]
                bno.append(lot)

            block = mode(bno)

    if (tesData.__contains__("LOT")):

        pos = -1
        if (tesData.__contains__("LOTS")):
            findBlocks = re.split('LOTS', tesData)
        else:
            findBlocks = re.split('LOT', tesData)

        splitData = re.split(',| |\n', findBlocks[1])

        if (splitData[0] == ''):
            lot = splitData[1]
        else:
            lot = splitData[0]

        # lot = lot.replace("I", "1")
        # lot = lot.replace("!", "1")
        # lot = lot.replace("S", "5")

        if lot == '' or lot[0].isdigit() == False:
            print("lot not found, trying yolo")
            lots = yolo.fetchLotFromYolo(path)
            if (len(lots) > 1):
                lot = lots[0] + "-" + lots[-1]
            else:
                lot = lots[0]

    else:
        print("lot not found, trying yolo")
        lots = yolo.fetchLotFromYolo(path)
        if (len(lots) > 1):
            lot = lots[0] + "-" + lots[-1]
        else:
            lot = lots[0]

    disallowed_characters = "._!"
    for character in disallowed_characters:
        lot = lot.replace(character, "")
        block = block.replace(character, "")

    lot = lot.replace("I", "1")
    lot = lot.replace("!", "1")
    lot = lot.replace("S", "5")
    block = block.replace("I", "1")
    block = block.replace("!", "1")
    block = block.replace("S", "5")

    lotFound = False
    blockFound = False
    if lot != "":
        lotFound = True
    if block != "":
        blockFound = True

    json = {"lot": lot, "lotFound": lotFound, "block": block, "blockFound": blockFound, }
    print(json)
    return json







directory = os.listdir("Pdf2Img")
wb = Workbook()
sheet1 = wb.add_sheet('Sheet 1')
for i in range(len(directory)):
    f = os.path.join("Pdf2Img/", directory[i])
    if os.path.isfile(f):
        print(f,i)
        resjson = findBlockAndLot(f)

        sheet1.write(i, 0, f)
        sheet1.write(i, 1, str(resjson))

        wb.save('abc.xls')


# findBlockAndLot(directory)



# def pdf2img(pdfpath):
#     print(pdfpath)
#     pages = convert_from_path(pdfpath, 800, poppler_path=r"C:\Users\VRA\Downloads\poppler-0.68.0\bin", size=7680)
#     save_path = r'SitePlanImages'
#     if os.path.exists(save_path):
#         shutil.rmtree(save_path)
#     os.mkdir(save_path)
#     for i in range(len(pages)):
#         pages[i].save(save_path + '\\' + str(i) + '.jpg', 'JPEG')
#         resjson = findBlockAndLot(save_path + '\\' + str(i) + '.jpg')
#
#         wb = Workbook()
#         sheet1 = wb.add_sheet('Sheet 1')
#
#         sheet1.write(i, 0, pdfpath.split("/")[-1])
#         sheet1.write(0, i, resjson)
#
#         wb.save('xlwt example.xls')
#
#
# pdfPath = "Abbott Square Individual Site Plans/245282000912 5860 Newberry Pines Avenue Site Plan.pdf"
# pdf2img(pdfPath)
