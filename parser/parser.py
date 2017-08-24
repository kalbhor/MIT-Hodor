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


def attendance(values, data):
    try:
        subs = values['subject']
        output = "You've attended {} classes out of {}; You have {}% attendance in {} right now. \n"
    except KeyError:
        output = "{}/{} {}% attendance in {}. \n"

        subs = [{'value' : 'bio'}, {'value':'maths'}, {'value':'evs'}, {'value' : 'psuc'}, {'value' : 'psuc lab'}, {'value' : 'eg'}, {'value': 'chemistry'}, {'value' : 'bet'}, {'value': 'chemistry lab'}]
    #time = values['time'][0]['value']

    subject = { 'bio': 'BIO', 'maths': 'MATHS1', 'evs': 'EVS',
            'psuc': 'PSUC', 'psuc lab': 'PSUCLAB', 'eg': 'EG',
            'chemistry': 'CHEM', 'bet': 'BET', 'chemistry lab': 'CHEMLAB',
            }

    resp = ""

    for sub in subs:
        sub = sub['value']
        try:
            resp += output.format(data[subject[sub]]['present'], data[subject[sub]]['totalclasses'], data[subject[sub]]['percent'], sub)
        except KeyError:
            resp += "SLCM hasn't been updated for {}\n\n".format(sub)
        try:
            after_percent = 100 * int(data[subject[sub]]['present'])/(int(data[subject[sub]]['totalclasses'])+1)
            after_percent = round(after_percent, 2)
            if 'attendance' in values:
                if any(vals['value'] == 'bunk' for vals in values['attendance']):
                    resp += 'After bunking one class, you will have {}%. \n\n'.format(after_percent)

        except:
            resp += "Sorry, there seems to be a problem. Perhaps SLCM hasn't been updated yet for {}\n\n".format(sub)

    return resp
