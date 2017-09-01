from selenium import webdriver
from pprint import pprint
from time import sleep
from bs4 import BeautifulSoup

SUBJECTS = {
    "1":
        {"CHEMISTRY GROUP": {
            "BIOLOGY FOR ENGINEERS": "BIO",
            "ENGINEERING MATHEMATICS - I": "MATHS1",
            "ENVIRONMENTAL STUDIES": "EVS",
            "PROBLEM SOLVING USING COMPUTERS": "PSUC",
            "ENGINEERING GRAPHICS - I": "EG",
            "ENGINEERING GRAPHICS - I LAB": "EG",
            "ENGINEERING CHEMISTRY": "CHEM",
            "BASIC ELECTRICAL TECHNOLOGY": "BET",
            "ENGINEERING CHEMISTRY LAB": "CHEMLAB",
            "PSUC LAB": "PSUCLAB",
        },

        "PHYSICS GROUP": {
                "BASIC MECHANICAL ENGINEERING": "BME",
                "ENGINEERING MATHEMATICS - I": "MATHS1",
                "COMMUNICATION SKILLS IN ENGLISH": "ENG",
                "ENGINEERING PHYSICS": "PHY",
                "ENGINEERING PHYSICS LAB": "PHYLAB",
                "MECHANICS OF SOLIDS": "MOS",
                "BASIC ELECTRONICS": "BE",
                "WORKSHOP PRACTICE": "WORKSHOP",
                "ENGINEERING GRAPHICS - I": "EG",
                "ENGINEERING GRAPHICS - I LAB": "EG",
            }
        
        }}


def end(driver):
    driver.quit()


def login(rollno, password):
    driver = webdriver.PhantomJS()
    driver.get("http://slcm.manipal.edu/loginForm.aspx")
    user_field = driver.find_element_by_id("txtUserid")
    pass_field = driver.find_element_by_id("txtpassword")

    user_field.send_keys(rollno)
    pass_field.send_keys(password)
    driver.find_element_by_css_selector('#btnLogin').click()

    try:
        driver.find_element_by_id("txtUserid")
        return None
    except:
        pass

    return driver


def timetable(driver):
    driver.get("http://slcm.manipal.edu/StudentTimeTable.aspx")
    sleep(1.5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    skeleton = soup.find_all('div', {'class': 'fc-content-skeleton'})
    content_skeleton = skeleton[1]

    week = []

    for td in content_skeleton.find_all('div', {'class': 'fc-content-col'}):
        try:
            day = []
            classes = td.find_all('div', {'class': 'fc-title'})
            timings = td.find_all('div', {'class': 'fc-time'})

            for i in range(len(classes)):
                day.append((timings[i].text, classes[i].text))
        except:
            pass
        week.append(day)

    timetable = {
        "monday": week[0],
        "tuesday": week[1],
        "wednesday": week[2],
        "thursday": week[3],
        "friday": week[4],
        "saturday": week[5],
    }

    return timetable


def guardian(driver):
    driver.get("http://slcm.manipal.edu/Academics.aspx")

    guardian_phone = driver.find_element_by_id(
        "ContentPlaceHolder1_lblGuardianTeacherMobile")
    guardian_name = driver.find_element_by_id(
        "ContentPlaceHolder1_lblGuardian")
    guardian_mail = driver.find_element_by_id(
        "ContentPlaceHolder1_lblGuardianTeacherEmail")

    guardian_mail = guardian_mail.get_attribute('innerHTML')
    guardian_phone = guardian_phone.get_attribute('innerHTML')
    guardian_name = guardian_name.get_attribute('innerHTML')

    guardian_details = {
        "name": guardian_name,
        "phone": guardian_phone,
        "email": guardian_mail,
    }

    return guardian_details


def group(driver):
    driver.get("http://slcm.manipal.edu/Academics.aspx")
    sleep(1.5)
    group = driver.find_element_by_id("ContentPlaceHolder1_lblGroup")

    if group == "":
        return None

    return str(group.text)


def semester(driver):
    numerals = {"I": 1,
                "II": 2,
                "III": 3,
                "IV": 4,
                "V": 5,
                "VI": 6,
                "VII": 7,
                "VIII": 8,
                }
    driver.get("http://slcm.manipal.edu/Academics.aspx")
    sleep(1.5)
    semester = driver.find_element_by_id("ContentPlaceHolder1_lblSemester")
    semester = semester.text

    if semester in numerals:
        return numerals[semester]

    return None


def attendance(driver, semester, group):
    driver.get("http://slcm.manipal.edu/Academics.aspx")
    navbar = driver.find_elements_by_xpath('//a[@class="fa"]')[1]
    attend = driver.find_element_by_id(
        "tblAttendancePercentage").get_attribute('innerHTML')
    soup = BeautifulSoup(attend, "html.parser")
    fields = soup.find_all("th", {"class": "text-center"})
    values = soup.find_all("td", {"class": "text-center"})

    fields = [n.text for n in fields]
    values = [n.text for n in values]

    attendance = {}

    if group is None:
        try:
            i = 0
            while i < len(values):
                val = SUBJECTS[semester][values[i+1]]
                attendance[val] = {
                    "year": values[i],
                    "sem": values[i + 2],
                    "totalclasses": values[i + 3],
                    "present": values[i + 4],
                    "absent": values[i + 5],
                    "percent": values[i + 6],
                }
                i += 7
        except KeyError:
            pass

    elif group is not None and semester == '1':
        try:
            i = 0
            while i < len(values):
                val = SUBJECTS[semester][group][values[i+1]]
                attendance[val] = {
                    "year": values[i],
                    "sem": values[i + 2],
                    "totalclasses": values[i + 3],
                    "present": values[i + 4],
                    "absent": values[i + 5],
                    "percent": values[i + 6],
                }
                i += 7
        except KeyError:
            pass

    return attendance


if __name__ == '__main__':
    pass
