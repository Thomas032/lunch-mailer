import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import requests
from bs4 import BeautifulSoup
import re

my_mail = "chalka.dne@gmail.com"
my_pass = "gwdyxncaqhlpajju"


def get_food(code:int):
    BASE = "https://www.strava.cz/Strava/Stravnik/Jidelnicky?zarizeni="
    data = {}
    index = 1
    page= requests.get(BASE + str(code))
    soup = BeautifulSoup(page.text, "html.parser")
    day = soup.find_all("div", class_="objednavka-jidla-obalka")[0]
    tags = day.find_all("div", class_="objednavka-jidlo-popis")
    names = day.find_all("div", class_="objednavka-jidlo-nazev")
    for i,tag in enumerate(tags):
        if re.match("Oběd \dD", tag.text):
            data["obed"+str(index)] = names[i].text
            index+=1
    return data

def get_food_url(food_name):
    URL = "https://search.seznam.cz/obrazky/?q="
    if ',' in list(food_name):
        food_name_parsed = food_name.split(',')[0]
    else:
        food_name_parsed = food_name
    page = requests.get(URL + food_name_parsed)
    soup = BeautifulSoup(page.text, "html.parser")
    img_container = soup.find_all("div", class_="_1fa4fe")[0]
    img_holder = soup.find_all("div", class_="_1fa4fe")[0].find_all("div", class_="ed8bb5")[0].find_all("img")[0]
    img_url = img_holder["src"]  
    return img_url
    
    
    
def send_mail(user_email):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    
    server.login(my_mail, my_pass)
    date = datetime.datetime.now().strftime("%d/%m")
    subject = f"Report o chálce dne"
  
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Report of todays lunch!"
    msg["From"] = my_mail
    msg["To"] = user_email
    data = get_food(4038)
    food_one, food_two = data["obed1"], data["obed2"]
    food_one_url = get_food_url(food_one)
    food_two_url = get_food_url(food_two)
    
    
    html =f"""


<div class="wrapper">
    <div class="header">
        <h1>Chálky dne...</h1>
    </div>
    <div class="food_holder">
        <div class="food_one">
            <img src="{food_one_url}" alt="chalka_1" style="max-width:100%;">
            <h3 >{food_one}</h3>

        </div>
        <div class="food_one">
            <img src="{food_two_url}" alt="chalka_2" style="max-width:100%;">
            <h3>{food_two}</h3> 
        </div>

    </div>
    <i class="shady">UPOZORNĚNÍ: fotky jídel v tomto mailu jsou jen orientační !</i>
    
    
</div>
    """
    part = MIMEText(html, "html")
    msg.attach(part)
    server.sendmail(
        my_mail,
        user_email,
        msg.as_string()
    )
    print(f"Email to {user_email} sent successfully!")
    server.quit()


