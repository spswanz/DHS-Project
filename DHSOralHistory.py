### DHS Project 67 Oral Histories

### Purpose:
# Retrieve webpage (transcript and other metadata) for each story and save as pdf. Pdfs will save in same folder
# where running this program.

### Requirements:
# uses Python 3 on Mac/Unix
# requires these packages to be installed
import requests
from bs4 import BeautifulSoup
import pdfkit   # uses wkhtmltopdf
import pickle

## Part 1: create list of hrefs to individual story pages

base_url = 'http://detroit1967.detroithistorical.org/items/browse'
params = {'page': 1}
r = requests.get(base_url, params = params)
soup = BeautifulSoup(r.text, 'html.parser')

interviewlist = []   # list of links formatted "/items/show/###"

for page in range(17): # website indicates there are 17 pages to page thru, will need to change parameter if more added
    r = requests.get(base_url, params = params)
    soup = BeautifulSoup(r.text, 'html.parser')
    for tag in soup.find_all("div", class_="item hentry"):
        for person in tag.find_all("a", class_="permalink"):
            interviewlist.append(person.attrs['href'])
    params['page'] += 1

print("Total pages: " + str(len(interviewlist)))  # confirm number of story webpages


# Part 2: Loop through interview list and generate pdf from each webpage

base_url = 'http://detroit1967.detroithistorical.org'
tot = 0
video_embed_list = []
std_options = {                     # options for conversion using pdfkit
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'no-outline': None,
    'dpi' : "400",
    'disable-plugins': None,
}
video_embed_options  = {
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'no-outline': None,
    'dpi' : "400",
    'enable-plugins': None,  # important for pages with embedded video
}

cache_fname = 'url_cache.txt' # cache urls of completed pages to this file
try:
    saved_cache = pickle.load(open(cache_fname, "rb"))
except:
    saved_cache = []

# to test file for embedded video page use interviewlist = ["/items/show/59"]

for ref in interviewlist:
    full_url = base_url + ref
    # create pdfs of new urls only and add new url to cache
    if full_url in saved_cache:
        print("Pdf already created for " + full_url)
    else:
        r = requests.get(full_url, headers = {'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, 'html.parser')
        # locate name of interviewee using HTML tags and CSS ids, classes
        for tag in soup.find_all("div", id = "dublin-core-title"):
            for title in tag.find_all("div", class_="element-text"):
                name = title.text
                outfile = str(name) + ".pdf"  # change name of outfile per interviewee
                if soup.find_all("div", id="oral-history-item-type-metadata-video"):
                    # need to set options differently for pages with embedded video
### THERE ARE TWO WAYS TO HANDLE PAGES WITH EMBEDDED VIDEO
    #Option 1: creates pdf, but crashes program and won't loop thru remaining pages
                #    pdfkit.from_url(full_url, outfile, options=video_embed_options)
    #Option 2: does not create pdf, but will loop thru remaining pages and identifies which pages did not print
                    video_embed_list.append(name)
                else:
                    pdfkit.from_url(full_url, outfile, options=std_options)
                tot += 1
                saved_cache.append(full_url)
                print("New pdf created for " + full_url)
pickle.dump(saved_cache, open(cache_fname, "wb"))
print("You converted " + str(tot) + " pages to pdf.")
print("Pdfs NOT created for the following pages with embedded video: ", video_embed_list)
