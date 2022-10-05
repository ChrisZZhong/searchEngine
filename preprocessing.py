from datetime import datetime
from nltk.stem import PorterStemmer

import regex as re

from htmlParser import Parser
import consts


def read_collection(file_path):
    """This function takes a single file and returns a list of strings. Each
    string is a document (between opening and closing <DOC> tags."""

    with open(file_path, 'r') as wholeFile:
        text = wholeFile.read()
        text = text.replace('</DOC>', '</DOC> BREAK_NEW_DOC')
        documents = text.split('BREAK_NEW_DOC')
    return documents


def readFile(filePath):
    """
    :param filePath: read from file path and return the text lower cases
    :return: lower cases after case folding
    """
    f = open(filePath, 'r')
    text = f.read()
    f.close()
    text = text.lower().replace(". ", " ").replace("\n", " ")
    return text


## For html parser
def getDocId(text):
    parser = Parser()
    parser.feed(text)
    return parser.getDocId()


def getFilterData(text):
    parser = Parser()
    parser.feed(text)
    return parser.getFilterData()


def getStopWords():
    stopWordText = readFile("./stops.txt")
    stopWords = splitByType(stopWordText, "term")
    stopWordDict = set()
    for word in stopWords:
        if (word not in stopWordDict) and word:
            stopWordDict.add(word)
    return stopWordDict


################################ common
def normalizeDate(token):
    # normalize (%m/%d/%Y or %m-%d-%Y) and remove invalid dates
    matchedDate1 = re.findall(consts.DATE1, token)
    for obj in matchedDate1:
        try:
            if valid_date(obj):
                time_format = datetime.strptime(obj, '%m/%d/%Y')
                token = re.sub(obj, (datetime.strftime(time_format, '%m:%d:%Y')), token)
            else:
                token = re.sub(obj, " STOP ", token)
        except:
            pass
    # normalize (January 4, 1994)
    matchedDate2 = re.findall(consts.DATE2, token)
    for obj in matchedDate2:
        try:
            time_format = datetime.strptime(obj, '%B %d, %Y')
            token = re.sub(obj, (datetime.strftime(time_format, '%m:%d:%Y')), token)
        except:
            pass
    return token


def valid_date(dateString):
    try:
        if re.match("(0\d|1[0-2])[/.-]([0-2]\d|3[01])[/.-]([12]\d{3})", dateString):
            ## MM-DD-YYYY
            return True
    except ValueError:
        return False


def normalizeDigAlpha(token, Type):
    # normalize Dig-Alpha
    matches = re.findall(consts.digAlpha, token)
    for obj in matches:
        try:
            if Type == "term":
                token = re.sub(consts.digAlpha, obj[1] + obj[2], token)
            else:
                token = re.sub(consts.digAlpha, " STOP ", token)
        except:
            pass
    # normalize Alpha-Dig
    matches = re.findall(consts.alphaDig, token)
    for obj in matches:
        try:
            if Type == "term":
                token = re.sub(consts.alphaDig, obj[1] + obj[2], token)
            else:
                token = re.sub(consts.alphaDig, " STOP ", token)
        except:
            pass
    return token


def normalizeDigit(token, Type):
    # normalize XXX.000 to XXX
    if Type == "phrases":
        token = re.sub(consts.zeroTrailingDigit, " STOP ", token)
        token = re.sub(consts.digit, " STOP ", token)

    elif Type == "term":
        matches = re.findall(consts.zeroTrailingDigit, token)
        for obj in matches:
            try:
                token = re.sub(consts.zeroTrailingDigit, obj.split(".")[0], token)
            except:
                pass
    return token


def splitByType(text, Type):
    if Type == "term":
        return text.split(" ")
    elif Type == "phrases":
        text = re.sub('[ ]+', ' ', text)
        return text.split("STOP")


def removeOrReplaceSpecialCharacters(text, Type):
    if Type == "term":
        try:
            text = re.sub(consts.specialCharacter, " ", text)
        except:
            pass
    elif Type == "phrases":
        try:
            text = re.sub(consts.specialCharacter, " STOP ", text)
        except:
            pass
    return text


