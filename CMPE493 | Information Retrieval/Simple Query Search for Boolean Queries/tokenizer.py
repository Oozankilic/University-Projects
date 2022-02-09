# this module is written for creating tokenBase.json file. There are two ways of
# using the module. First, it can be directly called from main module named searchQuery.
# Second, it can be run from terminal via writing python3 tokenizer.py
# note: the sgm files that will be scanned should be in the same directory with tokenizer.py

import io
import re
import string
import json
import os

class bcolors:
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'

# tools for parsing the tokens
punctuations = string.punctuation
IDReg = re.compile(r'NEWID="\d+"')
titleReg = re.compile(r'<TITLE>')
bodyReg = re.compile(r'<BODY>')
titleEndReg = re.compile(r'</TITLE>')
bodyEndReg = re.compile(r'</BODY>')

# called for each sgm file by prepareDict method. Iterates over the file one time and saves ids of the tokens
# between <title></title> and <body></body> parts. Before saving, normalizes the words.
def iterateDoc(iterator, currentID, tokenList, stopWords, file, percentage):
    #try except for iteration exception. At the end of the iteration, StopIteration exception is throwed
    try:
        while True:
            # the below part is looks for <body> or <title> tag to start saving tokens
            item = next(iterator)
            while not (bool(titleReg.search(item) or bool(bodyReg.search(item)))):
                if bool(IDReg.search(item)):
                    currentID = ''
                    for char in item:
                        if char.isdigit():
                            currentID += char
                item = next(iterator)
            if bool(titleReg.search(item)):
                index = item.find('<TITLE>')
                item = item[index+7:]

                for elem in item:
                    if elem in punctuations:
                        item = item.replace(elem, '')
                item = item.lower()

                if not item in stopWords:
                    tokenList.append((item, currentID))

            elif bool(bodyReg.search(item)):
                index = item.find('<BODY>')
                item = item[index+6:]

                for elem in item:
                    if elem in punctuations:
                        item = item.replace(elem, '')
                item = item.lower()

                if not item in stopWords:
                    tokenList.append((item, currentID))

            #In that part, every word's document ids are stored until iterator is faced with </body> or </title> tag
            item = next(iterator)
            while not (bool(titleEndReg.search(item) or bool(bodyEndReg.search(item)))):
                for elem in item:
                    if elem in punctuations:
                        item = item.replace(elem, '')
                item = item.lower()
                if not item in stopWords:
                    tokenList.append((item, currentID))
                item = next(iterator)
    except:
        percentage = "{:.2f}".format(percentage)
        print(f'{bcolors.OKGREEN}{file} is processed. ({percentage} % completed){bcolors.ENDC}')


# called when the module wanted to be used from another module. searchQuery.py calls that part. This part iterates every document and write
# down the final dictionary to the tokenBase.json file.
def prepareDict(files,fileLength):
    uniqueList = []
    fileCounter = 0
    for file in files:
        # reads the sgm files with latin1 encoding
        read_file = io.open(file, "r", encoding="ISO-8859-1")
        read_text = read_file.read()
        read_file.close()
        
        #takes stopwords from the file in order to eliminate them before adding document Ids.
        stopWords = []
        with open('./stopwords.txt', 'r') as words:
            for word in words:
                stopWords.append(word[:-1])
        #percentage is for showing completion ratio of reading files
        percentage = (fileCounter/fileLength)*100
        
        #below part creates an iterator for the file and send it to iterateDoc method to be searched.
        words = read_text.split()
        docIterator = iter(words)
        currentID = 0
        tokenList = []
        iterateDoc(docIterator, currentID, tokenList, stopWords, file, percentage)
        uniqueList += list(set(tokenList))
        fileCounter += 1

    #this two lines of code sorts names of tokens in a list by their document numbers
    sortedList = sorted(uniqueList, key=lambda x: (x[0], int(x[1])))
    endDict = {}

    #this for loop creates final dictionary to be saved as Json file
    for elem in sortedList:
        if not elem[0] == "":
            if elem[0] in endDict:
                endDict[elem[0]].append(elem[1])
            else:
                temp = []
                temp.append(elem[1])
                endDict[elem[0]] = temp

    saveAsJson = open('tokenBase.json', 'w')
    json.dump(endDict, saveAsJson)
    saveAsJson.close()

# this module is for creating the tokenBase.json file when the module is run as main. Functionality is same with preapareDict method.
def manualStart():
    uniqueList = []
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    sgmFiles = []
    for file in files:
        if file[-3:] == 'sgm':
            sgmFiles.append(file)

    fileCounter = 0
    for file in sgmFiles:
        read_file = io.open(file, "r", encoding="ISO-8859-1")
        read_text = read_file.read()
        read_file.close()

        stopWords = []
        with open('./stopwords.txt', 'r') as words:
            for word in words:
                stopWords.append(word[:-1])

        percentage = (fileCounter/len(sgmFiles))*100
        words = read_text.split()
        docIterator = iter(words)
        currentID = 0
        tokenList = []
        iterateDoc(docIterator, currentID, tokenList, stopWords,file, percentage)
        uniqueList += list(set(tokenList))
        fileCounter += 1

    sortedList = sorted(uniqueList, key=lambda x: (x[0], int(x[1])))
    endDict = {}

    for elem in sortedList:
        if not elem[0] == "":
            if elem[0] in endDict:
                endDict[elem[0]].append(elem[1])
            else:
                temp = []
                temp.append(elem[1])
                endDict[elem[0]] = temp

    saveAsJson = open('tokenBase.json', 'w')
    json.dump(endDict, saveAsJson)
    saveAsJson.close()
    print(f'{bcolors.OKGREEN}tokenBase.json file is created. (100 % completed){bcolors.ENDC}')


# to check if the code is runned as main or called from another file.
if __name__ == '__main__':
    manualStart()


