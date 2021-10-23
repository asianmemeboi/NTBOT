import cfscrape #http requests to login and verify.
import math #Calculate some encryption stuff
import time #Same as above.
import websocket #Connect to the NT live server
import json #Parse through responses from http request & live server
import threading #Used when typing the text
import random #used so bot does not get detected.
from cryptography.fernet import Fernet
import string, jsonpickle, os, requests
from automation import get_cookies
import asyncio
chars = list(string.ascii_letters+string.punctuation+string.digits)
scraper = cfscrape.create_scraper() 
index = chars.index('\'')
del chars[index]
index = chars.index('\"')
del chars[index]
def write_json(data, file='info.json'):
    with open('info.json', 'w') as f:
        json.dump(data, f, indent=4)
key = os.getenv('key')
def encrypt(message):
    """
    Encrypts a message
    """
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    return (encrypted_message.decode())
class racer():
    def __init__(self, usr, pwd, spd, acc, rcs, nitro):
        with open('scrapers.json') as f:
            data = json.load(f)
        scraper = cfscrape.create_scraper()
        self.sesh = scraper#HTTP session to be used

        self.username = usr
        self.password = pwd
        self.speed = spd
        self.accuracy = acc
        self.races = rcs
        self.nitros = nitro
        self.server = 1
    def getCookies(self, cookie_jar): #Turn cookies from a jar into a string.
        cookie_dict = cookie_jar.get_dict() #Dict
        if('2G8DA665' in cookie_dict):
            self.cookie_speed = str(cookie_dict['2G8DA665'])
        else:
            self.cookie_speed = "20"

        found = ['%s=%s' % (name, value) for (name, value) in cookie_dict.items()]
        return ';'.join(found)
    def get_time(self): #Hash a timestamp
        num = round(time.time())
        alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
        length = 64
        encoded = ''
        while num > 0:
            encoded = alphabet[num % length] + encoded
            num = math.floor(num / length)
        return encoded
    def login(self): #Login to account
        headers = {}
        #headers['accept'] = 'application/json, text/plain, */*'
        #headers['accept-encoding'] = 'gzip, deflate'
        #headers['accept-language'] = 'en-US,en;q=0.9'
        '''
        headers['cache-control'] = 'no-cache'
        headers['origin'] = 'https://www.nitrotype.com'
        headers['pragma'] = 'no-cache'
        headers['referer'] = 'https://www.nitrotype.com/login'
        '''
        headers['referer'] = 'https://www.nitrotype.com/login'
        headers['origin'] = 'https://www.nitrotype.com'
        '''log = self.sesh.post("https://www.nitrotype.com/api/login", data = {"username": self.username, "password":self.password}, headers=headers)
        #(log.text)
        self.log = log.json()'''
        self.cookies = asyncio.run(get_cookies(self.username, self.password))
        for x in self.cookies:
            self.sesh.cookies.set(x['name'], x['value'])
        self.log = self.sesh.get('https://www.nitrotype.com/api/friends').json()
        return True
    def logout(self): #Logout of account
        log_out = self.sesh.post("https://www.nitrotype.com/api/logout")
        return log_out.text
    def raceRequests(self): #Requests for race verification
        prefix = f'realtime{str(self.server)}.nitrotype.com/realtime/'
        sid_get_request = self.sesh.get(f"https://{prefix}?_primuscb=" + self.get_time() + "&EIO=3&transport=polling&t=" +  self.get_time() + "&b64=1").text
        sid = json.loads(sid_get_request.split("96:0")[1])['sid'] #SID is used in other requests
        with open('data.json') as f:
            data = json.load(f)
        print(self.log)
        length = len(str(data))+1
        data = str(length)+':4'+str(data).lower()
        raceCheck = self.sesh.post(f"https://{prefix}?_primuscb=" + self.get_time() + "&EIO=3&transport=polling&t=" + self.get_time() + "&b64=1&sid=" + sid, data = data)
        #self.sesh.get(f"https://{prefix}?_primuscb=" + self.get_time() + "&EIO=3&transport=polling&t=" + self.get_time() + "&b64=1&sid=" + sid)
        cookieString = self.getCookies(self.sesh.cookies)
        raceUrl = f"wss://{prefix}?_primuscb=" + self.get_time() + "&EIO=3&transport=websocket&sid=" + sid + "&t=" + self.get_time() + "&b64=1"
        return[cookieString, raceUrl] #Need cookies & url to connect to websocket.

    def on_open(self, ws): #Requests to send once the WS is open - verifies that websocket is good
        self.closed = False
        ws.send('2probe')
        time.sleep(0.5)
        ws.send("5")
        #4{"stream":"race","msg":"join","payload":{"update":"03417","cacheId":"7dad11db285be6cfcef037df7f970acb31a820b61357","cacheIdInteger":1357}}
        payload = '4{"stream":"race","msg":"join","payload":{"update":"03417","cacheId":"7dad11db285be6cfcef037df7f970acb31a820b61361","cacheIdInteger":1361}}'
        print(payload)
        ws.send(payload)
    def doCaptcha(self):
        self.ws.close()
        self.logout()
        req = scraper.post('https://captcha-bypass-bot.adl212.repl.co', data={'username': self.username, 'password': self.password})
        #print(req.text)
        return req
    #ws.close()
    def on_message(self,ws, message):
        print("message: ", message)
        try:
            if json.loads(message.split('4')[1])['payload']['type'] == 'captcha':
                self.doCaptcha()
        except:
            pass
        def scan_for_text(message): #Scanning messages to see if we can find the typing text.
            try:
                message = json.loads(message[1:])['payload']
                if "lessonLength" in message: #If message contains typing text
                    return message.popitem()[1]
            except:
                None
            return None

        def type(msg):
            if(len(msg) == 0 or str(msg[0]).startswith("{'user")): #These are wrong messages
                return
            delay1 = random.randrange(7, 9) / 10 #If the delays are longer apart, they have more variety. Put in race function
            delay2 = random.randrange(11, 14) / 10
            words = msg.split(" ") #Turn into a list
            wordString = ' '.join(words)#Sounds nicer than "msg"
            biggestWord = max([len(w) for w in (words[0:len(words)-1])]) #Get len of biggest word
            words = [w + ' ' for w in words[0:len(words)-1]] + [words[len(words)-1]] #add spaces
            numOfChars = len(wordString)
            numOfWords = numOfChars/5
            numOfSecs = (numOfWords/self.speed) * 60
            sleepTime = numOfSecs / numOfChars
            sleep1 = round((sleepTime * delay1), 6) * 10000000
            sleep2 = round((sleepTime * delay2), 6) * 10000000 #Get time to sleep after each char
            time.sleep(4.3) #wait until race starts
            if(self.nitros == 'true'):
                usedNitro = False
            elif(self.nitros == 'random'): #Random check to see if we should use nitros
                check = random.randrange(1,3)
                if(check == 1):
                    usedNitro = False
                else:
                    usedNitro = True
            else:
                usedNitro = True
            ws.send('4{"stream":"race","msg":"update","payload":{"t":1,"f":0}}') #First character has to have "f":0
            t  = 2
            e = 1

            for w in words:
                if self.closed == True:
                    break
                if(int(len(w)) >= int(biggestWord) and usedNitro == False):
                    t += len(w)
                    payload = '4{"stream":"race","msg":"update","payload":{"n":1,"t":' + str(t) + ',"s":' + str(len(w)) + '}}' #Using nitro
                    ws.send(payload)
                    time.sleep(0.2)
                    payload = '4{"stream":"race","msg":"update","payload":{"t":' + str(t) + '}}' #sending another character
                    ws.send(payload)
                    t += 1
                    usedNitro = True
                else:
                    for c in w:
                        if self.closed == True:
                            break
                        errorProbability = random.randrange(0,100) / 100
                        accuracyWrongPercentage = 1 - self.accuracy/100
                        if(accuracyWrongPercentage >= errorProbability):
                            #print('Wrong character')
                            payload = '4{"stream":"race","msg":"update","payload":{"e":' + str(e) + '}}' #sending error
                            ws.send(payload)
                            e += 1
                        if t % 4 == 0 or t >= numOfChars - 4:
                            payload = '4{"stream":"race","msg":"update","payload":{"t":' + str(t) + '}}' #sending character
                            ws.send(payload)
                        t += 1
                        sleeptime = random.randrange(int(sleep1), int(sleep2)) / 10000000 #sleep between each character at a random interval according to the WPM
                        time.sleep(sleeptime)
            if self.closed == False:
                ws.close()
        words = scan_for_text(message)
        if words != None:

            typingTheText = threading.Thread(target = type, args  = [words]) #starting a thread to race
            typingTheText.start()
    def on_error(self, ws, error):
        print("error:", error)

    def on_close(self, ws):
        self.closed = True
    def race(self):
        #print("New Race for " + self.username + ": ")
        starting = self.raceRequests()
        cookieString = starting[0]
        socketLink = starting[1] #Connecting to websocket below, lambda so it can be used in a class
        self.ws = websocket.WebSocketApp(socketLink,
                              on_message = lambda ws,msg: self.on_message(ws, msg),
                              on_error   = lambda ws,msg: self.on_error(ws, msg),
                              on_close   = lambda ws:     self.on_close(ws),
                              header = {'cookie': cookieString, 'Origin':'https://www.nitrotype.com', 'User-Agent':"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/55.0.2883.87 Chrome/55.0.2883.87 Safari/537.36"})
        self.ws.on_open = lambda ws:     self.on_open(ws)                        
        self.ws.run_forever()
    def stopBot(self):
        self.currentRaces = self.races
        #print('stopped')
    def startBot(self):
        self.currentRaces = 0
        while self.currentRaces < self.races:
            if(self.currentRaces % 50 == 0):
                self.logout()
                while True:
                    logged = self.login()
                    #print(self.log)
                    try:
                        self.logout()
                        if (self.log)['success'] == False and self.log['data']['captchaStatus'] == 'pending':
                            thread = threading.Thread(target=self.doCaptcha)
                            thread.start()
                            thread.join(10)
                        else:
                            break
                    except:
                        break
                #every 100 races
                if str(logged) == 'False':
                    #print("Invalid Username/Password! Please restart the program and try again.")
                    #a = input()
                    return
                else:
                    print(self.log)
                    print("Loggged in successfully!")
            #print("Racing...")
            self.race()
            self.currentRaces += 1
            #print(f"Race completed for {self.username}! (Race #" + str(self.currentRaces) + ')')
            if random.randint(0, 250) ==  0:
              time.sleep(random.randint(60, 120000))
            time.sleep(3)
            if self.currentRaces == self.races:
                pass
                #print(f"Race completed for {self.username}! (Race #" + str(self.currentRaces) + ')')
            
        #print("Completed Races!")
    def realStart(self):
        typingThread = threading.Thread(target = self.startBot, args = [])
        typingThread.start()
