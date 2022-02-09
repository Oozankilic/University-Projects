import string

# Data is taken from txt file and informations in the file extracted as variables
f = open('data.txt', 'r')
mode = 'vertices'
vertices = ['']
verticeInfo = f.readline()
verticeNum = int(verticeInfo.split()[-1])
teleportationRate = 0.15
teleportationValue = teleportationRate/verticeNum
theMatrix = [[teleportationValue for i in range(verticeNum)] for k in range(verticeNum)]

# for loop is to traverse data.txt file
for line in f:
    if mode == 'vertices':
        if '*Edges' in line:
            mode = 'edges'
        else:
            vertices.append(line.split()[-1])
    else:
        splitted = line.split()
        a = int(splitted[0])-1
        b = int(splitted[1])-1
        theMatrix[a][b] = 1
        theMatrix[b][a] = 1
vertices.pop(0)

# Probability matrice is being created
for row in range(len(theMatrix)):
    counter = 0
    for elm in range(verticeNum):
        if theMatrix[row][elm] == 1:
            counter += 1
    theValue = teleportationValue + (1-teleportationRate)/counter
    for elm in range(verticeNum):
        if theMatrix[row][elm] == 1:
            theMatrix[row][elm] = theValue

# Result array is created and multiplied with Pmatrice until there is no difference between results
theArray=list()
theArray.append([ 1/459 for i in range(verticeNum)])

while True:
    tempArray = theArray
    theArray = [[sum(a * b for a, b in zip(A_row, B_col)) for B_col in zip(*theMatrix)] for A_row in theArray]
    if tempArray == theArray:
        break

# Sorting is done for printing result
theDict = {}
for elm in range(len(theArray[0])):
    theDict[vertices[elm]] = theArray[0][elm]
sortedList = sorted(theDict, key= lambda x: theDict[x], reverse=True)

# First 50 best result is printed
for elm in range(50):
    print(f'{elm+1}-) {sortedList[elm]}:     \t {theDict[sortedList[elm]]}')
