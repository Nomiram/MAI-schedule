'''
fork https://gitlab.mai.ru/FMRodin/mai-schedule-ical/-/tree/master
Расписание с сайта МАИ в различных форматах
Исправлено в соответствии с изменениями в выдаче json на сайте public.mai.ru
Добавлен экспорт в TXT (CSV)
'''
import urllib.request
import json
import hashlib
import icalendar
from datetime import datetime
from dateutil import parser
DELIM = "; "
def getscedule(group_list, console = True, ics = False, txt = False):
    '''
    Функция выводит расписание с сайта МАИ в различных форматах:
    TXT, ICS для добавления в календарь
    '''
    for group_list_el in group_list:
        group_name = group_list_el
        if txt:
            f = open(group_name + ".txt", "wt")
        group_hash = hashlib.md5(group_name.encode('utf-8')).hexdigest()
    
        link = "https://public.mai.ru/schedule/data/" + group_hash + ".json"
        print(link)
        rasp = urllib.request.urlopen(link).read()
        rasp = json.loads(rasp)
        cal = icalendar.Calendar()
        cal.add('prodid', '-//My calendar product//mxm.dk//')
        cal.add('version', '2.0')
    
        rasp.pop("group")
        # print(rasp)
    
        for day in rasp.items():
            date = datetime.fromisoformat(str(parser.parse(day[0], dayfirst=True)))
            if console:
                print("Дата:", date.date())
            if txt:
                f.write("Дата: "+str(date.date())+"\n")
            pary = day[1]["pairs"]
            # print("PARY::", pary)
            for _para in pary.items():
                paraoff = _para[1]
                para = paraoff[list(paraoff)[0]]
                # print("para:", para )
                time_start = datetime.fromisoformat(str(parser.parse(para["time_start"])))
                time_start = datetime.combine(date.date(), time_start.time())
                time_end = datetime.fromisoformat(str(parser.parse(para["time_end"])))
                time_end = datetime.combine(date.date(), time_end.time())
    
                name = []
                for _name in paraoff.items():
                    name.append(_name[0])
                name = ' / '.join(name)
    
                lector = []
                for _lector in para["lector"].items():
                    lector.append(_lector[1])
                lector = ', '.join(lector)
    
                type_ = []
                for _type in para["type"].items():
                    type_ = _type[0]
    
                room = []
                for _room in para["room"].items():
                    room.append(_room[1])
                room = ', '.join(room)
                
                event = icalendar.Event()
                event.add('summary', str(type_ + " " + name))
                event.add('dtstart', time_start)
                event.add('dtend', time_end)
                event.add('dtstamp', time_start)
                event.add('location', room)
                event.add('description', lector)
                cal.add_component(event)
                if console:
                    print(time_start, time_end, name, type_, lector, room)
                if txt:
                
                    f.write(str(time_start)+DELIM+str(time_end)+DELIM\
                    +name+DELIM+type_+DELIM+lector+DELIM+room+"\n")
    if txt:
        f.close()
    if ics:
        f = open(group_name + ".ics", "wb")
        f.write(cal.to_ical())
        f.close()
    
    print("done with", group_name)

def main():
    '''
    main function
    '''
    group_list = [
        'М3О-117М-22',
    ]
    getscedule(group_list, ics = True, txt = True)
    # getscedule(group_list)
    # help(getscedule)

if __name__ == "__main__":
    main()
