from flask import Flask,jsonify
from flask import make_response
import requests,getpass,bs4
app=Flask(__name__)

payload={
    'studentAccount':'180051',
    'studentPassword':'180051'
}

url='https://tkmce.linways.com/student/'
home_url=url+ 'student.php?menu=home'
attendence_url='https://tkmce.linways.com/student/attendance/ajax/ajax_subjectwise_attendance.php?action=GET_REPORT'
assignment_url='https://tkmce.linways.com/student/asimark/ajax_assignment_mark.php'

studentdata={}

@app.route('/',methods=['GET'])
def home():
    with requests.Session() as session:
        post = session.post(url, data=payload)
        r = session.get(home_url)
    soup=bs4.BeautifulSoup(r.text,'html')
    
   
    studentdata['Name']=soup.select('.truncate')[0].getText()

    studentdata['Batch']=soup.select('.panel-heading')[1].getText()

    return jsonify({'studentdata':studentdata})

@app.route('/attendance',methods=['GET'])
def attendance():
    with requests.Session() as session:
        post = session.post(url, data=payload)
        r = session.get(attendence_url)
 
        soup=bs4.BeautifulSoup(r.text,'lxml')


        table1 = soup.find("table")
        body=table1.find("tbody")
        subjects = soup.find_all('tr')
        subjects.pop(-1)
        attendict={}
        j=0
        for i in subjects: 
            j+=1
            attendict[j]={}
            s=i.find_all('td')
            if s == []:
                continue
            attendict[j]["Name"]=str(s[1].string).replace('\\n                    ','')
            attendict[j]['Hours Attended']=s[2].string
            attendict[j]['Total Hours']=s[3].string
            attendict[j]['Attendence Percentage']=s[4].string

    return jsonify({'subject':attendict})

@app.route('/assignment',methods=['GET'])
def assignment():
    assignmentdict={}
    with requests.Session() as session:
        post = session.post(url, data=payload)
        r = session.post(assignment_url,data={"semID":4})
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

    return jsonify({'assignmentMarks':assignmentdict})        

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

  
if __name__=='__main__':
    app.run(debug=True)