def normalizePeriod(token, Type):
    if "." in token:
        if re.findall(consts.periodEnd, token):
            if Type == "phrases":
                return re.sub(consts.periodEnd, " STOP ", token)
            else:
                return token[:-1]
        elif re.findall(consts.ip, token) or re.findall(consts.url, token) or re.findall(consts.email, token):
            if Type == "term":
                return token
            else:
                token = re.sub(consts.ip, " STOP ", token)
                token = re.sub(consts.url, " STOP ", token)
                token = re.sub(consts.email, " STOP ", token)
                return token
        elif re.findall(consts.files, token):
            if Type == "term":
                return re.sub(consts.files, r'\2', token)
            else:
                return re.sub(consts.files, r'\1\2', token)
        elif re.findall(consts.abbrev, token) or re.findall(consts.abbrevTwo, token):
            if Type == "term":
                return token.replace(".", "")
            else:
                token = re.sub(consts.abbrev, " STOP ", token)
                token = re.sub(consts.abbrevTwo, " STOP ", token)
                return token
    return token


def normalizeHyphenated(token, Type):
    if re.findall(consts.hyphenated, token):
        if Type == "term":
            return list(re.findall(consts.hyphenated, token)[0])
        else:
            matches = re.findall(consts.hyphenated, token)
            for obj in matches:
                try:
                    token = re.sub(consts.hyphenated, "".join(obj), token)
                except:
                    pass
    return token


def dropEmpty(tokens):
    return [token for token in tokens if token]


###########################################
# single term
def caseFolding(tokens, Type):
    """

    :param tokens: terms
    :param Type: single
    :return: token after case folding
    """
    tokenResult = []
    if Type == "term":
        for token in tokens:
            # Dig-Alpha and Alpha-Dig
            token = normalizeDigAlpha(token, Type)
            # Digit 100.000->100
            token = normalizeDigit(token, Type)
            # email/url/ip and endPeriod and abbreviation
            token = normalizePeriod(token, Type)
            # pre-process -> preprocess and pre/process
            token = normalizeHyphenated(token, Type)
            if type(token) == str:
                tokenResult.append(token)
            if type(token) == list:
                for i in token:
                    tokenResult.append(i)

    return tokenResult


# phrases
def cleaningTextForPhrases(text, Type):
    text = normalizeDigAlpha(text, Type)
    text = normalizeDigit(text, Type)
    text = normalizePeriod(text, Type)
    text = replaceStopWord(text)
    text = removeOrReplaceSpecialCharacters(text, Type)
    text = normalizeHyphenated(text, Type)
    return text


def replaceStopWord(text):
    stopWordSet = getStopWords()
    for stop in stopWordSet:
        text = text.replace(f" {stop} ", " STOP ")
    return text


def identify2_3termPhrases(tokens):
    res = []
    for token in tokens:
        token = token.strip()
        # recognize useful phrases
        if len(token) > 1:
            res.append(token)
    return res


def getStemWord(tokens):
    """
    use porter stemmer library to get stem word
    :return:
    """
    res = []
    ps = PorterStemmer()
    for phrase in tokens:
        words = phrase.split()
        for word in words:
            res.append(ps.stem(word))
    return res


def processPipLine(text, Type):
    # get data
    # docId = getDocId(text)
    # process data

    text = normalizeDate(text)  # date may exist AUG 4, 2023 (many spaces between)
    if Type == "phrases":
        text = cleaningTextForPhrases(text, Type)
        tokens = splitByType(text, Type)
        tokens = identify2_3termPhrases(tokens)
    elif Type == "term":
        text = removeOrReplaceSpecialCharacters(text, Type)
        tokens = splitByType(text, Type)
        tokens = caseFolding(tokens, Type)
    elif Type == "stem":
        text = cleaningTextForPhrases(text, "phrases")
        tokens = splitByType(text, "phrases")
        tokens = getStemWord(tokens)
    elif Type == "position":
        text = removeOrReplaceSpecialCharacters(text, "term")
        tokens = splitByType(text, "term")
        tokens = caseFolding(tokens, "term")
        tokens = getSingle(tokens)
    tokens = dropEmpty(tokens)
    return tokens


def getSingle(singlePotentialTerms):
    res = []
    stops = getStopWords()
    for term in singlePotentialTerms:
        if term not in stops:
            res.append(term)
    return res


def getTokens(doc, Type):
    # get Token by type

    text = doc.lower().replace(". ", " ").replace("\n", " ")
    docId = getDocId(text)
    text = getFilterData(text)
    # tokens[term, term not include stop word, phrases, stem]
    tokens = processPipLine(text, Type)
    return tokens, docId
