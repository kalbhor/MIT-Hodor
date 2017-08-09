from selenium import webdriver
from bs4 import BeautifulSoup

def main(rollno, password):
    driver = webdriver.PhantomJS()
    login(driver, rollno, password)
    x = attendance(driver)
    return x

def login(driver, rollno, password):
    driver.get("http://slcm.manipal.edu/loginForm.aspx")
    user_field = driver.find_element_by_id("txtUserid")
    pass_field = driver.find_element_by_id("txtpassword")

    user_field.send_keys(rollno)
    pass_field.send_keys(password)
    driver.find_element_by_css_selector('#btnLogin').click()

def attendance(driver):
    # tblAttendancePercentage
    driver.get("http://slcm.manipal.edu/Academics.aspx")
    navbar = driver.find_elements_by_xpath('//a[@class="fa"]')[1]
    attend = driver.find_element_by_id("tblAttendancePercentage").get_attribute('innerHTML')
    soup = BeautifulSoup(attend,"html.parser")
    fields = soup.find_all("th", {"class":"text-center"})
    values = soup.find_all("td", {"class":"text-center"})

    attrs = {}
    for n in range(7):
        attrs[fields[n].text] = values[n].text
    return attrs 

def announcement(driver):
    driver.get("http://slcm.manipal.edu/loginForm.aspx#announcement")


if __name__ == '__main__':
   x= main(170906092,"1amLawli3t")
   print(x)

