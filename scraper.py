from bs4 import BeautifulSoup
import concurrent.futures
import requests

class LinkDownloader:

    def __init__(self, numberOfThreads,mustHave):
        self.numberOfThreads = numberOfThreads
        self.mustHave = mustHave
    def getLinks(self,url):
        # print("url:",url)
        links = []
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data,"html.parser")
        for link in soup.find_all('a'):
            links.append(link.get('href'))
        returnValue = []
        # print(links)
        for link in links:
            # print(link,self.mustHave)
            if link is None:
                pass
            else:
                if link.startswith(self.mustHave):
                    returnValue.append(link)
                    # print(link)
        # print(list(set(returnValue)))
        return list(set(returnValue))


    def getLinksInPool(self,urlList):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.numberOfThreads) as executor:
            # Start the load operations and mark each future with its URL
            future_to_url = {executor.submit(self.getLinks, url): url for url in urlList}

            data = []
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                a = list(set(future.result()))
                # print("a:",a)
            data.extend(a)
            return list(set(data))



def getLinks(url):
    links = []
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data,"html.parser")
    for link in soup.find_all('a'):
        links.append(link.get('href'))

    return links

def cleanLinks(UrlList,mustHave):
    returnValue = []
    for link in UrlList:
        if link is None:
            pass
        else:
            if link.startswith(mustHave):
                returnValue.append(link)
    return returnValue

def searchInLinks(UrlList,terms):
    returnValue = []
    for link in UrlList:
        print(terms,link)
        if link is None:
            pass
        else:
            for item in terms:
                if item in link:
                    returnValue.append(link)
    return returnValue

# https://www.hasznaltauto.hu/szemelyauto/toyota/yaris/toyota_yaris_1_33_terra_plusz_99000kmgyarifeny1tulajmo-i-13144077

originalURL = "https://www.hasznaltauto.hu/talalatilista/PDNG2U23R2VTADG5JMLDAAX2JY726NGS7XURNED3GE2M3K2KAKNDF2W6V4B3IBIKH5EMPDT5PR6AY7EV6FP47U4MGMEQCK7LASOLAYKHYJJM47ELDLKR32TAHNUM2GNINHRGTQBPYIKRRUBXKCAG7WPRZSJ2CSCDWABJO23BMKIS2Z43ER7GYHUHT4EO2OC3EXXYIDLHLC5XYUVEEB4J27DF3OSYIWFF4CDWZHL6NW3IPV5XPPZCI5QGKTEK7YDU3W26ALHN73KLSAQH42PQAJP4IJBBMFIBMXGUFDDITTI2DOTAWAF6DF2C6YN24ANOGAUJO4CWCJX5F3DPMEDSY7LB7W4B6YA46HKEXZOQ24VPRWED3CS32ZX37E5P46CX6ZHSRJGBJHEEKEKTVF67YHIIWUCSVVOBINPBBN62L5IY34RCBNWGQOQIZ525EYCZSLWD7IX5GKDXORCURJDII2JREJOJFM2CSD5FS3JRGQUUKVDLOISZQO2U5QEKJ4FP5CW5MSP55CNICUTQWNQVY4KFTKQKTUGV53CZ3MH5MCZWTOHPJCR2LB5XJ5UW6VXGMQAA2M5KWVBI7HZBUJFPEKOUVWKR3VPO2ZENS6CPDIBAYDSJQZSOW7JLZFBXFDGTXEEG6S7RGMDFGQSRUEGM42XLOM4CXGB4RI6VITL6GFRAZE2HUUJBUZVJAH2S34UZOTULZDVOCGW3JZW6RRR2IFP23OGHYY4NXVMGPK2JCXNALVKAONDZ7F6WKWQPJBGRVY7X6OV2G75HR7AHD3LGS3Q"

mustHave = "https://www.hasznaltauto.hu/"

searchTerm = ["talalatilista","szemelyauto"]

Continue = True

links = [originalURL]
seenLinks = [originalURL]

crawler = LinkDownloader(50,mustHave)


# print(crawler.getLinksInPool(getLinks("https://www.hasznaltauto.hu/")))

# links = []
i = 1
while len(links) > 0:

    nextPage = links.pop()
    nextLinks = crawler.getLinksInPool(cleanLinks(getLinks(nextPage),mustHave))
    nextLinks = list(set(nextLinks))
    # cleanedLinks = cleanLinks(nextLinks,mustHave)


    seenLinks.append(nextPage)
    seenLinks = list(set(seenLinks))
    for item in nextLinks:
        if item not in seenLinks:
            if item not in links:
                links.append(item)
                # print(item)
    for item in links:
        # print("itt:",item)
        pass
    print("links:",len(links),"seenlinks:",len(seenLinks))
    i = i + 1
