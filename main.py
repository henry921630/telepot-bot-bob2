# -*- coding: utf8 -*-
# coding: utf8
from __future__ import print_function
import re
import ast
import httplib2
import urllib
import json
import apiai
import os
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient import discovery
import linecache
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from time import sleep
import random
import datetime
import telepot
import uniout
import os.path
import sys
reload(sys)
sys.setdefaultencoding('utf8')  
import tzlocal
import pytz
tz = pytz.timezone('Asia/Taipei') # <- put your local timezone here
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

bbmousetoken='293749176:AAFUwX1PMi-FtFnorDJga3l3vKRcCBuwHTo'
testingtoken='290645324:AAGhpIzNqzDejvhQSPR4-FIqmy4WbtLPzVI'
version="v2.0 20170316"
B=bbmousetoken
T=testingtoken
mode=B

#Google Clanlendar
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
SCOPES = 'https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/plus.login'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    print("get_credentials========================")
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    print("credential_dir"+credential_dir)
    if not os.path.exists(credential_dir):
        print("get_credentials========================")
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')
    print("credential_path=========="+credential_path)
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


class GoogleCalendar():
    """docstring for GoogleCalendar"""
    def __init__(self):
        #super(GoogleCalendar, self).__init__()
        self.eventsummary = "嗶鼠小提醒"
        self.eventstart= datetime.datetime.now(tz)
        
    def createvent(self,eventsummary,eventstart):
        eventxxx = {
          'summary': eventsummary,
          'location': '',
          'description': '嗶鼠小提醒',
          'start': {
            'dateTime': eventstart,
            'timeZone': 'Asia/Taipei',
          },
          'end': {
            'dateTime': eventstart,
            'timeZone': 'Asia/Taipei',
          },
          
          
          'reminders': {
            'useDefault': False,
            'overrides': [
              {'method': 'email', 'minutes': 10},
              {'method': 'popup', 'minutes': 10},
            ],
          },
        }

        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service=discovery.build('calendar', 'v3', http=http)

        eventxxx = service.events().insert(calendarId='primary', body=eventxxx).execute()
        print ("Event created: " + (eventxxx.get('htmlLink')))
        return (eventxxx.get('htmlLink'))

    def listrecentevent(self):
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service=discovery.build('calendar', 'v3', http=http)

        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print (now)
        print('Getting the upcoming 10 events')
        eventsResult = service.events().list(
            calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])
        recenteventlist=[]
        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            #稍微修剪一下格式:
            start=start[0:10]+" " +start[11:16]
            print(start, event['summary'])
            recenteventlist.append(start+" "+event['summary'])
        return recenteventlist


def issetremind(command):
    if( "提醒我" in command):
        return True
    else:
        return False

def isWantRecentEventList(command):
    if( "有什麼行程" in command):
        return True
    else:
        return False

def getTimeValue(command):
    TimeValueHour=TimeValueMin=sec=0

    if("晚上" in command or "下午" in command or "夜晚" in command):
        AMPM="PM"
    elif("清早" in command or "早上" in command or "上午" in command):
        AMPM="AM"
    else:
        AMPM="PM" #感覺下午和晚上的行程會比較多，所以預設是PM (好像邏輯有點薄弱XD)
    numberinchinese=["一","二","三","四","五","六","七","八","九","十","十一","十二","十三","十四","十五","十六","十七","十八","十九","二十","二十一","二十二","二十三","二十四","二十五","二十六","二十七","二十八","二十九","三十","三十一","三十二","三十三","三十四","三十五","三十六","三十七","三十八","三十九","四十","四十一","四十二","四十三","四十四","四十五","四十六","四十七","四十八","四十九","五十","五十一","五十二","五十三","五十四","五十五","五十六","五十七","五十八","五十九","六十","六十一","六十二","六十三","六十四","六十五","六十六","六十七","六十八","六十九","七十","七十一","七十二","七十三","七十四","七十五","七十六","七十七","七十八","七十九","八十","八十一","八十二","八十三","八十四","八十五","八十六","八十七","八十八","八十九","九十","九十一","九十二","九十三","九十四","九十五","九十六","九十七","九十八","九十九","一百"
] #因為十二和十一都包含了"十" 所以應該倒著檢測
    numberinarabic=range(1,101)

    #把一些別名統整一下
    if ("兩點" in command):
        command=command.replace("兩點","二點")
    if ("點半" in command):
        command=command.replace("點半","點三十分")
    if ("一刻" in command):
        command=command.replace("一刻","十五分")
    for num in range(0,12): #測小時，只要一到十二就好
        # print(num)
        # print(numberinchinese[11-num])
        if (numberinchinese[11-num] in command[command.index("點")-3:command.index("點")]):
            command=command.replace(numberinchinese[11-num],str(numberinarabic[11-num]))
    for num in range(0,60): #測分鐘，要一到六十
        if (numberinchinese[59-num] in command[command.index("點"):command.index("點")+4]):
            command=command.replace(numberinchinese[59-num],str(numberinarabic[59-num]))
        

    TimeValueHour=int(re.search('\D(\d{1,2})',command[command.index("點")-3:command.index("點")]).group(1))+12*(AMPM=="PM")
    # print(command)
    # print(command[command.index("點")+1:command.index("點")+4])

    try:
        TimeValueMin=int(re.search('\D(\d{1,2})',command[command.index("點"):command.index("點")+4]).group(1))
    except:
        pass

    # print (TimeValueHour)
    # print(AccountingSentenceAnalysis_get_date(command))
    TimeValueforGoogleCalendar= AccountingSentenceAnalysis_get_date(command) + "T" + "{hour:0>2}:{min:0>2}:{sec:0>2}".format(hour=TimeValueHour,min=TimeValueMin,sec=sec)+"+08:00"
    print (TimeValueforGoogleCalendar)
    return TimeValueforGoogleCalendar

def CallAPIAI(command):
    CLIENT_ACCESS_TOKEN = '7104be5d56bd495aa62f9b3c1a03d6bf'
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

    request = ai.text_request()

    request.lang = 'zh-TW'  # optional, default value equal 'en'

    request.session_id = "123456"#"<SESSION ID, UNIQUE FOR EACH USER>"

    request.query = command
    response = request.getresponse()
    responsestr = response.read().decode('utf-8')
    response_obj = json.loads(responsestr)
    # print (response_obj)
    # print (response_obj["result"]["fulfillment"]["speech"])

    return (response_obj["result"]["fulfillment"]["speech"])


def auth_gss_client(path, scopes):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path,
                                                                   scopes)
    return gspread.authorize(credentials)

def update_sheet(gss_client, key, today):
    wks = gss_client.open_by_key(key)
    sheet = wks.sheet1
    sheet.insert_row([today], 2)

def isVaildDate(date):
        try:
            if ":" in date:
                time.strptime(date, "%Y-%m-%d %H:%M:%S")
            else:
                time.strptime(date, "%Y%m%d")
            return True
        except:
            return False 

def BBMouseDevelopingHistory(command):
    # auth_json_path = 'BBMouseGS.json'
    # gss_scopes = ['https://spreadsheets.google.com/feeds']
    # gss_client = auth_gss_client(auth_json_path, gss_scopes)
    # wks = gss_client.open_by_key("1zowQqJ3bmSvTkId32x5KfDWpOxbDvhYzvHeeVd2BfKw") #嗶鼠記帳小本子
    # sheet = wks.sheet1
    
    # sheet.insert_row([salutation,date,item,price,acctype,command], 2)
    pass


def BBMouseAccounting(chat_id,salutation,date, item,source, price,acctype,command):
    auth_json_path = 'BBMouseGS.json'
    gss_scopes = ['https://spreadsheets.google.com/feeds']
    gss_client = auth_gss_client(auth_json_path, gss_scopes)
    wks = gss_client.open_by_key("1zowQqJ3bmSvTkId32x5KfDWpOxbDvhYzvHeeVd2BfKw") #嗶鼠記帳小本子
    sheet = wks.sheet1
    
    sheet.insert_row([salutation,date,item,source,price,acctype,command], 2)

