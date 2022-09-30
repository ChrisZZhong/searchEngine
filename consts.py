## Dates 2005; Oct 10, 2005;
import regex

DATE1 = '\d{2}[/-]\d{1,2}[/-]\d{2,6}'  # 10/10/05  or 10/10/2005 or 10-10-2005

DATE2 = '\S{3,9}[.]*[ ]\d{1,2}[,][ ]\d{4}'  # Aug(.) 28, 2008 or December, 2009

digAlpha = '(([0-9]+)[-]([a-z]+))+'  # F-16

alphaDig = '(([a-z]+)[-]([0-9]))+'  # 1-hour

zeroTrailingDigit = '\d+[.][0-9]+'

abbrevTwo = "\\b(?:[a-zA-Z]+\\.){2,}"  # M.S.

abbrev = "\\b(?:[a-zA-Z]+\\.){1,}[a-z]$"  # ph.d

files = '(\w+)[.](pdf|html|doc|xls)'

periodEnd = '[.][ ]|[.][\n]|[.]$'

ip = '(\d{2,3}[.]\d{2,3}[.]\d{2,3}[.]\d{2,3})'  # 123.67.65.870

url = '[www.]\w+[.](com|edu|net)'  # http://www.cnn.com

email = '[\w]+@[\w]+[.]'  # mouse@hotmail.com

hyphenated = '([a-z]+)[-]([a-z]+)'

digit = '[0-9]+'

specialCharacter = '[>|,|/|%|=|+|<|#|^|(|)|:|;|`|\[|\]|?|\*|␣|§|&|×|\']'

percentage = '[%](\D)'

start_of_heading = '\x01'
