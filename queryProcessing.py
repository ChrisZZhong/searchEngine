from subprocess import getstatusoutput
import preprocess
import math
import time
from collections import OrderedDict
from operator import itemgetter
from texttable import Texttable


def RES1(sLexi, sTermList, stLexi, stTermList, queries, outputResPath):
    """
        display of result1
        """
    dataRes1 = {'vsm': {'SMAP': '', 'SQPT': '', 'STMAP': '', 'STQPT': ''},
                'bm25': {'SMAP': '', 'SQPT': '', 'STMAP': '', 'STQPT': ''},
                'dirichlet': {'SMAP': '', 'SQPT': '', 'STMAP': '', 'STQPT': ''}}
    types = {'bm25', 'vsm', 'dirichlet'}
    indexes = ['single', 'stem']

    for indexType in indexes:
        for processingType in types:
            queryStart = time.time()
            with open(outputResPath, 'w', encoding="UTF-8") as resultsFile:
                for queryID in sorted(queries):
                    score = {}
                    queryTerms = getQueryLexicon(queries[queryID], indexType)
                    # do a switch
                    if processingType == 'vsm' and indexType == 'single':
                        score = getVsmScore(queryTerms, sLexi, sTermList)
                    elif processingType == 'vsm' and indexType == 'stem':
                        score = getVsmScore(queryTerms, stLexi, stTermList)
                    elif processingType == 'bm25' and indexType == 'single':
                        score = BM25Score(queryTerms, sLexi, sTermList, score, 'single')
                    elif processingType == 'bm25' and indexType == 'stem':
                        score = BM25Score(queryTerms, stLexi, stTermList, score, 'stem')
                    elif processingType == 'dirichlet' and indexType == 'single':
                        score = DirichletScore(queryTerms, sLexi)
                    elif processingType == 'dirichlet' and indexType == 'stem':
                        score = DirichletScore(queryTerms, stLexi)
                    scoresSorted = OrderedDict(sorted(score.items(), key=itemgetter(1), reverse=True))
                    # only calculate top 100 docs
                    for index, doc in enumerate(scoresSorted):
                        if index < 100:
                            resultsFile.write(f"{queryID} 0 {doc} {index + 1} {scoresSorted[doc]} {processingType}\n")
            queryEnd = time.time()
            if indexType == 'single':
                dataRes1[processingType]['SQPT'] = str(queryEnd - queryStart)
            elif indexType == 'stem':
                dataRes1[processingType]['STQPT'] = str(queryEnd - queryStart)
            status, output = getstatusoutput(f"treceval.exe qrel.txt {outputResPath}")
            output = output.replace('\t', ' ')
            MAP = output.split('Exact')[-1].split(' ')[-1]
            if indexType == 'single':
                dataRes1[processingType]['SMAP'] = MAP
            elif indexType == 'stem':
                dataRes1[processingType]['STMAP'] = MAP
        score.clear()
    return dataRes1


def ShowStaticRes(dataRES1, indexType, method):
    """This function shows the result of report 1 analysis."""
    if indexType == "single":
        idx = "SMAP"
        QPT = "SQPT"
    elif indexType == "stem":
        idx = "STMAP"
        QPT = "STQPT"
    pro2Res1 = Texttable()
    pro2Res1.add_row(['-', f"{idx}", '-'])
    pro2Res1.add_row(['Retrieval Model', 'MAP', 'Time'])
    pro2Res1.add_row([f'{method}', dataRES1[method][idx], dataRES1[method][QPT]])
    print(pro2Res1.draw())


def ShowRes1(dataRES1):
    """This function shows the result of report 1 analysis."""

    pro2Res1 = Texttable()
    pro2Res1.add_row(['-', 'SINGLE', '-', 'STEM', '-'])
    pro2Res1.add_row(['Retrieval Model', 'MAP', 'Time', 'MAP', 'Time'])
    pro2Res1.add_row(
        ['vsm', dataRES1['vsm']['SMAP'], dataRES1['vsm']['SQPT'], dataRES1['vsm']['STMAP'], dataRES1['vsm']['STQPT']])
    pro2Res1.add_row(['bm25', dataRES1['bm25']['SMAP'], dataRES1['bm25']['SQPT'], dataRES1['bm25']['STMAP'],
                      dataRES1['bm25']['STQPT']])
    pro2Res1.add_row(
        ['LM_Dirichlet', dataRES1['dirichlet']['SMAP'], dataRES1['dirichlet']['SQPT'], dataRES1['dirichlet']['STMAP'],
         dataRES1['dirichlet']['STQPT']])
    print(pro2Res1.draw())


