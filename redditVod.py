import glob
import textwrap
import os
from math import ceil
from random import choice

import praw, json, re
from gtts import gTTS
from moviepy.editor import concatenate_videoclips, ImageClip, VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips
from PIL import Image, ImageDraw, ImageFont
import pyttsx3

for name in glob.glob("temp_files/comment_files/*.mp3"):
    os.remove(name)
for name in glob.glob("temp_files/Images/*.png"):
    os.remove(name)

with open('credentials.txt', 'r') as credfile:
    credentials = json.load(credfile)


reddit = praw.Reddit(client_id=credentials['reddit']['client_id'],
                     client_secret=credentials['reddit']['client_secret'],
                     username=credentials['reddit']['username'],
                     password=credentials['reddit']['password'],
                     user_agent=credentials['reddit']['user_agent'])

subreddit = 'askreddit'
english = ['en-ca', 'en-uk', 'en-au', 'en-ie', 'en-nz']

# sub = reddit.subreddit(subreddit).hot(limit=1)
submission = reddit.submission(id='f25p55')#next(sub)
if not submission.stickied and not submission.is_video:
    tts = gTTS(text=submission.title, lang=choice(english))
    tts.save('temp_files/title/title.mp3')

# submission.comments = sorted(submission.comments[0:10], key=lambda x: x.score)

def remove_urls (text):
    text = re.sub('http[s]?://\S+', '', text, flags=re.MULTILINE)
    return(text)

def draw_comment_sub(x, y, offset, author, score, body, draw):
    font_body = ImageFont.truetype(r"Open_Sans\OpenSans-Regular.ttf", 30)
    font_meta = ImageFont.truetype(r"Open_Sans\OpenSans-BoldItalic.ttf", 20)
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
    img.save(f"temp_files/Images/${count}$atop_comment.png")
    if second_level_comment:
        img = Image.open(r'Images\commentbg.png')
        draw = ImageDraw.Draw(img)
        top_body_pixel_size = ceil(len(str(top_level_comment.body))/char_per_line)*line_height
        draw_comment_sub(80, 60, 0, top_level_comment.author.name, top_level_comment.score, wrapper.fill(text=top_level_comment.body), draw)
        draw_comment_sub(120, 140, top_body_pixel_size, second_level_comment.author.name, second_level_comment.score, wrapper.fill(text=second_level_comment.body), draw)
        img.save(f"temp_files/Images/${count}$bsecond_comment.png")
    if third_level_comment:
        img = Image.open(r'Images\commentbg.png')
        draw = ImageDraw.Draw(img)

        top_body_pixel_size = ceil(len(str(top_level_comment.body))/char_per_line)*line_height
        second_body_pixel_size = ceil(len(str(second_level_comment.body))/char_per_line)*line_height
        draw_comment_sub(80, 60, 0, top_level_comment.author.name, top_level_comment.score, wrapper.fill(text=top_level_comment.body), draw)
        draw_comment_sub(120, 140, top_body_pixel_size, second_level_comment.author.name, second_level_comment.score, wrapper.fill(text=second_level_comment.body), draw)
        draw_comment_sub(160, 220, (top_body_pixel_size + second_body_pixel_size), third_level_comment.author.name, third_level_comment.score, wrapper.fill(text=third_level_comment.body), draw)
        img.save(f"temp_files/Images/${count}$cthird_comment.png")

def draw_title():
    wrapper = textwrap.TextWrapper(width=45) 
    string = wrapper.fill(text=submission.title) 
    img = Image.open(r'Images\background.png')
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(r"Open_Sans\OpenSans-Regular.ttf", 50)
    # draw the message on the background

    draw.text((70, 200), string, fill='rgb(255, 255, 255)', font=font)
    img.save("temp_files/title/titleIMG.png")


def make_comments(top=False, second=False, third=False):
    draw_comment(top_level_comment, count)
    voice_choice = choice([1,2])
    if voice_choice == 1:
        tts_1 = gTTS(text=top_level_comment.body, lang=choice(english))
        tts_1.save(f'temp_files/comment_files/${count}$atopComment.mp3')
    else:
        engine.setProperty('voice', choice(voices).id)
        engine.save_to_file(top_level_comment.body, f'temp_files/comment_files/${count}$atopComment.mp3')
        engine.runAndWait()
        
    if top: return

    draw_comment(top_level_comment, count, second_level_comment)#draw must go first, if deleted comment tts will work, but draw wont
    voice_choice = choice([1,2])    
    if voice_choice == 1:
        tts_2 = gTTS(text=second_level_comment.body, lang=choice(english))
        tts_2.save(f'temp_files/comment_files/${count}$bsecondComment.mp3')
    else:
        engine.setProperty('voice', choice(voices).id)
        engine.save_to_file(second_level_comment.body, f'temp_files/comment_files/${count}$bsecondComment.mp3')
        engine.runAndWait()

    if second: return

    draw_comment(top_level_comment, count, second_level_comment, third_level_comment)
    voice_choice = choice([1,2])
    if voice_choice == 1:
        tts_3 = gTTS(text=third_level_comment.body, lang=choice(english))
        tts_3.save(f'temp_files/comment_files/${count}$cthirdComment.mp3')
    else:
        engine.setProperty('voice', choice(voices).id)
        engine.save_to_file(third_level_comment.body, f'temp_files/comment_files/${count}$cthirdComment.mp3')
        engine.runAndWait()        

    if third: return

