# AlexaMiniWorkout

<img src="https://github.com/ALLIESXO/AlexaMiniWorkout/blob/master/alexa-logo.png" width="300">

### Alexa Home Workout App - Work on your body with the help of alexa 

To use this skill you will need Python2.7, SQLite, Serveo, Wit.ai and Watson Tone Analyzer + Translator of the IBM Cloud.  

We used third party services to maximize the potential of an alexa skill. Therefor we could not use the Alexas own intent recognition and were forced to used the free alternative 'Wit.ai'.  

To workaround the official alexas intent you need to create an intent which is based on name slots and taking {any} spoken text. Then Alexa will not recognize any intent and give the spoken text directly trough the json value. 

#### The goal was to make the alexa skill 'smarter' than usual with following features: 
* Mood Predicition -> leading to an training adjustment. 
* Long Term Memory -> to adjust and improve the training quality for the user. 
* Feedback capability -> changing intensities to individual training programs or specific exercises.
* Consideration of training time -> Alexa knows after a while at what time you can give the most. 
* ... 

### IBM Cloud 
Watson Tone Analyzer and Translator are free to use to a specific usage limit. 
More Info: [IBM CLOUD](https://www.ibm.com/cloud)

### Flask-Ask 
For running the application flask-ask is used. 
Find more: [Flask Ask](https://github.com/johnwheeler/flask-ask)

### SQLite
[SQLite](https://www.sqlite.org/index.html)

### Wit.ai 
[Wit.ai](https://wit.ai/)

### Serveo 
Exposes service to the internet using ssh.  
No need to install, just use following command: `ssh -R <subdomain>:80:<IP>:<Port> serveo.net`  
For example `ssh -R AlexaHomeWorkout:80:localhost:5050 serveo.net`

Find more information: [Serveo](www.serveo.net)
