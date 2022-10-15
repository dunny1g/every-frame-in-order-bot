# Every Frame In Order Twitter Bot

A Python bot to post every frame of a TV show in order to Twitter with a set interval between tweets.

I would like to thank [Every SpongeBob Frame In Order](https://twitter.com/SbFramesInOrder) for the inspiration.

# Requirements

- Computer that will run 24/7 - I run this bot through Linux and even though I briefly tested it on Windows, I can't guarantee long-term Windows compatibility
- Frames from your chosen TV show in `jpg` format - I recommend [ffmpeg](https://ffmpeg.org/) to extract frames from episodes
- `tweepy` installed with pip - `pip install -U tweepy`
- `discord-webhook` installed with pip - `pip install -U discord-webhook` 
- Twitter account signed up on the Twitter Developer Portal with generated API key and secret, access token and secret with write permissions
- Discord account with admin privileges to a server to [create a webhook to receive bot error notifications](https://support.discord.com/hc/en-us/articles/228383668)

# How to use

1. Download `main.py` and `allEPs.txt` from this repo.
2. Create a folder to store both of these files, this folder will then store the `frames` folder, `log.txt` and `config.json` after they have been generated.
3. Run `main.py` once to generate `config.json` and the `frames` folder, the `frames` folder will be used to store frames from your chosen TV show. If you want to use a different name for the frames folder, you can edit the `frame_dir` variable on line 22 in `main.py`.

Your bot folder should now look like this:

<img src="https://raw.githubusercontent.com/KDunny/every-frame-in-order-bot/main/Root%20folder%20structure.png"/>

4. Edit `allEPs.txt` so it contains each season and episode number based on the frame folder structure on each line just like the example inside the file. Ensure you follow the example and enter an additional line at the end of the file with any text inside it, in the example I wrote `End`, this is needed so the bot picks up the actual last episode of your show. For example, for my instance of the bot I post frames of the show South Park which currently has 319 episodes and a movie that my bot will also post so my local `allEPs.txt` contains 321 lines, one more than the number of episodes including the movie. This method of storing the season and episode names means you **don't** have to have every future episode stored even though the bot may be months away from needing it and allows you to add episode frame filled folders while the bot is running and can delete episode folders after the bot has posted them, this is useful for longer shows where you don't want to store hundreds of episodes as frames at a time.
5. Edit `config.json` with your generated Twitter API key and secret, access token and secret ensuring write permissions were enabled for the access token and secret. Also enter your [Discord webhook URL](https://support.discord.com/hc/en-us/articles/228383668), [Discord user ID](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-), TV show name and delay between tweets in seconds.
6. Extract frames from your chosen TV show with [ffmpeg](https://ffmpeg.org/) and store them inside your `frames` folder, each season with a dedicated folder and each episode with a dedicated folder inside its associated season folder, in your ffmpeg command ensure the file output is `frame-%d.jpg`, this will extract frames in order named as `frame-1.jpg`,`frame-2.jpg`, etc. After extraction, your frames should be stored like this example `frames/Season 1/Episode 1/frame-1.jpg`.
7. Finally you can run `main.py` and the bot should start posting frames to your Twitter!

# Optional - Include episode names in tweets

1. Download `EPnames.txt` from this repo into the bot's folder.
2. Edit `EPnames.txt` so it contains each episode's name on the same line number that episode appears in `allEPs.txt`. Just like `allEPs.txt` ensure there is an additional line at the end of the file with any text inside it.
3. Edit `config.json` by changing `enableEPname` from `0` to `1`.

# Accounts running this bot
Please contact me through the [@SPFramesInOrder](https://twitter.com/SPFramesInOrder) Twitter DM's if you are using this script for your Twitter bot, I would love to add your account to this list!

<a href="https://twitter.com/SPFramesInOrder">
<img src="https://pbs.twimg.com/profile_images/1554072503227645952/t-IIpZar_200x200.jpg" alt="logo" align="left" height="80"/>
</a>

Show: **South Park**

Twitter: [**@SPFramesInOrder**](https://twitter.com/SPFramesInOrder)
