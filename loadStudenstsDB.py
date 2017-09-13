#! /usr/bin/env python3.5
import requests
import sqlite3
import local_settings as ls


def extract_stud_table(html_page):
    pos = 0
    start_pos = 0
    ind = 0
    poss = [0, 0, 0, 0, 0, 0]

    while pos >= 0:
        pos = html_page.find("<table", start_pos)
        poss[ind] = pos
        start_pos = pos + 1
        ind += 1

    s = poss[2]
    end = poss[3]

    return html_page[s:end]


def login(host,user,password):
    payload = {'login':user,'pass':password}
    r = requests.post(host + '/login/login_code.php', data=payload)
    r.close()
    return r.cookies


def get_info(url,cookies):
    r = requests.get(url, cookies=cookies)

    if r.status_code != 200:
        print(r.status_code)
        return []
    # print(r.text.replace("&nbsp;", ""))
    htmltext = r.text.replace("&nbsp;", " ").replace("\n","").replace("\t","").replace("\r","")
    # print(htmltext)
    start = htmltext.find('viewstud_marks_new_code')
    stop = htmltext.find('>',start)
    mark_href = htmltext[start:stop - 1]
    # print(mark_href)

    start = htmltext.find("</tr>",stop)
    info = {}
    is0 = True

    while start != -1:
        start = htmltext.find("<tr",start + 1)
        key_str = ""
        val_str = ""

        if is0:
            td0s = htmltext.find("<td",start)
            td1s = htmltext.find("<td", td0s + 4)
            s = htmltext.find(">",td1s) + 1
            e = htmltext.find("<",s)
            key_str = htmltext[s:e - 1]
            td2s = htmltext.find("<td", td1s + 4)
            s = htmltext.find(">",td2s) + 1
            e = htmltext.find("</t",s)
            val_str = htmltext[s:e].strip(" ")
            is0 = False
        else:
            stop = htmltext.find("tr", start + 2)
            td1s = htmltext.find("<td", start)
            if stop < td1s:
                continue
            s = htmltext.find(">",td1s) + 1
            e = htmltext.find("<",s)
            key_str = htmltext[s:e - 1]
            td2s = htmltext.find("<td", td1s + 4)
            s = htmltext.find(">",td2s) + 1
            e = htmltext.find("</t",s)
            val_str = htmltext[s:e].strip(" ")
            pass

        if key_str != "":
            info[key_str.replace(":","")] = val_str.replace("<b>","").replace("</b>","").replace("\"","--")

    return info, mark_href


def get_mark(url, cookies):
   # print(url)
    r = requests.get(url, cookies=cookies)

    if r.status_code != 200:
        print(r.status_code)
        return []

    # print(r.text.replace("&nbsp;", ""))
    htmltext = r.text.replace("&nbsp;", " ").replace("\n","").replace("\t","").replace("\r","")
    start = 0
    marks = []
    # print("             ")

    while True:
        start = htmltext.find("<table ", start)
        if start == -1:
            break
        stop = htmltext.find("</table>", start + 4)
        # text = htmltext[start:stop + 8].replace("<th","\n<th")
        text = htmltext[start:stop + 8]

        if text == "":
            continue

        ar = text.split("<th")

        for a in ar[5:]:
            b = a.replace("<tr","\n<tr").replace("<tr><td class = view>","").replace("<td class = view>",",").replace("</td>","").replace("</tr>","")
            b = b.replace("</table>","").replace("\n<tr>","").replace("\"","--")
            # print(b)
            ar_task = b.split("\n")
            ar_task[0] = ar_task[0].replace(" class=view colspan = 4 align=left style='background-color:#999999'> ","").replace("</th>","")
            # print(ar_task)
            # print(" -- ")
            marks.append(ar_task)

        start = stop
    # print(htmltext)
    return marks


def get_page(host,cookies,params,isInfo):
    url = host + '/show_students/show_all_st_code.php'
    r = requests.get(url, cookies=cookies, params=params)
    ststr = extract_stud_table(r.text)
   # print(ststr)
    r.close()
    tr_pos = 0
    pos = ststr.find("<th", 0)
    student_table = []
    info_table = []
    mark_table = []

    while tr_pos >= 0:
        tr_pos = ststr.find("<tr", pos)
        if tr_pos < 0:
            break
        pos = tr_pos + 1
        s = tr_pos + 3
        student = []

        for _ in range(0, 15):
            td_pos = ststr.find("<td", s)

            if td_pos < 0:
                break
            start = ststr.find(">", td_pos) + 1
            stop = ststr.find("</", start)
            s = stop + 1
            value_str = ststr[start:stop].strip(' \t\n\r').replace("&nbsp;", "")
            student.append(value_str)

        student_info = []
        student_mark = []

        if isInfo:
            pattern = '<a href = "'
            start = student[14].find(pattern)
            if start != -1:
                start += len(pattern)
                stop = student[14].find('">', start)
                hrefstr = student[14][start:stop]
                infourl = host + "/show_students/" + hrefstr
                student_info, mark_href = get_info(infourl, cookies)

                if mark_href != "":
                    markurl = host + "/show_students/" + mark_href
                    student_mark = get_mark(markurl, cookies)
                else:
                    print("no marks")

        # print(str(student_info))
        student_table.append(student)

        info_table.append(student_info)
        mark_table.append(student_mark)

    return student_table, info_table, mark_table


def open_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
                N INTEGER UNIQUE,
                fullname TEXT,
                student_id TEXT,
                birth_date TEXT,
                student_group TEXT,
                faculty TEXT,
                department TEXT,
                decanat TEXT,
                form TEXT,
                O TEXT,
                code TEXT,
                commerce TEXT,
                current_state TEXT,
                state_description TEXT
                  );''')

    return conn, cursor


def save_student_to_db(cursor, s, inf, mark):
    if inf:
        inf['marks'] = mark

    sqlstr = '''INSERT INTO students (N,fullname,student_id,birth_date,student_group,faculty,department,decanat,
            form,O,code,commerce,current_state,state_description) 
              VALUES ( {0}, "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", "{8}", "{9}", "{10}", "{11}", "{12}", "{13}");'''.format(
        s[1],s[2],s[3],s[4],s[5],s[6],s[7],s[8],s[9],s[10],s[11],s[12],s[13],str(inf))

    try:
        cursor.execute(sqlstr)
    except sqlite3.Error as e:
        print(sqlstr)
        print(e)


if __name__ == "__main__":
    # conn, cursor = open_db('test.db')

    host = ls.students_host
    cookies = login(host,ls.login,ls.password)

    for ind in range(2,3):
        print(ind)
        students, infos, marks = get_page(host,cookies,{'page': str(ind), 'dep':'34'},False)
        for s in students:
            print(s)
        if students == []:
            break

        # for s,inf,mark in zip(students, infos, marks):
        #      save_student_to_db(cursor, s, inf, mark)

    # conn.commit()
    # conn.close()

