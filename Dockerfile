FROM python:3.9-slim 
 
    ffmpeg  
 
WORKDIR /app 
 
COPY . /app 
 
RUN python -m venv /opt/venv  
Collecting python-telegram-bot==13.5 (from -r requirements.txt (line 1))
  Downloading python_telegram_bot-13.5-py3-none-any.whl.metadata (11 kB)
Requirement already satisfied: yt-dlp in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 2)) (2025.1.12)
Requirement already satisfied: requests in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 3)) (2.32.3)
Requirement already satisfied: google-auth in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 4)) (2.37.0)
Requirement already satisfied: google-auth-oauthlib in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 5)) (1.2.1)
Requirement already satisfied: google-auth-httplib2 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 6)) (0.2.0)
Requirement already satisfied: google-api-python-client in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 7)) (2.159.0)
Requirement already satisfied: python-dotenv in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 8)) (1.0.0)
Requirement already satisfied: pyTelegramBotAPI in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from -r requirements.txt (line 9)) (4.23.0)
Requirement already satisfied: certifi in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from python-telegram-bot==13.5->-r requirements.txt (line 1)) (2024.12.14)
Requirement already satisfied: tornado>=5.1 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from python-telegram-bot==13.5->-r requirements.txt (line 1)) (6.4.1)
Collecting APScheduler==3.6.3 (from python-telegram-bot==13.5->-r requirements.txt (line 1))
  Downloading APScheduler-3.6.3-py2.py3-none-any.whl.metadata (5.4 kB)
Requirement already satisfied: pytz>=2018.6 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from python-telegram-bot==13.5->-r requirements.txt (line 1)) (2024.2)
Requirement already satisfied: setuptools>=0.7 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from APScheduler==3.6.3->python-telegram-bot==13.5->-r requirements.txt (line 1)) (75.7.0)
Requirement already satisfied: six>=1.4.0 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from APScheduler==3.6.3->python-telegram-bot==13.5->-r requirements.txt (line 1)) (1.16.0)
Requirement already satisfied: tzlocal>=1.2 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from APScheduler==3.6.3->python-telegram-bot==13.5->-r requirements.txt (line 1)) (5.2)
Requirement already satisfied: charset-normalizer<4,>=2 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from requests->-r requirements.txt (line 3)) (3.3.2)
Requirement already satisfied: idna<4,>=2.5 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from requests->-r requirements.txt (line 3)) (2.10)
Requirement already satisfied: urllib3<3,>=1.21.1 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from requests->-r requirements.txt (line 3)) (1.26.20)
Requirement already satisfied: cachetools<6.0,>=2.0.0 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from google-auth->-r requirements.txt (line 4)) (4.2.2)
Requirement already satisfied: pyasn1-modules>=0.2.1 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from google-auth->-r requirements.txt (line 4)) (0.4.1)
Requirement already satisfied: rsa<5,>=3.1.4 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from google-auth->-r requirements.txt (line 4)) (4.9)
Requirement already satisfied: requests-oauthlib>=0.7.0 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from google-auth-oauthlib->-r requirements.txt (line 5)) (2.0.0)
Requirement already satisfied: httplib2>=0.19.0 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from google-auth-httplib2->-r requirements.txt (line 6)) (0.22.0)
Requirement already satisfied: google-api-core!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.0,<3.0.0.dev0,>=1.31.5 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from google-api-python-client->-r requirements.txt (line 7)) (2.24.0)
Requirement already satisfied: uritemplate<5,>=3.0.1 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from google-api-python-client->-r requirements.txt (line 7)) (4.1.1)
Requirement already satisfied: googleapis-common-protos<2.0.dev0,>=1.56.2 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from google-api-core!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.0,<3.0.0.dev0,>=1.31.5->google-api-python-client->-r requirements.txt (line 7)) (1.66.0)
Requirement already satisfied: protobuf!=3.20.0,!=3.20.1,!=4.21.0,!=4.21.1,!=4.21.2,!=4.21.3,!=4.21.4,!=4.21.5,<6.0.0.dev0,>=3.19.5 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from google-api-core!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.0,<3.0.0.dev0,>=1.31.5->google-api-python-client->-r requirements.txt (line 7)) (4.25.5)
Requirement already satisfied: proto-plus<2.0.0dev,>=1.22.3 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from google-api-core!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.0,<3.0.0.dev0,>=1.31.5->google-api-python-client->-r requirements.txt (line 7)) (1.25.0)
Requirement already satisfied: pyparsing!=3.0.0,!=3.0.1,!=3.0.2,!=3.0.3,<4,>=2.4.2 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from httplib2>=0.19.0->google-auth-httplib2->-r requirements.txt (line 6)) (3.2.0)
Requirement already satisfied: pyasn1<0.7.0,>=0.4.6 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from pyasn1-modules>=0.2.1->google-auth->-r requirements.txt (line 4)) (0.6.1)
Requirement already satisfied: oauthlib>=3.0.0 in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from requests-oauthlib>=0.7.0->google-auth-oauthlib->-r requirements.txt (line 5)) (3.2.2)
Requirement already satisfied: tzdata in c:\users\amanf\appdata\local\programs\python\python312\lib\site-packages (from tzlocal>=1.2->APScheduler==3.6.3->python-telegram-bot==13.5->-r requirements.txt (line 1)) (2024.2)
Downloading python_telegram_bot-13.5-py3-none-any.whl (455 kB)
Downloading APScheduler-3.6.3-py2.py3-none-any.whl (58 kB)
Installing collected packages: APScheduler, python-telegram-bot
  Attempting uninstall: APScheduler
    Found existing installation: APScheduler 3.11.0
    Uninstalling APScheduler-3.11.0:
      Successfully uninstalled APScheduler-3.11.0
  Attempting uninstall: python-telegram-bot
    Found existing installation: python-telegram-bot 21.10
    Uninstalling python-telegram-bot-21.10:
      Successfully uninstalled python-telegram-bot-21.10
Successfully installed APScheduler-3.6.3 python-telegram-bot-13.5
 
ENV PATH="/opt/venv/bin:$PATH" 
 
CMD ["python", "yt.py"] 
