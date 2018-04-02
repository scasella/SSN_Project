
import pytesseract
import cv2
from io import BytesIO
import numpy
import re
import PyPDF2
import os, os.path
try:
    import Image
except ImportError:
    from PIL import Image


def passFolder(path):
    #Initialize SSN Regex Query
    ssnRE = re.compile('[0-9][0-9][0-9][-\s][0-9][0-9][-\s][0-9][0-9][0-9][0-9]', re.MULTILINE|re.DOTALL)
    ssnDict = {}
    count = 0

    for f in os.listdir(path):
        ext = os.path.splitext(f)[1]
        if ext.lower() in ['.jpg','.png']:
            #Func outputs list of found SSNs and the str(filename)
            outList, outFilename = doJPGPNG(os.path.join(path,f),(ext.lower() is '.png'),ssnRE)
        elif ext.lower() in ['.pdf']:
            outList, outFilename = doPDF(os.path.join(path,f),ssnRE)
        else:
            continue
        ssnDict = checkDict(ssnDict,outList,outFilename)
        count = printCount(count,len(ssnDict))

    print('')
    print('{0} unique SSNs found in {1} files.'.format(len(ssnDict),len(os.listdir(path))))
    print(ssnDict)


def printCount(c,sLength):
    c+=1
    if sLength == 1:
        ssnSP = "SSN"
    else:
        ssnSP = "SSNs"
    if c != 1:
        print('{0} files scanned, {1} {2} found'.format(c,sLength,ssnSP))
    else:
        print('1 file scanned, {0} {1} found'.format(sLength,ssnSP))
    return c


def formatSSN(ssn):
    tempList = []
    for val in ssn:
        #Format all SSNs to XXX-XX-XXXX
        tempList.append(val[:3]+'-'+val[4:6]+'-'+val[7:11])
    return tempList


def checkDict(ssnDict,outList,outFilename):
    for ssn in outList:
        if ssn in ssnDict:
            ssnDict[ssn].append(outFilename)
        else:
            ssnDict[ssn] = [outFilename]
    return ssnDict


def doJPGPNG(file,isPNG,ssnRE):

    ima = Image.open(file)

    #Scales img to 1500 pixels and mantains aspect ratio
    f = lambda x,y,z: (int(z), int(y/x*z))
    nWidth,nHeight = f(ima.size[0],ima.size[1],1500)
    image = ima.resize((nWidth, nHeight), Image.LANCZOS)

    #Converts to PNG without creating new file in directory
    if not isPNG:
        with BytesIO() as f:
            image.save(f, format='PNG')
            f.seek(0)
            image = Image.open(f).convert('RGB')
    else:
            image = image.convert('RBG')

    #OpenCV Preprocessing to make img grayscale, make bg black and foreground/text white
    open_cv_image = numpy.array(image)
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    #Tesseract find text from img
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'
    final = ssnRE.findall(pytesseract.image_to_string(thresh).replace(' ', ''))
    final = formatSSN(final)

    return (final,os.path.basename(file))


def doPDF(file,ssnRE):
    pdfFileObj = open(file, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    allTxt = ""

    for i in range(pdfReader.numPages):
        allTxt+=pdfReader.getPage(i).extractText()

    final = ssnRE.findall(allTxt.replace('\n', '').replace('\r', ''))
    final = formatSSN(final)

    return (final,os.path.basename(file))


#passFolder('C:\\Users\\scasella\\Desktop\\SSN Project')
var = input("Please enter a folder path: ")
print("Scanning...")
SSNList = passFolder(var)
