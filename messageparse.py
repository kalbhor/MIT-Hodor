from fuzzywuzzy import fuzz
import json
from constants import MARKS, ATTENDANCE

'''
Hard-coded NLP library for MIT-HODOR
'''

def match(key, reference, threshold=67):
    value = False
    for ele in reference:
        if fuzz.ratio(key.lower(), ele) > threshold:
            value = True
            break
    return value

def attendance_match(key):
    return match(key, reference=ATTENDANCE)

def marks_match(key):
    return match(key, reference=MARKS)

# Returns the action(s) to be carried out for the given message
def intent(message = "", scraped_data={}):
    message = message.split()
    attendance = False
    marks = False
    subject = []

    sub_list = extract_subjects(scraped_data)

    for word in message:
        if attendance != True and attendance_match(word) == True:
            attendance = True
            continue

        if marks != True and marks_match(word) == True:
            marks = True
            continue

        sub = subject_match(word, sub_list)
        if sub is not None:
            subject.append(sub)

    actual_intent = {}
    actual_intent['marks'] = marks
    actual_intent['attendance'] = attendance
    actual_intent['subject'] = subject

    return actual_intent

# Returns an abbreviated and an easy to compare subject-list
def extract_subjects_easy(subjects):
    rem_words = ['ENGINEERING ', ' OF ', ' - ', ' III', ' II', ' IV', ' I']

    # Removing meaningless characters for abbreviation list
    for word in rem_words[2:]:
        subjects = [i.replace(word, '') for i in subjects]

    # Abbreviations list
    subject_abbr = []
    for i, subject in enumerate(subjects):
        subject_abbr.append("")
        for x in subject.split():
            subject_abbr[i] +=(x[0])

    # Removing redundant and useless characters for the subject list
    for word in rem_words[:2]:
        subjects = [i.replace(word, ' ') for i in subjects]

    subjects = [i.strip() for i in subjects]
    return subjects, subject_abbr


# Extracts subject names from the data scraped
def extract_subjects(scraped_data):
    subjects = [i for i in scraped_data["Subjects"]]
    return subjects

# the real OG - checks whether a word matches a subject
def subject_match(key, original_subjects):
    key = key.replace(".", "").lower()

    cur_match = 0
    max_match = 0
    pos = None

    subjects, subject_abbr = extract_subjects_easy(original_subjects)

    # If subject given is an abbreviation
    for i, sub in enumerate(subject_abbr):
        cur_match = fuzz.ratio(key, sub.lower())
        if cur_match > max_match:
            max_match = cur_match
            pos = i

    if max_match == 100:     # Can expect 100% accuracy for abbreviations
        return original_subjects[pos]

    else:
        max_match = 0
        # Not an abbreviation
        for i, sub in enumerate(subjects):
            cur_match = fuzz.ratio(key, sub.lower())

            if cur_match > max_match:
                max_match = cur_match
                pos = i

    if max_match > 50:
        return original_subjects[pos]
    else:
        return None


'''
The main function to be called from this file.
The returned string can be sent to the user as message.
'''
def get_response(message="", scraped_data={}):
    actual_intent = intent(message=key, scraped_data=scraped_data)
    #print(actual_intent)

    reply = ""
    if actual_intent['subject'] != []:

        for i in actual_intent['subject']:
            reply += i + "...\n"
            if actual_intent['marks'] is True:
                reply += "\nMARKS -\n"

                if scraped_data['Subjects'][i] != {}:
                    reply += "Grade: {}\n".format(scraped_data['Subjects'][i]['Grade'])

                    for j in scraped_data['Subjects'][i]['Internals']:
                        reply += "{}: {}\n".format(j, scraped_data['Subjects'][i]['Internals'][j]["Obtained"])

            if actual_intent['attendance'] is True:
                reply += "\nATTENDANCE -\n"

                if scraped_data['Attendance'][i] != {}:
                    reply += "{}:\
                            \nAttended: {}/{}\
                            \nPercentage: {}%".format(i, scraped_data['Attendance'][i]['Attended'],
                            scraped_data['Attendance'][i]['Total'],
                            scraped_data['Attendance'][i]['Percentage'])

                #if not actual_intent['attendance'] and not actual_intent['marks']:
            else:
                reply += "What do you want me to do?"

    elif actual_intent['marks'] or actual_intent['attendance']:
        reply += "Please mention the subject for which you want to see."
    else:
        reply += "Hodor?"

    return reply
