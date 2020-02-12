import glob
import textwrap
import os
import math
from random import choice

import gtts
import praw
from gtts import gTTS
from moviepy.editor import concatenate_videoclips, ImageClip, VideoFileClip, AudioFileClip, CompositeAudioClip
from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment

for name in glob.glob("temp_files/comment_files/*.mp3"):
    os.remove(name)
for name in glob.glob("temp_files/Images/*.png"):
    os.remove(name)


reddit = praw.Reddit(client_id='kelKdk05QO6sNg',
                     client_secret='TGnU9oeS8KGjEGe2EvK_vxVTvNE',
                     username='Feisty-Zombie',
                     password='ThisismyPassword!',
                     user_agent='my user agent')

subreddit = 'askreddit'
english = ['en-ca', 'en-uk', 'en-au', 'en-in', 'en-ie', 'en-nz', 'en-ph']

# sub = reddit.subreddit(subreddit).hot(limit=1)
submission = reddit.submission(id='99eh6b')#next(sub)
if not submission.stickied and not submission.is_video:
    raw_post = str(submission.title) + " \u2191 " + str(submission.score) + "  r/" + str(subreddit)
    tts = gTTS(text=submission.title, lang=choice(english))
    tts.save('temp_files/title/title.mp3')

# submission.comments = sorted(submission.comments[0:10], key=lambda x: x.score)


def draw_comment_sub(x, y, offset, author, score, body, draw):
    font_body = ImageFont.truetype(r"Open_Sans\OpenSans-Light.ttf", 30)
    font_meta = ImageFont.truetype(r"Open_Sans\OpenSans-Italic.ttf", 20)
    draw.text((x, y + offset), str(author), fill='rgb(0, 0, 255)', font=font_meta)
    author_pixel_size = draw.textsize(str(author), font = font_meta)
    draw.text((x + author_pixel_size[0] + 20, y + offset), str(score) + ' points', fill='rgb(211, 211, 211)', font=font_meta)
    draw.text((x, y + offset + 20), body, fill='rgb(255, 255, 255)', font=font_body)


def draw_comment(top_level_comment, count, second_level_comment='', third_level_comment=''):
    img = Image.open(r'Images\commentbg.png')
    draw = ImageDraw.Draw(img)
    char_per_line = 70
    line_height = 30
    wrapper = textwrap.TextWrapper(width=70) 
    # draw the message on the background
    draw_comment_sub(80, 60, 0, top_level_comment.author.name, top_level_comment.score, wrapper.fill(text=top_level_comment.body), draw)
    img.save(f"temp_files/Images/{count}atop_comment.png")
    if second_level_comment:
        img = Image.open(r'Images\commentbg.png')
        draw = ImageDraw.Draw(img)
        top_body_pixel_size = math.ceil(len(str(top_level_comment.body))/char_per_line)*line_height
        draw_comment_sub(80, 60, 0, top_level_comment.author.name, top_level_comment.score, wrapper.fill(text=top_level_comment.body), draw)
        draw_comment_sub(120, 140, top_body_pixel_size, second_level_comment.author.name, second_level_comment.score, wrapper.fill(text=second_level_comment.body), draw)
        img.save(f"temp_files/Images/{count}bsecond_comment.png")
    if third_level_comment:
        img = Image.open(r'Images\commentbg.png')
        draw = ImageDraw.Draw(img)

        top_body_pixel_size = math.ceil(len(str(top_level_comment.body))/char_per_line)*line_height
        second_body_pixel_size = math.ceil(len(str(second_level_comment.body))/char_per_line)*line_height
        draw_comment_sub(80, 60, 0, top_level_comment.author.name, top_level_comment.score, wrapper.fill(text=top_level_comment.body), draw)
        draw_comment_sub(120, 140, top_body_pixel_size, second_level_comment.author.name, second_level_comment.score, wrapper.fill(text=second_level_comment.body), draw)
        draw_comment_sub(160, 200, (top_body_pixel_size + second_body_pixel_size), third_level_comment.author.name, third_level_comment.score, wrapper.fill(text=third_level_comment.body), draw)
        img.save(f"temp_files/Images/{count}cthird_comment.png")

def draw_title():
    wrapper = textwrap.TextWrapper(width=45) 
    string = wrapper.fill(text=submission.title) 
    img = Image.open(r'Images\background.png')
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(r"Open_Sans\OpenSans-Regular.ttf", 50)
    # draw the message on the background

    draw.text((70, 200), string, fill='rgb(255, 255, 255)', font=font)
    img.save("temp_files/title/titleIMG.png")
