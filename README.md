# AlexaMiniWorkout

<img src="https://github.com/ALLIESXO/AlexaMiniWorkout/blob/master/alexa.PNG" width="350">

#### Alexa Home Workout App - Work on your body with the help of alexa 

## How to setup all components on Raspberry Pi 
Components used:
* Node-RED for the Telegram Chat Bot
* Serveo to expose the Alexa Skill
* SQLite as Database 
* Amazon Alexa Web Development Console

### Serveo 
Exposes service to the internet using ssh.  
No need to install, just use following command: `ssh -R <subdomain>:80:<IP>:<Port> serveo.net`  
For example `ssh -R AlexaHomeWorkout:80:localhost:5050 serveo.net`

Find more information: www.serveo.net

### Node-RED for Raspberry PI 
Run following commands:  

1. `curl -sL https://raw.githubusercontent.com/node-red/raspbian-deb-package/master/resources/update-nodejs-and-nodered > "installNodeRed.sh"`

2. `chmod +x installNodeRed.sh`  

3. `./installNodeRed.sh` + follow instructions  

(opt. 4.) If you want to open the port of the raspi then run following commands:  
`sudo iptables -N HTTP_NODE_RED` and `sudo iptables -A HTTP_NODE_RED -p tcp --dport 1880 -j ACCEPT`  
Then you should be able to access the Node-RED website within the home network via IP_of_RPi:1880  
If the port does not work you can always check the NODE-Red daemon for logs. (`sudo systemctl status nodered.service`)  
 
The next step is to install via the node-red interface (Settings -> manage pallets) the node-red-contrib-telegrambot module.    
Now we are done and can implement our telegram chatbot.   
Find more information about Node-RED: www.nodered.org

### Install SQLite DB on Raspberry 
`sudo apt-get install sqlite3`
Then SQLite shall be ready to go.  
For detailed information: www.sqlite.org

