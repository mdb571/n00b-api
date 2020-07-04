from flask import Flask, jsonify,request
from flask import make_response
import requests
import getpass
import bs4
app = Flask(__name__)

# payload = {
#     'studentAccount': '180051',
#     'studentPassword': '180051'
# }

url = 'https://tkmce.linways.com/student/'
home_url = url + 'student.php?menu=home'
attendence_url = 'https://tkmce.linways.com/student/attendance/ajax/ajax_subjectwise_attendance.php?action=GET_REPORT'
assignment_url = 'https://tkmce.linways.com/student/asimark/ajax_assignment_mark.php'
attendence_total='https://tkmce.linways.com/student/attendance/ajax_hour_wise.php'

studentdata = {}




@app.route('/', methods=['GEt'])
def index():
    return(jsonify({'Status': '500','Error':'Send a POST request to view data '}))

@app.route('/', methods=['POST'])
def home():
    request_data=request.get_json(force=True)
    print(request_data)
    global payload
    studentdata={}
    payload = {
        'studentAccount': request_data['Username'],
        'studentPassword':request_data['Pass']
    }
    with requests.Session() as session:
     post = session.post(url, data=payload)
    r = session.get(home_url)
    soup = bs4.BeautifulSoup(r.text, 'html')

    studentdata['Name'] = soup.select('.truncate')[0].getText()

    studentdata['Batch'] = soup.select('.panel-heading')[1].getText()

    return jsonify({'status':'OK','studentdata': studentdata})


@app.route('/attendance', methods=['GET'])
def attendance():
    with requests.Session() as session:
        post = session.post(url, data=payload)
        min_attendance=75
        r = session.get(attendence_url)
        soup = bs4.BeautifulSoup(r.text, 'lxml')
        table1 = soup.find("table")
        body = table1.find("tbody")
        subjects = soup.find_all('tr')
        subjects.pop(-1)
        attendict = {}
        j = 0
        for i in subjects:
            x=1
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
            percentage=int(float(s[4].string.replace('%',''))) 
            if percentage>=75:
                bunk=(int(s[2].string) - (min_attendance/100*int(s[3].string)))/(min_attendance/100)
                if int(bunk)==0:
                    attendict[j]['Bunk Status']= "You can't bunk anymore"
                else:
                    attendict[j]['Bunk Status']= 'You can bunk '+str(int(bunk))+' classes'
            else:
                attend=((((min_attendance/100)*int(s[3].string)) - int(s[2].string)) / ((100-min_attendance)/100))

                attendict[j]['Bunk Status']= 'You must attend '+str(int(attend))+' classes'
   

    return jsonify({'status':'OK','subject':attendict})



@app.route('/attendance/total',methods=['GET'])
def attendancetotal():
    with requests.Session() as session:
        post = session.post(url, data=payload) 
        attendencetotal={}
        r = session.get(attendence_total)
        soup=bs4.BeautifulSoup(r.text,'lxml')
        table=soup.find('table')
        elem=table.find_all('td')
        elem.pop(0)
        attendencetotal['Period']=table.thead.text.replace('\n','')
        attendencetotal['Attended Hours']=elem[1].text.replace(":",'')
        attendencetotal['Total Hours']=elem[3].text.replace(':','')
        attendencetotal['Percentage']=elem[5].text.replace(':','')

    return(jsonify({'Attendance Overall':attendencetotal}))

@app.route('/assignment',methods=['GET'])
def assignmenthome():
    return jsonify({'status':'OK','Message':'Specify sem  in the url to see response'})



@app.route('/assignment/sem=<semID>',methods=['GET'])
def assignmentsem(semID):
    with requests.Session() as session:
        post = session.post(url, data=payload)
        assignmentdict={}
        r = session.post(assignment_url,data={"semID":semID})
        soup=bs4.BeautifulSoup(r.text,'lxml')
        table=soup.find_all('table',{ "class" : "table table-striped" })
        table.pop(0)
        # row=[i.text.replace("\n",' ') for i in head]
        for elem in table:
            assignmentdict[elem.thead.text.replace('\n','')]={}
            assignmentdict[elem.thead.text.replace('\n','')]['Subject']={}
            row=elem.find_all('tr')
            for tr in row:
                cols = tr.find_all('td')
                if cols==[]:
                    continue
                if cols[0].text=="Subjects":
                    continue
                assignmentdict[elem.thead.text.replace('\n','')]['Subject'][cols[0].text]={}
                assignmentdict[elem.thead.text.replace('\n','')]['Subject'][cols[0].text]['Marks']=cols[1].text
                assignmentdict[elem.thead.text.replace('\n','')]['Subject'][cols[0].text]['Max Marks']=cols[2].text

    return jsonify({'status':'OK','assignmentMarks':assignmentdict})        

@app.route('/internal',methods=['GET'])
def internalhome():
    return jsonify({'status':'OK','Message':'Specify sem  in the url to see response'})


@app.route('/internal/sem=<semID>',methods=['GET'])
def internal(semID):
    internal={}
    internal_url='https://tkmce.linways.com/student/mymark/ajax_mark_details.php?semID='
    with requests.Session() as session:
        post = session.post(url, data=payload)
        internal_url+=semID
        r = session.get(internal_url)
        soup=bs4.BeautifulSoup(r.text,'lxml')
        table=soup.find_all('table')
        for elem in table:
            testnum=elem.find('th').text.replace('\n','')
            internal[testnum]={}
            row=elem.find_all('tr')
            for tr in row:
                cols = tr.find_all('td')
                
                if cols!=[]:
                    if len(cols)>3:
                        internal[testnum][cols[0].text.replace('\xa0','')]={}
                        internal[testnum][cols[0].text.replace('\xa0','')]["Marks Obtained"]=cols[1].text.replace('\xa0','')
                        internal[testnum][cols[0].text.replace('\xa0','')]["Percentage"]=cols[2].text.replace('\xa0','')
                        internal[testnum][cols[0].text.replace('\xa0','')]["Class Average"]=cols[3].text.replace('\xa0','')
                        internal[testnum][cols[0].text.replace('\xa0','')]["Max Marks"]=cols[4].text.replace('\xa0','')


    return jsonify({'status':'OK','internalMarks':internal})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'status':'Not found','error': 'Cannot find requested endpoint'}), 404)

  
if __name__=='__main__':
    app.run(debug=True)
