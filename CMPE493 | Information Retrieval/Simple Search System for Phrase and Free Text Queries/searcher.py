import math

# This method is used to calculate cosine scores of documents matching with the query. First, 
# it calculates query weight with queryWeightCalculator method. Than multiples the terms' weights with
# the document terms' tf-idf scores. At the end, length of documents" tf-idf values are calculated and
# scores divided by this weight for normalization.
def cosineScore(query,tokenDict,docTfIdf):
    totalDocNumber = len(docTfIdf)
    scores = {}
    queryWeights = queryWeightCalculator(query,tokenDict,totalDocNumber)
    for elem in queryWeights:
        for doc in tokenDict[elem]:
            if doc in scores:
                scores[doc] += docTfIdf[doc][elem] * queryWeights[elem]
            else:
                scores[doc] = docTfIdf[doc][elem] * queryWeights[elem]

    #Length normalization
    for doc in scores:
        docLengthSquare = 0
        for term in docTfIdf[doc]:
            docLengthSquare += docTfIdf[doc][term] ** 2
        docLength = math.sqrt(docLengthSquare)
        scores[doc] = scores[doc]/docLength

    return scores

def queryWeightCalculator(query,tokenDict,totalDocNumber):
    elemCounter = {}
    for elm in query:
        if elm in elemCounter:
            elemCounter[elm] += 1
        else:
            elemCounter[elm] = 1

    weights = {}
    for elm in elemCounter:
        tf = 1 + math.log(int(elemCounter[elm]),10)
        idf = math.log(totalDocNumber/len(tokenDict[elm]))
        weights[elm] = tf * idf
        
    lengthSquare = 0
    for elem in weights:
        lengthSquare += weights[elem] ** 2
    length = math.sqrt(lengthSquare)
    for elem in weights:
        weights[elem] = weights[elem]/length
    return weights



# used for searching phrase queries. This function uses andMerge and indexMerge methods to find documents which 
# including the query in the sequenced order
def justAnd(tokens):
    tokenIndexes = {}
    index = 0
    for token in tokens:
        tokenIndexes[token] = index
        index += 1

    sortedTokens = sorted(tokens, key=lambda x: (len(tokens[x])))

    docIds = {}
    tempInt = 0
    prevIndex = 0
    currentIndex = 0
    for token in sortedTokens:
        if(tempInt == 0):
            docIds.update(tokens[token])
            prevIndex = tokenIndexes[token]
            tempInt = 1
        else:
            currentIndex = tokenIndexes[token]
            distance = currentIndex - prevIndex 
            mergedIds = andMerge(docIds, tokens[token], distance)
            docIds.clear()
            docIds = mergedIds
            
    return(list(docIds.keys()))


# the merge algorithm is used for checking common documents of the terms. Sends common documents to indexMerge method to
# control the terms' positions in the common documents

def andMerge(dict1, dict2, distance):
    list1 = dict1.keys()
    list2 = dict2.keys()
    if (len(list1) == 0) or (len(list2) == 0):
        return {}
    iter1 = iter(list1)
    iter2 = iter(list2)
    result = {}
    id1 = int(next(iter1))
    id2 = int(next(iter2))
    while(True):
        try:
            if id1  == id2:
                tempDict = {}
                id1 = str(id1)
                resultList = indexMerge(dict1[id1],dict2[id1],distance)
                if not len(resultList) == 0:
                    tempDict[id1] = resultList
                result.update(tempDict)
                id1 = int(next(iter1))
                id2 = int(next(iter2))

            elif id1 < id2:

                id1 = int(next(iter1))

            else:
                
                id2 = int(next(iter2))

        except:
            return result



# This method controls indexes of the document. If two word is at the same sequence with the query, 
# then their positions are saved and, at the end returned.
def indexMerge(indexes1, indexes2, distance):
    iter1 = iter(list(indexes1))
    iter2 = iter(list(indexes2))
    id1 = int(next(iter1))
    id2 = int(next(iter2))
    result = []
    
    while(True):
        try:
            if id1 + distance == id2:
                result.append(id1)
                id1 = int(next(iter1))
                id2 = int(next(iter2))
            elif id1 + distance < id2:
                id1 = int(next(iter1))
            else:
                id2 = int(next(iter2))
        except:
            return result
