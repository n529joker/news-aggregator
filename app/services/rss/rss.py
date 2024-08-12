import requests
from bs4 import BeautifulSoup
import json
import os, sys
import asyncio

current_file_path = os.path.abspath(__file__)


class ProcessLocalFeeds:
    def __init__(self, filePath, fileFormat = 'xml') -> None:
        
        if os.path.exists(filePath):
            f = open(filePath, "rb") #We consider it to be a file
            doc = f.read()
            
        self.soup = BeautifulSoup(doc, 'lxml')

        if(self.soup.rss):
            self.handleRss()
        
        elif(self.soup.feed):
            self.handleFeed()
        
        assert(self.soup), "Invalid file format"

        f.close()

    def handleRss(self):
        items = self.soup.find_all("item")

        for item in items:
            title = item.title.text
            link = item.link.text
            
            desc = BeautifulSoup(str(item), 'lxml')
            new_desc = BeautifulSoup(str(desc.encoded.text), 'xml')
            
            final_desc = new_desc.find('p')

            print(f"This is the description : \n\n\t {final_desc.text}")
            
            print("\n\n------------------\n\n")
            # print(f"Page Title: {title} \n\nLink : {link} \n\nDescription : {desc}\n\n------------------\n")   

    def handleFeed(self):
        items = self.soup.find_all("entry")

        for item in items:
            title = item.title.text
            link = item.link['href']
            print(f"Page Title: {title} \nLink : {link} \n------------------\n")    


class ProcessFeed:

    def __init__(self, url: str, source_id: int) -> None:
        self.url = url
        self.source_id = source_id

    async def launch(self):
        result = await self.fetch_url(self.url)
        status, response = result["status"], result["response"]
        assert(status), response
            
        self.soup = BeautifulSoup(response, features='lxml-xml')

        if(self.soup.rss):
            await self.handleRss()
        
        elif(self.soup.feed):
            await self.handleFeed()
        
        assert(self.soup), "Invalid file format"


    async def fetch_url(self, page_url):
        try:
            response = requests.get(page_url)
            response.raise_for_status()
            
            # Handle the response based on the status code
            if response.status_code == 200:
                return {'status': True, "response": response.content}
            
            elif response.status_code == 404:
                return {'status': False, "response": "Page not found"}
                
            elif response.status_code == 500:
                return {'status': False, "response": "Server error"}
                
            else:
                return {'status': False, "response": "unexpected status code"}
            
        except Exception as exc:
            return {"status": False, "response": exc}


    async def handleRss(self):
        items = self.soup.find_all("item")

        for item in items:
            item_object = {
                'title' : item.title.text,
                'link' : item.link.text,
                'pub_date' : item.pubDate.text,
                'body' : item.description.text
            }

            print(item_object)
            

    async def handleFeed(self):
        items = self.soup.find_all("entry")

        for item in items:
            title = item.title.text
            link = item.link['href']

    async def saveContent(): 
        type = 'Text'
        image_url = None
    



def saveSources(data):
    fp = open(os.path.join(current_file_path, '..', 'assets', 'sources.json'), "+w")
    
    fp.write(json.dumps(data))
    fp.close()


async def main():
    sources_url = "http://127.0.0.1:8000/sources/"
    my_sources = requests.get(sources_url)

    if my_sources.status_code == 200:
        data = my_sources.json() 

        print(type(data))

        for dt in data:
            print(dt['id'])
            processFeed = ProcessFeed(dt['url'], dt['id'])
            await processFeed.launch()
        
            
if __name__ == '__main__':
    asyncio.run(main())


