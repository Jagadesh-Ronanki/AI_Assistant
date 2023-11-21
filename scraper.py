import re
import urllib
import requests
import wikipedia
from helium import *
from bs4 import BeautifulSoup
import urllib.request as urllib2


class Scraper:
    def __init__(self,text):
        self.text = text

    def definition(self):
        definition = wikipedia.summary(self.text,sentences=3)
        return definition

    def resources(self):
        self.text = urllib.parse.quote_plus(self.text)  # avl+trees
        url = 'https://google.com/search?q='+self.text 
        response = requests.get(url)
        soup = BeautifulSoup(response.text,'lxml')
        sources = dict()
        for a in soup.find_all('a'):
            href = a.get('href')
            if '/url' in href:
                source = href[7:]
                source = source.partition('&')[0]
                domain = ''.join(re.findall(r'(?<=\.)([^.]+)(?:\.(?:co\.uk|ac\.us|[^.]+(?:$|\n)))',source))
                if('/' not in domain and domain!='google'):
                    try:
                        sources[domain].append(source)
                    except KeyError:
                        sources[domain] = [source]
        return sources
    
    def mcqs(self):
        self.text = 'sandford mcqs '+self.text
        text = urllib.parse.quote_plus(self.text)
        url = 'https://google.com/search?q='+text
        response = requests.get(url)
        soup = BeautifulSoup(response.text,'lxml')
        for a in soup.find_all('a'):
            href = a.get('href')
            if '/url' in href:
                sanfoundry = href[7:]
                sanfoundry = sanfoundry.partition('&')[0]
                break
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        resource = opener.open(sanfoundry)
        data = resource.read()
        soup = BeautifulSoup(data,'lxml')

        text=soup.text
        '''print(text)'''
        answers_list = re.findall(r'(?<=: )(.?)(?:$|\n)',text,flags=re.IGNORECASE)
        explaination_list = re.findall(r'Explanation: [^\n]*',text,flags=re.IGNORECASE)
        COUNTER = 0
        tag = soup.find_all('p')
        mcqs = dict()     
        for p in tag[1:len(tag)-3]:
            value = p.text
            if(re.match(r'\d+\.',value)):
                values = value.split('\n')
                try:
                    values.remove('View Answer')
                    values.append(answers_list[COUNTER])
                    values.append(explaination_list[COUNTER])
                except:
                    pass
                if(len(values)>1):
                    if(len(values)==7):
                        mcqs[values[0]] = {'options':[values[1],values[2],values[3],values[4]], 'answer':values[5], 'explain':values[6]}
                    elif(len(values)==5):
                        mcqs[values[0]] = {'options':[values[1],values[2]], 'answer':values[3], 'explain':values[4]}
                    COUNTER+=1
            else:
                COUNTER+=1
        # get google forms link and send it to user
        return mcqs


class ScheduledTasks:
    #------------ CODECHEF ---
    q_href = []
    def __init__(self):
        self.url='https://www.codechef.com/problems/school/?sort_by=Accuracy&sorting_order=desc'
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    def Scrape_link(self):
        resource = self.opener.open(self.url)
        data = resource.read()
        soup = BeautifulSoup(data, 'lxml')
        for div in soup.find_all('div',class_='problemname'):
            ScheduledTasks.q_href.append((div.b.text, 'https://www.codechef.com/'+div.a['href']))


    def Scrape_problem(count):
        Pname = ScheduledTasks.q_href[0][0]
        Purl = ScheduledTasks.q_href[0][1]
        browser = helium.start_firefox(Purl, headless=True)
        soup = BeautifulSoup(browser.page_source, 'lxml')
        print(soup.title.text)
        print()
        problem = soup.find('div', id='problem-statement')
        heads = [(i.text).lower() for i in problem.find_all('h3')]
        d = dict.fromkeys(heads)
        d['para'] = None

        key = 'para'
        i = -1
        prev = '-2'
        finalString = ''
        for string in problem.strings:
            if (string != 'Input' or string != 'Constraints'):
                if (string == '\n'): continue
                if (prev == string): continue
                prev = string
                if (string == 'Author:'):
                    d[key] = finalString
                    break
                if (string.lower() not in d.keys()):
                    finalString += string
                else:
                    d[key] = finalString
                    i += 1
                    key = heads[i]
                    finalString = ''
            else:
                if (string.lower() not in d.keys()):
                    finalString += string
                else:
                    d[key] = finalString
                    i += 1
                    key = heads[i]
                    finalString = ''

        if('sample input' in d.keys()): d['sample input'] = d['sample input'].split('\n')
        if('sample output' in d.keys()): d['sample output'] = d['sample output'].split('\n')

        submit = soup.find('a', class_='button blue mathjax-support')
        submit_link = 'https://www.codechef.com' + submit['href']
        ScheduledTasks.q_href.pop(0)

        problem = d

        while count>0:
            for key, values in problem.items():
                if type(values) == list:
                    print(key)
                    for val in values:
                        print(val)
                else:
                    print(key)
                    print(values)
                print()
            count -= 1
            print("Wanna Submit? Please login and try your code here ", submit_link)
            print('-' * 30)
    #--------------------------------------------------------------------------

