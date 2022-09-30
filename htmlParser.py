from html.parser import HTMLParser


class Parser(HTMLParser):
    """
        parser text of file and return the useful content
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.docID = ''
        self.status = ''
        self.filterData = ""

    def getDocId(self):
        return self.docID

    def handle_starttag(self, tag, attrs):
        self.status = tag
        # print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        self.status = ''
        # print("Encountered an end tag :", tag)

    def handle_data(self, data):
        # print("Encountered some data  :", data[:5])
        if self.status == "docno":
            self.docID = data.strip()
        elif self.status == "text":
            self.filterData += data


    def getFilterData(self):
        return self.filterData

