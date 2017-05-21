from bs4 import BeautifulSoup
import bs4
import requests
from collections import defaultdict,OrderedDict
import re
from anytree.dotexport import RenderTreeGraph
from anytree import Node, RenderTree
import locale
import home
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def freq_dict(lst):
    fq = defaultdict(int)
    for item in lst:
        fq[item] += 1
    return sorted(fq.iteritems(), key=lambda (k, v): v, reverse=False)

def drink_soup(url):
    r = requests.get(url, headers={'user-agent': 'My app'}) #Fake header bypasses some redirects
    data = r.text
    soup = BeautifulSoup(data, 'lxml')
    return soup

def find_common_classes(url=None, soup=None, flatten=False):
    if soup is None:
        if url is None:
            raise ValueError("url or soup must be specified")
        soup = drink_soup(url)
    divs = soup.find_all('div')
    class_list = [div.get('class') for div in divs if div.get('class') is not None]
    if flatten:
        class_to_class_list_map = {item:item for sublist in class_list for item in sublist}
        classes = [item for sublist in class_list for item in sublist]
    else:
        class_to_class_list_map = {','.join(item): item for item in class_list}
        classes = [','.join(item) for item in class_list]
    return freq_dict(classes),class_to_class_list_map

def find_common_text(soup, which_class = None):
    divs = soup.find_all('div', which_class)
    text_list = [div.getText() for div in divs]
    return freq_dict(text_list)

def find_common_id_bases(soup, which_class = None):
    divs = soup.find_all('div', which_class)
    id_list = [div.get('id') for div in divs if div.get('id') is  not None]
    id_list_common = [re.sub("\d+", "X",item) for item in id_list]
    return freq_dict(id_list_common)

def find_common_parent_classes(soup, which_class = None, all=False, flatten=False):
    divs = soup.find_all('div', which_class)
    if all:
        class_list = [parent.get('class') for div in divs for parent in div.parents if parent.get('class') is not None]
    else:
        class_list = [div.parent.get('class') for div in divs if div.parent.get('class') is not None]
    if flatten:
        classes = [item for sublist in class_list for item in sublist]
    else:
        classes = [','.join(item) for item in class_list]
    return freq_dict(classes)

def find_parent_rules(soup, which_class):
    divs = soup.find_all('div', which_class) # TODO: Rewrite to avoid this redundancy
    common_parent_classes = find_common_parent_classes(soup, which_class, False, False)
    #TODO: Finish if this even makes sense. 'always' rule is really just len(common_parent_classes)==1.

def find_next_split(soup, id, which_class=""):
    divs = soup.find_all("div", which_class, id=id)
    #TODO: Add check for len(divs)==1
    div = divs[0]
    print(div)
    prefix = "--"
    while len(list(div.children)) == 1:
        div=list(div.children)[0]
        print(prefix + str(div))
        prefix += "--"
    return div


def find_next_split(tag):
    print(tag)
    prefix = "--"
    while len(list(tag.children)) == 1:
        tag=list(tag.children)[0]
        print(prefix + str(tag))
        prefix += "--"
    return tag

def find_base_info(tag, prefix="", parent=None):
    prefix += "--"
    children = list(tag.children)
    if len(children)==1 and type(children[0]) in (bs4.element.NavigableString,bs4.element.Comment) :
        #try:
        #text=str(children[0].encode("utf-8").strip())
        text=children[0]
        #text=str(children[0])
        #except:
            #text="-"
        new_node = Node(text, parent)
        #print(prefix+text)
    else:
        new_node = Node("", parent)
        #print(prefix)
        for child in children:
            if getattr(child, "children", None) is not None:
                find_base_info(child, prefix, new_node)
    return new_node

def print_tree(tree):
    for pre, fill, node in RenderTree(tree):
        print("%s%s" % (pre, node.name))

url = "https://www.redfin.com/neighborhood/157585/IL/Chicago/Lakeview"
soup = drink_soup(url)
#common_classes,class_to_class_list_map = find_common_classes(url)
#common_ids = find_common_id_bases(soup)

#common_classes.sort(key=lambda x: x[1], reverse=True)
#single_parent_classes = OrderedDict()
#for common_class in common_classes:
#    parent_classes = find_common_parent_classes(soup, class_to_class_list_map[common_class[0]])
#    if len(parent_classes)==1:
#        single_parent_classes[common_class] = parent_classes[0][0]

homes = soup.find_all(class_="HomeCardV2 card-frame")
home_ex = homes[0]
home_tree = find_base_info(home_ex, "--")
print_tree(home_tree)
RenderTreeGraph(home_tree).to_picture("test.png")

def get_facts(tree):
    facts = []
    for pre, fill, node in RenderTree(home_tree):
        if node.name!="":
            for sibling in node.siblings:
                if sibling.name!="":
                    facts.append(tuple(sorted((node.name,sibling.name), cmp=locale.strcoll, reverse=True)))
    facts = list(set(facts))
    return facts


#--------------- End of current attempt

#h_divs = [div for div in soup.find_all('div') if div.get("class") is not None and "HomeCardV2" in div.get('class')]

#cols = soup.find_all(string=re.compile("606"))
#col = cols[0]
#while True:
#    print col
#    if col.parent is None:
#        break
#    col = col.parent
#    raw_input()



    #for link in soup.find_all('a'):
#    print(link.get('href'))

#from lxml import html
#tree = html.fromstring(r.content)

#from selenium import webdriver
#path_to_chromedriver = '/usr/local/bin/chromedriver'
#browser = webdriver.Chrome(executable_path = path_to_chromedriver)
#browser.get(url)

#import urllib2
#html = urllib2.urlopen('"http://www.realtor.com/realestateandhomes-search/Chicago_IL').read()
#print 'js-record-user-activity js-navigate-to srp-item listing-turbo' in html # -> True