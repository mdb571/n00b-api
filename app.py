from flask import Flask, jsonify, request
from flask import make_response,redirect,render_template
from flask import url_for
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

# payload = {
#     'studentAccount': '180xxx',
#     'studentPassword': '180xxx'
# }
base='https://tkmce.linways.com'
url = 'https://tkmce.linways.com/student/'
home_url = url + 'student.php?menu=home'
attendence_url = 'https://tkmce.linways.com/student/attendance/ajax/ajax_subjectwise_attendance.php?action=GET_REPORT'
assignment_url = 'https://tkmce.linways.com/student/asimark/ajax_assignment_mark.php'
attendence_total = 'https://tkmce.linways.com/student/attendance/ajax_hour_wise.php'
internal_url = 'https://tkmce.linways.com/student/mymark/ajax_mark_details.php?semID='
logged_in=False
# @app.route('/', methods=['GET'])
# def index():
#     return(jsonify({'Status': '500','Error':'Send a POST request to view data '}))

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'GET':
        return(render_template('index.html'))
    else:
        request_data = request.get_json(force=True)
        print(request_data)
        global payload
        global logged_in
        studentdata = {}
        payload = {
            'studentAccount': request_data['Username'],
            'studentPassword': request_data['Pass']
        }
        with requests.Session() as session:
            post = session.post(url, data=payload)
        r = session.get(home_url)
        fail = BeautifulSoup(post.text, 'lxml')
        soup = BeautifulSoup(r.text, 'html')
        login_val = fail.find('red')
        if login_val == None:
            logged_in=True
            studentdata['Name'] = soup.select('.truncate')[0].getText()
            studentdata['Batch'] = soup.select('.panel-heading')[1].getText()
            return jsonify({'status': 'OK', 'studentdata': studentdata})
        else:
            return jsonify({'status': 'Not Found', 'Error': 'Login Failed! Invalid Username/Password'})


@app.route('/attendance', methods=['GET'])
def attendance():
    if logged_in==True:
        with requests.Session() as session:
            post = session.post(url, data=payload)
            min_attendance = 75
            r = session.get(attendence_url)
            soup = BeautifulSoup(r.text, 'lxml')
            table1 = soup.find("table")
            body = table1.find("tbody")
            subjects = soup.find_all('tr')
            subjects.pop(-1)
            attendict = {}
            j = 0
            for i in subjects:
                x = 1
                j += 1
                attendict[j] = {}
                s = i.find_all('td')
                if s == []:
                    continue
                attendict[j]["Name"] = str(s[1].string).replace(
                    '\\n                    ', '')
                attendict[j]['Hours Attended'] = s[2].string
                attendict[j]['Total Hours'] = s[3].string
                attendict[j]['Attendence Percentage'] = s[4].string
                percentage = int(float(s[4].string.replace('%', '')))
                if percentage >= 75:
                    bunk = (int(s[2].string) - (min_attendance /
                                                100*int(s[3].string)))/(min_attendance/100)
                    if int(bunk) == 0:
                        attendict[j]['Bunk Status'] = "You can't bunk anymore"
                    else:
                        attendict[j]['Bunk Status'] = 'You can bunk ' + \
                            str(int(bunk))+' classes'
                else:
                    attend = (
                        (((min_attendance/100)*int(s[3].string)) - int(s[2].string)) / ((100-min_attendance)/100))

                    attendict[j]['Bunk Status'] = 'You must attend ' + \
                        str(int(attend))+' classes'

        return jsonify({'status': 'OK', 'subject': attendict})
    else:
        return  redirect(url_for('home'))


@app.route('/attendance/total', methods=['GET'])
def attendancetotal():
    if logged_in==True:
        with requests.Session() as session:
            post = session.post(url, data=payload)
            attendencetotal = {}
            r = session.get(attendence_total)
            soup = BeautifulSoup(r.text, 'lxml')
            table = soup.find('table')
            elem = table.find_all('td')
            elem.pop(0)
            attendencetotal['Period'] = table.thead.text.replace('\n', '')
            attendencetotal['Attended Hours'] = elem[1].text.replace(":", '')
            attendencetotal['Total Hours'] = elem[3].text.replace(':', '')
            attendencetotal['Percentage'] = elem[5].text.replace(':', '')

        return(jsonify({'Attendance Overall': attendencetotal}))
    else:
        return  redirect(url_for('home'))


@app.route('/assignment', methods=['GET'])
def assignmenthome():
    if logged_in==True:
        return jsonify({'status': 'OK', 'Message': 'Specify sem  in the url to see response'})
    else:
        return  redirect(url_for('home'))


