#! /usr/bin/env python3.5

#  Copyright (c) 28.08.2021, 18:45
#  Denis Kudryashov

import requests
import local_settings as ls
import studb
from bs4 import BeautifulSoup



def login(host, user, password):
        payload = {'login': user, 'pass': password}
        r = requests.post(host + '/login/login_code.php', data=payload)
        r.close()
        return r.cookies


def getInfoFildName(desc):
    if "Документ" in desc:
        return "document"
    if "Пол" in desc:
        return "sex"
    if "Гражданство" in desc:
        return "citizenship"
    if "Индекс" in desc:
        return "post_index"
    if "Адрес" in desc:
        return "address"
    if "Телефон" in desc:
        return "phone"
    if "Кафедра" in desc:
        return "high_school_desc"
    if "Магистр" in desc:
        return "okso_mag"
    elif "ОКСО" in desc:
        return "okso_bac"
    if "общежитие" in desc:
        return "student_residence"
    if "Целевой" in desc:
        return "celevoy"
    return ""


def get_stud_info(url, cookies, params):
    response = requests.get(url, cookies=cookies, params=params)
    htmltext = response.text.strip(' \t\n\r').replace("&nbsp;", "").replace("\n","")
    soup = BeautifulSoup(htmltext, 'html5lib')

    ahrefs = soup.find_all('a')

    markurl = ""
    href_list = ahrefs[3].get_attribute_list("href")
    if href_list:
        hrefstr = href_list[0]
        markurl = host + "/show_students/" + hrefstr


    tables = soup.find_all('table')

    student_info_table = {}
    trs = tables[0].find_all('tr')
    for tr in trs[2:-1]:
        tds = tr.find_all('td')
        id_descr = tds[0].get_text()
        id_name = getInfoFildName(id_descr)
        if len(id_name) > 0:
            student_info_table[id_name] = tds[1].get_text().lstrip().rstrip()

    trs = tables[1].find_all('tr')
    for tr in trs[1:]:
        tds = tr.find_all('td')
        if tds:
            if tds[0].get_text():
                id_descr = tds[0].get_text()
                id_name = getInfoFildName(id_descr)
                if len(id_name) > 0:
                    student_info_table[id_name] = tds[1].get_text().lstrip().rstrip()

    return student_info_table, markurl

def get_stud_marks(url,cookies, params):
    response = requests.get(url, cookies=cookies, params=params)
    htmltext = response.text.strip(' \t\n\r').replace("&nbsp;", "").replace("\n", "")
    soup = BeautifulSoup(htmltext, 'html5lib')
    student_mark_table = []
    tables = soup.find_all('table')
    for table in tables:
        trs = table.find_all('tr')
        semestr = ""
        isSkip = False
        for tr in trs:
            ths = tr.find_all('th')
            if len(ths) == 1:
                if isSkip:
                    isSkip = False
                    continue
                semestr = ths[0].get_text()
                isSkip = True
                continue
            elif len(ths) > 1:
                continue

            tds = tr.find_all('td')
            disciplin = {}
            disciplin['discipline'] = tds[1].get_text()
            disciplin['form'] = tds[2].get_text()
            disciplin['session'] = tds[3].get_text()
            disciplin['result'] = tds[4].get_text()
            disciplin['semester'] = semestr.lstrip()
            student_mark_table.append(disciplin)
    return student_mark_table

def get_students(host, cookies, params, isInfo):
    url = host + '/show_students/show_all_st_code.php'
    response = requests.get(url, cookies=cookies, params=params)
    htmltext = response.text.strip(' \t\n\r').replace("&nbsp;", "").replace("\n","")
    soup = BeautifulSoup(htmltext,'html5lib')
    # print(htmltext)
    tables = soup.find_all('table')
    if not tables:
        return None
    if len(tables) < 3:
        return None

    trs = tables[2].find_all('tr')
    student_table = []
    for tr in trs[1:]:
        tds = tr.find_all('td')
        student = {}
        student['fullname'] = tds[2].get_text()
        student['student_id'] = tds[3].get_text()
        student['birth_date'] = tds[4].get_text()
        student['course'] = tds[5].get_text()
        student['group'] = tds[6].get_text()
        student['institute'] = tds[7].get_text()
        student['high_school'] = tds[8].get_text()
        student['education_form'] = tds[10].get_text()
        student['education_type'] = tds[11].get_text()
        student['code'] = tds[12].get_text()
        student['commerce'] = 1 if tds[13].img else 0
        student['current_state'] = tds[14].get_text()

        href_list =  tds[15].a.get_attribute_list("href")

        markulr = ""
        if href_list:
            hrefstr = href_list[0]
            infourl = host + "/show_students/" + hrefstr
            student_info, markulr = get_stud_info(infourl, cookies, params)
            if student_info:
                student['info'] = student_info


        if markulr:
            student_marks = get_stud_marks(markulr,cookies, params)
            if student_marks:
                student['marks'] = student_marks

        # print(student)

        student_table.append(student)

    return student_table


if __name__ == "__main__":
    host = ls.students_host
    try:
        cookies = login(host, ls.login, ls.password)

        sdb = studb.StudentsDB('StudentBase.db')



        for ind in range(1, 50):
            print("Page: " + str(ind))
            students = get_students(host,cookies, {'page': str(ind), 'dep': '56'}, True)
            if not students:
                print("End at page: " + str(ind))
                break

            for student in students:
                st = studb.Student(
                        fullname = student['fullname'], student_id = student['student_id'],
                        birth_date = student['birth_date'], course = student['course'],
                        student_group = student['group'], institute = student['institute'],
                        high_school = student['high_school'], education_form = student['education_form'],
                        education_type = student['education_type'], code = student['code'],
                        commerce = student['commerce'], current_state = student['current_state'])
                sdb.insert(st)
                sdb.commit()

                try:
                    info = student['info']
                    inft = studb.Info()
                    for key, value in info.items():
                        inft.__dict__[key] = value
                    inft.sid = st.id
                    sdb.insert(inft)
                    sdb.commit()
                except :
                    continue

                try:
                    marks = student['marks']
                    for disciplin in marks:
                        markt  = studb.Mark()
                        for key, value in disciplin.items():
                            markt.__dict__[key] = value
                        markt.sid = st.id
                        sdb.insert(markt)
                    sdb.commit()
                except :
                    pass

    except requests.HTTPError as err:
        print(err.errno,err.strerror)
    except requests.RequestException as err:
        print(err.errno, err.strerror)