def valid_comment(score, length, top=False, second=False, third=False):
    if top:
        if top_level_comment.score > score and len(top_level_comment.body) < length and top_level_comment.author.name:
            return True
    if second:
        if second_level_comment.score > score and len(second_level_comment.body) < length and second_level_comment.author.name:
            return True
    if third:
        if third_level_comment.score > score and len(third_level_comment.body) < length and third_level_comment.author.name:
            return True
    return False

engine = pyttsx3.init()
voices =  engine.getProperty('voices')
engine.setProperty('rate', 190)
num_comments_dict = {}
total_num_comments = 30
print("Getting Comments")
draw_title()


for count, top_level_comment in enumerate(submission.comments[:total_num_comments]):
    try:
        top_level_comment.body = remove_urls(top_level_comment.body)
        if valid_comment(1000, 600, top=True):#valid_comment(score, len)
            second_level_comment = top_level_comment.replies[0]
            second_level_comment.body = remove_urls(second_level_comment.body)
            third_level_comment = second_level_comment.replies[0]
            third_level_comment.body = remove_urls(third_level_comment.body)

            if valid_comment((top_level_comment.score // 10), 400, second=True):
                if valid_comment((top_level_comment.score // 12), 200, third=True):
                	make_comments(third=True)
                	num_comments_dict[str(count) ] = 3
                else:
               		make_comments(second=True)
               		num_comments_dict[str(count) ] = 2
            else:
            	make_comments(top=True)
            	num_comments_dict[str(count) ] = 1
        elif valid_comment(2000, 900, top=True):
            make_comments(top=True)
            num_comments_dict[str(count) ] = 1
    except Exception as e: print(e)


#save down each comment separately, combine them with the commented affect and save them into a folder then do the code below 
def create_audio_file():
    all_comments = [AudioFileClip(mp3_file) for mp3_file in glob.glob("temp_files/comment_files/*.mp3")] 
    transition = AudioFileClip(r"transitions\TVColorBars.mp3")
    all_comments_names = [name for name in glob.glob("temp_files/comment_files/*.mp3")]


    all_comments_final = []
    lendict = {}
    title = AudioFileClip('temp_files/title/title.mp3')
    title_dur = title.duration
    all_comments_final.append(title)
    all_comments_final.append(transition)
    count = 0

    for comment_count, indiv in enumerate(all_comments):
        comment_num = all_comments_names[comment_count].split('$')[1]
        all_comments_final.append(indiv)
        lendict[comment_num + str(count)] = indiv.duration
        count += 1
        if count % num_comments_dict[comment_num] == 0:
            count = 0
            all_comments_final.append(transition)

    print("Writing Audio")
    audio_concat = concatenate_audioclips(all_comments_final)
    audio_concat.write_audiofile("comments/all.mp3", 44100)
    return lendict, title_dur, all_comments_names


def create_video_file():
    img = [img_file for img_file in glob.glob("temp_files/Images/*.png")] 
    durations = [dur for dur in lendict.values()]
    transition_clip = VideoFileClip("transitions/TVColorBars.mp4")

    count = 0
    clips = [ImageClip([img_file for img_file in glob.glob("temp_files/title/*.png")][0]).set_duration(title_dur), transition_clip]#adding title and transition clip
    for comment_count, indiv in enumerate(img):
        comment_num = str(all_comments_names[comment_count].split('$')[1])
        clips.append(ImageClip(indiv).set_duration(durations[comment_count]))
        count += 1
        if count % num_comments_dict[comment_num] == 0:
            clips.append(transition_clip)
            count = 0
    concat_clip = concatenate_videoclips(clips, method="compose")
    return concat_clip



lendict, title_dur, all_comments_names = create_audio_file()
concat_clip = create_video_file()
music = ['dream of her', 'kavv', 'mem', 'sorry i like you', "the girl i haven't met"]
music_choice = choice(music)
audio_foreground = AudioFileClip('comments/all.mp3')
audio_background = AudioFileClip(f'music/{music_choice}.mp3').volumex(0.15)


audio_ratio = ceil(audio_foreground.duration/audio_background.duration)
audio_concat = concatenate_audioclips([audio_background]*audio_ratio)
final_audio = CompositeAudioClip([audio_foreground, audio_concat])

print("Writing Video")
final_audio = final_audio.set_end(audio_foreground.duration+1)
final = concat_clip.set_audio(final_audio)
final.write_videofile("Comment Video2.mp4", fps=24, threads=4)


