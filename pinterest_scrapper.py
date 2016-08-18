'''
Pin-Scrape&Download
https://github.com/npraveenkum/Scrapper/

This is a set of Python methods that will help you to scrape and Download pins from any user  
It was written mainly to download Pins

IF you think any improvement are needed feel free to make changes and submit a Pull.

Thanks To:
sergeyk at https://github.com/sergeyk/vislab/blob/master/vislab/datasets/pinterest.py .Most of the  code is based on this.

Contributors:
Praveen Kumar 

'''

from bs4 import BeautifulSoup
import requests
import shutil
from selenium import webdriver



def get_driver(limit=3):#Creates a new webdriver object for chrome and returns it

    Connection_attempted = 0
    while Connection_attempted<limit:
        try:
        
            driver = webdriver.Chrome()
            return driver   
        except Exception as e:
            Connection_attempted+=1
            print('Getting driver again...')
            print('  connections attempted: {}'.format(connections_attempted))
            print('  exception message: {}'.format(e))



def process_page(driver,url,process,limit=50,connections_to_attempt=3, scrolls_to_attempt=3,
                       sleep_interval=2):
					   
#Process the whole page until the limit for the results is reached
    connection_attempted=0
    while connection_attempted<limit:
        driver.get(url)
        soup=BeautifulSoup(driver.page_source,'html.parser')
        results = process(soup)
        
        all_scroll_attempt=0
        if len(results)<limit:
            scroll_attempt=0
            while(scroll_attempt<scrolls_to_attempt and len(results)<limit):
                scroll_attempt+=1
                all_scroll_attempt+=1
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
                soup=BeautifulSoup(driver.page_source,'html.parser')
                new_results=process(soup)
                if len(new_results)>len(results):
                    results=new_results
                    scroll_attempt=0
        driver.quit()
        return results[:limit]

            


def download_pin(url,path="pin.jpg"):#Downloads a pin when the pins source is provided

    try:
        response = url_reader(url,True)
        with open(path,'wb') as out:
            shutil.copyfileobj(response.raw,out)
        del response
        return
    except Exception as e:
        return 
    




def get_user_boards(username):#gets all the board information for a user in a dictionary object.
#Infromation in the dictionary are URL,BoardNameand and username

    driver = get_driver()
    url = 'https://www.pinterest.com/' + username +'/boards' 
    return process_page(driver,url, 
    lambda soup : [parse_board_info(board) for 
    board in soup.find_all('a',{'class':'boardLinkWrapper'})        
        ])
    

def parse_board_info(board):#Returns a dictionary of Board information
    board=board['href']
    data={
               'username':board.split('/')[1],
               'boardname' : board.split('/')[2],
               'url': 'https://www.pinterest.com{}'.format(board),
                 
         }
    return data


def parse_pin_info(pin):#Returns a dictionary of Pin information
    
    data={
            'pin':pin.find_all('a')[0]['href'],
            'url':'https://www.pinterest.com{}'.format(pin.find_all('a')[0]['href'].split('/')[2]),
            'src':pin.find_all('img')[0]['src']
         }
    return data

def get_user_pins(url):#gets all the PIN information for a Pin in a dictionary object.
#Infromation in the dictionary are URL,Pin and pin Source
    driver = get_driver()
    return process_page(driver,url,lambda soup : [parse_pin_info(pin) for pin in soup.find_all('div',{'class':'GrowthUnauthPinImage'})

            ])
			
def url_reader(url,image=False):

    while True:
        try:
            if image==False:
                content=requests.get(url)
            else:
                content=requests.get(url,stream = True)
        except IncompleteRead:
            continue
        return content

		
		
def get_pin_link(pin):#Get the pin source
#

    url = 'https://www.pinterest.com' + pin
    response = url_reader(url).text
    pin_link = str(BeautifulSoup(response,'html.parser').find_all('meta',{"property":"og:image"})[0]).split('"')[1]
    pin_link=pin_link.split('/')
    pin_link[3]='564x'#Image size as availabel on the pinterest.Will provide a list of all available sizes later
    pin_link='/'.join(pin_link)
    del response
    return pin_link
	
	
def user_pins(username):     #Takes a usernaame, gets all their boards, then goes through those boards to find all the Pins and downloads those pins
    user_all_pins=[]
    user_boards=get_user_boards(username)
    for board in user_boards:
        user_all_pins.extend(get_user_pins(board['url']))

    path=''

    for pin in user_all_pins:
        pin_link = pin['src']
        pin_link=pin_link.split('/')
        pin_link[3]='564x'#Image size as availabel on the pinterest.Will provide a list of all available sizes later
        pin_link='/'.join(pin_link)
        path=''
        path=pin['pin'].split('/')[2]+'.jpg'
        download_pin(pin_link,path)

    return user_all_pins
    
    
