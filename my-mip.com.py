# -*- coding: utf-8 -*-
import requests, time, os, csv, psycopg2, logging
from bs4 import BeautifulSoup

def get_db_credentials():
    global hostname_db
    global port_db
    global username_db
    global password_db
    global database_db
    
    cd = os.path.dirname(os.path.abspath(__file__))
    db_credentials={}
    csvFile = os.path.join(cd, 'db_credentials.csv')
    with open(csvFile) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=';')
        for row in readCSV:
            db_credentials[row[0]]=(row[1])
        
    hostname_db = db_credentials['hostname_db']
    port_db = db_credentials['port_db']
    username_db = db_credentials['username_db']
    password_db = db_credentials['password_db']
    database_db = db_credentials['database_db']


def create_engine(CONNECT_STRING):
    try:
        conn = psycopg2.connect(CONNECT_STRING)
        cur = conn.cursor()
    except  Exception as e:
        logging.error(e)
        logging.info("I am unable to connect to the database")
        cur = None
        conn = None        
    return cur, conn



# Creating Table
def CreateTable(cur):
    try:
        cur.execute("CREATE TABLE companies111 (id serial PRIMARY KEY, name text, main_activity text, secondary_activities text, genres text, region__country text, contact_information text, website text);")
    except Exception as e:
        logging.error(e)
        logging.info("Can't create the table")
    else:
        logging.info('successfully created a table')
        return True
    return False


#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



url = 'https://www.my-mip.com'
user = 'yaroslav.haletsky@gmail.com'
pas = 'Qwerty12345'




# Getting the list of links of the companies and link to the next page
def GetLinks(page_link):
    my_url = url + page_link
    print(my_url)
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
        print(next_page)
    except:
        next_page = None
    data = soup.findAll('h3', {'class': 'name'})
    for link in data:
        links.append(link.find('a').get('href'))
    s.close()
    
    return(links, next_page)
    

#

# Getting information and write it to the table
def GetInfo(cur, conn):
    
    my_features = ['Company Main Activity','Company Secondary Activities', 'Company Genres', 'Region/Country']
    sort_links = ['0','A','B','C''D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    counter_of_companies = 0
    
    for Alink in sort_links:
        final_info = {}
        page_link = '/en/online-database/mipcom/companies/?rpp=12&d=103832|0{}'.format(Alink)
        
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
                info = data.findAll('dl')
                
                information = {}
                # init dict with ' - ' 
                for i in range(len(my_features)):
                    information[my_features[i]] = ' - '                
                
                #Getting information
                for dl in info:
                    sub_info = []
                    sub_info.append(dl.find('dt').text)
                    dd = dl.findAll('dd')
                    for i in range(len(dd)):
                        
                        new_string1 = ''
                        new_string2 = ''
                        try:
                            dd[i].contents[1]
                        except:
                            sub_info.append(dd[i].text.replace(' ','').replace('\n', ''))
                        else:
                            string1 = dd[i].text.replace('\n', '')
                            string2 = dd[i].contents[1].text.replace('\n', '')
                            
                            #Give the information presentable appearance
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
                            

                        for num_inf in range(1,len(sub_info)):
                            if sub_info[0] in my_features and num_inf == 1:
                                information[sub_info[0]] = sub_info[num_inf]                            
                            elif sub_info[0] in my_features and num_inf > 1:
                                information[sub_info[0]] += ';' + ' ' + sub_info[num_inf]
                            
                                
                        

                
                # Edding contact information
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
                    
                    
                final_info[name] = information
                final_info[name]['contact'] = contact
                final_info[name]['website'] = website
                
                
                counter_of_companies += 1
                print(name, final_info[name])
                print(counter_of_companies)
                print('---------------------------------------------------------------------------------------')
    
    
            # If there is no link to the next page, write to the table and exit the cycle
            page_link = next_page
            if page_link == None:
                for key1 in final_info.keys():
                    putdb = []
                    for key2 in final_info[key1].keys():
                        putdb.append(final_info[key1][key2])
                    cur.execute("INSERT INTO companies111 ( name, main_activity, secondary_activities, genres, region__country, contact_information, website) VALUES (%s, %s, %s, %s, %s, %s,  %s)",
                                                    (key1, putdb[0], putdb[1], putdb[2], putdb[3], putdb[4], putdb[5]))
                        
                conn.commit()                
                break
        
    return final_info 


# Master function
def run():
    start = time.time()
    get_db_credentials()
    logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.DEBUG, filename = u'mylog.log')
    CONNECT_STRING = 'dbname=' + database_db + ' ' + 'user=' + username_db  +  ' ' + 'host=' + hostname_db + ' ' + 'password=' + password_db 
    cur, conn = create_engine(CONNECT_STRING)
    CreateTable(cur)
    GetInfo(cur, conn)
    cur.close()
    conn.close()    
    Time = time.time() - start
    logging.info("Lead Time: " + str(Time))
    
       
run()


