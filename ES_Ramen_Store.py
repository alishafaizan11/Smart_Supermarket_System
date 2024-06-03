from keypadfunc import keypad
from picamera import PiCamera
from flask import send_file
from flask import render_template
from flask import Flask
import PCF8591 as ADC
import serial
import urllib.request
ADC.setup(0x48)
import DHT11
import time
from datetime import datetime
import LCD1602 as LCD
import RPi.GPIO as GPIO
from statistics import mean
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
global buzz
#R_API_KEY=""
W_API_KEY="WLHP1M5X692FRI9L"#"CH4HHIAXSH1PUJZT"
SERIAL_PORT = '/dev/ttyS0'
ser=serial.Serial(baudrate=2400, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, port=SERIAL_PORT, stopbits=serial.STOPBITS_ONE, timeout=1)

LCD.init(0x27,1)
PB=12
PB2=17
PIR=27
BLUE=5
##D=17
R=4
TRIG=6
ECHO=18
flag = False
buzz=16
mode1=""
ID=""
CHID=2289674#2324408
Field_number = 1
no_of_readings = 5
elementnumber = 3
values = []
values1=[]

GPIO.setup(buzz,GPIO.OUT)
GPIO.setup(PIR,GPIO.IN,pull_up_down=GPIO.PUD_UP)