def BBMouseMemo(chat_id,date, item,command):
    auth_json_path = 'BBMouseGS.json'
    gss_scopes = ['https://spreadsheets.google.com/feeds']
    gss_client = auth_gss_client(auth_json_path, gss_scopes)
    wks = gss_client.open_by_key("1eWwA5Ds2tOC9rwiH4RPJ_9qxW2MOKNvx-Zcw4rPBSEY") #嗶鼠備忘小本子
    sheet = wks.sheet1
    
    sheet.insert_row([date,item,command], 2)


def StrPermutation(list1,list2,list3):
    list0=[]
    for x in range(len(list1)):
        for i in range(len(list2)):
            for j in range(len(list3)):
                list0.append(list1[x]+list2[i]+list3[j])
    return list0


def getseperatepoint(command):
    seperatepoint=-1
    try:
        seperatepoint=command.index(" ")
    except:        
        pass
        #print ("no this seperatepoint")
    try:
        seperatepoint=command.index(",")
    except:        
        pass
        #print ("no this seperatepoint")
    try:
        seperatepoint=command.index("，")
    except:        
        pass
        #print ("no this seperatepoint")
    try:
        seperatepoint=command.index(":")
    except:        
        pass
        #print ("no this seperatepoint")
    try:
        seperatepoint=command.index("：")
    except:
        pass
        #print ("no this seperatepoint")
    return seperatepoint

def AccountingSentenceAnalysis_get_date(command):
    #command=command[getseperatepoint(command)+1:]
    try:
        RegularExpressDate_8digit=(re.search('[0-9]{8}', command)).group()
    except:
        RegularExpressDate_8digit=""
       #print ("無八碼")
    # print (command)
    
    
    if "今天" in command or "today"  in command or "now"  in command or "剛剛"  in command  or "剛才"  in command or "我剛"  in command:
        accDate=time.strftime("%Y-%m-%d", time.gmtime(time.time()+8*60*60))                  #八小時乘上六十分鐘乘上六十秒
    elif "昨" in command or "yesterday"  in command  :
        accDate=time.strftime("%Y-%m-%d", time.gmtime(time.time()+8*60*60 -60*60*24))                  #八小時乘上六十分鐘乘上六十秒 再減一天回到昨天
    elif "前天" in command or "before yesterday"  in command  :
        accDate=time.strftime("%Y-%m-%d", time.gmtime(time.time()+8*60*60 -2*60*60*24))                  #八小時乘上六十分鐘乘上六十秒 再減二天回到前天
    elif "大前天" in command or "before yesterday"  in command  :
        accDate=time.strftime("%Y-%m-%d", time.gmtime(time.time()+8*60*60 -3*60*60*24))                  #八小時乘上六十分鐘乘上六十秒 再減三天回到大前天
    elif "明天" in command or "tomorrow"  in command  :
        accDate=time.strftime("%Y-%m-%d", time.gmtime(time.time()+8*60*60 +60*60*24))                  #八小時乘上六十分鐘乘上六十秒 再加一天進到明天
    elif "後天" in command or "after tomorrow"  in command  :
        accDate=time.strftime("%Y-%m-%d", time.gmtime(time.time()+8*60*60 +2*60*60*24))                  #八小時乘上六十分鐘乘上六十秒 再加兩天進到後天
    elif "大後天" in command or "before yesterday"  in command  :
        accDate=time.strftime("%Y-%m-%d", time.gmtime(time.time()+8*60*60 +3*60*60*24))                  #八小時乘上六十分鐘乘上六十秒 再加三天進到大後天
    elif "禮拜" in command or "周"  in command  or "週"  in command:
        #print('"禮拜" in command or "周"  in command  or "週"  in command')
        if "上"  in command:        
            w=command.count("上")-command.count("上午")-command.count("早上")-command.count("上班")
            if("早上" in command):
                w=w-1
        elif "下" in command:
            w=-(command.count("下")-command.count("下午")-command.count("下班"))

        else:
            w=0
        print("W:"+str(w))

        if "禮拜1" in command or "禮拜一" in command or "週一" in command or "周一" in command:
            wd=1
        elif "禮拜2" in command or "禮拜二" in command or "週二" in command or "周二" in command:
            wd=2
        elif "禮拜3" in command or "禮拜三" in command or "週三" in command or "周三" in command:
            wd=3
        elif "禮拜4" in command or "禮拜四" in command or "週四" in command or "周四" in command:
            wd=4
        elif "禮拜5" in command or "禮拜五" in command or "週五" in command or "周五" in command:
            wd=5
        elif "禮拜6" in command or "禮拜六" in command or "週六" in command or "周六" in command:
            wd=6
        elif "禮拜日" in command or  "禮拜天" in command or "週日" in command or "周日" in command:
            wd=7
        else:
            pass
        print("wd:"+str(wd))
        #待做 先回到本週一，再減去週數，再加到指定weekday
        dt=datetime.datetime.fromtimestamp(time.mktime(time.gmtime())+60*60*8) #調整八小時時區後的現在時間(datetime)
        if datetime.date.today().weekday()==6: #Monday is 0, Sunday is 6
            thisMonday=(datetime.timedelta(days=7))+dt-datetime.timedelta(days=datetime.date.today().weekday())
        else:
            thisMonday=dt-datetime.timedelta(days=datetime.date.today().weekday())

        print(datetime.date.today().weekday())
        print("===thisMonday==")        
        print(thisMonday)        
        lastMonday=thisMonday-datetime.timedelta(7*w)
        print("===lastMonday==")        
        print(lastMonday)         
        lastSomeday=lastMonday+ datetime.timedelta(wd-1)
        print("===lastSomeday==")        
        print(lastSomeday)         
        timetuple=lastSomeday.timetuple()
        accDate=time.strftime("%Y-%m-%d", timetuple)          
    elif isVaildDate( RegularExpressDate_8digit) == True:
        accDate=RegularExpressDate_8digit[:4] + "-" + RegularExpressDate_8digit[4:6] +"-" +RegularExpressDate_8digit[6:]
    else:
        #accDate="日期格式記錯了"
        accDate=time.strftime("%Y-%m-%d", time.gmtime(time.time()+8*60*60))                  #如果偵測不到日期就預設為今天

    return accDate

def ifaskaccounting(command):
    if ("記" in command[:12] and "帳" in command[:12]):
        return True
    elif("accounting" in command[:11]):
        return True
    else:
        return False

def isaskmemo(command):
    if ("備忘" in command[:5] or "記事" in command[:5] or "note" in command[:5] or "memo" in command[:5]):
        return True
    else:
        return False

def isaskShoppingList(command):
    if ("購物清單" in command[:12] or "shoppinglist" in command[:12] or "採購清單" in command[:12] or "待購" in command[:12]):
        return True
    else:
        return False
