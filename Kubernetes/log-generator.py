import random as rd
import string
from datetime import datetime
import time # Added back import time

def generate_and_print_string():
    timestamp_str = "2020-03-30T12:15:17.705Z"
    dt = datetime.fromisoformat(timestamp_str)

    str1='abcdefghijklmnopqrstwxyzABCDEFGHIJKLMNOPQRSTWXYZ123456789'
    lst1=list(str1)
    # print(lst1) # Removed this print to avoid cluttering output every 5 seconds
    n=5

    result = ''

    for i in range(1,n+1):
      if i==1:
        result +=''.join(rd.choices(lst1,k=8))
        result +='-'
      elif i==2:
        res=''.join(rd.choices(lst1,k=4))
        result +=res + '-'
      elif i==3:
        res=''.join(rd.choices(lst1,k=4))
        result +=res + '-'
      elif i==4:
        res=''.join(rd.choices(lst1,k=4))
        result +=res + '-'
      elif i==5:
        res=''.join(rd.choices(lst1,k=12))
        result +=res

    # Recalculate current datetime for actual output
    current_dt = datetime.now()
    current_dt_z_string = current_dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    print(f"{current_dt_z_string}  {result}")

# Loop to call the function every 5 seconds
while True:
    generate_and_print_string()
    time.sleep(5)
