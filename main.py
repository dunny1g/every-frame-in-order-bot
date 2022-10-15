from time import sleep
from datetime import timedelta
import socket
import os
import sys
import logging
import json
import traceback
import tweepy
from discord_webhook import DiscordWebhook

#Store the working directory
dir = os.path.abspath(os.path.dirname(__file__))

#Begin logging
logging.basicConfig(filename="{dir}/log.txt".format(dir=dir), level=logging.INFO)

print("Every Frame In Order Twitter Bot\n")
logging.info("Every Frame In Order Twitter Bot\n")

#Set frame directory name and check it exists, if not create it
frame_dir = "frames"
check_frame_dir = os.path.isdir("{dir}/{frame_dir}".format(dir=dir, frame_dir=frame_dir))
if not check_frame_dir:
    os.makedirs("{dir}/{frame_dir}".format(dir=dir, frame_dir=frame_dir))
    print("Created frame folder: {dir}/{frame_dir} \n".format(dir=dir, frame_dir=frame_dir))
    logging.info("Created frame folder: {dir}/{frame_dir} \n".format(dir=dir, frame_dir=frame_dir))

#Load configuration from file
config_file = 'config.json'
config_path = '{dir}/{config_file}'.format(dir=dir, config_file=config_file)
config_data = {
    'api_key': 'YOUR_TWITTER_API_KEY_HERE',  # Twitter API Key
    'api_secret': 'YOUR_TWITTER_API_SECRET_HERE',  # Twitter API Secret
    'access_token': 'YOUR_TWITTER_ACCESS_TOKEN_HERE',  # Twitter API Access Token
    'access_secret': 'YOUR_TWITTER_ACCESS_SECRET_HERE',  # Twitter API Access Secret
    'webhookURL': 'YOUR_DISCORD_WEBHOOK_URL_HERE', # Discord Webhook URL for alerts
    'userID': 'YOUR_DISCORD_USER_ID_HERE', # Discord user ID so the bot knows who to tag, read GitHub README to find your ID
    'showName': 'NAME OF TV SHOW HERE', # Name of TV Show for use in tweet text
    'enableEPname': '0', # Includes episode name in frame tweets if enabled, read GitHub README for more info
    'tweetDelay': '180', # Number of seconds between each tweet
    'currentEPnum': '1', # Current episode number, will be updated by bot
    'currentEP': '', # Current season and episode in plain text, will be updated by bot
    'currentFrame': '1', # Current frame, will be updated by bot
}

def load_config():
    global config_path, config_data
    try:
        #Try to load config data from file
        with open(config_path) as f:
            config_data = json.load(f)
    except ValueError:
        #If config file exists but it's malformed, add a flag
        config_data['malformed'] = True
    except Exception:
        #If config file doesn't exist, create it and exit bot
        with open(config_path, 'w') as f:
            f.write(json.dumps(config_data, indent=4, sort_keys=False))
            print("Please configure config located at {config_path}".format(config_path=config_path))
            logging.info("Please configure config located at {config_path}".format(config_path=config_path))
            sys.exit(1)

    #Check file for if any fields are missing, if so add malformed flag
    if any(item not in config_data for item in ['api_key', 'api_secret', 'access_token', 'access_secret', 'webhookURL', 'userID', 'showName', 'enableEPname', 'tweetDelay', 'currentEPnum', 'currentEP', 'currentFrame']):
        config_data['malformed'] = True

load_config()

#Twitter access tokens
api_key = config_data['api_key']
api_secret = config_data['api_secret']
access_token = config_data['access_token']
access_secret = config_data['access_secret']

#Authenticating with Twitter
auth = tweepy.OAuth1UserHandler(api_key,api_secret,access_token,access_secret) 
api = tweepy.API(auth, wait_on_rate_limit=True, retry_count=3, retry_delay=60, retry_errors=set([503]))
client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)

#Discord webhook for alerts
webhookURL = config_data['webhookURL']
userID = config_data['userID']

#TV show name
showName = config_data['showName']
print("TV Show:", showName)
logging.info("TV Show: {showName}".format(showName=showName))

#Episode name in tweets
enableEPname = int(config_data['enableEPname'])

#Number of seconds between tweets
tweetDelay = int(config_data['tweetDelay'])

#Store number of all episodes, current episode and then place in season_slash_episode which can be used to pull the current Season and Episode
#Also used to find episode name
filer1 = open("{dir}/allEPs.txt".format(dir=dir),"r")
allEPs = filer1.readlines()
allEPs_lines = len(allEPs)
filer1.close()
if enableEPname == 1:
    filer2 = open("{dir}/EPnames.txt".format(dir=dir),"r")
    EPnamer = filer2.readlines()
