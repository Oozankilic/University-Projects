# this module is used for searching in the tokenBase.json file
# used for queries including 'or' and 'not'
def orNot(includedTokens, excludedTokens):
    includedTokenIds = justOr(includedTokens)
    excludedTokenIds = justOr(excludedTokens)
    return exclusion(includedTokenIds, excludedTokenIds)

# used for queries including 'and' and 'not'


def andNot(includedTokens, excludedTokens):
    includedTokenIds = justAnd(includedTokens)
    excludedTokenIds = justOr(excludedTokens)
    return exclusion(includedTokenIds, excludedTokenIds)

# used for queries including just 'or'. every time concatenates first two smallest dictionaries


def justOr(tokens):
    sortedTokens = sorted(tokens, reverse=True, key=lambda x: (len(tokens[x])))
    tempId = 'aoaooaoa'  # for naming the concatenation uniquely not to be confused with tokens
    tempIdNum = 0
    while len(sortedTokens) > 1:
        min1 = sortedTokens.pop()
        min2 = sortedTokens.pop()
        min1Ids = tokens.pop(min1)
        min2Ids = tokens.pop(min2)
        result = orMerge(min1Ids, min2Ids)
        resultId = tempId + str(tempIdNum)
        tempIdNum += 1
        tokens[resultId] = result
        sortedTokens = sorted(tokens, reverse=True,
                              key=lambda x: (len(tokens[x])))
    endList = [int(theId) for theId in tokens[sortedTokens.pop()]]
    return endList
# used for queries including just 'and'. Uses merge algorithm for efficiency


def justAnd(tokens):
    
    sortedTokens = sorted(tokens, key=lambda x: (len(tokens[x])))
    docIds = []
    tempInt = 0
    for token in sortedTokens:
        if(tempInt == 0):
            docIds = [int(elm) for elm in tokens[token]]
            tempInt = 1
        else:
            docIds = andMerge(docIds, tokens[token])
    return(docIds)

# the merge algorithm to be used for 'and' queries

def andMerge(list1, list2):
    iter1 = iter(list1)
    iter2 = iter(list2)
    result = []
    id1 = int(next(iter1))
    id2 = int(next(iter2))
    while(True):
        try:
            if id1 == id2:
                print(id1)
                result.append(id1)
                id1 = int(next(iter1))
                id2 = int(next(iter2))
            elif id1 < id2:
                id1 = int(next(iter1))
            else:
                id2 = int(next(iter2))
        except:
            return result

# the merge algorithm to be used for 'or' queries

def orMerge(list1, list2):
    iter1 = iter(list1)
    iter2 = iter(list2)
    result = []
    id1 = int(next(iter1))
    id2 = int(next(iter2))
    while(True):
        if id1 == id2:
            result.append(id1)
            try:
                id1 = int(next(iter1))
            except:
                try:
                    id2 = int(next(iter2))
                    while(True):
                        try:
                            result.append(id2)
                            id2 = int(next(iter2))
                        except:
                            return result
                except:
                    return result
            try:
                id2 = int(next(iter2))
            except:
                id1 = int(next(iter1))
                while(True):
                    try:
                        result.append(id1)
                        id1 = int(next(iter1))
                    except:
                        return result
        elif id1 < id2:
            try:
                result.append(id1)
                id1 = int(next(iter1))
            except:
                while(True):
                    try:
                        result.append(id2)
                        id2 = int(next(iter2))
                    except:
                        return result
        else:
            try:
                result.append(id2)
                id2 = int(next(iter2))
            except:
                while(True):
                    try:
                        result.append(id1)
                        id1 = int(next(iter1))
                    except:
                        return result

# exclusion method which is called when 'not' term used.

def exclusion(originals, excludeds):
    result = []
    orgIter = iter(originals)
    exIter = iter(excludeds)
    org = int(next(orgIter))
    ex = int(next(exIter))
    while(True):
        if org < ex:
            result.append(org)
            try:
                org = int(next(orgIter))
            except StopIteration:
                return result
        elif ex < org:
            try:
                ex = int(next(exIter))
            except StopIteration:
                while(True):
                    try:
                        result.append(org)
                        org = int(next(orgIter))
                    except:
                        return result
        else:
            try:
                org = int(next(orgIter))
            except StopIteration:
                return result
            try:
                ex = int(next(exIter))
            except StopIteration:
                while(True):
                    try:
                        result.append(org)
                        org = int(next(orgIter))
                    except:
                        return result