def RES2(stLexi, stTermList, pLexi, pTermList, poLexi, poTermList, queries, queryStart, outputResPath):
    """
    display of result2
    """
    idxCounter = {'phrase': 0, 'positional': 0, 'stem': 0}
    dataRes2 = {'bm25': {'PMAP': '', 'PQPT': ''}}
    with open(outputResPath, 'w', encoding="UTF-8") as resultsFile:
        for queryID in sorted(queries):
            queryTerms = getQueryLexicon(queries[queryID], 'phrase')
            # idxDecision = "phrase"
            idxDecision = makeDecision(queryTerms, pTermList)

            queryTerms = getQueryLexicon(queries[queryID], idxDecision)
            score = {}
            if idxDecision == 'phrase':
                idxCounter[idxDecision] += 1
                score = BM25Score(queryTerms, pLexi, pTermList, score, 'phrase')
            elif idxDecision == 'positional':
                idxCounter[idxDecision] += 1
                score = BM25Score(queryTerms, poLexi, poTermList, score, 'positional')
            if len(score) < 5:
                idxCounter['stem'] += 1
                idxCounter[idxDecision] -= 1
                queryTerms = getQueryLexicon(queries[queryID], 'stem')
                score = BM25Score(queryTerms, stLexi, stTermList, score, 'stem')
            scoresSorted = OrderedDict(sorted(score.items(), key=itemgetter(1), reverse=True))
            for index, doc in enumerate(scoresSorted):
                if index < 100:
                    resultsFile.write(f"{queryID} 0 {doc} {index + 1} {scoresSorted[doc]} phraseStem \n")
    queryEnd = time.time()
    dataRes2['bm25']['PQPT'] = str(queryEnd - queryStart)
    status, output = getstatusoutput(f"treceval.exe qrel.txt {outputResPath}")
    output = output.replace('\t', ' ')
    MAP = output.split('Exact')[-1].split(' ')[-1]
    dataRes2['bm25']['PMAP'] = MAP

    return idxCounter, dataRes2


def ShowRes2(dataRes2, idxCounter):
    """This report prints the result of Report 2 processing."""

    print('\n' + str(idxCounter['phrase']) + " queries processed based on phrase index.")
    print(str(idxCounter['positional']) + " queries processed based on positional index.")
    print(str(idxCounter['stem']) + " queries processed based on stem index.")
    pro2Res2 = Texttable()
    pro2Res2.add_row(['Retrieval Model', 'MAP', 'Total Time'])
    pro2Res2.add_row(['bm25', dataRes2['bm25']['PMAP'], dataRes2['bm25']['PQPT']])
    print(pro2Res2.draw())
    print("result based on qrel.txt and result file, please change qrel.txt manually")


def queryInput(queryFile):
    """
    read query
    """
    queryID = 'EMPTY'
    title = ''
    desc = ''
    narr = ''
    nextLine = ''
    queries = {}

    with open(queryFile, 'r') as queryFile:
        for line in queryFile:
            if queryID == 'EMPTY' and "<num>" in line:
                queryID = line.replace('<num> Number: ', '')
                queryID = queryID.replace('\n', '')
            elif title == '' and "<title>" in line:
                title = line.replace('<title> Topic:', '')
                title = title.replace('\n', '')
            elif desc == '' and nextLine == '':
                nextLine = 'desc'
            elif nextLine == 'desc':
                if "<narr>" in line:
                    nextLine = 'narr'
                else:
                    add = line.replace('<desc> Description:', '')
                    add = add.replace('\n', ' ')
                    desc += add
            elif nextLine == 'narr':
                if "</top>" in line:
                    add = line.replace('\n', ' ')
                    add.replace('</top>', ' ')
                    queries[queryID] = {"title": title, "desc": desc, "narr": narr}
                    queryID = 'EMPTY'
                    title = ''
                    desc = ''
                    narr = ''
                    nextLine = ''
                else:
                    add = line.replace('\n', ' ')
                    narr += add
    return queries


def getQueryLexicon(query, indexType):
    """This function builds an index of the
    term weights for the query terms. """

    terms = preprocess.processing(query, indexType)
    queryTerms = {}

    for term in terms:
        if term in queryTerms:
            queryTerms[term] += 1
        else:
            queryTerms[term] = 1

    return queryTerms