#o = Scraper('avl trees')
#print(o.mcqs())

'''
#---------------------------------------------------
# Extract definition of search term from wiki
#---------------------------------------------------
text='avl trees'
definition = wikipedia.summary(text,sentences=3)

#---------------------------------------------------
# send request and parse search result page
#---------------------------------------------------
text = urllib.parse.quote_plus(text)  #avl+trees
url = 'https://google.com/search?q='+text 
response = requests.get(url)
soup = BeautifulSoup(response.text,'lxml')

#---------------------------------------------------
# get top 10 links from search into dict sources={}
#---------------------------------------------------
sources = dict()
for a in soup.find_all('a'):
    href = a.get('href')
    if '/url' in href:
        source = href[7:]
        source = source.partition('&')[0]
        domain = ''.join(re.findall(r'(?<=\.)([^.]+)(?:\.(?:co\.uk|ac\.us|[^.]+(?:$|\n)))',source))
        if('/' not in domain and domain!='google'):
            try:
                sources[domain].append(source)
            except KeyError:
                sources[domain] = [source]
'''
'''
#---------------------------------------------------
# scrape mcqs and options and answer
# [ {Question: {options:bool}} ]
#---------------------------------------------------
url = 'https://www.sanfoundry.com/data-structure-questions-answers-avl-tree/'
#url='https://www.sanfoundry.com/minimum-spanning-tree-multiple-choice-questions-answers-mcqs/'
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
resource = opener.open(url)
data = resource.read()
soup = BeautifulSoup(data,'lxml')
'''
'''EXTRACTION OF ANSWERS'''
'''
text=soup.text
answers_list = re.findall(r'(?<=: )(.?)(?:$|\n)',text,flags=re.IGNORECASE)
'''
'''{ QUESTION:{OPTIONS:[A.STRING,B.STRING,C.STRING,D.STRING], ANSWER:CORRECT_OPTION, EXPLAIN:UNDER_DEV} }'''
'''
COUNTER = 0
tag = soup.find_all('p')
mcqs = dict() 
'''
'''
for p in tag[1:len(tag)-3]:
    value = p.text
    if(re.match(r'\d+\.',value)):
        values = value.split('\n')
        try:
            values.remove('View Answer')
            values.append(answers_list[COUNTER])
        except:
            pass
        if(len(values)>1):
            if(len(values)==6):
                mcqs[values[0]] = {'options':[values[1],values[2],values[3],values[4]], 'answer':values[5], 'explain':None}
            elif(len(values)==4):
                mcqs[values[0]] = {'options':[values[1],values[2]], 'answer':values[3], 'explain':None}
            COUNTER+=1
    else:
        COUNTER+=1

print(mcqs)
'''

'''DYNAMIC WEBPAGES SCRAPE CODE'''

'''
import urllib
import urllib2
from BeautifulSoup import BeautifulSoup

article= "Albert Einstein"
article = urllib.quote(article)

opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')] #wikipedia needs this

resource = opener.open("http://en.wikipedia.org/wiki/" + article)
data = resource.read()
resource.close()
soup = BeautifulSoup(data)
print soup.find('div',id="bodyContent").p
'''