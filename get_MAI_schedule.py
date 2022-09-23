'''
fork https://gitlab.mai.ru/FMRodin/mai-schedule-ical/-/tree/master
Расписание с сайта МАИ в различных форматах
Исправлено в соответствии с изменениями в выдаче json на сайте public.mai.ru
Добавлен экспорт в CSV
'''
import hashlib
import json
import urllib.request
from datetime import datetime

import icalendar
from dateutil import parser
# pylint: disable=W0105
'''
Формат json public.mai.ru:
'<dd.mm.yyyy>':{
    'day': '<day of the week>',
        'pairs':{
            '<hh:mm:ss>':{
            '<name of pair>':{
                'time_start': '<hh:mm:ss>',
                'time_end'  : '<hh:mm:ss>',
                'lector': {'<id>': '<name>'},
                'type': {'<type>': 1},
                'room': {'<id>': '<room name>'},
                'lms': '<url?>',
                'teams': '<url?>',
                'other': '<url?>'
            }
            }
        },
        {...}
}
'''


DELIM = "; "


def getscedule(group_list):
    '''
    Получение расписания по группам с сайта public.mai.ru
    '''
    scedule_list = {}
    #[{'group_name': [dict, dict,...]},...]
    # dict
    for group_list_el in group_list:
        group_name = group_list_el
        group_hash = hashlib.md5(group_name.encode('utf-8')).hexdigest()

        scedule_list[group_name] = []

        link = "https://public.mai.ru/schedule/data/" + group_hash + ".json"
        # print(link)
        rasp = urllib.request.urlopen(link).read()
        rasp = json.loads(rasp)
        # print(rasp)
        cal = icalendar.Calendar()
        cal.add('prodid', '-//My calendar product//mxm.dk//')
        cal.add('version', '2.0')

        rasp.pop("group")
        for day in rasp.items():
            date = datetime.fromisoformat(
                str(parser.parse(day[0], dayfirst=True)))

            pary = day[1]["pairs"]
            for _para in pary.items():
                paraoff = _para[1]
                para = paraoff[list(paraoff)[0]]
                time_start = datetime.fromisoformat(
                    str(parser.parse(para["time_start"])))
                time_start = datetime.combine(date.date(), time_start.time())
                time_end = datetime.fromisoformat(
                    str(parser.parse(para["time_end"])))
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

                scedule_list[group_name].append({'date': date.strftime('%Y-%m-%d'), 'time_start': para["time_start"],
                                                 'time_end': para["time_end"], 'name': name, 'type': type_,
                                                 'lector': lector, 'room': room})

    return scedule_list
    # print(scedule_list)
    # print("done with", group_name)


def export_scedule(schedule, console=True, ics=False, csv=False):
    '''
    Функция экспортирует расписание с сайта МАИ в различных форматах:
    CSV, ICS для добавления в календарь
    '''
    for group_name in schedule:
        if csv:
            f_txt = open(group_name + ".csv", "wt")
        if ics:
            cal = icalendar.Calendar()
            cal.add('prodid', '-//My calendar product//mxm.dk//')
            cal.add('version', '2.0')
        pairs = schedule[group_name]
        pairdate = 0

        f1 = open(group_name + ".ics", "wb")
        # f = open(group_name + "1.ics", "w")
        # f.write('BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//My calendar product//mxm.dk//'+'\n')
        for pair in pairs:
            if csv or console:
                if pair['date'] != pairdate:
                    pairdate = pair['date']
                    if console:
                        print("Дата: "+pairdate)
                    # if csv: f_txt.write("Дата: "+pairdate+"\n")
                if csv:
                    f_txt.write(DELIM.join([pair[i] for i in list(pair)])+"\n")
                if console:
                    print(" ".join([pair[i] for i in list(pair)]))
            if ics:

                # f.write('BEGIN:VEVENT'+'\n')
                date = datetime.fromisoformat(str(parser.parse(pair['date'])))
                time_start = datetime.fromisoformat(
                    str(parser.parse(pair["time_start"])))
                time_start = datetime.combine(date.date(), time_start.time())
                time_end = datetime.fromisoformat(
                    str(parser.parse(pair["time_end"])))
                time_end = datetime.combine(date.date(), time_end.time())

                event = icalendar.Event()
                event.add('summary', str(pair['type'] + " " + pair['name']))
                event.add('dtstart', time_start)
                event.add('dtend', time_end)
                event.add('dtstamp', time_start)
                event.add('location', pair["room"])
                event.add('description', pair['lector'])
                cal.add_component(event)
                # f.write('SUMMARY:'+str(pair['type'] + " " + pair['name'])+'\n')
                # f.write('DTSTART;VALUE=DATE-TIME:'+time_start.strftime("%Y%m%dT%H%M%S")+'\n')
                # f.write('DTEND;VALUE=DATE-TIME:'+time_end.strftime("%Y%m%dT%H%M%S")+'\n')
                # f.write('DTSTAMP;VALUE=DATE-TIME:'+time_end.strftime("%Y%m%dT%H%M%S")+'Z'+'\n')
                # f.write('LOCATION:'+pair["room"]+'\n')
                # f.write('DESCRIPTION:'+pair['lector']+'\n')
                # f.write('END:VEVENT\n')

        if csv:
            f_txt.close()
        if ics:
            # f.write('END:VCALENDAR\n')
            # f.close()
            f1.write(cal.to_ical())
            f1.close()


def main():
    '''
    main function
    '''
    group_list = [
        'М3О-117М-22',
    ]
    schedule = getscedule(group_list)
    export_scedule(schedule, ics=True, csv=True)
    # getscedule(group_list)

    # help(getscedule)


if __name__ == "__main__":
    main()
