#! /usr/bin/env python3.5
import requests
import local_settings as ls
import studb
from bs4 import BeautifulSoup



def login(host, user, password):
        payload = {'login': user, 'pass': password}
        r = requests.post(host + '/login/login_code.php', data=payload)
        r.close()
        return r.cookies


def get_students(host, cookies, params, isInfo):
    url = host + '/show_students/show_all_st_code.php'
    response = requests.get(url, cookies=cookies, params=params)
    htmltext = response.text.strip(' \t\n\r').replace("&nbsp;", "").replace("\n","")
    soup = BeautifulSoup(htmltext,'html5lib')
    # print(htmltext)
    tables = soup.find_all('table')
    trs = tables[2].find_all('tr')
    student_table = []
    for tr in trs[1:]:
        tds = tr.find_all('td')
        student = {}
        student['N'] = tds[1].get_text()
        student['fullname'] = tds[2].get_text()
        student['student_id']=tds[3].get_text()
        student['birth_date'] =tds[4].get_text()
        student['student_group'] =tds[5].get_text()
        student['department'] =tds[6].get_text()
        student['kafedra'] =tds[7].get_text()
        student['decanat'] =tds[8].get_text()
        student['ed_form'] =tds[9].get_text()
        student['ed_type'] =tds[10].get_text()
        student['code'] =tds[11].get_text()
        student['commerce'] = 1 if tds[12].img else 0
        student['current_state'] =tds[13].get_text()
        student_table.append(student)
    return student_table

    # for table in body.find_all('table'):
    #     print(table)


if __name__ == "__main__":
    host = ls.students_host
    try:
        cookies = login(host, ls.login, ls.password)
        students = get_students(host,cookies, {'page': str(1), 'dep': '34'}, True)
        for s in students:
            print(s)

    except requests.HTTPError as err:
        print(err.errno,err.strerror)
    except requests.RequestException as err:
        print(err.errno, err.strerror)