currentEPnum = int(config_data['currentEPnum'])
totalEPs = allEPs_lines - 1
print("Total episodes:", totalEPs)
logging.info("Total episodes: {totalEPs}".format(totalEPs=totalEPs))

#Time remaining conversion from seconds
def get_time_remaining(sec):
    #Create timedelta and convert to string
    timedelta_str = str(timedelta(seconds=sec))
    #Split string into individual component
    x = timedelta_str.split(':')
    dh = x[0]
    m = x[1]
    s = x[2]
    print("Frames remaining in episode: {remainingFrames} - Time remaining: {dh} hours {m} minutes {s} seconds".format(remainingFrames=remainingFrames, dh=dh, m=m, s=s))
    logging.info("Frames remaining in episode: {remainingFrames} - Time remaining: {dh} hours {m} minutes {s} seconds".format(remainingFrames=remainingFrames, dh=dh, m=m, s=s))

#Store traceback exception and print to console and log
def print_error():
    error = traceback.format_exc()
    print(error)
    logging.exception("An exception was thrown and the bot might have stopped posting!")
    print("An error has occurred and the bot might have stopped posting!")

#Discord webhook to inform about error, second message can fail if error is longer than maximum Discord message character count of 2000
def send_discord_webhook():
    webhook = DiscordWebhook(url=webhookURL, content='<@{userID}> An error has occurred with the Twitter bot and it might have stopped posting!'.format(userID=userID))
    response = webhook.execute()
    sleep(2)
    error = traceback.format_exc()
    webhook = DiscordWebhook(url=webhookURL, content='{error}'.format(error=error))
    response = webhook.execute()
    sleep(2)
    webhook = DiscordWebhook(url=webhookURL, content='Error occurred on frame: {currentFrame}'.format(currentFrame=currentFrame))
    response = webhook.execute()

