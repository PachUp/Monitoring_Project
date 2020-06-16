# Monitoring_Project

configuration values:  
os.environ["HEROKU_POSTGRESQL_PINK_URL"] - The URI for the database  
os.environ["SECRET_KEY_ENV"] - the keyword for the encryption of the cookies  
os.environ["REDIS_URL"] - Redis's database URL  
os.environ["MAIL_USERNAME"] - The mail you want your verification mail to be sent to the users  
os.environ["MAIL_PASSWORD"] - the mail's password  
os.environ["AWS_ACCESS_KEY_ID"] - AWS's acces key  
os.environ["AWS_SECRET_ACCESS_KEY"] - AWS's secret key  
os.environ["S3_BUCKET"] - S3 bucket's name  
  
For admin on the site:  
username: user  
password: user123  
  
To run the server on localhost:  
• put your own configuration values  
• client URL needs to be changed to your localhost URL  
• change all the links in the HTML pages from http://admin-monitor.herokuapp.com/... to your localhost(127.0.0.1/...).  
• ofcourse, download all the libraries
