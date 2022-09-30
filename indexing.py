import statistics
import time
import json

from preprocessing import getTokens

# termDIct is the term dict of one file for one Type
termDict = dict()
# termDictOfFile is the term dict of all files for one Type
termDictOfFile = dict()
constraint = 1000
tempFiles = []
fileCounter = 0
tempfilePath = "./tempFile/"


def writeTempFile():
    global termDict
    global tempFiles
    global fileCounter
    with open(f"{tempfilePath}{fileCounter}.json", "w", encoding="UTF-8") as f:
        te = {}
        for term in sorted(termDict.keys()):
            te[term] = termDict[term]
        f.write(json.dumps(te, indent=4))
    f.close()
    termDict = {}
    tempFiles.append(f"{tempfilePath}{fileCounter}.json")
    fileCounter += 1


def writeIndexToRes(Type, termDictTotal):
    with open(f"./index/{Type}.json", "w", encoding="UTF-8") as f:
        te = {}
        for term in sorted(termDictTotal.keys()):
            te[term] = termDictTotal[term]
        f.write(json.dumps(te, indent=4))
    f.close()


def mergeDict(termDictTotal, tempDict):

    for term, tf in tempDict.items():
        for docId, frequency in tf.items():
            if term not in termDictTotal:
                termDictTotal[term] = {}
            if docId in termDictTotal[term]:
                termDictTotal[term][docId] += frequency
            else:
                termDictTotal[term][docId] = frequency
    return termDictTotal


def mergeFile():
    global tempFiles
    termDictTotal = dict()
    for fPath in tempFiles:
        with open(fPath, 'r', encoding="UTF-8") as f:
            tempDict = json.load(f)
            termDictTotal = mergeDict(termDictTotal, tempDict)
    tempFiles = []
    return termDictTotal


def buildIndexByType(filePaths, Type):
    """
    main function of building index
    traverse all files to build index according to the Type
    :param filePaths:
    :param Type: one of ["term", "phrases", "stem", "position"]
    :return:
    """
    global constraint
    global termDict
    start = time.time()
    for filePath in filePaths:
        # print(f"start processing {filePath} Type = {Type}")
        tokens, docId = getTokens(filePath, Type)
        # print(f"{Type} length {len(tokens)}")
        if Type != "position":
            for token in tokens:
                addTermIndex(token, docId)
            if len(termDict.keys()) >= constraint:
                writeTempFile()
        else:
            for idx, token in enumerate(tokens):
                addTermPositionIndex(idx, token, docId)
            if len(termDict.keys()) >= constraint:
                writeTempFile()
    merge = time.time()
    termDictTotal = mergeFile()
    end = time.time()

    indicates = calculate_term_list()
    evaluate(indicates, start, merge, end, Type)
    # write termDictTotal to res
    writeIndexToRes(Type, termDictTotal)


def addTermPositionIndex(position, term, docId):
    global termDict
    global termDictOfFile
    if term not in termDict:
        termDict[term] = {docId: [position]}
        if term not in termDictOfFile:
            termDictOfFile[term] = 1
        else:
            termDictOfFile[term] += 1
    else:
        if docId in termDict[term]:
            termDict[term][docId].append(position)
        else:
            termDict[term][docId] = [position]
            termDictOfFile[term] += 1


def addTermIndex(term, docId):
    global termDict
    global termDictOfFile
    if term not in termDict:
        termDict[term] = {docId: 1}
        if term not in termDictOfFile:
            termDictOfFile[term] = 1
        else:
            termDictOfFile[term] += 1
    else:
        if docId in termDict[term]:
            termDict[term][docId] += 1
        else:
            termDict[term][docId] = 1
            termDictOfFile[term] += 1


def calculate_term_list():
    global termDictOfFile

    num = len(termDictOfFile.keys())
    max_df = max(termDictOfFile.values())
    min_df = min(termDictOfFile.values())
    mean_df = statistics.mean(termDictOfFile.values())
    median_df = statistics.median(termDictOfFile.values())

    return [num, max_df, min_df, mean_df, median_df]


def evaluate(indicates, start, merge, end, Type):
    """
    evaluate the time and other performance
    :param indicates: num, max_df, min_df, mean_df, median_df
    :param start: start time
    :param merge: merge start time
    :param end: process end time
    :param Type: ["term", "phrases", "stem", "position"]
    :return:
    """
    if Type == 'term':
        print("SINGLE INDEX")
    elif Type == 'stem':
        print("STEM INDEX")
    elif Type == 'phrases':
        print("PHRASE INDEX")
    elif Type == 'position':
        print("POSITIONAL INDEX")

    print(f"Execution Time Total: {round(end - start, 2)} s")
    print(f"Time to Merge Temp Files: {round(end - merge, 2)} s")

    print("Terms in dict: " + str(indicates[0]))
    print("Max df: " + str(indicates[1]))
    print("Min df: " + str(indicates[2]))
    print("Mean df: " + str(indicates[3]))
    print("Median df: " + str(indicates[4]) + '\n')
