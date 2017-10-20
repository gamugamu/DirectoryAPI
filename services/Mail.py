
import smtplib
from threading import Thread


def sendmail(mail, title, body):
    t = Thread(target=sendmail_bkg, args=(mail, title, body))
    t.start()

def sendmail_bkg(mail, title, body):
    print "sendmail"
    server = smtplib.SMTP('smtp.gmail.com', 25)
    server.starttls()
    server.login("cryptodraco@gmail.com", "superpassE0")
    print "****sendded"
    msg = "YOUR MESSAGE!"
    server.sendmail("YOUR EMAIL ADDRESS", "THE EMAIL ADDRESS TO SEND TO", msg)
    server.quit()
    print "DONE"
