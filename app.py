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
        attendict={}
        for i in subjects: 
            for j in range(1,len(subjects)):
                s=i.find_all('td')
                if s == []:
                    continue
                # print(s[1].string)
                attendict[j]={}
                attendict[j]['Name']=s[1].string
                attendict[j]['Hours Attended']=s[2].string
                attendict[j]['Total Hours']=s[3].string
                attendict[j]['Attendence Percentage']=s[4].string


    return jsonify({'subject':attendict})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

  
if __name__=='__main__':
    app.run(debug=True)