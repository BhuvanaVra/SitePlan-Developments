# -*- coding: utf-8 -*-
import os
import re
import shutil

import pytesseract
import cv2
import numpy as np
import xlwt
from pdf2image import convert_from_path
from xlwt import Workbook

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
dictt = {}
elements = ['LOT', 'LIVING AREA', 'PORCH', 'GARAGE', 'COVERED LANAI', 'PATIO', 'POOL AREA', 'CONC. DRIVE',
            'AC CONC PAD', 'SIDEWALK', 'LOT SOD', 'RW SOD', 'LOT OCCUPIED', 'AREA TO IRRIGATE']


def getArea(res):
    pos = -1
    for ele in elements:
        eleFound = False
        if (res.__contains__(ele)) or res.__contains__(ele.replace(' ', '')):
            if res.__contains__(ele):
                pos = res.index(ele)
            elif (res.__contains__(ele.replace(' ', ''))):
                pos = res.index(ele.replace(' ', ''))

            if (ele == 'LOT OCCUPIED' or ele == 'AREA TO IRRIGATE'):
                dictt[ele] = res[pos + 1] + ' %'
            else:
                dictt[ele] = res[pos + 1].strip().split(' ')[0] + ' SQ FT'
            eleFound = True

        else:
            templ = list(filter(lambda x: ele in x, res))
            if not templ:
                item = ele.replace(' ', '')
                templ = list(filter(lambda x: item in x.replace(' ', ''), res))

            new_templ = []
            for t in templ:
                t = re.sub('[^a-zA-Z0-9 \n\.]', '', t)
                new_templ.append(t.strip())
            templ = new_templ
            # print(templ)

            if len(templ) > 0:
                # print(templ[0])
                if (templ[0] == ele or templ[0].replace(' ', '') == ele.replace(' ', '')):
                    # print("if")
                    if res.__contains__(templ[0]):
                        pos = res.index(templ[0])
                    elif (res.__contains__(templ[0].replace(' ', ''))):
                        pos = res.index(templ[0].replace(' ', ''))

                    if ele == 'LOT OCCUPIED' or ele == 'AREA TO IRRIGATE':
                        dictt[ele] = res[pos + 1] + ' %'
                    else:
                        dictt[ele] = res[pos + 1].strip().split(' ')[0] + ' SQ FT'
                    eleFound = True

            if eleFound == False and len(templ) > 0 and len(templ[0].split(ele)) > 0:
                # print("else")
                val = templ[0].split(ele)[-1]

                if ele == 'LOT OCCUPIED' or ele == 'AREA TO IRRIGATE':
                    dictt[ele] = val + ' %'
                else:
                    dictt[ele] = val.strip().split(' ')[0] + ' SQ FT'

            if len(templ) > 0 and len(templ[0].split(ele)) == 0:
                val = templ[0].split(ele)[-1]

                if ele == 'LOT OCCUPIED' or ele == 'AREA TO IRRIGATE':
                    dictt[ele] = val + ' %'
                else:
                    dictt[ele] = val.strip().split(' ')[0] + ' SQ FT'
    return dictt


