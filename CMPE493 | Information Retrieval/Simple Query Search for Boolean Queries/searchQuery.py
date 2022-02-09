import searcher
import tokenizer
import json
import os


# processor called by main function for each query. It waits input from the user and
# calls related function from searcher.py 
def processor():
    print('\033[94mplease enter your query ->\033[0m')
    queryList = input().lower().split(' ')
    if len(queryList) < 3:
        print('Wrong or missing input')
    else:
        argIter = iter(queryList)                       # Input is evaluated via an iterator argIter
        token = str(next(argIter))
        logic = str(next(argIter))
        includedTokens = {}                             # Tokens which will be included and excluded are stored in different dictionaries
        excludedTokens = {}

        # The code until the other comment seperates tokens and calls the right function according to the user's input. 
        # If there is an unappropriate input it gives error
        try:                                            
            includedTokens[token] = tokenDict[token]
        except:
            if logic == 'and':
                print('[]')
                return 
        if logic == 'and':
            while not logic == 'not':
                token = str(next(argIter))
                try: 
                    includedTokens[token] = tokenDict[token]
                except:
                    print('[]')
                    return 
                try:
                    logic = str(next(argIter))
                except:
                    print(searcher.justAnd(includedTokens)) 
                    return
            if logic == 'not':
                while(True):
                    token = str(next(argIter))
                    try: 
                        excludedTokens[token] = tokenDict[token]
                    except:
                        print(f'{token} can not be found anywhere')
                        pass
                    try:
                        logic = str(next(argIter))
                    except:
                        print(searcher.andNot(includedTokens,excludedTokens)) 
                        return
            else:
                print('Wrong input structure')
            
        elif logic == 'or':
            while not logic == 'not':
                token = str(next(argIter))
                try: 
                    includedTokens[token] = tokenDict[token]
                except:
                    print('[]')
                    return
                try:
                    logic = str(next(argIter))
                except:
                    print(searcher.justOr(includedTokens)) 
                    return
            if logic == 'not':
                token = str(next(argIter))
                try: 
                    excludedTokens[token] = tokenDict[token]
                except:
                    print(f'{token} can not be found anywhere')
                    pass
                try:
                    logic = str(next(argIter))
                except:
                    print(searcher.orNot(includedTokens,excludedTokens)) 
                    return
            else:
                print('Wrong input structure')
        else:
            print('Wrong input structure')

        # The code part mentioned above finishes here
            
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

    #processor is called repeatedly for new query searches
    while(True):
        processor()



