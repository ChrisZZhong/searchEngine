from pathlib import Path

import index
import time
import os
import queryProcessing
import json
import sys


def static(inputs):
    print("now processing query statically. Please wait a few seconds")
    indexPath = inputs[0]
    queryPath = inputs[1]
    method = inputs[2]
    indexTypeInput = inputs[3]
    outputResPath = inputs[4]
    outputDir = "/".join(outputResPath.split("/")[:-1])
    if not Path(outputDir).exists():
        os.makedirs(outputDir)
    print("now load indexes")
    indexes = ['single', 'stem', 'phrase', 'positional']
    termLists = []
    LexiLists = []
    for indexType in indexes:
        termList, LexiList = LoadIndex(indexPath, indexType)
        termLists.append(termList)
        LexiLists.append(LexiList)

    # PROCESSES QUERIES
    print('now Query Processing')
    Queries = queryProcessing.queryInput(queryPath)
    queries = {}
    for queryID in Queries:
        queries[queryID] = Queries[queryID]['title']

    dataRes1 = queryProcessing.RES1(LexiLists[0], termLists[0], LexiLists[1], termLists[1], queries, outputResPath)
    queryProcessing.ShowStaticRes(dataRes1, indexTypeInput, method)


def main():
    """entrance of the whole program"""
    indexes = ['single', 'stem', 'phrase', 'positional']
    inputs = sys.argv[1:]
    if len(inputs) == 3:
        if inputs[1] in indexes:
            buildIndex(inputs)
        else:
            dynamic(inputs)
    elif len(inputs) == 5:
        static(inputs)
    else:
        print("invalid input, please check the input!")


def buildIndex(inputs):
    """
    build index of one of ["single", "stem", "phrase", "positional"]
    """
    print("now building index. Please wait a few seconds")
    inputPath = inputs[0]
    indexType = inputs[1]
    outputPath = inputs[2]
    input_files = []
    for filename in os.listdir(inputPath):
        if filename != '.DS_Store':
            input_files.append(filename)
    pro1Res1 = {}
    index.getAllTokens(inputPath, input_files, outputPath, indexType, 0, pro1Res1)
    print(f"{indexType} successfully built")


def LoadIndex(indexPath, indexType):
    fileLex = open(f"{indexPath}/{indexType}Lex.json", 'r', encoding="UTF-8")
    Lexi = json.load(fileLex)
    fileTerm = open(f"{indexPath}/{indexType}Term.json", 'r', encoding="UTF-8")
    termList = json.load(fileTerm)
    return termList, Lexi


def dynamic(inputs):
    print("now processing query dynamically. Please wait a few seconds")
    indexPath = inputs[0]
    queryPath = inputs[1]
    outputResPath = inputs[2]
    outputDir = "/".join(outputResPath.split("/")[:-1])
    if not Path(outputDir).exists():
        os.makedirs(outputDir)
    indexes = ['single', 'stem', 'phrase', 'positional']
    termLists = []
    LexiLists = []
    for indexType in indexes:
        termList, LexiList = LoadIndex(indexPath, indexType)
        termLists.append(termList)
        LexiLists.append(LexiList)

    # PROCESSES QUERIES
    print('now Query Processing')
    Queries = queryProcessing.queryInput(queryPath)
    queries = {}
    for queryID in Queries:
        queries[queryID] = Queries[queryID]['title']

    Start = time.time()
    index_count, dataRes2 = queryProcessing.RES2(LexiLists[1], termLists[1], LexiLists[2], termLists[2], LexiLists[3],
                                                 termLists[3], queries, Start, outputResPath)
    queryProcessing.ShowRes2(dataRes2, index_count)


if __name__ == "__main__":
    main()
