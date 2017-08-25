from datetime import date, timedelta
import calendar

def witintent(msg, client):
    try:
        resp = client.message(msg)
    except:
        resp = client.message('Error')
    return resp['entities']

def guardian(values, data):
    values = values['guardian']
    resp = ""

    response = {
            'guardian' : "Your teacher guardian is {}. ".format(data['name']),
            'number' : "Phone number - {}. ".format(data['phone']),
            'mail' : "email ID: {}. ".format(data['email'])
            }

    for val in values:
        resp += response[val['value']]

    return resp


def timetable(values, data):
    today = calendar.day_name[date.today().weekday()].lower()
    tomorrow = calendar.day_name[(date.today().weekday() + 1) % 7].lower()

    #timetable = values['timetable']
    try:
        time = values['time'][0]['value']
    except KeyError:
        time = 'today'

    if time == 'today':
        time = today
    elif time == 'tomorrow':
        time = tomorrow

    if time == 'sunday':
        return "Sunday is not a working day."

    response = "The timetable for {} is : \n\n ".format(time.upper())

    for subj in data[time]:
        t, sub = subj
        response += "({}) - {} \n\n".format(t,sub)

    if len(data[time]) == 0:
        return "There are no classes or {} is a holiday".format(time.upper())

    return response


def attendance(values, data, group):

    if group == 'CHEMISTRY GROUP':
        subs = [{'value': 'BIO'}, {'value': 'MATHS1'},
                    {'value': 'EVS'}, {'value': 'PSUC'},
                    {'value': 'PSUCLAB'}, {'value': 'EG'},
                    {'value': 'CHEM'}, {'value': 'BET'},
                    {'value': 'CHEMLAB'}]

    elif group == 'PHYSICS GROUP':
        subs = [{'value': 'BME'}, {'value': 'ENG'},
                    {'value': 'MATHS1'}, {'value': 'EG'},
                    {'value': 'PHY'}, {'value': 'PHYLAB'},
                    {'value': 'MOS'}, {'value': 'BME'},
                    {'value': 'WORKSHOP'}]


    try:
        subs = values['subject']
        output_att = "You've attended {}/{} classes; You have {}% attendance in {} right now.\n"
        output_bunk ="After bunking one class, you will have {}%.\n"
    except KeyError:
        output_att = "{}/{} {}% attendance in {}.\n"
        output_bunk = "{}% after 1 bunk.\n"

    slcm_error = "SLCM hasn't been updated for {}\n"
    #time = values['time'][0]['value']

    resp = ""
    BUNK = False

    for sub in subs:
        sub = sub['value']
        try:
            resp += output_att.format(data[sub]['present'], data[sub]['totalclasses'], data[sub]['percent'], sub)
        except KeyError:
            resp += slcm_error.format(sub)

        try:
            after_percent = 100 * int(data[sub]['present'])/(int(data[sub]['totalclasses'])+1)
            after_percent = round(after_percent, 2)
            if 'attendance' in values:
                if any(vals['value'] == 'bunk' for vals in values['attendance']):
                    resp += output_bunk.format(after_percent)
                    BUNK = True
        except KeyError:
            pass

    resp = resp.splitlines()
    if BUNK:
        x = []
        i = 0
        while i < len(resp):
            x.append(resp[i]+resp[i+1])
            i += 2
        resp = x 

    return resp
