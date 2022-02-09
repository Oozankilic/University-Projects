# this module is written for creating tokenBase.json and docTfIdj.json files. There are two ways of
# using the module. First, it can be directly called from main module named searchQuery.py.
# Second, it can be run from terminal via writing python3 tokenizer.py
# note: the sgm files that will be scanned should be in the same directory with tokenizer.py

import io
import re
import string
import json
import os
import math

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
textEndReg = re.compile(r'</TEXT>')

# called for each sgm file by prepareDict method. Iterates over the file one time and saves ids of the tokens
# between <title></title> and <body></body> parts. Before saving, normalizes the words.
def iterateDoc(iterator, currentID, tokenList, stopWords, file, percentage, indexCounter, docTfIdf):
    # try except for iteration exception. At the end of the iteration, StopIteration exception is throwed

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
                            indexCounter = 1
                    currentID = int(currentID)
                    docTfIdf[currentID] = {}
                item = next(iterator)

            if bool(titleReg.search(item)):
                index = item.find('<TITLE>')
                item = item[index+7:]

                if not item in stopWords:
                    for elem in item:
                        if elem in punctuations:
                            item = item.replace(elem, '')
                    item = item.lower()
                    if not item == '':
                        tokenList.append((item, currentID, indexCounter))
                        if item in docTfIdf[currentID]:
                            docTfIdf[currentID][item] +=1
                        else:
                            docTfIdf[currentID][item] = 1
                        indexCounter += 1

            elif bool(bodyReg.search(item)):
                index = item.find('<BODY>')
                item = item[index+6:]

                if not item in stopWords:
                    for elem in item:
                        if elem in punctuations:
                            item = item.replace(elem, '')
                    item = item.lower()
                    if not item == '':
                        tokenList.append((item, currentID, indexCounter))
                        if item in docTfIdf[currentID]:
                            docTfIdf[currentID][item] +=1
                        else:
                            docTfIdf[currentID][item] = 1
                        indexCounter += 1

            # In that part, every word's document ids are stored until iterator is faced with </body> or </title> tag
            item = next(iterator)
            while not (bool(titleEndReg.search(item) or bool(bodyEndReg.search(item)))):

                if not item in stopWords:
                    for elem in item:
                        if elem in punctuations:
                            item = item.replace(elem, '')
                    item = item.lower()
                    if not item == '':
                        tokenList.append((item, currentID, indexCounter))
                        if item in docTfIdf[currentID]:
                            docTfIdf[currentID][item] +=1
                        else:
                            docTfIdf[currentID][item] = 1
                        indexCounter += 1
                item = next(iterator)

            if (bool(titleEndReg.search(item))):
                item = item[:-8]

                if not item in stopWords:
                    for elem in item:
                        if elem in punctuations:
                            item = item.replace(elem, '')
                    item = item.lower()
                    if not item == '':
                        tokenList.append((item, currentID, indexCounter))
                        if item in docTfIdf[currentID]:
                            docTfIdf[currentID][item] +=1
                        else:
                            docTfIdf[currentID][item] = 1
                indexCounter += 10
            

    except:
        percentage = "{:.2f}".format(percentage)
        print(f'{bcolors.OKGREEN}{file} is processed. ({percentage} % completed){bcolors.ENDC}')
        return currentID


