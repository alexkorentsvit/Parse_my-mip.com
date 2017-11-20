# -*- coding: utf-8 -*-
import requests, time, os, csv
from bs4 import BeautifulSoup

url = 'https://www.my-mip.com'
user = 'yaroslav.haletsky@gmail.com'
pas = 'Qwerty12345'


# Getting the list of banks and links to them
def GetLinks(page_link):
    my_url = url + page_link
    links = []
    flag = False
    while flag == False:
        try:
            s = requests.Session()
            r = s.get(my_url, auth=(user, pas))
        except:
            print('internet conn error')
        else:
            flag = True
    soup = BeautifulSoup(r.text, "html5lib")
    try:
        next_page = soup.find('li', {'class': 'gButton'}).find('a').get('href')
    except:
        print(soup)
        print('------------------------')
        next_page = None
    data = soup.findAll('h3', {'class': 'name'})
    for link in data:
        links.append(link.find('a').get('href'))
    s.close()
    
    return(links, next_page)
    



    



# Getting info
def GetInfo():
    final_info = {}
    page_link = '/en/online-database/mipcom/companies/#search=startRecord%3D900%26rpp%3D12'
    counter_of_companies = 0
    while True:
        links, next_page = GetLinks(page_link)
        for link in links:
            my_url = url + link
            flag = False
            while flag == False:
                try:
                    s = requests.Session()
                    r = s.get(my_url, auth=(user, pas))
                except:
                    print('internet conn error')
                else:
                    flag = True            
            soup = BeautifulSoup(r.text, "html5lib")
            name = soup.find('h2', {'class': 'exhibitorName'}).text
            try:
                website = soup.find('li', {'class': 'link'}).find('a').get('href')
            except:
                website = ' - '
            data = soup.find('div', {'class': 'inner-attribute-container'}).find('ol')
            features = data.findAll('dt')
            info = data.findAll('dd')
            sub_info = []
            for i in range(len(info)):
        
                new_string1 = ''
                new_string2 = ''
                try:
                    info[i].contents[1]
                except:
                    sub_info.append(info[i].text.replace(' ','').replace('\n', ''))
                else:
                    string1 = info[i].text.replace('\n', '')
                    string2 = info[i].contents[1].text.replace('\n', '')
                    for j in range(len(string1)-3):
                        if not string1[j] == ' ' or not string1[j+1] == ' ' or not string1[j+2] == ' ':
                            new_string1 += string1[j]
                        if not string1[j] == ' ' and string1[j+1] == ' ' and string1[j+2] == ' ' and string1[j+3] == ' ':
                            break
                        
                    for j in range(len(string2)-3):
                        if not string2[j] == ' ' or not string2[j+1] == ' ' or not string2[j+2] == ' ':
                            new_string2 += string2[j] 
                    new_string1 = new_string1.replace('  ', ' ')[1:]
                    new_string2 = new_string2.replace('  ', ', ')[2:]
                    sub_info.append(new_string1 + ' ' + '(' + new_string2 + ')')
                    
                                                  
            info = {}
            for i in range(len(features)): 
                if not features[i].text == 'Participation Type':
                    info[features[i].text] = sub_info[i]
            
            
            data = soup.find('div', {'class': 'addresses'}).find('div', {'class': 'adr'})
            data = data.findAll('span')    
            contact_info = ''
            for i in data:
                if i.text.replace('\n', '') not in contact_info:
                    contact_info += i.text.replace('\n', '') + ' ' +'|' + ' '
                             
            contact_info = contact_info[ : -3].split('|')
            contact = ''
            for i in range(len(contact_info)):
                if contact_info[i][0] == ' ':
                    contact_info[i] = contact_info[i].replace(' ', '')
            for i in range(len(contact_info)):
                contact += contact_info[i] + ' ' + '|' + ' '
            contact = contact[:-3]
                
                
            final_info[name] = info
            final_info[name]['contact'] = contact
            final_info[name]['website'] = website
            
            
            counter_of_companies += 1
            print(name, final_info[name])
            print(counter_of_companies)
            print('---------------------------------------------------------------------------------------')
            

        page_link = next_page 
        if page_link == None:
            break
        
    counter = 0
    for key in final_info.keys():
        print(key, final_info[key])
        counter += 1
        print(counter)
    return final_info 


GetInfo()





#def csv_writer(path, fieldnames, data):

    #with open(path, "w", newline='') as out_file:
        #writer = csv.DictWriter(out_file, delimiter=';', fieldnames=fieldnames)
        #writer.writeheader()
        #for row in data:
            #writer.writerow(row)





#def run():
    #start = time.time()
    #final_info = GetInfo()
    #fieldnames = ['Name', 'Main Activity', 'Secondary Activities', 'Genres', 'Region/Country', 'Contact Information', 'Website']
    #data = []
    #for key1 in final_info.keys():
        #new_data = []
        #new_data.append(key1)
        #for key2 in final_info[key1].keys():
            #new_data.append(final_info[key1][key2])
        #data.append(new_data)

    #my_list = []
    #cell = data
    #for values in cell:
        #print('строки', values)
        #inner_dict = dict(zip(fieldnames, values))
        #my_list.append(inner_dict)

    #path = "table.csv"
    #csv_writer(path, fieldnames, my_list)    
    
    #Time = time.time() - start
    #print("Lead Time: " + str(Time))
    
   
#run()


