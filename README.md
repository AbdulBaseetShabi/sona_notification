# sona_notification
## Table of Content 
 - [About](#about)
 - [Inspiration](#inspiration)
 - [Technologies](#technologies) 
 - [Usage](#usage)

### About
---
An automation script used by 30+ students to get notification about new studies available on the Sona Website. Each study done is worth a certain bonus percentage.

### Inspiration
---
This script was created due to the lack of a notification feature on the Sona Website (a website to do research studies). Students do this studies for cash and grade benefits. Without a notification system, students have to constantly check and guess when a new study is available to be done.

### Technologies
---
The script was written in ***Python***, uses ***MongoDB*** to store its data and is deployed on ***Heroku***

### Usage
---
- General 
  ```sh
  git clone https://github.com/AbdulBaseetShabi/sona_notification
  ```
- Steps 
  - Please be advised to use a private repository 
  - Create a folder called ***secrets***
  - Under ***secrets*** 
    - Create a file called ***credentials.txt*** 
    - Create a file called ***mailinglist.txt*** 
  - Create a MongoDB account 
    - Create a database in that account 
    - Create 2 collections in the database
    - Go to security and create a user with read-write access to the database you created above
  - ***credentials.txt*** 
    - line 1 is the sona username 
    - line 2 is the sona password 
    - line 3 is the Gmail account you want to use to send the email 
    - line 4 is the Gmail account password
      - NOTE: you would have to reduce the security for the account 
    - line 5 is the username of the MongoDB user you created to have the read-write access
    - line 6 is the password for that user 
    - line 7 is the name of the database
    - line 8 is the name of the first collection 
    - line 9 is the name of the second collection
  - ***mailinglist.txt**
    - put the email to send the notifications to 
    - if there are multiple put each email on a new line
  - Create a Heroku account and deploy code there as a cron job