@app.route('/assignment/sem=<semID>', methods=['GET'])
def assignmentsem(semID):
    if logged_in==True:
        with requests.Session() as session:
            post = session.post(url, data=payload)
            assignmentdict = {}
            r = session.post(assignment_url, data={"semID": semID})
            soup = BeautifulSoup(r.text, 'lxml')
            table = soup.find_all('table', {"class": "table table-striped"})
            if table!=[]:
                table.pop(0)
            # row=[i.text.replace("\n",' ') for i in head]
            for elem in table:
                assignmentdict[elem.thead.text.replace('\n', '')] = {}
                assignmentdict[elem.thead.text.replace(
                    '\n', '')]['Subject'] = {}
                row = elem.find_all('tr')
                for tr in row:
                    cols = tr.find_all('td')
                    if cols == []:
                        continue
                    if cols[0].text == "Subjects":
                        continue
                    assignmentdict[elem.thead.text.replace(
                        '\n', '')]['Subject'][cols[0].text] = {}
                    assignmentdict[elem.thead.text.replace(
                        '\n', '')]['Subject'][cols[0].text]['Marks'] = cols[1].text
                    assignmentdict[elem.thead.text.replace(
                        '\n', '')]['Subject'][cols[0].text]['Max Marks'] = cols[2].text

        return jsonify({'status': 'OK', 'assignmentMarks': assignmentdict})
    else:
        return  redirect(url_for('home'))


@app.route('/internal', methods=['GET'])
def internalhome():
    if logged_in==True:
        return jsonify({'status': 'OK', 'Message': 'Specify sem  in the url to see response'})
    else:
        return  redirect(url_for('home'))


@app.route('/internal/sem=<semID>', methods=['GET'])
def internal(semID):
    if logged_in==True:
        internal = {}
        global internal_url
        with requests.Session() as session:
            post = session.post(url, data=payload)
            internal_url += semID
            r = session.get(internal_url)
            soup = BeautifulSoup(r.text, 'lxml')
            table = soup.find_all('table')
            for elem in table:
                testnum = elem.find('th').text.replace('\n', '')
                internal[testnum] = {}
                row = elem.find_all('tr')
                for tr in row:
                    cols = tr.find_all('td')

                    if cols != []:
                        if len(cols) > 3:
                            internal[testnum][cols[0].text.replace('\xa0', '')] = {
                            }
                            internal[testnum][cols[0].text.replace(
                                '\xa0', '')]["Marks Obtained"] = cols[1].text.replace('\xa0', '')
                            internal[testnum][cols[0].text.replace(
                                '\xa0', '')]["Percentage"] = cols[2].text.replace('\xa0', '')
                            internal[testnum][cols[0].text.replace(
                                '\xa0', '')]["Class Average"] = cols[3].text.replace('\xa0', '')
                            internal[testnum][cols[0].text.replace(
                                '\xa0', '')]["Max Marks"] = cols[4].text.replace('\xa0', '')

        return jsonify({'status': 'OK', 'internalMarks': internal})
    else:
        return  redirect(url_for('home'))


@app.route('/notify', methods=['GET'])
def notif():
    if logged_in==True:
        notify={}
        j=0
        with requests.Session() as session:
            post = session.post(url, data=payload)
            r = session.get(home_url)
            soup = BeautifulSoup(r.text, 'lxml')
            notif = soup.find_all('a', {"class": "notification-list"})
            for i in notif:
                notify[j]={}
                notify[j]['Date Published'] = re.findall(r"[\d]{4}-[\d]{2}-[\d]{2}", i.decode())[0]
                notify[j]['Message'] = i.find('div').text
                j+=1
            return(jsonify({'Status':'OK','Notifications':notify}))
    else:
        print(logged_in)
        return  redirect(url_for('home'))

@app.route('/profile')
def prof():
    if logged_in==True:
        profile={}
        with requests.Session() as session:
            post = session.post(url, data=payload)
        r = session.get(home_url)
        soup = BeautifulSoup(r.text, 'lxml')
        img=soup.find('div',{"class":"list-group-item text-center profile_pic"})
        img=img.find('img')['src'].replace('..','')
        photo=base+img
        profile["Url"]=photo
        return(jsonify({'Status':'OK','Profile Url':profile["Url"]}))

    else:
        print(logged_in)
        return  redirect(url_for('home'))

@app.route('/pending',methods=['GET'])
def pending():
    if logged_in==True:
        with requests.Session() as session:
            post = session.post(url, data=payload)
        r = session.post(pending_url,data={"action":"GET_STUDENT_ASSIGNMENT_LIST"})
        data=r.json()
        for elem in data['data']:
            if elem['isSubmited']!=1:
                print(elem['assiNu'],elem['submissionDate'],elem['submissionTime'],elem['subjectDesc'],elem['assignmentID'])
    


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'status': 'Not found', 'error': 'Cannot find requested endpoint'}), 404)


if __name__ == '__main__':
    app.run(debug=True)