def buildDocIndex(index):
    """This function builds diction of {docID: [terms in doc]}"""
    docCounter = 0
    termByDoc = {}

    for term in index:
        for docID in index[term]:
            if docID in termByDoc:
                termByDoc[docID].append(term)
            else:
                termByDoc[docID] = [term]
                docCounter += 1
    return termByDoc, docCounter


def makeDecision(queryTerms, pTermList):
    """choose phrase or positional index."""

    sumDF = 0
    phrasesCounter = 0

    for phrase in queryTerms:
        if phrase in pTermList:
            sumDF += pTermList[phrase]
            phrasesCounter += 1

    if phrasesCounter == 0 or sumDF == 0:
        return 'positional'
    else:
        avgDF = float(sumDF) / phrasesCounter

    if avgDF > 1:
        idxDecision = 'phrase'
    else:
        idxDecision = 'positional'

    return idxDecision


# THIS IS THE SECTION WHICH HANDLES QUERY PROCESSING FOR VSM COSINE


def getVsmScore(queryTerms, index, termList):
    """ calculate COSINE score"""

    vsmScore = {}
    dictTermWeights = {}

    termsByDoc, docCounter = buildDocIndex(index)
    termsIdf = VsmIdf(termList, docCounter)

    queryTermWeights = VsmQueryTermWeight(termsIdf, queryTerms)

    for term in queryTerms:
        if term in index:
            queryTermPostingList = index[term]

            for docID in queryTermPostingList:
                if docID not in dictTermWeights:
                    dictTermWeights = VsmTermWeight(docID, termsIdf, index, termsByDoc[docID], dictTermWeights)

                if docID not in vsmScore:
                    vsmScore[docID] = queryTermWeights[term] * dictTermWeights[docID][term]
                else:
                    vsmScore[docID] += queryTermWeights[term] * dictTermWeights[docID][term]
        else:
            pass

    for docID in vsmScore:
        vsmScore[docID] = vsmScore[docID] / math.sqrt(pow(sumTermWeightOfDoc(dictTermWeights, docID), 2) * pow(
            sumTermWeightsOfQuery(queryTermWeights), 2))

    return vsmScore


def VsmIdf(termList, docCounter):
    """calculates all the term idfs."""

    termsIdf = {}
    for term in termList:
        termsIdf[term] = math.log10((float(docCounter) / termList[term]))

    return termsIdf


def getVsmTermWeight(termIdf, termFreq):
    """
        calculates the numerator of the term weight for a term in a document.
    """

    weight = (math.log(termFreq) + 2) * termIdf

    return weight


def VsmTermWeight(docID, termsIdf, index, termsInDocID, dictTermWeights):
    """
        This function calculates all the term weights for terms in a specific document.
    """

    sumTermWeightsDocID = 0
    for term in termsInDocID:
        if docID not in dictTermWeights:
            dictTermWeights[docID] = {term: getVsmTermWeight(termsIdf[term], index[term][docID])}
        else:
            dictTermWeights[docID][term] = getVsmTermWeight(termsIdf[term], index[term][docID])
        sumTermWeightsDocID += dictTermWeights[docID][term]

    for term in dictTermWeights[docID]:
        dictTermWeights[docID][term] = dictTermWeights[docID][term] / sumTermWeightsDocID

    return dictTermWeights


def sumTermWeightOfDoc(dictTermWeights, docID):
    """This calculates the sum of the term
    weights for a given document."""

    sumWeights = 0
    for term in dictTermWeights[docID]:
        sumWeights += dictTermWeights[docID][term]

    return sumWeights


def sumTermWeightsOfQuery(queryTermWeights):
    """This is the sum of the term weights in the query."""

    sumWeights = 0
    for term in queryTermWeights:
        sumWeights += queryTermWeights[term]

    return sumWeights


def VsmQueryTermWeight(termsIdf, queryTerms):
    """This is the function that builds the term weights
    of the query terms."""

    sumTermWeightsQuery = 0
    queryTermWeightsDict = {}

    for term in queryTerms:
        if term in termsIdf:
            queryTermWeightsDict[term] = getVsmTermWeight(termsIdf[term], queryTerms[term])
        else:
            queryTermWeightsDict[term] = getVsmTermWeight(1, queryTerms[term])
        sumTermWeightsQuery += queryTermWeightsDict[term]

    # Normalization
    for term in queryTermWeightsDict:
        queryTermWeightsDict[term] = queryTermWeightsDict[term] / sumTermWeightsQuery

    return queryTermWeightsDict


"""THIS IS THE SECTION WHICH HANDLES QUERY PROCESSING FOR BM-25"""


