
A Simple Flask API to scrape data from our college student portal [linways tkmce](https://tkmce.linways.com).This API can be used for your projects to create bots,mobile applications etc.However this is not the official one.This was done for development purposes only.

## Endpoints

#### Home `/` `Request method=POST`
  - Send a `POST` request with the **json body** `{"Username":"ADMNO","Pass":"SOMEPASS"}` to perform login</br>
    eg: `{"Username":"181234","Pass":"181234"}` </br>
    Sample response:
    ```{
        "studendata":{
                    "Name":Romero, 
                    "Batch": "EEE2018, S4"
                    },
         "status":"OK"
#### Attendance `/attendance`
  - View the subject wise attendance details for the current semester
#### Total Attendance `/attendance/all`
  - View the total attendance for the entire sem.
#### Assignment `/assignment/sem=<sem>`
  - View the assignment evaluation details of the specified semester <sem>  
    eg: `assignment/sem=4`
#### Internals `/internal/sem=<sem>`
  - View the Internals evaluation details of the specified semester <sem>  
    eg: `internal/sem=4`
#### Notifications `/notify`
  - View notifications of new assignments,Note and quizess etc.
    


## Development

#### Clone the repo : 

`git clone https://github.com/mdb571/n00b-api.git`

#### Install dependencies :

`pip install -r requirements.txt`

#### Run server

`flask run`

## Contribution
 
 Feel free to open a pull request if you feel you can improve this project and add more functionalities
 
Give a ⭐ if this project helped you ❤️

<a href="https://github.com/mdb571/n00b-api/blob/master/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="LICENSE" />
  </a>
  
