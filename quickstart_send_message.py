# Ist gekoppelt mit Instapy/1_Like_not_business_follow_private
# Jeden Tag um 18 Uhr, 5min vorher follower save mylebenslauf.online

from instadm_v3_nur_message import InstaDM
#from instadm_v4_zuerst_Share_dann_message import InstaDM
from time import time as time0
from random import randint
from plyer import notification

#messageList1 = open('./SENDINGLIST/my_0.json',)
username1 = '#USERNAME'
password1= '#PASSWORD'
message1 = '#MESSAGE'
excludeUsers = ['lebenslauf.de', 'lebenslaufvorlage','meinlebenslauf','dein_lebenslauf_ch','360gradbewerbung','thisiscookiemonster4lif']
db_workspace= '#PATH_TO_SQLITE_DB'
file = "#FILE_WITH_INSTA_USERNAMES"

#Random number to sent messages for this session
randN = randint(14,18)

#VORSICHT; DASS SICH LISTEN NICHT ÜBERSCHREIBEN WENN GLEICHZEITIG SKRIPTE LAUFEN!!

with open(f'./FOLLOWLIST/{file}_interacted.txt','r') as g:
    messageList = []
    listNeu = []
    for i in g:
        if len(messageList) <= randN:
            i= i.replace('\n', '')
            messageList.append(i)
        else:
            listNeu.append(i)
        
    print(messageList)
    print("Werde nun dieser Liste DMs schicken...")

sleep= randint(0, 120)
print(f'Sleep {sleep} s before executing script...')
#random delay nach start des scripts aus Task Scheduler
#time.sleep(sleep)

if __name__ == '__main__':
    
    insta = InstaDM(username= username1, password=password1, headless=False,db_workspace=db_workspace)
    #start script
    startTime = time0()
    #print(f"Starttime: {startTime}")

    
    if len(messageList):
        insta.getPostAndSend(users=messageList, message= message1, excludeList=excludeUsers)
        print("DMs geschickt, jetzt Listen erneuern...")

        with open(f'./FOLLOWLIST/{file}_interacted.txt','r+') as f:
            #data = json.load(f)
            print(listNeu)
            f.seek(0)
            # g.write(f"{i}\n")
            # json.dump(listNeu, f)
            # f.truncate()
            for i in listNeu:
                #\n hier rausgenommen, weil \n noch von vorheriger Liste übernommen, ansonsten wären es zwei line breaks
                f.write(i)
            f.truncate()
        with open(f'./FOLLOWLIST/{file}_interacted_messagesent.txt','a') as g:
            for i in messageList:

                g.write(f"{i}\n")

                # g.replace(']', ',')
                # newjson = json.dump(listArr)
                # newjson.replace('[', '')
                # print(newjson)
                # json.dump(newjson, g)
            
    else:
        notification.notify(
            title="Insta MESSENGER BOT",
            message="DM-LISTE ist am Ende angelangt. Bitte neue Liste nehmen",
            app_name="InstaPy",
            timeout=30,
            ticker="To switch supervising methods, please review "
            "quickstart script",
        )
    
    insta.teardown()

    #end script
    endTime = time0()
    #print(f"Endtime: {endTime}")
    dauer = round(endTime-startTime)
    dauerMin = round(dauer/60)
    print(f"Benötigte Zeit: {dauer} Sekunden")
    print(f"Benötigte Zeit: {dauerMin} Minuten")
