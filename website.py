from flask import Flask, render_template, request
import random
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app._static_folder = 'static'

def scrape_cricinfo_news():
    url = "https://www.espncricinfo.com/cricket-news"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_articles = []

        # Extract news articles from the HTML
        for article in soup.find_all('div', class_='ds-border-b ds-border-line ds-p-4'):
            news_title = article.find('h2', class_='ds-text-title-s ds-font-bold ds-text-typo').text.strip()
            news_link = article.find('a', class_='')['href']
            news_articles.append({'title': news_title, 'link': news_link})

        return news_articles

    return None

def send_email(news_articles):
    # Set up your email configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'joe.piekos@gmail.com'
    smtp_password = 'iduo stcc hpsb zhvc'
    recipient_email = 'joe.piekos@gmail.com'

    # Create the email content
    subject = 'Daily Cricket News'
    body = '\n'.join([f"{article['title']} - https://www.espncricinfo.com{article['link']}" for article in news_articles])
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_username
    msg['To'] = recipient_email

    # Connect to the SMTP server and send the email
    #with smtplib.SMTP(smtp_server, smtp_port) as server:
     #   server.starttls()
      #  server.login(smtp_username, smtp_password)
       # server.sendmail(smtp_username, recipient_email, msg.as_string())
    
    with smtplib.SMTP(smtp_server, smtp_port) as mail_server:
        # identify ourselves to smtp gmail client
        mail_server.ehlo()
        # secure our email with tls encryption
        mail_server.starttls()
        # re-identify ourselves as an encrypted connection
        mail_server.ehlo()
        mail_server.login(smtp_username, smtp_password)
        mail_server.sendmail(smtp_username,recipient_email,msg.as_string())

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

#@app.route('/get_daily_news', methods=['POST'])
#def get_daily_news():
#    # Scrape daily news articles
#    news_articles = scrape_cricinfo_news()
#    bethanMessage = ""
#    if news_articles:
#        # Send the news articles via email
#        send_email(news_articles)
#        return render_template('index.html', message='Daily news articles sent to your email!', status = news_articles[0]['link'])
#    else:
#        return render_template('index.html', message='Failed to fetch news articles.',bethanMessage = bethanMessage)
    
@app.route('/find_match', methods=['POST'])
def find_match():
    date = request.form['date']
    team1 = request.form['team1']
    team2 = request.form['team2']
    match_url = find_match_url(date, team1, team2)
    return render_template('result.html', match_url=match_url)

@app.route('/find_database_info', methods=['POST'])
def find_datetime():
    id_number = request.form['id_number']

    # Construct the URL using the user-supplied ID number
    url = f"http://cricket.prod.qws.smartodds.co.uk/admin/core/game/{id_number}/change/"

    # Extract the value from the id_start_datetime_0 element
    start_datetime, before_vs, after_vs = get_database_info(url)

    return render_template('result.html', id_number=id_number, team1=before_vs, team2=after_vs, start_datetime=start_datetime)

def get_database_info(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        start_datetime = soup.find(name='start_datetime_0').get('value')
        teams = soup.find(name='name').get('value')
        parts = input_string.split("vs", 1)

        before_vs = parts[0].strip()  # Strip to remove any leading/trailing whitespaces
        after_vs = parts[1].strip()  # Strip to remove any leading/trailing whitespaces

        return start_datetime, before_vs, after_vs
    return None

def get_daily_news_daily():
    news_articles = scrape_cricinfo_news()
    send_email(news_articles)

def get_match_url(date):
    return f"https://www.espncricinfo.com/ci/engine/match/index.html?date={date};view=week"

def find_match_url(date, team1, team2):
    match_url = get_match_url(date)
    response = requests.get(match_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        match_blocks = soup.find_all('section', class_='default-match-block')
        for block in match_blocks:
            innings_info_1 = block.find('div', class_='innings-info-1').get_text().strip()
            innings_info_2 = block.find('div', class_='innings-info-2').get_text().strip()
            if (team1.lower() in innings_info_1.lower() and team2.lower() in innings_info_2.lower()) or (team2.lower() in innings_info_1.lower() and team1.lower() in innings_info_2.lower()):
                match_no = block.find('span', class_='match-no').find('a')['href']
                return match_no
    return None


if __name__ == '__main__':
    app.run(debug=True)
    #tst = scrape_cricinfo_news()
    #print(tst[0]['title'])