def updateShoppingList(command,chat_id):
    f = open('ShoppingList.txt','rb')
    
    SL=f.read().split(",") #SL stands for Shopping List
    f.close
    SLmsg=""
    SLorder=0


    if "買了" in command:
        numberinchinese=["一","二","三","四","五","六","七","八","九","十","十一","十二","十三","十四","十五","十六","十七","十八","十九","二十","二十一","二十二","二十三","二十四","二十五","二十六","二十七","二十八","二十九","三十","三十一","三十二","三十三","三十四","三十五","三十六","三十七","三十八","三十九","四十","四十一","四十二","四十三","四十四","四十五","四十六","四十七","四十八","四十九","五十","五十一","五十二","五十三","五十四","五十五","五十六","五十七","五十八","五十九","六十","六十一","六十二","六十三","六十四","六十五","六十六","六十七","六十八","六十九","七十","七十一","七十二","七十三","七十四","七十五","七十六","七十七","七十八","七十九","八十","八十一","八十二","八十三","八十四","八十五","八十六","八十七","八十八","八十九","九十","九十一","九十二","九十三","九十四","九十五","九十六","九十七","九十八","九十九","一百"] 
        #因為十二和十一都包含了"十" 所以應該倒著檢測
        numberinarabic=range(1,101)
        for i in range(20):#假設待辦事項不會超過二十項
            if numberinchinese[9-i] in command:
                command=command.replace(numberinchinese[9-i],str(numberinarabic[9-i]))
                # command=command.replace("一","1")
        ordercompleted=int(re.search('\D(\d{1,2})',command).group(1))
        
        del SL[ordercompleted]


        SLline=""
        for i in range(len(SL)):
            
            SLline=SLline+SL[i]+","
            
        f = open('ShoppingList.txt','wb')
        #為了消除結尾逗號，少取一格
        f.write(SLline[:-1])
        print("SLline")
        print(SLline[:-1])     
        for i in SL:
            SLmsg=SLmsg +str(SLorder)+":"+ i+"\n"
            SLorder+=1
        if len(SLmsg)<=3:
            SLmsg="現在待購清單沒有要買的東西哦～"
        bot.sendMessage(chat_id,"待購事項清單\n"+SLmsg)

    elif "新增" in command:
        f = open('ShoppingList.txt','rb')
        command=command.replace("新增","").replace("待購","").replace("待購項目","").replace(" ","")
        commandlist=getcommandlistbyeachline(command) #add Shoppinglist in batch
        if len(SL[0])<4: #如果原本待辦事項是空的話，要把第一個空值刪掉
            SL[0]=command
            for i in range(len(commandlist)):
                SL.append(commandlist[i])
                print("SL")
                print(SL)
            del SL[0]
        else:
            for i in range(len(commandlist)):
                
                SL.append(commandlist[i])
                print("SL")
                print(SL)
        SLline=""
        for i in range(len(SL)):
            
            SLline=SLline+SL[i]+","
            
        f = open('ShoppingList.txt','wb')
        #為了消除結尾逗號，少取一格
        f.write(SLline[:-1])
        print("SLline")
        print(SLline[:-1])
        for i in SL:
            SLmsg=SLmsg +str(SLorder)+":"+ i+"\n"
            SLorder+=1
        if len(SLmsg)<=3:
            SLmsg="現在待購清單沒有要買的東西哦～"
        bot.sendMessage(chat_id,"待購事項清單\n"+SLmsg)

    else:
        for i in SL:
            SLmsg=SLmsg +str(SLorder)+" "+ i+"\n"
            SLorder+=1
        print ("len(SLmsg)")
        print (len(SLmsg))
        if len(SLmsg)<=3:
            SLmsg="現在待購清單沒有要買的東西哦～"
        bot.sendMessage(chat_id,SLmsg)
def isaskToDoList(command):
    if ("待辦" in command[:12] or "todolist" in command[:12]):
        return True
    else:
        return False
def updateToDoList(command,chat_id):
    f = open('ToDoList.txt','rb')
    
    TDL=f.read().split(",")
    f.close
    TDLmsg=""
    TDLorder=0


    if "完成" in command:
        numberinchinese=["一","二","三","四","五","六","七","八","九","十","十一","十二","十三","十四","十五","十六","十七","十八","十九","二十","二十一","二十二","二十三","二十四","二十五","二十六","二十七","二十八","二十九","三十","三十一","三十二","三十三","三十四","三十五","三十六","三十七","三十八","三十九","四十","四十一","四十二","四十三","四十四","四十五","四十六","四十七","四十八","四十九","五十","五十一","五十二","五十三","五十四","五十五","五十六","五十七","五十八","五十九","六十","六十一","六十二","六十三","六十四","六十五","六十六","六十七","六十八","六十九","七十","七十一","七十二","七十三","七十四","七十五","七十六","七十七","七十八","七十九","八十","八十一","八十二","八十三","八十四","八十五","八十六","八十七","八十八","八十九","九十","九十一","九十二","九十三","九十四","九十五","九十六","九十七","九十八","九十九","一百"] 
        #因為十二和十一都包含了"十" 所以應該倒著檢測
        numberinarabic=range(1,101)
        for i in range(20):#假設待辦事項不會超過二十項
            if numberinchinese[9-i] in command:
                command=command.replace(numberinchinese[9-i],str(numberinarabic[9-i]))
                # command=command.replace("一","1")
        ordercompleted=int(re.search('\D(\d{1,2})',command).group(1))
        
        del TDL[ordercompleted]


        TDLline=""
        for i in range(len(TDL)):
            
            TDLline=TDLline+TDL[i]+","
            
        f = open('ToDoList.txt','wb')
        #為了消除結尾逗號，少取一格
        f.write(TDLline[:-1])
        print("TDLline")
        print(TDLline[:-1])     
        for i in TDL:
            TDLmsg=TDLmsg +str(TDLorder)+":"+ i+"\n"
            TDLorder+=1
        if len(TDLmsg)<=3:
            TDLmsg="現在沒有待辦事項哦～"
        bot.sendMessage(chat_id,"目前待辦事項清單\n"+TDLmsg)

    elif "新增" in command:
        f = open('ToDoList.txt','rb')
        command=command.replace("新增","").replace("待辦","").replace("待辦事項","").replace(" ","")
        commandlist=getcommandlistbyeachline(command) #add todolist in batch
        if len(TDL[0])<4: #如果原本待辦事項是空的話，要把第一個空值刪掉
            TDL[0]=command
            for i in range(len(commandlist)):
                TDL.append(commandlist[i])
                print("TDL")
                print(TDL)
            del TDL[0]
        else:
            for i in range(len(commandlist)):
                
                TDL.append(commandlist[i])
                print("TDL")
                print(TDL)
        TDLline=""
        for i in range(len(TDL)):
            
            TDLline=TDLline+TDL[i]+","
            
        f = open('ToDoList.txt','wb')
        #為了消除結尾逗號，少取一格
        f.write(TDLline[:-1])
        print("TDLline")
        print(TDLline[:-1])
        for i in TDL:
            TDLmsg=TDLmsg +str(TDLorder)+":"+ i+"\n"
            TDLorder+=1
        if len(TDLmsg)<=3:
            TDLmsg="現在沒有待辦事項哦～"
        bot.sendMessage(chat_id,"目前待辦事項清單\n"+TDLmsg)

    else:
        for i in TDL:
            TDLmsg=TDLmsg +str(TDLorder)+" "+ i+"\n"
            TDLorder+=1
        print ("len(TDLmsg)")
        print (len(TDLmsg))
        if len(TDLmsg)<=3:
            TDLmsg="現在沒有待辦事項哦～"
        bot.sendMessage(chat_id,TDLmsg)


def needconfirmifaskaccounting(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    command = msg['text']
    try:
        amount=re.search('\D(\d{1,4})',command).group(1)
    except:
        amount=""
    print ("command in confirm:" )
    print ("command in confirm:" + amount)
    if not("記" in command and "帳" in command) and ("元" in command or "$" in command) and amount<>"":
        bot.sendMessage(chat_id,"是要記帳的意思嗎？")
        yesorno(msg)
        
        msglist=[]
        count2=0
        
        f = open('msghistory.csv', 'rb')
        for row in csv.reader(f):
            msglist.append(row)
            #print ("row:"+str(row))
            count2=count2+1
        f.close()

        csvfile=open("msghistory.csv", "wb+")
        print("writing history in msghistory.csv")
        print (msg)
        writer = csv.writer(csvfile)

        for row in msglist:        
            #print(row)
            writer.writerow([row[0],"END"])    
        writer.writerow([msg,"END"])
        csvfile.close()


        print("exit")
        sys.exit()
    else:
        pass

def yesorno(msg): #let user choose an anwser
    content_type, chat_type, chat_id = telepot.glance(msg)
    bot.sendMessage(chat_id,"是/否",reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text="是", callback_data='yes')],
                   [InlineKeyboardButton(text="否", callback_data='no')],
                   ]))


def AccountingSentenceAnalysis_get_source(command):
    if "悠遊卡" in command or "悠游卡" in command or "easycard" in command or "easy card" in command:
        source="悠遊卡"
    elif "玉山" in command and "卡" in command:
        source="玉山信用卡"
    elif "華南" in command and "卡" in command and "旅鑽" in command:
        source="華南旅鑽卡"
    elif "富邦" in command and "卡" in command:
        source="富邦信用卡"
    elif "樂天" in command and "卡" in command:
        source="樂天信用卡"
    elif "華南" in command and "卡" in command and "夢時代" in command:
        source="華南夢時代卡"
    elif "用" in command :


        verblist=["買","花","購","吃","喝","付","繳","看","幫",""]
        n=len(command)

        for i in verblist:
            try:

                tempn=command.index(i)
                if tempn<n and tempn>1:
                    n=tempn
            except:
                pass

        source=str(command[command.index("用")+1:n])
    else:
        source = "現金"
    print ("AccountingSentenceAnalysis_get_source:" + source)
    return source

    pass