draw_title()

for count, top_level_comment in enumerate(submission.comments[:8]):
    try:
        if len(top_level_comment.body) < 1000:
            second_level_comment = top_level_comment.replies[0]
            third_level_comment = second_level_comment.replies[0]
            tts = gTTS(text=top_level_comment.body, lang=choice(english))
            tts.save(f'temp_files/comment_files/{count}atopComment.mp3')
            print(top_level_comment.body)

            if second_level_comment.score > (top_level_comment.score // 10) and len(second_level_comment.body) < 1000:
                tts = gTTS(text=second_level_comment.body, lang=choice(english))
                tts.save(f'temp_files/comment_files/{count}bsecondComment.mp3')
                print('\t' + second_level_comment.body)

                if third_level_comment.score > (second_level_comment.score / 10) and len(third_level_comment.body) < 600:
                    tts = gTTS(text=third_level_comment.body, lang=choice(english))
                    tts.save(f'temp_files/comment_files/{count}cthirdComment.mp3')
                    print('\t\t' + third_level_comment.body)
                    print("All Comments")
                    draw_comment(top_level_comment, count, second_level_comment, third_level_comment)
                else:
                    print("Only Second & Top Comment")
                    draw_comment(top_level_comment, count, second_level_comment)
            
            else:
                print("Only Top Comment") 
                draw_comment(top_level_comment, count)
            print()
    except Exception as e: print(e)


#save down each comment separately, combine them with the commented affect and save them into a folder then do the code below 
transition = AudioSegment.from_mp3(r"transitions\TVColorBars.mp3")

all_comments = [AudioSegment.from_mp3(mp3_file) for mp3_file in glob.glob("temp_files/comment_files/*.mp3")] 
all_comments_names = [name for name in glob.glob("temp_files/comment_files/*.mp3")]

def find_num_of_comments(all_comments_names):
    emptyDict = {}
    numbers = ['0','1','2','3','4','5','6','7','8']
    for j in numbers:
        count = 0
        for i in all_comments_names:
            if j in i[25:26]:
                count += 1
        emptyDict[j] = count
    return emptyDict

num_comments_dict = find_num_of_comments(all_comments_names) 

lendict = {}
combined = AudioSegment.from_mp3('temp_files/title/title.mp3')
title_dur = len(combined)
combined += transition
count = 0
for comment_count, indiv in enumerate(all_comments):
    comment_num = str(all_comments_names[comment_count][25:26])
    lendict[comment_num + str(count)] = len(indiv)
    combined += indiv
    count += 1
    if count % num_comments_dict[comment_num] == 0:
        combined += transition
        count = 0
#combined = combined.append(song, crossfade=5000)
combined.export("comments/all.mp3", format="mp3")

# img = [img_file for img_file in glob.glob("temp_files/Images/*.png")] 
# durations = [dur/1000 for dur in lendict.values()]
# transition_clip = VideoFileClip("transitions/TVColorBars.mp4")
## clips = [ImageClip(j).set_duration(durations[i]) for i,j in enumerate(img)]


# count = 0
# clips = [ImageClip([img_file for img_file in glob.glob("temp_files/title/*.png")][0]).set_duration(title_dur/1000), transition_clip]
# for comment_count, indiv in enumerate(img):
#     comment_num = str(all_comments_names[comment_count][25:26])
#     clips.append(ImageClip(indiv).set_duration(durations[comment_count]))
#     count += 1
#     if count % num_comments_dict[comment_num] == 0:
#         clips.append(transition_clip)
#         count = 0




# music = ['dream of her', 'kavv', 'mem', 'sorry i like you', "the girl i haven't met"]
# music_choice = choice(music)
# audio_background = AudioFileClip(f'music/{music_choice}.mp3').volumex(0.1)
# audio_foreground = AudioFileClip('comments/all.mp3')
# final_audio = CompositeAudioClip([audio_foreground, audio_background])
# # final_audio.write_audiofile('test.mp3', fps=44100)


# concat_clip = concatenate_videoclips(clips, method="compose")
# final_audio = final_audio.set_end(audio_foreground.duration+2)
# final = concat_clip.set_audio(final_audio)
# final.write_videofile("Comment Video2.mp4", fps=24)
#need to slightly increase length of transition mp3
#maybe find the exact length of both