# called when the module wanted to be used from another module. searchQuery.py calls that part. This part iterates every document and write
# down the final dictionary to the tokenBase.json and docTfIdf.json files.
def prepareDict(files,fileLength):
    tokenList = []
    docTfIdf = {}
    fileCounter = 0
    for file in files:
        # reads the sgm files with latin1 encoding
        read_file = io.open(file, "r", encoding="ISO-8859-1")
        read_text = read_file.read()
        read_file.close()

        # takes stopwords from the file in order to eliminate them before adding document Ids.
        stopWords = []
        with open('./stopwords.txt', 'r') as words:
            for word in words:
                stopWords.append(word[:-1].strip())

        # percentage is for showing completion ratio of reading files
        percentage = (fileCounter/fileLength)*100
        
        # below part creates an iterator for the file and send it to iterateDoc method to be searched.
        words = read_text.split()
        docIterator = iter(words)
        currentID = 0
        indexCounter = 1
        iterateDoc(docIterator, currentID, tokenList, stopWords, file, percentage, indexCounter,docTfIdf)
        fileCounter += 1

    # this two lines of code sorts names of tokens in a list by their document numbers
    sortedList = sorted(tokenList, key = lambda x:(x))
    endDict = {}

    # this for loop concatenates tokenList elements and creates the end dictionary
    for elem in sortedList:
        if not elem[0] == "":
            if elem[0] in endDict:
                if elem[1] in endDict[elem[0]]:
                    endDict[elem[0]][elem[1]].append(elem[2])
                else:
                    temp = []
                    temp.append(elem[2])
                    endDict[elem[0]][elem[1]] = temp
            else:
                temp = {}
                tempList = []
                tempList.append(elem[2])
                temp[elem[1]]=tempList
                endDict[elem[0]] = temp

    #This for loop calculates Tf-Idf values of elements in the docs
    totalDocNumber = len(docTfIdf)
    for doc in docTfIdf:
        for term in docTfIdf[doc]:
            if not term == '':
                tf = 1+math.log(docTfIdf[doc][term],10)
                idf = math.log(totalDocNumber/len(list(endDict[term])),10)  
                docTfIdf[doc][term] = tf*idf

    #These two parts of code creates json files to be used by searchQuery.py file.
    saveAsJson = open('docTfIdf.json', 'w')
    json.dump(docTfIdf, saveAsJson)
    saveAsJson.close()
    print(f'{bcolors.OKGREEN}docTfIdf.json file is created. {bcolors.ENDC}')

    saveAsJson = open('tokenBase.json', 'w')
    json.dump(endDict, saveAsJson)
    saveAsJson.close()



# this module is for creating the tokenBase.json and dicTfIdf.json file when the module is run as main. Functionality is same with preapareDict method.
def manualStart():
    docTfIdf = {}
    tokenList = []
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
                stopWords.append(word[:-1].strip())

        percentage = (fileCounter/len(sgmFiles))*100
        words = read_text.split()
        docIterator = iter(words)
        currentID = 0
        indexCounter = 1
        iterateDoc(docIterator, currentID, tokenList, stopWords,file, percentage, indexCounter, docTfIdf)
        fileCounter += 1


    # this for loop concatenates tokenList elements and creates the end dictionary
    sortedList = sorted(tokenList, key = lambda x:(x))
    endDict = {}
    for elem in sortedList:
        if not elem[0] == "":
            if elem[0] in endDict:
                if elem[1] in endDict[elem[0]]:
                    endDict[elem[0]][elem[1]].append(elem[2])
                else:
                    temp = []
                    temp.append(elem[2])
                    endDict[elem[0]][elem[1]] = temp
            else:
                temp = {}
                tempList = []
                tempList.append(elem[2])
                temp[elem[1]]=tempList
                endDict[elem[0]] = temp


    #These two parts of code creates json files to be used by searchQuery.py file.

    saveAsJson = open('tokenBase.json', 'w')
    json.dump(endDict, saveAsJson)
    saveAsJson.close()
    print(f'{bcolors.OKGREEN}tokenBase.json file is created.{bcolors.ENDC}')
    
    totalDocNumber = len(docTfIdf)
    for doc in docTfIdf:
        for term in docTfIdf[doc]:
            if not term == '':
                tf = 1+math.log(docTfIdf[doc][term],10)
                idf = math.log(totalDocNumber/len(list(endDict[term])),10)  
                docTfIdf[doc][term] = tf*idf
                if doc == 1394 or doc == 9999999 or doc == 15179:
                    print(term)
                    print(f'TF-{doc}:{tf}')
                    print(f'IDF-{doc}:{idf}')
    

    
    
    saveAsJson = open('docTfIdf.json', 'w')
    json.dump(docTfIdf, saveAsJson)
    saveAsJson.close()
    print(f'{bcolors.OKGREEN}docTfIdf.json file is created. (100 % completed){bcolors.ENDC}')

# to check if the code is runned as main or called from another file.
if __name__ == '__main__':
    manualStart()