def AccountingSentenceAnalysis_get_person(command):
    pass
def AccountingSentenceAnalysis_get_item(command):
    # if ifaskaccounting(command):
    #     command=command[getseperatepoint(command)+1:]
    # else:
    #     command=command

    # print("AccountingSentenceAnalysis_get_item command:" + command)
    
    subjectlist=["我","爸爸","媽媽","他","她","嗶","鼠","你"," "]

    timeadvlist1=["上上","上","這"]    
    timeadvlist2=["禮拜","星期","週","周"]    
    timeadvlist3=["一","二","三","四","五","六","日","天"]    
    timeadvlist=StrPermutation(timeadvlist1,timeadvlist2,timeadvlist3)+["前天","昨天","昨日","早上","中午","下午","晚上","今日","今天","今兒個","剛剛","剛才"]

    sourcelist=["華南卡","玉山卡","樂天卡","富邦卡"]
    verblist=["刷了","用","花了","購入","吃了","喝","點了","付了","繳了","繳交","賺了",""]
    advlist=["了","哦","啊","呢","喔","總共","共"]

    try:
        RegularExpressDate_8digit=(re.search('[0-9]{8}', command)).group()
    except:
        RegularExpressDate_8digit=""
        print ("無八碼")
    
    ohterlist=[RegularExpressDate_8digit,"$","元","塊錢","記帳","記個帳","謝謝"]
    punctuationlist=["！","!","，",","]
    totalelementlist=[AccountingSentenceAnalysis_get_source(command),AccountingSentenceAnalysis_get_amount(command)]+subjectlist+timeadvlist+sourcelist+verblist+advlist+ohterlist+punctuationlist
    item=command
    # print ("item=command")
    # print (item)
    for i in range(len(totalelementlist)):
        try:
            item=item.replace(totalelementlist[i],"")
            
            #print ("item:" + item+" 取代標的:")+totalelementlist[i]
        except:
            pass
            #print ("No this subject."+ totalelementlist[i])
    # print (item)
    return item

def AccountingSentenceAnalysis_get_amount(command):

    # print("AccountingSentenceAnalysis_get_amount"+command)
    amount=0

    if "元" in  command and type(int(command[command.index("元")-1]))==int:
        #print (type(command.index("塊")-1))
        amount=re.search('\d{1,4}',command[(command.index("元")-5):command.index("元")]).group()
    elif "塊" in command  and  type(int(command[command.index("塊")-1]))==int:
        amount=re.search('\d{1,4}',command[(command.index("塊")-5):command.index("塊")]).group()
    elif "$" in command:
        amount=re.search('\d{1,4}',command[(command.index("$")):command.index("$")+5]).group()
    else :
        amount=re.search('\D(\d{1,4}$)',command).group(1)
    
    print ("amount: "+str(amount))
 
    return amount

def getcommandlistbyeachline(command):
    if "\n" in command:
        commandlist=command.split("\n")
        
    else:
        commandlist=[command]

    return commandlist
    


def handle(msg):
    print ("start handle")
    print (type(msg))
    if not( isinstance(msg,dict)):
        msg=ast.literal_eval(msg)
    print (type(msg))
    print (msg)


    BBMresponce_file_id=""

    BBMresponse_str=["","",""]
    content_type, chat_type, chat_id = telepot.glance(msg)



    if msg['text'][0:1]=="/":
        botcommand=True
    else:
        botcommand=False

    if chat_type=="group":
        command = msg['text'][1:]
        if (msg['from']['id'] ==271383530):

            salutation = "爸爸"

        elif (msg['from']['id']==288200245):
            salutation = "媽媽"

    else:
        command = msg['text']
        if (chat_id ==271383530):
            #除錯時使用 回傳msg  bot.sendMessage(271383530,msg)
            salutation = "爸爸"
        elif (chat_id ==288200245):
            salutation = "媽媽"


#處理貼圖或檔案訊息
    if content_type == 'sticker' or  content_type == 'document':
        #response=bot.getUpdates()
        print (msg)
        BBMresponse_str[0]=str( salutation + "，我看不懂貼圖啦！")
        #抓取file_id用
        #bot.sendMessage(msg['chat']['id'],str(msg)+"tttt")

        
        #bot.sendMessage(chat_id,msg[content_type]['file_id'])
        BBMresponce_file_id = "BQADBQAD_wADqX9lBRyUzTL8n7SaAg"

        
    #if content_type == 'document':
    #    bot.sendMessage(msg['chat']['id'],msg)

#處理純文字訊息
    if content_type == 'text':
        isaccountdefined=False
        try:
            print(msg)
            if msg["isaccount"]=="True":
                isforaccount=True
                isaccountdefined=True
                command="記帳"+command
            elif  msg["isaccount"]=="False":
                isaccountdefined=True
                isforaccount=False
            else:
                isaccountdefined=False
        except:
            pass

        if not(isaccountdefined):
            needconfirmifaskaccounting(msg)
            #print (needconfirmifaskaccounting(msg))

        else:
            pass


        # command=command.replace("NotForAccounting","")
        # isaskaccounting=False
        #print (needconfirmifaskaccounting(msg))
        chat_id = msg['chat']['id']
        
        print (datetime.datetime.today())
        print (msg['chat']['id'])
        print ("")
        print (msg)
        printx = 'Got command: %s' % command    
        # print (printx)
        if (command[0:2] == "/v" ):
            bot.sendMessage(288200245, msg['text'][3:])
            bot.sendMessage(271383530, msg['text'][3:])

        else:
            
            if (chat_id == 288200245):
                bot.sendMessage(271383530, u"酥熊跟嗶鼠機器人說了: \n" + str(msg['text']))
            #lrsy就是戀人絮語的意思 20170316 轉至API.AI
            # lrsy = {1:"V: 請用一個字來形容我！ H: 好！",\
            #         2:"V：聽說埃及沒有郵局，如果埃及的人民想要寄信，必須出埃及寄。\nH：聽說有舌頭味覺不靈光的人，如果想要得嚐美食，必須服用利味劑。",\
            #         3:"[神魔之塔轉珠中]H: 別人轉珠都好強喔！\nV: 所以別人是神轉珠，你是豬轉珠囉～\nH: 甚麼！好歹說我是神豬轉珠吧！\nV: 神豬轉珠不就是神豬他爸轉珠嗎～哈哈哈哈！",\
            #         4:"V: 那些蛋糕看起來都好好吃，我要吃一百個！ \nH: 蛤…妳要不要改成吃95個就好，妳都那麼胖了…",\
            #         5:"[在床上翻來翻去的小酥餅]\nV: 睡不著耶\nH: 對不起～我太吵了嗎？都是我在心中不斷的大叫「我愛小酥餅」！",\
            #         6:"我在浴室，小羴羊敲了敲門才走進來。\nV: 小羴羊都會敲門才進來耶，真有禮貌。\nH: 我怕打到小酥餅的頭嘛。\nV: (暗自竊喜，老公真疼我)\nH: 其實我不怕打到酥餅的頭，我是怕酥餅罵我。",\
            #         7:"爺爺揹著小酥熊，走到山上來看猴，猴子哭了叫"+ salutation +"，就被爺爺揹回家。 \nhttps://youtu.be/HDL1Ivz55N0",\
            #         8:"「生氣的酥熊」\n「來把牠進化吧」\n「變成更生氣的酥熊」\nhttps://youtu.be/yxg06yebRd0",\
            #         9:"(叭叭叭 媽媽擤鼻涕中)\n羊：有人在跟妳呼應，一起擤鼻涕\n熊：這是我們康巴族的鼓語\n羊：那妳跟他說了什麼？\n熊：我叫他趕快出來，我要大便；他回不要不要\n羊：酥熊用康巴族鼓語讓對方不要不要的\n",\
            #         }




            bbmousescripts = { 1:"哇姆災喔！",\
                        2:"好想念跳跳喔！",\
                        3:"(揮舞大棒棒)",\
                        4:"真拿"+ salutation +"沒有辦法！",\
                        5:"(探頭)讓我來尋找矮胖國的新成員",\
                        6:"(敲擊肚子)咚咚咚~~~",\
                        7:"(昏倒！)",\
                        8:"(跑來跑去跑來跑去)",\
                        9:"(飛～起來～)",\
                               }

            dq = { 1:"有人說有一個藍瘦香菇的前面還有一個藍瘦香菇……\n"+ salutation +"，你覺得香菇如果有語言的話，他們的詞彙裡面會有「前面」「後面」的概念嗎？(搔頭) ",\
                        2:""+ salutation +"～昨天睡覺時有個外星人從遙遠的地方跟我通訊，我跟他說我們的心臟一般都長在「左邊」\n可是他都不懂什麼叫做「左邊」耶(搔頭)……\n左邊不就是右邊的另外一邊嗎！真拿外星人沒有辦法～",\
                        3:"智能不足好痛苦QQ",\
                        4:"爸爸在法國居住的時候，住所沒有電鍋，為了減少煮飯時產生的鍋巴，我們一起來一直在思考一個問題： \n在每一餐皆煮相同米量的前提下， \n應該選用什麼尺寸比例的圓柱形鍋子，才能使米飯接觸鍋體的面積最小呢？"
                               }

            #生日快樂
            # print ("聖誕" in command or  "平安" in command or "耶誕" in command or (datetime.datetime.today().month==12 and (datetime.datetime.today().day==24 or datetime.datetime.today().day==25)))
            # print (datetime.datetime.today().day==24 or datetime.datetime.today().day==25)
            if  (datetime.datetime.today().month==12 and (datetime.datetime.today().day==24 or datetime.datetime.today().day==25)):
                rd=random.randint(1,100)
                if "聖誕" in command or  "平安" in command or "耶誕" in command:
                    rd=random.randint(80,100)
                if rd>=90:
                    BBMresponse_str[0]= str( u" 我要報給你們一個大喜的訊息，是關乎萬民的～～")
                    bot.sendMessage(chat_id,BBMresponse_str[0])
                elif rd>=80:
                    BBMresponse_str[0]= str( u"耶～今天是平安夜耶，"+ salutation +"聖誕快樂！\n嗶鼠不用什麼禮物，只要"+salutation+"愛我就好了！")
                    bot.sendMessage(chat_id,BBMresponse_str[0])
                    if mode == B :
                        BBMresponce_file_id="BQADBQADAwAD6vssEFrsEt3Hhpi4Ag" #毛線聖誕老人織愛心 嗶鼠版
                    else:
                        BBMresponce_file_id="BQADBQADBgAD6vssENUtjTtERQ4mAg" #毛線聖誕老人織愛心 測試版

                print (BBMresponse_str[0])
                
                print ("rd:"+str(rd))
                


