import random
import math
def Otp_send():
    data = "0123456789"
    length=len(data)
    otp = ""
    for i in range(6):
	    otp += data[math.floor(random.random()*length)]
    return otp

Otp_send()