def BM25Score(queryTerms, index, termList, score, indexType):
    """This is the main function which produces the BM25 score."""

    if indexType == 'positional':
        score = PositionalBM25(queryTerms, index, termList, score, indexType)
        return score
    k1 = 1.2
    k2 = 1000
    b = 0.75

    docLength, avgLength, docCounter = buildBM25DocLength(index, indexType)
    for term in queryTerms:
        if term in index:
            termWeight = getBM25Weight(termList, term, docCounter)
            B = ((k2 + 1) * queryTerms[term]) / float(k2 + queryTerms[term])
            queryTermPostingList = index[term]

            for docID in queryTermPostingList:
                A = ((k1 + 1) * index[term][docID]) / float(
                    index[term][docID] + k1 * (1 - b + b * (docLength[docID] / avgLength)))
                if docID not in score:
                    score[docID] = termWeight * A * B
                else:
                    score[docID] += termWeight * A * B
        else:
            pass

    return score


def PositionalBM25(queryTerms, index, termList, score, indexType):
    """This is the BM25 for the positional index, as the positional
    does not have tf but the positions stored so has to 
    be processed slightly differently."""

    k1 = 1.2
    k2 = 500
    b = 0.75

    docLength, avgLength, docCounter = buildBM25DocLength(index, indexType)
    for term in queryTerms:
        if term in index:
            termWeight = getBM25Weight(termList, term, docCounter)
            B = ((k2 + 1) * queryTerms[term]) / float(k2 + queryTerms[term])
            queryTermPostingList = index[term]

            for docID in queryTermPostingList:
                A = ((k1 + 1) * len(index[term][docID])) / float(
                    len(index[term][docID]) + k1 * (1 - b + b * (docLength[docID] / avgLength)))

                if docID not in score:
                    score[docID] = termWeight * A * B
                else:
                    score[docID] += termWeight * A * B
        else:
            pass

    return score


def getBM25Weight(termList, term, docCounter):
    termWeight = math.log((docCounter - termList[term] + 0.5) / (termList[term] + 0.5))
    return termWeight


def buildBM25DocLength(index, indexType):
    sumDocLen = 0
    docCounter = 0
    docLength = {}

    if indexType != "positional":
        for term in index:
            for docID in index[term]:
                sumDocLen += index[term][docID]
                if docID in docLength:
                    docLength[docID] += index[term][docID]
                else:
                    docLength[docID] = index[term][docID]
                    docCounter += 1
    elif indexType == "positional":
        for term in index:
            for docID in index[term]:
                sumDocLen += len(index[term][docID])
                if docID in docLength:
                    docLength[docID] += len(index[term][docID])
                else:
                    docLength[docID] = len(index[term][docID])
                    docCounter += 1
    avgLength = float(sumDocLen) / docCounter

    return docLength, avgLength, docCounter


# Dirichlet Smoothing

def DirichletScore(queryTerms, index):
    dirichletScore = {}
    docLength, avgLength, collectLen = buildDirichletDocCollectionLength(index)
    tfCollection = buildTfInCollection(index)
    miu = 500

    for term in queryTerms:
        if term in index:
            queryTermPostingList = index[term]
            for docID in queryTermPostingList:

                numerator = index[term][docID] + ((miu * float(tfCollection[term])) / collectLen)
                denominator = docLength[docID] + miu

                if docID not in dirichletScore:
                    # dirichletScore[docID] = math.log((float(numerator) / denominator))
                    dirichletScore[docID] = (float(numerator) / denominator)
                else:
                    # dirichletScore[docID] += math.log((float(numerator) / denominator))
                    dirichletScore[docID] = (float(numerator) / denominator)
        else:
            pass

    return dirichletScore


def buildDirichletDocCollectionLength(index):
    """This function builds the document
    lengths for all the documents in the collection."""

    collectLen = 0
    docCounter = 0
    docLength = {}

    for term in index:
        for docID in index[term]:
            collectLen += index[term][docID]
            if docID in docLength:
                docLength[docID] += index[term][docID]
            else:
                docLength[docID] = index[term][docID]
                docCounter += 1
    avgLength = float(collectLen) / docCounter

    return docLength, avgLength, collectLen


def buildTfInCollection(index):
    """This function builds the collection
    frequency for all the terms in the collection. """

    tfCollection = {}

    for term in index:
        for docID in index[term]:
            if term in tfCollection:
                tfCollection[term] += index[term][docID]
            else:
                tfCollection[term] = index[term][docID]

    return tfCollection