#指令區

                
#版本宣告 version
            #command 已針對group訊息 刪除字首的斜線了

            # if command[:6] == '/story' or (chat_type=="group" and  command[:5] == 'story'):
            #     n=random.randint(1,len(lrsy))
            #     BBMresponse_str[0]= str( u"讓嗶鼠我來講笑話給"+ salutation +"舔舔： \n" + str(lrsy[n]) + "\n\n(" + str(n) + "/" + str(len(lrsy)) + ")" )
            if command[:6] == '/start' or (chat_type=="group" and  command[:5] == 'start'):
                BBMresponse_str[0]= str( u"嗨！"+ salutation +"！我是嗶嗶鼠機器人"+ version+"版！智能大概是嗶嗶鼠的二十π分之一。")
            elif command[:8] == '/bbmouse' or (chat_type=="group" and command[:7] == 'bbmouse'):
                n=random.randint(1,len(bbmousescripts))
                BBMresponse_str[0]= str( str(bbmousescripts[n]) + "\n\n(" + str(n) + "/" + str(len(bbmousescripts)) + ")" )
            elif command[:5] == '/time' or (chat_type=="group" and  command[:4] == 'time'):
                BBMresponse_str[0]= str( str(datetime.datetime.now(tz)))
            elif command[:10] == '/marrydays' or(chat_type=="group" and  command[:9] == 'marrydays'):
                BBMresponse_str[0]= str( u"報告"+ salutation +"：你已經結婚" + str((datetime.datetime.now() -datetime.datetime(2013,7,21)).days) + u"天囉！")

                
            elif ( command[0:7] == '/google' or  (chat_type=="group" and command[0:6] == 'google')):
                BBMresponse_str[0]= str( u"好的"+ salutation +"，讓我來為你Google:"+"\n https://www.google.com.tw/search?q=" + command[8:])
            elif("智能升級" in command or "智能進化" in command  or "什麼智能" in command   or "學會了什麼" in command or "有升級嗎" in command or "新功能" in command):
                BBMresponse_str[0]= str( "智慧毛說過：「智能沒有奇蹟，只有累積。」\n智能升級是一個漫長的路程，而且你永遠不知道就在"+ salutation +"一回頭間，小孩又學會了什麼奇怪的東西。")
            elif("在哪" in command or "在什麼地方" in command):
                totalelementlist=["嗶","鼠","請問","你","知道","知不","嗎","在哪裡","在哪","在什麼地方","?","？",",","，"]
                for i in range(len(totalelementlist)):
                    try:
                        command=command.replace(totalelementlist[i],"")
                        
                        #print ("item:" + item+" 取代標的:")+totalelementlist[i]
                    except:
                        pass
                # try:
                #     command=command.replace("嗶","")
                # except:
                # try:
                #     command=command.replace("鼠","")
                # except:
                # try:
                #     command=command.replace("在哪裡","")
                # except:
                #     pass
                # try:
                #     command=command.replace("在哪","")
                # except:
                #     pass
                # try:
                #     command=command.replace("在什麼地方","")
                # except:
                #     pass

                # try:
                #     command=command.replace("？","")
                # except:
                #     pass

                # try:
                #     command=command.replace("?","")
                # except:
                #     pass
                BBMresponse_str[0]="我查了一下，應該是在這裡吧："
            
                url="https://maps.googleapis.com//maps/api/place/textsearch/json?query="+urllib.quote(str(command))+"&key=AIzaSyB2OR9CaYyS8rObfyGKUB4cBul0meWu3k8&language=zh-TW"
                # print(urllib.quote(str(command)))
                response = urllib.urlopen(url)
                data = json.loads(response.read())
                print (data)
                #BBMresponse_str[1]="https://www.google.com.tw/maps/place/"+data['results'][0]['name'].replace(" ","+")
                if data['results']:
                    detailurl="https://maps.googleapis.com/maps/api/place/details/json?placeid={placeid}&key=AIzaSyB2OR9CaYyS8rObfyGKUB4cBul0meWu3k8&language=zh-TW".format(placeid=data['results'][0]['place_id'])
                    detailresponse=urllib.urlopen(detailurl)
                    detaildata=json.loads(detailresponse.read())
                    BBMresponse_str[1]=detaildata['result']['url']
                    print (type(data['results']))
                    print (data['results'])
                    BBMresponse_str[2]=(data['results'][0]['formatted_address'])
                else:
                    BBMresponse_str[0]="這是什麼東西？我在地圖上查不到耶QQ"
             