def getTextRoi(image, pageNum):
    roi = []
    imgCopy = image.copy()
    imgGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (33, 33), 5555, cv2.BORDER_CONSTANT)
    thresh = cv2.threshold(imgBlur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    imgCanny = cv2.Canny(thresh, 1110, 1110)
    kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (88, 10))
    imgDialate = cv2.dilate(imgCanny, kernel1, iterations=1)
    contours, hierarchy = cv2.findContours(imgDialate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    dim = image.shape
    imarea = dim[0] * dim[1]

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if (area > 100000) and (area < imarea * 0.05):
            x, y, w, h = cv2.boundingRect(cnt)
            roi.append(image[y:y + h, x:x + w])
            cv2.rectangle(imgCopy, (x, y), (x + w, y + h), (0, 255, 0), 9)
    cv2.imwrite("SitePlanArea-Output/" + str(pageNum) + "Image.png", imgCopy)

    for r in range(len(roi)):

        grImg = cv2.cvtColor(roi[r], cv2.COLOR_BGR2GRAY)
        se = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
        bg = cv2.morphologyEx(grImg, cv2.MORPH_DILATE, se)
        out_gray = cv2.divide(grImg, bg, scale=1)
        out_binary = cv2.threshold(out_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        out_binary = cv2.resize(out_binary, None, fx=6, fy=6)

        # clahe = cv2.createCLAHE().apply(out_binary)
        # sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        # sharpen = cv2.filter2D(clahe, -1, sharpen_kernel)
        # thresh = cv2.threshold(sharpen, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        # cv2.imwrite('thresh.png', thresh)

        tesData = f"{pytesseract.image_to_string(out_binary, config=r'--oem 3 --psm 6')}"

        if (str(tesData.upper()).__contains__("PATIO") or str(tesData.upper()).__contains__("PORCH") or str(
                tesData.upper()).__contains__("POOL AREA") or str(tesData.upper()).__contains__("COVERED LANAI") or str(
                tesData.upper()).__contains__("SIDEWALK")):
            # print(tesData)
            res = []
            splitData = re.split('=|\n|-|_|\'|\"', tesData)
            for sp in splitData:
                sp = re.sub('[^a-zA-Z0-9 \n\.]', '', sp)
                res.append(sp.strip())

            new_res = [x for x in res if x != '']
            # print(new_res)

            getArea(new_res)

            # dictt['A/C & CONC PAD'] = dictt['AC CONC PAD']
            # del dictt['AC CONC PAD']
            pattern = "[[0-9]*]?"
            for key, value in dictt.items():
                new_value = re.findall(pattern, value)[0]
                if (new_value != ''):
                    dictt[key] = new_value + " SQ FT"
                else:
                    dictt[key] = 'NA SQ FT'
            # print(dictt)
            return True


# directory = os.listdir("Pdf2Img")
# for i in range(len(directory)):
#     f = os.path.join("Pdf2Img/", directory[i])
#     if os.path.isfile(f):
#         print(f, i)
#         image = cv2.imread(f)
#         getTextRoi(image, i)

# image = cv2.imread("Pdf2Img/36_pdf_0.png")
# getTextRoi(image, 3)

# directory = os.listdir("Pdf2Img")
# wb = Workbook()
# sheet1 = wb.add_sheet('Sheet 1')
# for i in range(len(directory)):
#     f = os.path.join("Pdf2Img/", directory[i])
#     if os.path.isfile(f):
#         print(f,i)
#         image = cv2.imread(f)
#         resjson = getTextRoi(image, i)
#         print(dictt)
#
#         sheet1.write(i, 0, f)
#         sheet1.write(i, 1, str(dictt))
#
#         wb.save('area1.xls')

dir = "Abbott Square Individual Site Plans"
directory = os.listdir(dir)
wb = Workbook()
sheet1 = wb.add_sheet('Sheet 1')
for i in range(len(directory)):
    print(directory[i])
    f = os.path.join(dir, directory[i])
    pages = convert_from_path(f, 800, poppler_path=r"C:\Users\VRA Laptop 36\Documents\AI_WORKSPACE\poppler-22.04.0\Library\bin", size=7680)
    save_path = r'SitePlanImages'
    if os.path.exists(save_path):
        shutil.rmtree(save_path)
    os.mkdir(save_path)
    for j in range(len(pages)):
        impath = save_path + '\\' + str(j) + '.jpg'
        pages[j].save(impath, 'JPEG')
        image = cv2.imread(impath)
        getTextRoi(image,i)
        print(dictt)

    sheet1.write(i+1, 1, directory[i])
    sheet1.write(i+1, 2, str(dictt))

    wb.save('abc4.xls')