# Reddit to Video

The purpose of this project is to create a script which automatically creates a video version of any given askreddit or other text based subreddit thread. The porject uses google text to speech and pyttsx3 to create the voices and pillow to create the frames. The audio and video is then stitched together with moviepy.

## Installing
Install the required packages:
    * Praw
    * Pillow
    * gtts
    * pyttsx3
    * moviepy
To set up Praw you will need to set up reddit credentials, moviepy should install ffmpeg, however you may need to install it separately and add it to PATH.