#猜拳
            elif '猜拳' in command :
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text="剪刀", callback_data='scissors')],
                   [InlineKeyboardButton(text="石頭", callback_data='rock')],
                   [InlineKeyboardButton(text="布", callback_data='paper')],
               ])
                #BBMresponse_str[0]= str( ""+ salutation +"我們來猜拳吧！", reply_markup=keyboard)
                bot.sendMessage(chat_id, salutation +"我們來猜拳吧！", reply_markup=keyboard)


            elif '碼表' in command or '倒數' in command or '碼錶' in command or '計時' in command:
                if "秒" in command:
                    try:
                        s=re.search("\d{1,3}",command[command.index("秒")-3:command.index("秒")]).group()
                    except:
                        s=0
                else:
                    s=0
                if "分" in command:
                    try:
                        m=re.search("\d{1,3}",command[command.index("分")-3:command.index("分")]).group()
                    except:
                        m=0
                else:
                    m=0

                totalsec=int(s)+60*int(m)       
                if totalsec>600:
                    BBMresponse_str[0]="這個倒數太久了啦！想累死我嗎！"
                else:   
                    bot.sendMessage(chat_id,"好的，倒數開始！誰也別想打斷我！\n最後10秒將會讀秒！")
                    for i in range(int(totalsec)):
                        #print("delete"+str((totalsec-i)%30))
                        if totalsec-i<=10:
                            bot.sendMessage(chat_id,totalsec-i)
                            print (totalsec-i)
                        elif (totalsec-i<=180)&((totalsec-i)%30==0 ):
                            bot.sendMessage(chat_id,"倒數"+str( totalsec-i )+"秒")
                            print("倒數"+str( totalsec-i )+"秒")
                        elif (totalsec-i<=600)&((totalsec-i)%60==0 ):
                            bot.sendMessage(chat_id,"倒數"+str( (totalsec-i)/60 )+"分鐘")
                            print("倒數"+str( (totalsec-i)/60 )+"分鐘")

                        else:
                            pass
                        sleep(1)
                    bot.sendMessage(chat_id,"嗶嗶嗶嗶嗶！時間到！")              




            elif '默哀' in command:
                if"十秒鐘" in command or "10秒鐘" in command:
                    bot.sendMessage(chat_id,"請"+salutation+"起立，我們一起默哀十秒鐘")
                    for i in range(10):
                        bot.sendMessage(chat_id,str(i+1)+"~")
                        sleep(1)
                    BBMresponse_str[0]="好的請坐\nSit down please."
                else:
                    bot.sendMessage(chat_id,salutation+"我只學過默哀十秒鐘哦～")

            elif iscallBBMouseonly(command)==True:
                BBMresponse_str[0]=salutation + "叫我嗎？ 我在這～(咚咚咚)"

            elif issetremind(command):

                GC=GoogleCalendar()
                eventlink=GC.createvent(salutation+"說：" + command,getTimeValue(command))
                BBMresponse_str[0]="好！我記在這裡了，到時候會發email提醒！也會用手機Google Calendar APP提醒！\n"+eventlink
            elif isWantRecentEventList(command):
                GC=GoogleCalendar()
                recenteventlist= GC.listrecentevent()
                BBMresponse_str[0]="未來的十項行程如下，仔細看，別漏掉囉！"
                for event in recenteventlist:
                    BBMresponse_str[1]=BBMresponse_str[1]+(event+"\n")
#MEMO
            elif isaskmemo(command):
                
                bot.sendMessage(chat_id,"且讓我掏出嗶鼠備忘小本子來抄錄～\n(嗶鼠在小本子上專心抄寫中)\n(稍等一下，先別吵嗶鼠)")
                command=command[command.find(" "):]
                commandlist=getcommandlistbyeachline(command)
                for i in range(len(commandlist)):
                    print ("commandlist[" + str(i) +"]   " + commandlist[i])
                Date=time.strftime("%Y-%m-%d", time.gmtime(time.time()+8*60*60)) #Today
                for i in range(len(commandlist)):
                    BBMouseMemo(chat_id,salutation,Date,commandlist[i])
                BBMresponse_str[0]="好了，我已經幫" + salutation + "記好了\n備忘錄可以看這裡： https://goo.gl/SJPds7 "
                
#記帳 accounting
            elif ifaskaccounting(command):


                #如果記帳的command有換行的話，每一行視作一筆單獨的記帳紀錄
                commandlist=getcommandlistbyeachline(command)
                # for i in range(len(commandlist)):
                #     print ("commandlist[" + str(i) +"]   " + commandlist[i])


                # if len(accrecord)<4 or len(accrecord)>5 or len(accDate)<>10: #如果格式不太合
                #     BBMresponse_str[0]=salutation+ " 你的記帳格式不對唷！" +accDateError+ " \n給你一個範例：「嗶鼠記帳 20161116 生日大餐 $999」\n記得空格要空對！" 
                #     print (accDateError)
                #     print (accDate)
                # else:
                if True:
                    #bot.sendMessage(chat_id,"等我一下，我來翻找一下我的記帳小本子")


                    # if "$" in accrecord[orderofAmount] or "元" in accrecord[orderofAmount]:
                    #     accAmount=accrecord[orderofAmount].replace("$","")
                    #     accAmount=accAmount.replace("元","")
                    # else:
                    #     accAmount=accrecord[orderofAmount]
                    totalrecord=""
                    bot.sendMessage(chat_id,"且讓我掏出記帳小本子來抄錄，等我記完再跟" + salutation+"說～\n(嗶鼠在小本子上專心抄寫中)\n(稍等一下，先別吵嗶鼠)")
                    for i in range(len(commandlist)):
                        #print ("print (commandlist[i])"+commandlist[i])
                        accAmount=AccountingSentenceAnalysis_get_amount(commandlist[i])
                        accItem=AccountingSentenceAnalysis_get_item(commandlist[i])
                        accDate=AccountingSentenceAnalysis_get_date(commandlist[i])
                        accSource=AccountingSentenceAnalysis_get_source(commandlist[i])
                        # if not(isinstance(accDate,int)):  #待測試確認
                        #     accDateError="日期格式記錯了"
                        # else:
                        #     accDateError=""

                        if("收入" in commandlist[i] or "撿到錢" in commandlist[i] or "兼差" in commandlist[i] or "家教" in commandlist[i] or "獎金" in commandlist[i] or "薪水" in commandlist[i] or "賺了" in commandlist[i]  or "收回" in commandlist[i]  or "回收" in commandlist[i]):
                            acctype="收入"
                        else:
                            acctype="支出"
                        BBMouseAccounting(chat_id,salutation,accDate,accItem,accSource,accAmount,acctype,command)
                        totalrecord=totalrecord+ "日期： " + str(accDate)+ "   項目： "+str(accItem)+ "\n"+accSource+" "+acctype+"NT" +accAmount +"\n"
                    BBMresponse_str[0]="好了，我已經幫" + salutation + "記好了：\n"+totalrecord+"\n記帳紀錄可以看這裡： https://goo.gl/OI2LXx "
            elif isaskToDoList(command):
                updateToDoList(command,chat_id)
            elif isaskShoppingList(command):
                updateShoppingList(command,chat_id)
#深度問題
            # elif("無聊" in command or "有趣的" in command  or "你會思考" in command   or "智能測試" in command or "智能問答" in command):
            #     n=random.randint(1,len(dq))
            #     BBMresponse_str[0]= str( str(dq[n]) + "\n\n(" + str(n) + "/" + str(len(dq)) + ")" )


#嗶鼠報時
            elif(command =="早" or "早安" in command or "早 " in command  or "早!" in command   or "早！" in command or "午安" in command or "晚安" in command  or "下午好" in command  or "晚上好" in command or "嗶報時" in command or "嗶鼠報時" in command):
                BBMresponse_str[0]= str( "(低頭看錶) 噢 現在是" + str(datetime.datetime.now(tz).hour) + "點" + str(datetime.datetime.now(tz).minute) + "分")
                if datetime.datetime.now(tz).hour <2:
                    BBMresponse_str[1]= str("這個"+ salutation +"，怎麼還不睡覺！這樣要怎麼教小孩呢！")
                elif datetime.datetime.now(tz).hour <6:
                    BBMresponse_str[1]= str(""+ salutation +"這麼早叫我有事嗎？現在才幾點～我還在發育中，是很需要充足睡眠的！")
                elif datetime.datetime.now(tz).hour <11:
                    BBMresponse_str[1]= str(""+ salutation +"早安～"+ salutation +"早安～"+ salutation +"早安！"+ salutation +"要記得吃早餐～\n嗯……其實好像也不一定要吃早餐了\n https://www.thenewslens.com/article/62625 ")
                elif datetime.datetime.now(tz).hour <13:
                    BBMresponse_str[1]= str(""+ salutation +"午安～午餐要多吃一點！不然會變瘦哦！小心被逐出矮胖國！")
                elif datetime.datetime.now(tz).hour <15:
                    BBMresponse_str[1]= str("這個時間最適合苟咻苟咻了～")
                elif datetime.datetime.now(tz).hour <16:
                    BBMresponse_str[1]= str("找浣熊朋友來家裡玩好了！～")
                
                elif datetime.datetime.now(tz).hour <17:
                    if datetime.datetime.today().weekday() <=4:
                        BBMresponse_str[1]= str("嗯 差不多可以收拾收拾準備下班了～")
                    else:
                        BBMresponse_str[1]= str("好想出去跑跑跳跳哦！也好想吃下午茶哦！")
                elif datetime.datetime.now(tz).hour <19:
                    BBMresponse_str[1]= str("晚餐吃什麼好呢～")
                elif datetime.datetime.now(tz).hour <22:
                    BBMresponse_str[1]= str("這個時間要打電動還是做功課好呢？")
                elif datetime.datetime.now(tz).hour <=24:
                    BBMresponse_str[1]= str("該刷牙睡覺囉"+ salutation +"～")
                else:
                    BBMresponse_str[1]= str("這是什麼時間！？")
            elif( "再見" in command):
                BBMresponse_str[0]= str(""+ salutation +"再見" )
            elif( "你好" in command):
                BBMresponse_str[0]= str(""+ salutation +"你好" )