for j in range (currentEPnum, allEPs_lines):
    while True:
        try:
            #Writes season_episode and EPname for use in tweet text
            temp_season_slash_episode = allEPs[currentEPnum-1]
            season_slash_episode = temp_season_slash_episode.replace("\n", "")
            season_episode = season_slash_episode.replace("/", " ")
            if enableEPname == 1:
                tempEPname = EPnamer[currentEPnum-1]
                EPname = tempEPname.replace("\n", "")
                print('Current episode: {currentEPnum} - {season_episode} "{EPname}"'.format(currentEPnum=currentEPnum, season_episode=season_episode, EPname=EPname))
                logging.info('Current episode: {currentEPnum} - {season_episode} "{EPname}"'.format(currentEPnum=currentEPnum, season_episode=season_episode, EPname=EPname))
            else:
                print('Current episode: {currentEPnum} - {season_episode}'.format(currentEPnum=currentEPnum, season_episode=season_episode))
                logging.info('Current episode: {currentEPnum} - {season_episode}'.format(currentEPnum=currentEPnum, season_episode=season_episode))
            
            #Next episode variable
            temp_nextEP = allEPs[currentEPnum]
            nextEP_slash = temp_nextEP.replace("\n", "")
            nextEP = nextEP_slash.replace("/", " ")
            if enableEPname == 1:
                temp_nextEPname = EPnamer[currentEPnum]
                nextEPname = temp_nextEPname.replace("\n", "")
                print('Next episode: {nextEP} "{nextEPname}"'.format(nextEP=nextEP, nextEPname=nextEPname))
                logging.info('Next episode: {nextEP} "{nextEPname}"'.format(nextEP=nextEP, nextEPname=nextEPname))
            else:
                print('Next episode: {nextEP}'.format(nextEP=nextEP))
                logging.info('Next episode: {nextEP}'.format(nextEP=nextEP))
    
            #Counts number of frames in folder and store it in a variable
            frame_path = "{dir}/{frame_dir}/{season_slash_episode}".format(dir=dir, frame_dir=frame_dir, season_slash_episode=season_slash_episode)
            totalFrames = int(0)
            for path in os.listdir(frame_path):
                if os.path.isfile(os.path.join(frame_path, path)):
                    totalFrames += 1
            print('Total number of frames:', totalFrames)
            logging.info("Total number of frames: {totalFrames}".format(totalFrames=totalFrames))

            #Resume from current frame
            currentFrame = int(config_data['currentFrame'])
            print("Current frame: ", currentFrame, "\n")
            logging.info("Current frame: {currentFrame}".format(currentFrame=currentFrame))

            for i in range (currentFrame, totalFrames+1):
                while True:
                    try:
                        #Path to image that will be uploaded
                        image_path = ("{frame_path}/frame-{i}.jpg".format(frame_path=frame_path, i=i))
                        
                        #Uploading image of frame to Twitter
                        print("Uploading image of frame {i} to Twitter".format(i=i))
                        media = api.media_upload(image_path)
                        sleep(1)
                        
                        #Tweet text
                        if enableEPname == 1:
                            full_tweet = '{showName} - {season_episode} "{EPname}" - Frame {i} out of {totalFrames}'.format(showName=showName, season_episode=season_episode, EPname=EPname, i=i, totalFrames=totalFrames)
                        else:
                            full_tweet = '{showName} - {season_episode} - Frame {i} out of {totalFrames}'.format(showName=showName, season_episode=season_episode, i=i, totalFrames=totalFrames)
                        
                        #Send tweet with uploaded image and text
                        print("Sending tweet with frame {i} out of {totalFrames}".format(i=i, totalFrames=totalFrames))
                        logging.info("Sending tweet with frame {i} out of {totalFrames}".format(i=i, totalFrames=totalFrames))
                        client.create_tweet(text=full_tweet, media_ids=[media.media_id])
                        
                        #Calculate remaining frames left in episode
                        remainingFrames = totalFrames - currentFrame
                        
                        #Save current frame progress to config
                        print("Saving progress to config")
                        currentFrame = i + 1
                        config_data['currentFrame'] = '{currentFrame}'.format(currentFrame=currentFrame)
                        with open(config_path, 'w') as f:
                            f.write(json.dumps(config_data, indent=4, sort_keys=False))
                        
                        #Calculate total seconds left until the episode finishes so it can be used in the conversion defined above
                        secondsleft = remainingFrames * tweetDelay
                        get_time_remaining(secondsleft)
                        
                        #If statement to inform through Discord that the episode has ended and that the next episode is about to start
                        if remainingFrames == 0:
                            print("The bot has reached the end of {season_episode}".format(season_episode=season_episode))
                            logging.info("The bot has reached the end of {season_episode}".format(season_episode=season_episode))
                            if enableEPname == 1:
                                webhook = DiscordWebhook(url=webhookURL, content='<@{userID}> The bot has reached the end of {season_episode}. Next episode: {nextEP} "{nextEPname}"'.format(userID=userID, season_episode=season_episode, nextEP=nextEP, nextEPname=nextEPname))
                                response = webhook.execute()
                            else:
                                webhook = DiscordWebhook(url=webhookURL, content='<@{userID}> The bot has reached the end of {season_episode}. Next episode: {nextEP}'.format(userID=userID, season_episode=season_episode, nextEP=nextEP))
                                response = webhook.execute()
                        
                        #Sleep for specified time before posting next frame
                        sleep(tweetDelay)
                    #Twitter API error handling
                    except tweepy.errors.TwitterServerError as tweepyServerError:
                        #Twitter API likes to spam 503 Service Unavailable when everytime but one time I've checked, the tweet was posted successfully which causes a double post when the cycle continues
                        #This if statement prevents double posts by restarting the bot after saving frame progress but could miss frames if the tweet wasn't posted. Personally I'll tolerate one missed frame over 50 double posts.
                        if tweepyServerError.response.status_code == 503:
                            logging.exception('Twitter API: 503 Service Unavailable on frame {currentFrame}'.format(currentFrame=currentFrame))
                            print('Twitter API: 503 Service Unavailable on frame {currentFrame}'.format(currentFrame=currentFrame))
                            
                            #Discord webhook to inform about 503 error, intentionally doesn't tag user as it happens multiple times a day for me
                            webhook = DiscordWebhook(url=webhookURL, content='Twitter API: 503 Service Unavailable on frame {currentFrame}'.format(currentFrame=currentFrame))
                            response = webhook.execute()
                            
                            #Continuation of after frame posting cycle
                            #Calculate remaining frames left in episode
                            remainingFrames = totalFrames - currentFrame
                        
                            #Save current frame progress to config
                            print("Saving progress to config")
                            currentFrame = i + 1
                            config_data['currentFrame'] = '{currentFrame}'.format(currentFrame=currentFrame)
                            with open(config_path, 'w') as f:
                                f.write(json.dumps(config_data, indent=4, sort_keys=False))
                        
                            #Calculate total seconds left until the episode finishes so it can be used in the conversion defined above
                            secondsleft = remainingFrames * tweetDelay
                            get_time_remaining(secondsleft)
                        
                            #If statement to inform through Discord that the episode has ended during a 503 error which could be problematic, unlikely to occur at the same time as a 503 error but possible
                            if remainingFrames == 0:
                                print("The bot has reached the end of {season_episode}".format(season_episode=season_episode))
                                logging.info("The bot has reached the end of {season_episode}".format(season_episode=season_episode))
                                sleep(2)
                                if enableEPname == 1:
                                    webhook = DiscordWebhook(url=webhookURL, content='<@{userID}> The bot has reached the end of {season_episode}. Next episode: {nextEP} "{nextEPname}". This occurred during a Twitter API 503 error'.format(userID=userID, season_episode=season_episode, nextEP=nextEP, nextEPname=nextEPname))
                                    response = webhook.execute()
                                else:
                                    webhook = DiscordWebhook(url=webhookURL, content='<@{userID}> The bot has reached the end of {season_episode}. Next episode: {nextEP}. This occurred during a Twitter API 503 error'.format(userID=userID, season_episode=season_episode, nextEP=nextEP))
                                    response = webhook.execute()
                                sleep(tweetDelay)
                                continue
                            
                            #Sleep for specified time before posting next frame
                            sleep(tweetDelay)
                            
                            #Restart script after 503 error
                            print("Restarting bot to resolve Twitter API: 503 error...")
                            logging.info("Restarting bot to resolve Twitter API: 503 error...")
                            os.execv(sys.executable, ['python3'] + sys.argv)
                        #Store traceback exception and print to console and log
                        print_error()
                        
                        #Discord webhook to inform about error, second message can fail if error is longer than maximum Discord message character count of 2000
                        send_discord_webhook()
                        
                        #Sleep for specified time before retrying
                        sleep(tweetDelay)
                        continue
                    #Connection lost handling
                    except socket.gaierror:
                        #Store traceback exception and print to console and log
                        print_error()
                        
                        #Sleep for specified time before retrying
                        sleep(tweetDelay)
                        
                        #Discord webhook to inform about error, will fail if connection is still down which is why we run this after the sleep period
                        webhook = DiscordWebhook(url=webhookURL, content='<@{userID}> socket.gaierror exception has occurred with the Twitter bot and it might have stopped posting! Current frame: {currentFrame}'.format(userID=userID, currentFrame=currentFrame))
                        response = webhook.execute()
                        continue
                    #General error handling
                    except Exception:
                        #Store traceback exception and print to console and log
                        print_error()
                        
                        #Discord webhook to inform about error, second message can fail if error is longer than maximum Discord message character count of 2000
                        send_discord_webhook()
                        
                        #Sleep for specified time before retrying
                        sleep(tweetDelay)
                        continue
                    else:
                        break

            #Reset currentFrame to 1 for next episode
            currentFrame = 1
            config_data['currentFrame'] = '{currentFrame}'.format(currentFrame=currentFrame)
            with open(config_path, 'w') as f:
                f.write(json.dumps(config_data, indent=4, sort_keys=False))
            
            #Add 1 to current episode number and save it
            currentEPnum = j + 1
            config_data['currentEPnum'] = '{currentEPnum}'.format(currentEPnum=currentEPnum)
            with open(config_path, 'w') as f:
                f.write(json.dumps(config_data, indent=4, sort_keys=False))
            
            #Writes next season_episode for use in tweet text and saves it
            temp_season_slash_episode = allEPs[currentEPnum-1]
            season_slash_episode = temp_season_slash_episode.replace("\n", "")
            season_episode = season_slash_episode.replace("/", " ")
            config_data['currentEP'] = '{season_episode}'.format(season_episode=season_episode)
            with open(config_path, 'w') as f:
                f.write(json.dumps(config_data, indent=4, sort_keys=False))
        except Exception:
            #Store traceback exception and print to console and log
            print_error()
            
            #Discord webhook to inform about error, second message can fail if error is longer than maximum Discord message character count of 2000
            send_discord_webhook()
            
            #Sleep for specified time before retrying
            sleep(tweetDelay)
            continue
        else:
            break

#Store traceback exception and print to console and log
error = traceback.format_exc()
print(error)
logging.exception("If you are reading this then the bot has likely finished, if so congrats! if not an error occurred.")
print("If you are reading this then the bot has likely finished, if so congrats! if not an error occurred.")

#Discord webhook to inform either about bot completion or error, second message can fail if error is longer than maximum Discord message character count of 2000
webhook = DiscordWebhook(url=webhookURL, content='<@{userID}> If you are reading this then the bot has likely finished, if so congrats! if not an error occurred.'.format(userID=userID))
response = webhook.execute()
sleep(2)
webhook = DiscordWebhook(url=webhookURL, content='{error}'.format(error=error))
response = webhook.execute()

#Terminate script
sys.exit(1)