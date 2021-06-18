"""
Title: Security Alarm System for Home
Authors: Taraboanta Andreea
         Vanzariuc Maria 
Story:         
    The alarm is active when the green LED is on.
    When a person gets too close to the house, the green LED will turn off, the red LED will turn on, the buzzer will make some noise,
    and the homeowner will receives an email notification: "Uninvided guest!".
    Also, if the person is scare of the alarm and walks away from the house, the red LED will turn off, the green LED will turn on, the buzzer will stop,
    and the owner will receive an email notification: "The uninvited guest has left!"
"""

#import the libraries used
import smtplib
import time  
import pigpio 
import RPi.GPIO as GPIO

#create an instance of the pigpio library
pi = pigpio.pi()

#define the pin used by the Buzzer
#this pin will be used by the pigpio library
#which takes the pins in GPIO forms
#we will use GPIO18, which is pin 12
buzzer = 18

server=smtplib.SMTP('smtp.gmail.com',587)
server.starttls()
server.login("rasberrypizero.project","112233998877")
ok=1
message1="Uninvided guest!"
message2="The uninvited guest has left!"

#set the pin used by the buzzer as OUTPUT
pi.set_mode(buzzer, pigpio.OUTPUT) 
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

#define the pins used by the ultrasonic module
trig = 32 
echo = 38

#set the trigger pin as OUTPUT, the echo as INPUT
#set the pin 8 and 10 as OUTPUT
GPIO.setup(trig, GPIO.OUT) 
GPIO.setup(echo, GPIO.IN) 
GPIO.setup(8, GPIO.OUT)
GPIO.setup(10, GPIO.OUT)

GPIO.output(8, GPIO.LOW)
GPIO.output(10,GPIO.HIGH)


#function to calculate distance
def calculate_distance():
    #set the trigger to HIGH
	GPIO.output(trig, GPIO.HIGH)
	
    #sleep 0.00001 s and the set the trigger to LOW
	time.sleep(0.00001) 
	GPIO.output(trig, GPIO.LOW)
	
    #save the start and stop times
    	start = time.time() 
	stop = time.time()
	
    #modify the start time to be the last time until
    #the echo becomes HIGH
    	while GPIO.input(echo) == 0:
		start = time.time()
		
    #modify the stop time to be the last time until
    #the echo becomes LOW
   	while GPIO.input(echo) == 1: 
		stop = time.time()
		
    #get the duration of the echo pin as HIGH
    	duration = stop - start
    	
    #calculate the distance
    	distance = 34300/2 * duration
    	
	if distance < 0.5 and distance > 500: 
        	return 0
    	else:
            #return the distance
            return distance 

try: 
	while True : 
		if calculate_distance() < 15:
			if ok==1 :
				server.sendmail("rasberrypizero.project@gmail.com","miavanzariuc@gmail.com",message1)
				GPIO.output(8, GPIO.HIGH)
				GPIO.output(10, GPIO.LOW)
				ok=0
				
			#turn on the buzzer at a frequency of
            #500Hz for 50 ms
			pi.hardware_PWM(buzzer, 500, 500000)
			time.sleep(0.05)
			
            #turn off the buzzer and wait 50 ms
 	  		pi.hardware_PWM(buzzer, 0, 0) 
			time.sleep(0.05)
		else:
			if ok==0:
				server.sendmail("rasberrypizero.project@gmail.com","miavanzariuc@gmail.com",message2)
				GPIO.output(8, GPIO.LOW)
				GPIO.output(10, GPIO.HIGH)
				ok=1
				
			#turn off the buzzer
			pi.hardware_PWM(buzzer,0,0)
			
		#wait 100 ms before the next run
		time.sleep(0.1)

except KeyboardInterrupt: 
	pass
server.quit()

#turn off the buzzer
pi.write(buzzer, 0)

#stop the connection with the daemon
pi.stop()

#clean all the used ports
GPIO.cleanup()
