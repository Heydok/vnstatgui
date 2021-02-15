import json
from subprocess import Popen, PIPE
from datetime import datetime

vnstat = Popen(["vnstat", "--json"], stdout=PIPE)
data = json.loads(vnstat.stdout.read())
vnstat.wait()

def getoutput(params, iface='wlan0'):
    li = []
    downtxt = uptxt = totaltxt = 'MB'
    currentdate = datetime.now()
    ifacename = iface

    if params == 'h':
        for interface in data['interfaces']:
            hour = interface['traffic']['hour']
            if interface['name'] == ifacename:
                for traffic in hour:
                    jdate = datetime(
                        traffic['date']['year'],
                        traffic['date']['month'],
                        traffic['date']['day'],
                        traffic['time']['hour'],
                        traffic['time']['minute']
                    )
                    down = traffic['rx']/1024/1024
                    up = traffic['tx']/1024/1024
                    total = down + up
                    li.append([jdate, down, downtxt, up, uptxt, total, totaltxt])

    elif params == 'd':
        for interface in data['interfaces']:
            day = interface['traffic']['day']
            if interface['name'] == ifacename:
                for traffic in day:
                    jdate = datetime(
                        traffic['date']['year'],
                        traffic['date']['month'],
                        traffic['date']['day']
                    )
                    down = traffic['rx']/1024/1024
                    up = traffic['tx']/1024/1024
                    total = down + up
                    li.append([jdate.date(), down, downtxt, up, uptxt, total, totaltxt])

    elif params == 'm':
        for interface in data['interfaces']:
            month = interface['traffic']['month']
            if interface['name'] == ifacename:
                for traffic in month:
                    jdate = datetime(
                        traffic['date']['year'],
                        traffic['date']['month'],
                        1
                    )
                    down = traffic['rx']/1024/1024
                    up = traffic['tx']/1024/1024
                    total = down + up
                    li.append([jdate.date(), down, downtxt, up, uptxt, total, totaltxt])

    elif params == 't':
        for interface in data['interfaces']:
            top = interface['traffic']['day']
            if interface['name'] == ifacename:
                for traffic in top:
                    jdate = datetime(
                        traffic['date']['year'],
                        traffic['date']['month'],
                        traffic['date']['day']
                    )
                    down = traffic['rx']/1024/1024
                    up = traffic['tx']/1024/1024
                    total = down + up
                    li.append([jdate.date(), down, downtxt, up, uptxt, total, totaltxt])

    elif params == 'f':
        for interface in data['interfaces']:
            fiveminute = interface['traffic']['fiveminute']
            if interface['name'] == ifacename:
                for traffic in fiveminute:
                    jdate = datetime(
                        traffic['date']['year'],
                        traffic['date']['month'],
                        traffic['date']['day'],
                        traffic['time']['hour'],
                        traffic['time']['minute']
                    )
                    down = traffic['rx']/1024/1024
                    up = traffic['tx']/1024/1024
                    total = down + up
                    li.append([jdate, down, downtxt, up, uptxt, total, totaltxt])

    return li


def getinterfaces():
    interface_list = []
    for interface in data['interfaces']:
            iface = interface['name']                
            interface_list.append(iface)
    
    return interface_list