Buzz=GPIO.PWM(buzz,1) #for GPIO 16, with frequency 50
Buzz.start(50)
GPIO.setup(PB2,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.setup(PB,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BLUE,GPIO.OUT) #blue
#GPIO.setup(D,GPIO.OUT) #yellow
GPIO.setup(R,GPIO.OUT) #red
Mycamera=PiCamera()
Mycamera.resolution=(640,480)
dooropen=False
total_money=0.0
cancel=False

waterPour=False #to check if water is heated up and ready to pour

        
def food_ready():
    
    global Buzz
    print("Your Ramen is ready to be picked up. ENJOY YOUR MEAL!")
    LCD.write(0,0,"ENJOY YOUR MEAL")
    LCD.write(0,1,"See you again :)")
    #play()
    
    for i in range (0,3):
        Buzz.ChangeFrequency(500)
        GPIO.output(BLUE,GPIO.HIGH)
        time.sleep(1)
        GPIO.output(BLUE,GPIO.LOW)
        time.sleep(1)
    Buzz.ChangeFrequency(1)
    GPIO.output(BLUE,GPIO.LOW)
    

    
myapp=Flask(__name__, template_folder='xyz')

@myapp.route("/")#index route
def index():

    return render_template('index.html')
#"Welcome to S-MART<br> ⠀⠀⠀⠀⠀     ⠀⠀   ⠀⢀⣤⣦⣤⣤⣤⣤⣤⣶⣶⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡿⠛⢻⠛⢻⠛⢻⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡇⠀⡿⠀⣼⠀⢸⣿⡅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⡇⠀⣿⠀⢹⠀⢸⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⣤⣤⡀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⡀⠸⡆⠘⣇⠀⢿⣷⠀⠀⠀⠀⣀⣠⣤⣶⣶⣾⣿⠿⠿⠛⠋⢻⡆\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⣿⠀⢿⣄⣸⣿⣦⣤⣴⠿⠿⠛⠛⠉⠁⢀⣀⣀⣀⣄⣤⣼⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡇⠀⡿⠀⣼⣿⣿⣯⣿⣦⣤⣤⣶⣶⣶⣿⢿⠿⠟⠿⠛⠛⠛⠛⠋\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠁⣸⠃⢠⡟⢻⣿⣿⣿⣿⣿⣭⣭⣭⣵⣶⣤⣀⣄⣠⣤⣤⣴⣶⣦\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⡇⠀⣿⠀⣸⠀⢸⣿⣶⣦⣤⣤⣄⣀⣀⣀⠀⠀⠉⠈⠉⠈⠉⠉⢽⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣸⣿⡇⠀⣿⠀⢸⠀⢸⣿⡿⣿⣿⣿⣿⡟⠛⠻⠿⠿⠿⣿⣶⣶⣶⣶⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⢀⣤⣶⣿⡿⣿⣿⣿⣷⠀⠹⡆⠘⣇⠈⣿⡟⠛⠛⠛⠾⣿⡳⣄⠀⠀⠀⠀⠀⠀⠈⠉⠉⠁\n⠀⠀⠀⠀⠀⠀⣰⣿⢟⡭⠒⢀⣐⣲⣿⣿⡇⠀⣷⠀⢿⠀⢸⣏⣈⣁⣉⣳⣬⣻⣿⣷⣀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⣀⣤⣾⣿⡿⠟⠛⠛⠿⣿⣋⣡⠤⢺⡇⠀⡿⠀⣼⠀⢸⣿⠟⠋⣉⢉⡉⣉⠙⠻⢿⣯⣿⣦⣄⠀⠀⠀⠀\n⢠⣾⡿⢋⣽⠋⣠⠊⣉⠉⢲⣈⣿⣧⣶⣿⠁⢠⣇⣠⣯⣀⣾⠧⠖⣁⣠⣤⣤⣤⣭⣷⣄⠙⢿⡙⢿⣷⡀⠀⠀\n⣹⣿⣿⣷⣦⣍⣛⠻⠿⠶⢾⣤⣤⣦⣤⣬⣷⣬⣿⣦⣤⣬⣷⣼⣿⣧⣴⣾⠿⠿⠿⢛⣛⣩⣴⣾⣿⣿⡇⠀⠀\n⣸⣿⣟⡾⣽⣻⢿⡿⣷⣶⣦⣤⣤⣤⣬⣭⣉⣍⣉⣉⣩⣩⣭⣭⣤⣤⣤⣴⣶⣶⣿⡿⣿⣟⣿⣽⣿⣿⡇⠀⠀\n⢸⣿⡍⠉⠛⠛⠿⠽⣷⣯⣿⣽⣻⣻⣟⢿⣻⢿⡿⣿⣟⣿⣻⢟⣿⣻⢯⣿⣽⣾⣷⠿⠗⠛⠉⠁⢸⣿⡇⠀⠀\n⠘⣿⣧⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠛⠙⠛⠛⠛⠛⠋⠛⠋⠉⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⣿⡿⠀⠀⠀\n⠀⠹⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣦⡀⠀⠀⠀⠀⠀⠀⣼⣿⠇⠀⠀⠀\n⠀⠀⠹⣿⣆⠀⠀⠀⠀⠀⠀⠀⠻⠿⠟⠀⠀⠀⠿⣦⣤⠞⠀⠀⠀⠻⠿⠟⠀⠀⠀⠀⠀⢀⣼⣿⠋⠀⠀⠀⠀\n⠀⠀⠀⠘⢿⣷⣶⣶⣤⣤⣤⣀⣀⣀⡀⣀⠀⡀⠀⠀⠀⡀⣀⡀⣀⣀⣀⣠⣤⣤⣴⣶⣶⣿⡿⠃⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠙⢿⣿⣾⡙⠯⠿⠽⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠿⠙⢋⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠙⠻⢿⣶⣤⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣾⣿⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣈⠙⠻⠿⡿⠷⠶⡶⠶⠶⠶⠶⠶⣾⢿⣿⢿⠛⣉⣡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀";

@myapp.route("/Main_Menu")#static route

def embsys():
    return "S-MART menu::<br>1. Kimchi+Hot+Egg+Iced tea (1)  <br>2. Curry+Medium+Tteokbokki+Water (2) <br>3.Biryani+Hot+Egg+Vimto (3) <br> 4.Kimchi+Normal+Cheese+Water (4) <br> *Enter the corresponding code in the following link"

@myapp.route("/Main_Menu/<code>")#dynamic route
def pay(code):
    if(code=="1"):
        Price=price("Medium","Kimchi","Egg","Hot","Iced Tea")
        return "The calculated bill is: {0:2.2f}<br> Your choices were: Flavour: Kimchi  <br>Topping: Egg <br>Spice level: Hot<br> Drink: Iced Tea <br>ENJOY YOUR MEAL ;)".format(Price)
    elif(code=="2"):
        Price=price("Medium","Curry","Tteokbokki","Medium","Water")
        return "The calculated bill is: {0:2.2f}<br> Your choices were: Flavour: Curry  <br>Topping: Tteokbokki <br>Spice level: Medium<br> Drink: Water  <br>ENJOY YOUR MEAL ;)".format(Price)
    elif(code=="3"):
        Price=price("Medium","Biryani","Egg","Hot","Vimto")
        return "The calculated bill is: {0:2.2f}<br> Your choices were: Flavour: Biryani  <br>Topping: Egg <br>Spice level: Hot<br> Drink: Vimto <br>ENJOY YOUR MEAL ;)".format(Price)
    elif(code=="4"):
        Price=price("Medium","Kimchi","Cheese","Normal","Water")
        return "The calculated bill is: {0:2.2f}<br> Your choices were: Flavour: Kimchi  <br>Topping: Egg <br>Spice level: Hot<br> Drink: Water <br>ENJOY YOUR MEAL ;)".format(Price)
   #return "The calculated bill is: {}<br>Proceed to payment. <br> ENJOY YOUR MEAL ;)".format(Price)

@myapp.route("/staff_coolercheck")#static route
def check_cooler():
    element=float(read_cooler())
    if(element>4.0):
        return "Cooler temp is {0:2.2f} <br>HAZARD: CHECK COOLER IMMEDIATELY".format(element)
    else:
        return "Cooler temp is {0:2.2f} <br>Mart Component: Cooler is looking like a WOW".format(element)

        
@myapp.route("/staff_surveilance/<passkey>")#dynamic route
def check_picture(passkey):
    if(passkey=="111729"):
        return video()
    else:
        return "Unauthorized access....."
    

def photo(): #person enters store and camera captures image 
    timestamp=datetime.now().isoformat()
    
    Mycamera.start_preview()
    Mycamera.annotate_text="Picture: Person entered S-MART at {}".format(timestamp)
    time.sleep(3)
    
    Mycamera.capture("/home/pi/Desktop/F23/personenter.jpg")
    time.sleep(5)
    Mycamera.stop_preview()
##    response=send_file("/home/pi/Desktop/F23/personenter.jpg",mimetype="image/jpeg")
##    return response

def video():
    timestamp=datetime.now().isoformat()
    Mycamera.start_preview()
    Mycamera.annotate_text="Video: Person entered S-MART at {}".format(timestamp)
    Mycamera.start_recording("/home/pi/Desktop/F23/video1.h264")
    time.sleep(3)
    Mycamera.stop_recording()
    Mycamera.stop_preview()
    response=send_file("/home/pi/Desktop/F23/video1.h264",mimetype="video/h264")
    return response



def read_cooler():
    average=0.0
    x = urllib.request.urlopen("https://thingspeak.com/channels/{}/fields/{}.csv?results={}".format(CHID,3,no_of_readings)) # I changed from ch 1 to ch3
    data = x.read().decode('ascii')
    print(data)
    data = ",".join(data.split("\n"))
    for i in range(5,5*3+3,3): #check number of readings and change
        values.append(data.split(",")[i])
        
         
    for i in range (0,len(values)):
        average=average+float(values[i])
    element=average/len(values)
    #print(element)
    #return values[1]
    return element
 
def cooler():
    
    ADC_units= ADC.read(0)
    ADC_volts=(ADC_units*3.3)/256
    ADC_temp=ADC_volts *5.0/3.3
    print(ADC_temp)
    x= urllib.request.urlopen("https://thingspeak.com/update?api_key={}&field3={}".format(W_API_KEY,ADC_temp))#I changed field number to 3 
    time.sleep(2)
    #return ADC_temp

    
def pay_price(bill):
    global total_money
    loyalty_id=""
    card_id=""
    final_bill = bill
    loyalty = input("\nAre you an S-MART Loyalty member? Y/N: ")
    if(loyalty =='Y'or loyalty=='y'):
        print("Tap your Loyalty card to get a discount :)")
        loyalty_id=str(readrfid())
        while(loyalty_id=="False"):
            loyalty_id=str(readrfid())
        #print(loyalty_id)               
        if(loyalty_id == "540064F6C5"):
            print("\nYour Loyalty was authorized. You are eligible for  a 15% discount!!!")
            final_bill = bill-bill*0.15
            time.sleep(1)
            print("\nCalculating your bill...")
            time.sleep(2)
        else:
            print("\nSorry your Loyalty card is not registered in the system.")
            time.sleep(2)
            
    else:
        print("You are not eligible for any discounts. Proceeding to payment  ")
        
    print("\nYour total bill is: {} AED".format(final_bill))
    print("\nTap your credit card on the reader to pay.....")
    card_id=str(readrfid())
    while(card_id=="False"):
        card_id=str(readrfid())
    print("\nPayment success!!!! \nEnjoy your meal")
    total_money = total_money + final_bill
                                                                                                                       

def validate_rfid(code):
    s = code.decode("ascii")
    if (len(s) == 12) and (s[0] == "\n") and (s[11] == "\r"):
        return s[1:11]
    else:
        return False
    
def readrfid():
    ser.flushInput()
    ser.flushOutput()
    data=ser.read(12)
    code=validate_rfid(data)
    return code

def read_Ambient_temp():
    average=0.0
    x = urllib.request.urlopen("https://thingspeak.com/channels/{}/fields/{}.csv?results={}".format(CHID,2,no_of_readings))
    data = x.read().decode('ascii')
    #print(data)
    data = ",".join(data.split("\n"))
    for i in range(5,5*3+3,3): #check number of readings and change
        values1.append(data.split(",")[i])
    return values1[1]
    
   
         
    
    #print(element)
    #return "S-MART temperature is {}C.".format()

def Ambient_temp():

    result=""

    while (not result):        
        result = DHT11.readDht11(13)
        if result:
            humidity, temperature = result
            print ("humidity:{}%,  Temperature: {}C".format(humidity, temperature))
            x= urllib.request.urlopen("https://thingspeak.com/update?api_key={}&field2={}".format(W_API_KEY,temperature))
            

    time.sleep(1)

def price(size,flavor,topping,spice,drink):
    bill=0
    sizebill=0
    flavorbill = 0
    toppingbill =0
    spicebill=0
    drinkbill=0
    if(size == "S" or size == "s"):
        sizebill=5
    elif (size == "M" or size == "m"):
        sizebill=10
    elif (size == "L" or size == "l"):
        sizebill=15    

    if(flavor == "Kimchi"):
        flavorbill=20
    elif (flavor == "Biryani"):
        flavorbill=15
    elif (flavor == "Curry"):
        flavorbill=10


    if(topping == "Cheese"):
        toppingbill=20
    elif (topping == "Egg"):
        toppingbill=15
    elif (topping == "Tteokbokki"):
        toppingbill=10

     
    if(spice == "Normal"):
        spicebill=5
    elif (spice == "Medium"):
        spicebill=10
    elif (spice == "Hot"):
        spicebill=15

    if(drink == "Iced Tea"):
        drinkbill=5
    elif (drink == "Water"):
        drinkbill=2
    elif (drink == "Vimto"):
        drinkbill=3
    
    bill = sizebill+flavorbill+toppingbill+spicebill+drinkbill
    #print("bill is {}".format(bill))
   
    return bill



def main_menu():
    print("You can make all the customizations for your order here. Choose from any of our wide variety of choices for your perfect order :)")
    time.sleep(1)
    cancel=False
    size = ""
    Flavor = ""
    topping = ""
    spicy = ""
    bill=""
    drink=""
    
    size = cup_placement()
    time.sleep(1.5)
    Flavor = flavor()
    time.sleep(1.5)
    topping = Toppings()
    time.sleep(1.5)
    spicy = Spicy()
    time.sleep(1.5)
    drink=Drinks()
    time.sleep(1.5)

    bill = price(size,Flavor,topping,spicy,drink)
    LCD.clear()
    LCD.write(0,0,"Total bill: ")
    LCD.write(0,1,str(bill))
    time.sleep(1)
    
    time.sleep(2)
    print("\n\nThis is your order: \nSize = {}\nFlavor= {}\nTopping = {}\nSpicy = {}\nDrink = {}".format(size,Flavor,topping,spicy,drink))
    print("\nYour total bill for this order is {} AED\n".format(bill))

    return bill


def Spicy():
    spicy=""
    print("\nChoose the spice level for your ramen: \n1. Normal = AED 5 \n2. Medium = AED 10 \n3. Hot = AED 15\nEnter your ramen Spice Level on the Keypad:")
    
    key,keys = keypad()
    time.sleep(0.5)
    while (key != 1 and key != 2  and key !=3):
        print("Invalid Keypad character. Enter again")
        key,keys = keypad()
    if(key == 1):
       spicy = "Normal"
    elif(key == 2):
       spicy = "Medium"
    elif(key == 3):
       spicy = "Hot"
    print("The Spice level you have chosen is {}".format(spicy))
    return spicy

def Drinks():
    drink=""
    print("\nChoose your drink: \n1. Iced Tea = AED 5 \n2. Water(2) = AED 2 \n3. Vimto(3) = AED 3\nEnter your choice of drink on the Keypad:")
    
    key,keys = keypad()
    time.sleep(0.5)

    while (key != 1 and key != 2  and key !=3):
        print("Invalid Keypad character. Enter again")
        key,keys = keypad()
    if(key == 1):
       drink= "Iced Tea"
    elif(key == 2):
        drink= "Water"
    elif(key == 3):
        drink= "Vimto"
    print("The drink you have chosen is {}".format(drink))
    return drink


def Toppings():
    topping=""
    print("\nChoose the toppings for your ramen:\n1. Cheese = AED 20 \n2. Egg = AED 15 \n3. Tteokbokki = AED 10\nEnter your ramen Toppings on the Keypad: ")
    
    key,keys = keypad()
    time.sleep(0.5)
    
    while (key != 1 and key != 2 and key !=3):
        print("Invalid Keypad character. Enter again")
        key,keys = keypad()
    
    if(key == 1):
       topping = "Cheese"
    elif(key == 2):
       topping = "Egg"
    elif(key == 3):
       topping = "Tteokbokki"
    print("The Topping you have chosen is {}".format(topping))
    return topping

    
def flavor():
    Flavor=""
    print("\nChoose your ramen flavor: \n1. Kimchi = AED 20 \n2. Biryani= AED 15, \n3. Curry= AED 10,\nEnter your ramen Flavor on the Keypad: ")
    key,keys = keypad()
    
    time.sleep(0.5)
    while (key != 1 and key != 2 and key !=3):
        print("Invalid Keypad character. Enter again")
        key,keys = keypad()
    
    if(key == 1):
       Flavor = "Kimchi"
    elif(key == 2):
       Flavor = "Biryani"
    elif(key == 3):
       Flavor = "Curry"
    print("The flavor you have chosen is {}".format(Flavor))
    return Flavor
   
    
def cup_placement():#This function uses Ultrasonic sensor to detect the distance between the cup and machine
  
    size = input("\nChoose your ramen cup size:\n1. Large (L) = AED 15 \n2. Medium (M) = AED 10 \n3. Small (S)= AED 5 \nEnter your cup size: ")
    while (size != "L" and size!="l" and size != "M" and size!="m" and size!="S"and size!="s"):
        size=input("Invalid character. Choose your cup size again \n1. Large (L) = AED 15 \n2. Medium (M) = AED 10 \n3. Small (S)= AED 5 \n")
    print("Place the Ramen Cup inside the machine")
    time.sleep(2)
    x = distance()
    while x>5:
        print("Place Cup properly")
        x = distance()
        time.sleep(2)


    print("Cup has been placed successfully")

    return size

    
def distance():
    GPIO.output(TRIG,GPIO.LOW)
    time.sleep(0.000002)
    GPIO.output(TRIG,1)
    time.sleep(0.00001)
    GPIO.output(TRIG,0)
    while GPIO.input(ECHO)==0:
        a=0
    time1=time.time()
    while GPIO.input(ECHO)==1:
        a=0
    time2=time.time()
    duration = time2-time1
    return duration*1000000/58

    

def water_level():
    print("Water level being set by the machine...")
    ADC_units= ADC.read(2)#change 
    ADC_volts=(ADC_units*3.3)/256
    ADC_litre =ADC_volts *1000/3.3
    while (ADC_litre<=400): #ADC_read seperate function
        ADC_units= ADC.read(2)
        ADC_volts=(ADC_units*3.3)/256
        ADC_litre=ADC_volts *1000/3.3
        print("Adding water.........") #increasing time to let machine heat water up (ask prof)
        time.sleep(1)
    
    waterPour=True
    return ADC_litre

   
def heat_water():
    print("Water temperature is being set by the machine...")
    ADC_units= ADC.read(1)
    ADC_volts=(ADC_units*3.3)/256
    ADC_temp=ADC_volts *105/3.3
    while (ADC_temp<=99.9): #ADC_read seperate function
        time.sleep(1)
        ADC_units= ADC.read(1)
        ADC_volts=(ADC_units*3.3)/256
        ADC_temp=ADC_volts *105/3.3
        GPIO.output(R,GPIO.HIGH)
        
        print("Water heating in progress....") #increasing time to let machine heat water up (ask prof)
        time.sleep(1)
        
    GPIO.output(R,GPIO.LOW)
    ADC.write(ADC_units)
    print("Water is sufficiently heated, ready to pour")
    waterPour=True
    return ADC_temp
    

def action(self):
    global cancel
    print("\n Machine halt. Your order is cancelled")

    print("--------------------------------------------------------Your Order has been cancelled, Sayonara--------------------------------------------------------\n                                                                See you Later Alligator :)")
    exit()
    

GPIO.add_event_detect(PB2,GPIO.FALLING,callback=action,bouncetime=2000)

print("Welcome to S-MART") 
print("⠀⠀⠀⠀⠀     ⠀⠀   ⠀⢀⣤⣦⣤⣤⣤⣤⣤⣶⣶⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡿⠛⢻⠛⢻⠛⢻⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡇⠀⡿⠀⣼⠀⢸⣿⡅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⡇⠀⣿⠀⢹⠀⢸⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⣤⣤⡀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⡀⠸⡆⠘⣇⠀⢿⣷⠀⠀⠀⠀⣀⣠⣤⣶⣶⣾⣿⠿⠿⠛⠋⢻⡆\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⣿⠀⢿⣄⣸⣿⣦⣤⣴⠿⠿⠛⠛⠉⠁⢀⣀⣀⣀⣄⣤⣼⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡇⠀⡿⠀⣼⣿⣿⣯⣿⣦⣤⣤⣶⣶⣶⣿⢿⠿⠟⠿⠛⠛⠛⠛⠋\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠁⣸⠃⢠⡟⢻⣿⣿⣿⣿⣿⣭⣭⣭⣵⣶⣤⣀⣄⣠⣤⣤⣴⣶⣦\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⡇⠀⣿⠀⣸⠀⢸⣿⣶⣦⣤⣤⣄⣀⣀⣀⠀⠀⠉⠈⠉⠈⠉⠉⢽⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣸⣿⡇⠀⣿⠀⢸⠀⢸⣿⡿⣿⣿⣿⣿⡟⠛⠻⠿⠿⠿⣿⣶⣶⣶⣶⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⢀⣤⣶⣿⡿⣿⣿⣿⣷⠀⠹⡆⠘⣇⠈⣿⡟⠛⠛⠛⠾⣿⡳⣄⠀⠀⠀⠀⠀⠀⠈⠉⠉⠁\n⠀⠀⠀⠀⠀⠀⣰⣿⢟⡭⠒⢀⣐⣲⣿⣿⡇⠀⣷⠀⢿⠀⢸⣏⣈⣁⣉⣳⣬⣻⣿⣷⣀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⣀⣤⣾⣿⡿⠟⠛⠛⠿⣿⣋⣡⠤⢺⡇⠀⡿⠀⣼⠀⢸⣿⠟⠋⣉⢉⡉⣉⠙⠻⢿⣯⣿⣦⣄⠀⠀⠀⠀\n⢠⣾⡿⢋⣽⠋⣠⠊⣉⠉⢲⣈⣿⣧⣶⣿⠁⢠⣇⣠⣯⣀⣾⠧⠖⣁⣠⣤⣤⣤⣭⣷⣄⠙⢿⡙⢿⣷⡀⠀⠀\n⣹⣿⣿⣷⣦⣍⣛⠻⠿⠶⢾⣤⣤⣦⣤⣬⣷⣬⣿⣦⣤⣬⣷⣼⣿⣧⣴⣾⠿⠿⠿⢛⣛⣩⣴⣾⣿⣿⡇⠀⠀\n⣸⣿⣟⡾⣽⣻⢿⡿⣷⣶⣦⣤⣤⣤⣬⣭⣉⣍⣉⣉⣩⣩⣭⣭⣤⣤⣤⣴⣶⣶⣿⡿⣿⣟⣿⣽⣿⣿⡇⠀⠀\n⢸⣿⡍⠉⠛⠛⠿⠽⣷⣯⣿⣽⣻⣻⣟⢿⣻⢿⡿⣿⣟⣿⣻⢟⣿⣻⢯⣿⣽⣾⣷⠿⠗⠛⠉⠁⢸⣿⡇⠀⠀\n⠘⣿⣧⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠛⠙⠛⠛⠛⠛⠋⠛⠋⠉⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⣿⡿⠀⠀⠀\n⠀⠹⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣦⡀⠀⠀⠀⠀⠀⠀⣼⣿⠇⠀⠀⠀\n⠀⠀⠹⣿⣆⠀⠀⠀⠀⠀⠀⠀⠻⠿⠟⠀⠀⠀⠿⣦⣤⠞⠀⠀⠀⠻⠿⠟⠀⠀⠀⠀⠀⢀⣼⣿⠋⠀⠀⠀⠀\n⠀⠀⠀⠘⢿⣷⣶⣶⣤⣤⣤⣀⣀⣀⡀⣀⠀⡀⠀⠀⠀⡀⣀⡀⣀⣀⣀⣠⣤⣤⣴⣶⣶⣿⡿⠃⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠙⢿⣿⣾⡙⠯⠿⠽⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠿⠙⢋⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠙⠻⢿⣶⣤⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣾⣿⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣈⠙⠻⠿⡿⠷⠶⡶⠶⠶⠶⠶⠶⣾⢿⣿⢿⠛⣉⣡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀")
print("\n`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'")
print("\nPush the BLUE button on the door to enter the S-MART")

LCD.write(3,0,"Welcome to")
LCD.write(5,1, "S-MART")
        
temp=0

while True:
    global cancel
    GPIO.output(R,GPIO.LOW)
    GPIO.output(BLUE,GPIO.LOW)

    
    if(GPIO.input(PB)==1):#push button to enter store
       
        print("\nDoor is now open. You can enter the store\n\n")#Map of store
        print("⣿⣿⡿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⢿⡿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⢿⣿⣿\n⣿⣿⡇⢰⣶⣶⣶⣶⣶⣶⣶⣶⣶⡆⢸⡇⢰⣶⣶⣶⣶⣶⣶⣶⣶⣶⡆⢸⣿⣿\n⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿\n⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿\n⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿\n⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿\n⣿⣿⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⡇⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿\n⣿⣿⡇⠈⠉⠉⠉⠉⠉⠉⠉⠉⠉⠁⢸⡇⠈⠉⠉⠉⠉⠉⠉⠉⠉⠉⠁⢸⣿⣿\n⣿⣿⡷⠶⠶⠶⣄⠀⠀⠰⠶⠶⠶⠀⢸⡇⠀⠶⠶⠶⠆⠀⠀⣠⠶⠶⠶⢾⣿⣿\n⣿⣿⡇⠀⠀⠀⠈⠳⣄⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⣠⠞⠁⠀⠀⠀⢸⣿⣿\n⣿⣿⡟⠛⠛⢷⣄⠀⠈⠛⠛⠛⠛⠛⢻⡟⠛⠛⠛⠛⠛⠁⠀⣠⡾⠛⠛⢻⣿⣿\n⣿⣿⡇⠀⠀⠀⠙⢷⣄⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⣠⡾⠋⠀⠀⠀⢸⣿⣿\n⣿⣿⡇⠀⠀⠀⠀⠀⠙⠛⠛⠛⠛⠛⢻⡟⠛⠛⠛⠛⠛⠋⠀⠀⠀⠀⠀⢸⣿⣿\n⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿\n⣿⣿⣷⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣾⣷⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣾⣿⣿")
        time.sleep(2)
        print("\nYour photo will be taken for verification purposes")
        time.sleep(1)
        #photo()
        print("Photo taken successfully\n")
        time.sleep(2)
        print("`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'\n")

        
        Choice=input("Choose your method of order \n1. Manual  \n2. Online Kiosk\n")
        time.sleep(1)
        while (Choice != "1" and Choice != "2" and Choice!="Manual" and Choice!="Online"):
            Choice=input("Invalid character. Choose your method of order again \n1. Manual  \n2. Online Kiosk\n")
        
        
        if(Choice=="1" or Choice=="Manual"):
            
            bill = main_menu()
            time.sleep(1)
            print("`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'")
            print("Proceeding to payment...")
            time.sleep(1)
            pay_price(bill)
            print("`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'")
            time.sleep(1)
            
            print("\nThe Ramen Station is preparing your Order")
            time.sleep(1)
            quantity=water_level() #small POT
            time.sleep(1)
            print("\n{} ml will be poured into the ramen cup. Water is ready to be heated".format(quantity))
            time.sleep(1)
            print("`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'")
            
            temp=heat_water() #big POT
            time.sleep(1)
            print("\nWater is heated to {0:2.2f} C \nThe machine is pouring heated water and your chosen ramen flavoring into cup".format(temp))
            print("\n`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'\n")
            time.sleep(2)
            food_ready()
            print("`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'`-._,-'")
            print("\nThank you for visiting our store.\nCome again")
            
            
            
        elif(Choice=="2" or Choice=="Online"):
            
            #for i in range (0,5):    
            cooler()
            
            if __name__=="__main__":
                myapp.run(host='0.0.0.0',port=5020)
        
    
            
        
       
        