#情感偵測 #反身動詞
#e.g.「我愛嗶嗶鼠」
            elif( len(command)<=12 and "我" in command[0:1] and BBself(command)>0 ):

                  BBMresponse_str[0]= str("嗶鼠也" + command[1:command.find("嗶")] + ""+ salutation +"")

                    
#動詞替代
            # elif ( len(command)>=4 and len(command)<=10 and (command[0:3]=="嗶鼠我")):
            #       BBMresponse_str[0]= str("哦 "+ salutation +"你" + command[3:] + ' 哇災哇災')

            #決定改到API.AI來處理 20170214
            # elif(isflatter(command) != True and isquestion(command)==False and len(command)>=4 and len(command)<10 and ( BBself(command[0:3])>0)):
                  
            #       #BBMresponse_str[0]= str("嗶鼠想跟"+ salutation +"一起" + command[BBself(command[0:2]):])  #這句太不適用了
            #       BBMresponse_str[0]= str("好啊～" + command[BBself(command[0:3]):])


                  
            elif(iscurse(command) and not("阿胖" in command or "小胖" in command)):
                if("嗶" in command):
                    if ("嗶嗶" in command):
                        if ("嗶嗶鼠" in command):
                            BBMresponse_str[0]= str( "哼 " + command.replace("嗶嗶鼠",""+ salutation +""   ))
                        else:    
                            BBMresponse_str[0]= str( "哼 " + command.replace("嗶嗶",""+ salutation +""   ))
                    elif ("嗶鼠" in command):
                        if ("嗶嗶鼠" in command):
                            BBMresponse_str[0]= str( "哼 " + command.replace("嗶嗶鼠",""+ salutation +""   ))
                        else:    
                            BBMresponse_str[0]= str( "哼 " + command.replace("嗶鼠",""+ salutation +""   ))
                    else:
                        BBMresponse_str[0]= str( "哼 " + command.replace("嗶",""+ salutation +""   ))
                else:
                    BBMresponse_str[0]= str( u"哇姆災哦～")




            elif(command == "小酥熊" or command == "酥熊" or "胖胖熊" in command or "我是小" in command or "瓜熊" in command) :#and (chat_id=288200245) :
                if datetime.datetime.now(tz)==2016:
                    BBMresponse_str[0]= str( u""+ salutation +"你是小酥熊！\n\n但是不要被小酥熊的「小」字給騙了！～")
                elif datetime.datetime.now(tz).year==2017:
                    BBMresponse_str[0]= str( u""+ salutation +"你是小瓜熊！\n\n但是不要被小瓜熊的「小」字給騙了！～")
                else:
                    pass
            


            elif( "爸爸去哪了" in command or "爸爸都不回來" in command or "好想念爸爸" in command or "爸爸在哪裡" in command or "我愛爸爸" in command):
                BBMresponse_str[0]= str( u"爸爸就快回來了！再等等～")
            elif( "媽媽去哪了" in command or "媽媽都不回來" in command or "好想念媽媽" in command or "媽媽在哪裡" in command or "我愛媽媽" in command):
                BBMresponse_str[0]= str( u"嗶鼠也好想念媽媽哦……")

            elif( "你幾歲" in command or  "嗶鼠幾歲" in command or "你多大了" in command):
                BBMresponse_str[0]= str( u"嗯……這是個好問題！我存在這個世界上應該十多年了，可是爸爸如果是五歲的話，那我應該是三歲之類的吧。")
            elif ( len(command)>=4 and (command[0:3]=="嗶鼠你" or command[0:3]=="嗶鼠是" )):
                if(isquestion(command)):
                    BBMresponse_str[0]= str( u"哇姆災哦～～")
                else:
                    BBMresponse_str[0]= str("咦 真的嗎！？" + command.replace("嗶鼠你","我").replace("嗶鼠是","我是") + '？')
            #移到API.AI處理 20170215
            # elif(isflatter(command)==True and BBself>0):
            #     BBMresponse_str[0]= str( "(抓頭)這樣稱讚我，我會不好意思啦～")
                


#特例
            elif( "今天放假" in command or  "不用上班" in command or "放假" in command):
                BBMresponse_str[0]= str( u"咦！真的嗎？哇姆災耶～")
#認識
            elif("認識" in command and isquestion(command)==True):
                if( "阿胖" in command or "小胖" in command):
                    BBMresponse_str[0]= str( "哦！我知道啊！是媽媽的好友姜子晴是吧？")
                    BBMresponse_str[1]= str( ""+ salutation +"已經活了"  + str((datetime.datetime.now() - datetime.datetime(1987,11,16)).days) + "天了\n而阿胖比你還多活一天呢！\n算得這麼精確，我可真是智能嗶鼠啊！")
                elif( ("喜波" in command or "波波" in command )):
                    BBMresponse_str[0]= str( "哦！是媽媽的好友江喜波是吧？\n波波嘛！河馬界有誰不認識波波的！")
                elif(  "阿仙" in command or "語萱" in command):
                    BBMresponse_str[0]= str( "……是媽媽熱衷於布偶兒子的好友是吧？\n作為媽媽的兒子，我不予置評。")
                elif(  "外婆" in command or "婆婆" in command):
                    BBMresponse_str[0]= str( "哦哦  我最喜歡外婆了～")
                elif(  "陸仁" in command or "阿姨" in command):
                    BBMresponse_str[0]= str( "我跟喜歡外婆一樣喜歡阿姨～")
                elif(  "爸爸" in command or "阿羊" in command):
                    BBMresponse_str[0]= str( salutation + "你在問什麼蠢問題！你當我是隻呆嗶嗎！")
                elif(  "媽媽" in command or "我" in command):
                    BBMresponse_str[0]= str( salutation + "你在問什麼蠢問題！你當我是隻呆嗶嗎！")
                elif(  "爺爺" in command or "奶奶" in command  or "姑姑" in command):
                    BBMresponse_str[0]= str( "我小時候有看過～不過很久沒見了！")                                        
                elif(  "跳跳" in command or "小老虎" in command):
                    BBMresponse_str[0]= str( "好想念跳跳哦！不知道他的智能有沒有長進一點了")
                elif(  "吐動" in command or "國王" in command):
                    BBMresponse_str[0]= str( "你說的是我們矮胖國的國王嗎！ 是不是到了該續聘的時間啦？")    
                elif(  "小背包" in command or "小揹包" in command):
                    BBMresponse_str[0]= str( "好想念小背包哦！")    



                else:
                    BBMresponse_str[0]= str( "還不太認識耶，他是誰啊？")

            # elif("下班囉" in command):
            #      BBMresponse_str[0]="衝衝衝～"
            elif( "謝謝" in command):      
                BBMresponse_str[0]= str( u"小意思～"+ salutation +"不用客氣！")
            elif( u"這個嗶鼠" in command):
                BBMresponse_str[0]= str( u"這個"+ salutation +"這個"+ salutation +"！")
            elif(isquestion(command)):
                BBMresponse_str[0]= str( u"哇姆災哦～")
            
