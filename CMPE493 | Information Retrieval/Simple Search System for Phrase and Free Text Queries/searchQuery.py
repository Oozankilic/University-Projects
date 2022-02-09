import searcher
import tokenizer
import json
import os
import string

# processor called by main function for each query. It waits input from the user and
# calls related function from searcher.py 
def processor():
    print('\033[94mplease enter your query ->\033[0m')
    queryList = input().lower().split(' ')
    if queryList[0][0] == '"' and queryList[-1][-1] == '"':
        argIter = iter(queryList)                           #Input is evaluated via an iterator argIter
        token = str(next(argIter))[1:]
        includedTokens = {}     
        while(True):
            try:
                if token[-1] == '"':
                        token = token[:-1]  
                if token in stopWords:
                    token = str(next(argIter))
                else:        
                    for elem in token:
                        if elem in string.punctuation:
                            token = token.replace(elem, '')
                    token = token.lower()        
                    try:            
                        includedTokens[token] = tokenDict[token]
                    except:
                        print('[]')
                        return
                    token = str(next(argIter))
                    
            except:
                print(searcher.justAnd(includedTokens)) 
                return
                

    elif queryList[0][0] == '"' or queryList[-1][-1] == '"':
        print('Wrong input type please try again (Phase Queries should start and end with double quotation <"> )')
    else:
        for elm in queryList:
            if elm not in tokenDict:
                print(f'"{elm}" is not in any documents. Result without "{elm}" is below')
                queryList.remove(elm)
        if queryList == []:
            print('[]')
        result = searcher.cosineScore(queryList,tokenDict,docTfIdf)
        sortedResult = sorted(result, reverse=True, key = lambda x: result[x])
        
        for elm in sortedResult:
            print(f'DocID: {elm} - Cos Similarity: {result[elm]}')
            
    # class for coloring terminal outputs
class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'

    #The program starts with the below code. 
if __name__ == '__main__':
    print(f"{bcolors.HEADER}Boolean Query Searcher{bcolors.ENDC}")  

    #This part looks for tokenBase.json if there is not, searches for files in the current path and make a list of sgm files to create tokenBase.json
    files = [f for f in os.listdir('.') if os.path.isfile(f)]       
    if not 'tokenBase.json' in files:
        fileCounter = 0
        print('The inverted index document (tokenBase.json) is being prepared.. Please wait a second')
        sgmFiles = []
        for file in files:
            if file[-3:] == 'sgm':
                sgmFiles.append(file)
                fileCounter +=1

    #tokenizer.prepareDict creates tokenBase.json folder by using the sgm files
        tokenizer.prepareDict(sgmFiles,fileCounter)
        print(f'{bcolors.OKGREEN}tokenBase.json file is created. (100 % completed){bcolors.ENDC}')

    #program reads created tokenBase.json file to search
    jsonReader = open("tokenBase.json", "r")
    tokenDict = json.load(jsonReader)
    jsonReader.close()

    #program reads created docTfIdf.json file to search
    jsonReader = open("docTfIdf.json", "r")
    docTfIdf = json.load(jsonReader)
    jsonReader.close()

    stopWords = []
    with open('./stopwords.txt', 'r') as words:
        for word in words:
            stopWords.append(word[:-1].strip())

    
    #processor is called repeatedly for new query searches
    while(True):
        processor()