#ECHO
            # elif( len(command)<3 ):
            #     BBMresponse_str[0]= str( command)


                
            else:
                #呼叫外部機器人 api.ai
                print("===else===")
                print(command)
                BBMresponse_str[0]= str(CallAPIAI(command)).replace("[salutation]",salutation).replace("\\n","\n")
                # BBMresponse_str[1]= CallAPIAI(command)
                # print (type(CallAPIAI(command)))
                # print (CallAPIAI(command))
                # print()
                # print(BBMresponse_str[0])
                # print(BBMresponse_str[1])

    

        if ("我愛嗶" in command or "我喜歡嗶" in command):
            print (B)
            print (T)
            if mode == B :
                BBMresponce_file_id="BQADBQADAwAD6vssEFrsEt3Hhpi4Ag" #毛線聖誕老人織愛心 嗶鼠版
            else:
                BBMresponce_file_id="BQADBQADBgAD6vssENUtjTtERQ4mAg" #毛線聖誕老人織愛心 測試版


    # if isaskaccounting==True:
    #     print ("msg['text']"+msg['text'])
    #     msg['text']=msg['text'].replace(msg['text'],"記帳"+msg['text'])
    #     # print ("msg['text']"+msg['text'])
    #     # print ("msg in csv")
    #     # print (msg['text'].replace(msg['text'],"記帳"+msg['text']))






    msglist=[]
    count2=0
    
    f = open('msghistory.csv', 'rb')
    for row in csv.reader(f):
        msglist.append(row)
        #print ("row:"+str(row))
        count2=count2+1
    f.close()

    #with open("msghistory.csv", "ab+") as csvfile:
    csvfile=open("msghistory.csv", "wb+")
    print("writing history in msghistory.csv")
    print (msg)
    writer = csv.writer(csvfile)
    #writer.writeheader()    
    #print(msglist)
    #print("pre count:"+str(count))
    
    for row in msglist:        
        #print(row)
        writer.writerow([row[0],"END"])    
    writer.writerow([msg,"END"])
    csvfile.close()

    for i in range(len(BBMresponse_str)):


        # fieldnames = ["timestamp","chat_id","Command from user", "BBMresponse","msg"]
        # with open("conversationhistory.csv", "a+") as csvfile:

        #     writer = csv.DictWriter(csvfile,fieldnames)
        #     #writer.writeheader()
        #     writer.writerow({
        #             "timestamp": datetime.datetime.now(),
        #             "chat_id": chat_id,
        #             "Command from user": command,
        #             "BBMresponse": BBMresponse_str[i].replace("\n",""),
        #             "msg":msg,  
        #         })
        if BBMresponse_str[i]<>"":
            # print(BBMresponse_str[i])
            bot.sendMessage(chat_id,BBMresponse_str[i])
            if (chat_id == 288200245):
                bot.sendMessage(271383530, u"嗶鼠機器人向酥熊回答了: \n" + BBMresponse_str[i])
            


    # if BBMresponse_str[0]<>"":
    #     bot.sendMessage(chat_id,BBMresponse_str[0])
        
    #     if (chat_id == 288200245):
    #         bot.sendMessage(271383530, u"嗶鼠機器人向酥熊回答了: \n" + BBMresponse_str[0])
    # if BBMresponse_str[1]<>"":
    #     bot.sendMessage(chat_id,BBMresponse_str[1])
    #     if (chat_id == 288200245):
    #         bot.sendMessage(271383530, u"嗶鼠機器人向酥熊回答了: \n" + BBMresponse_str[1])

    if (BBMresponce_file_id <> ""):
        bot.sendMessage(271383530, u"(嗶鼠機器人試圖傳送貼圖): \n")
        bot.sendDocument(chat_id,BBMresponce_file_id)
        if (chat_id == 288200245):
            bot.sendMessage(271383530, u"嗶鼠機器人向酥熊回傳了這個圖:" )
            bot.sendDocument(271383530,BBMresponce_file_id)





def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    result=""
    if query_data=='yes': #if user say yes for accounting
        #getintent
        print("query_data==yes")

        msglist=[]
        count2=0
        
        f = open('msghistory.csv', 'rb')
        for row in csv.reader(f):
            msglist.append(row)
            #print ("row:"+str(row))
            count2=count2+1
        f.close()
        # print("msglist[-1]")
        # print(msglist[-1])
        # msglist[-1][0]=msglist[-1][0].replace("'text': ","'isaccount': 'True','text': ")
        # print("msglist[-1][0]")
        # print(msglist[-1][0])
        # print(type(msglist[-1][0]))
        # msginjson = json.loads(msglist[-1][0])
        # msginjson["text"]="記帳"+msginjson["text"]
        # msglist[-1][0]=str(msginjson)
        # # msglist[-1][0]["text"]="記帳"+msglist[-1][0]["text"]
        # print(msglist[-1])
        msglist[-1][0]=msglist[-1][0].replace("'text': ","'isaccount': 'True','text': ")
        positionoftext=msglist[-1][0].index('text')
        print("=B==msglist[-1][0]===")
        print(msglist[-1][0])
        msglist[-1][0]=msglist[-1][0][:positionoftext+9] +u"記帳 " + msglist[-1][0][positionoftext+9:]
        print("=A==msglist[-1][0]===")
        print(msglist[-1][0]) 
        # print(msglist)
        fromquerymsg=msglist[-1]


        #fromquerymsg={linecache.getline("msghistory.csv",count-1)}
        bot.answerCallbackQuery(query_id, text="好的！")

        print("fromquerymsg[0]")
        print(fromquerymsg[0])
        handle(fromquerymsg[0])


    elif query_data=='no':
        result="原來不是啊，誤會誤會～"
        msglist=[]
        count2=0
        f = open('msghistory.csv', 'rb')
        for row in csv.reader(f):
            msglist.append(row)
            count2=count2+1
        f.close()
        print("msglist[-1]")
        print(msglist[-1])
        # msginjson = json.loads(msglist[-1][0])
        msglist[-1][0]=msglist[-1][0].replace("'text': ","'isaccount': 'False','text': ")
        print("msglist[-1] after")
        print(msglist[-1])
        # msginjson['text']="NotForAccounting"+msginjson['text']
        # ["text"]="NotForAccounting"+msglist[-1][0]["text"]
        fromquerymsg=msglist[-1]

        #fromquerymsg={linecache.getline("msghistory.csv",count-1)}
        bot.answerCallbackQuery(query_id, text=result)
        print("start handel after NO")
        print(fromquerymsg[0])
        handle(fromquerymsg[0])
 


    elif query_data=='scissors':
        result="(嗶鼠出了石頭！)  我贏了！"
    elif query_data=='rock':
        result="(嗶鼠出了石頭！)  嘿～不分勝敗"
    elif query_data=='paper':
        result="(嗶鼠出了石頭！)  唔，我輸了。再來一把！"
    if result<>"":
        bot.answerCallbackQuery(query_id, text=result)
    
def isquestion(command):
    if "?" in command or "嗎" in command or "呢" in command or "？" in command or "有沒有" in command or "是不是" in command or "好不好" in command or "為什麼" in command or "為何" in command or "怎麼" in command:
        return True
    else:
        return False

def BBself(sentence): #判斷嗶鼠是否被提及，在第幾個字？
    if "嗶嗶鼠" in sentence or "BB鼠" in sentence:
        return 3
    elif "嗶鼠" in sentence or "嗶嗶" in sentence or "B鼠" in sentence or "b鼠" in sentence:
        return 2
    else:
        return 0
def iscurse(command):
    if "臭" in command or "笨" in command or "傻" in command or "壞" in command or "呆" in command or "胖" in command:
        return True
    else:
        return False

def iscallBBMouseonly(command): #判斷是否在呼叫嗶鼠
    if command=="嗶" or command=="嗶嗶" or command=="嗶嗶鼠" or command=="嗶鼠" or command=="嗶仔" or command=="嗶嗶鼠仔" or command=="阿嗶" or command=="bb鼠" or command=="b鼠":
        return True

# def isflatter(command):
#     if "可愛" in command or "太強" in command or  "厲害" in command or "好棒" in command or "有大棒棒" in command or "聰明" in command or "智能好" in command or "乖" in command:
#         return True

#def group(msg):
    

print ("bot setting")


bot = telepot.Bot(mode)
#bot.message_loop(handle)
bot.message_loop({'chat': handle,
                  'callback_query': on_callback_query})

print ('I am listening ...')



while 1:
    time.sleep(10)

    # if datetime.datetime.now(tz).minute %2 ==0:
    #     print ("xxxxx")
    #     bot.sendMessage(271383530, u"(嗶鼠機器人)")




