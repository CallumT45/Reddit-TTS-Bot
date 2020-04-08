# // To Do: Add small delay before transition, slow down voice, change comment reqs and make a main.py

import glob
import textwrap
import os
from math import ceil
from random import choice, choices

import praw, json, re
from gtts import gTTS
from moviepy.editor import concatenate_videoclips, ImageClip, VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips
from PIL import Image, ImageDraw, ImageFont
import pyttsx3

def remove_urls(text):
    text = re.sub('http[s]?://\S+', '', text, flags=re.MULTILINE)
    return(text)

def draw_comment_sub(x, y, offset, author, score, body, draw):
    font_body = ImageFont.truetype(r"Open_Sans\OpenSans-Regular.ttf", 30)
    font_meta = ImageFont.truetype(r"Open_Sans\OpenSans-BoldItalic.ttf", 20)
    draw.text((x, y + offset), str(author), fill='rgb(0,191,255)', font=font_meta)
    author_pixel_size = draw.textsize(str(author), font = font_meta)
    draw.text((x + author_pixel_size[0] + 20, y + offset), str(score) + ' points', fill='rgb(211, 211, 211)', font=font_meta)
    draw.text((x, y + offset + 20), body, fill='rgb(255, 255, 255)', font=font_body)


def draw_comment(top_level_comment, count, second_level_comment='', third_level_comment=''):
    img = Image.open(r'Images\commentbg.png')
    draw = ImageDraw.Draw(img)
    char_per_line = 65
    line_height = 30
    wrapper = textwrap.TextWrapper(width=65) 
    # draw the message on the background
    draw_comment_sub(80, 50, 0, top_level_comment.author.name, top_level_comment.score, wrapper.fill(text=top_level_comment.body), draw)
    img.save(f"temp_files/Images/${count}$atop_comment.png")
    if second_level_comment:
        img = Image.open(r'Images\commentbg.png')
        draw = ImageDraw.Draw(img)
        top_body_pixel_size = ceil(len(str(top_level_comment.body))/char_per_line)*line_height
        draw_comment_sub(80, 50, 0, top_level_comment.author.name, top_level_comment.score, wrapper.fill(text=top_level_comment.body), draw)
        draw_comment_sub(125, 140, top_body_pixel_size, second_level_comment.author.name, second_level_comment.score, wrapper.fill(text=second_level_comment.body), draw)
        img.save(f"temp_files/Images/${count}$bsecond_comment.png")
    if third_level_comment:
        img = Image.open(r'Images\commentbg.png')
        draw = ImageDraw.Draw(img)

        top_body_pixel_size = ceil(len(str(top_level_comment.body))/char_per_line)*line_height
        second_body_pixel_size = ceil(len(str(second_level_comment.body))/char_per_line)*line_height
        draw_comment_sub(80, 50, 0, top_level_comment.author.name, top_level_comment.score, wrapper.fill(text=top_level_comment.body), draw)
        draw_comment_sub(125, 140, top_body_pixel_size, second_level_comment.author.name, second_level_comment.score, wrapper.fill(text=second_level_comment.body), draw)
        draw_comment_sub(170, 230, (top_body_pixel_size + second_body_pixel_size), third_level_comment.author.name, third_level_comment.score, wrapper.fill(text=third_level_comment.body), draw)
        img.save(f"temp_files/Images/${count}$cthird_comment.png")

def draw_title(submission, ca=''):
    wrapper = textwrap.TextWrapper(width=30) 
    string = wrapper.fill(text=submission.title) 
    img = Image.open(r'Images\background.png')

    if ca:
        clip_art = Image.open(ca).convert("RGBA")
        basewidth = 350
        wpercent = (basewidth/float(clip_art.size[0]))
        hsize = int((float(clip_art.size[1])*float(wpercent)))

        clip_art = clip_art.resize((basewidth,hsize), Image.ANTIALIAS)
        img.paste(clip_art, (800,250), clip_art)

    draw = ImageDraw.Draw(img)


    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(r"Open_Sans\OpenSans-Regular.ttf", 50)
    # draw the message on the background
    frame_colour = choice(['rgb(255, 0, 0)', 'rgb(255, 255, 0)', 'rgb(255, 140, 0)', 'rgb(255, 69, 0)', 'rgb(255, 215, 0)'])
    draw.rectangle([(0,0), (1280,10)], fill=frame_colour)
    draw.rectangle([(0,720), (1280,710)], fill=frame_colour)
    draw.rectangle([(0,0), (10,720)], fill=frame_colour)
    draw.rectangle([(1270,0), (1280,720)], fill=frame_colour)

    draw.text((70, 250), string, fill='rgb(255, 255, 255)', font=font)
    img.save("temp_files/title/titleIMG.png")


def make_comments(count, engine, weights, voices, top=False, second=False, third=False):
    """
    Input boolean: top means only make top level comment, second means make second level comment and top, etc.
    Output: a frame corresponding to the comment and an mp3 file. For each comment voice choice determines if gtts or pyttsx3 will make the mp3 file.
    """
    global top_level_comment
    global second_level_comment
    global third_level_comment
    english = ['en-ca', 'en-uk', 'en-au', 'en-ie', 'en-nz']
    draw_comment(top_level_comment, count)
    voice_choice = choice([1,2])
    if voice_choice == 1:
        tts_1 = gTTS(text=top_level_comment.body, lang=choice(english))
        tts_1.save(f'temp_files/comment_files/${count}$atopComment.mp3')
    else:
        engine.setProperty('voice', choices(population=voices,weights=weights)[0].id)#Increasing liklihood of male voice
        engine.save_to_file(top_level_comment.body, f'temp_files/comment_files/${count}$atopComment.mp3')
        engine.runAndWait()
        
    if top: return

    draw_comment(top_level_comment, count, second_level_comment)#draw must go first, if deleted comment tts will work, but draw wont
    voice_choice = choice([1,2])    
    if voice_choice == 1:
        tts_2 = gTTS(text=second_level_comment.body, lang=choice(english))
        tts_2.save(f'temp_files/comment_files/${count}$bsecondComment.mp3')
    else:
        engine.setProperty('voice', choices(population=voices,weights=weights)[0].id)
        engine.save_to_file(second_level_comment.body, f'temp_files/comment_files/${count}$bsecondComment.mp3')
        engine.runAndWait()

    if second: return

    draw_comment(top_level_comment, count, second_level_comment, third_level_comment)
    voice_choice = choice([1,2])
    if voice_choice == 1:
        tts_3 = gTTS(text=third_level_comment.body, lang=choice(english))
        tts_3.save(f'temp_files/comment_files/${count}$cthirdComment.mp3')
    else:
        engine.setProperty('voice', choices(population=voices,weights=weights)[0].id)
        engine.save_to_file(third_level_comment.body, f'temp_files/comment_files/${count}$cthirdComment.mp3')
        engine.runAndWait()        

    if third: return

def valid_comment(score, length, top=False, second=False, third=False):
    """
    Input boolean: top means validate top level comment, second means validate second level comment, etc.
    Output boolean: True if comment meets requirements

    Requirements are the comment must exceed a certain score and be less than a certain length. author.name checks to see if the comment is deleted or not.
    """
    global top_level_comment
    global second_level_comment
    global third_level_comment
    if top:
        if top_level_comment.score > score and len(top_level_comment.body) < length and top_level_comment.author.name and remove_urls(top_level_comment.body):
            return True
    if second:
        if second_level_comment.score > score and len(second_level_comment.body) < length and second_level_comment.author.name and remove_urls(second_level_comment.body):
            return True
    if third:
        if third_level_comment.score > score and len(third_level_comment.body) < length and third_level_comment.author.name and remove_urls(third_level_comment.body):
            return True
    return False

def create_audio_file(num_comments_dict):
    """ 
    Reads all the mp3 files in the comment_files directory and converts them to AudioFileClips, also sets up the transition audio.
    Loops through the comment names and appends them to a new list, whenever a comment and it replies ends a transition is added. The length of each clip is also recorded to
    a dictionary. All audio clips are combined and outputted to all.mp3.
    """
    all_comments = [AudioFileClip(mp3_file) for mp3_file in glob.glob("temp_files/comment_files/*.mp3")] 
    transition = AudioFileClip(r"transitions/bar_transition.mp3")
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
            lendict[comment_num + str(count-1)] = indiv.duration + 0.5
            count = 0
            all_comments_final.append(transition)

    print("Writing Audio")
    audio_concat = concatenate_audioclips(all_comments_final)
    audio_concat.write_audiofile("comments/all.mp3", 44100)
    return lendict, title_dur, all_comments_names


def create_video_file(lendict, title_dur, all_comments_names, num_comments_dict):
    """
    Reads all the frames into a list and the durations for each frame. Creates a list with the title and transition then appends the next frame and sets it duration to the value 
    read from the length dictionary. Combines all the clips in the list.
    """
    img = [img_file for img_file in glob.glob("temp_files/Images/*.png")] 
    durations = [dur for dur in lendict.values()]
    transition_clip = VideoFileClip("transitions/TVColorBars.mp4")

    count = 0
    clips = [ImageClip([img_file for img_file in glob.glob("temp_files/title/*.png")][0]).set_duration(title_dur+0.5), transition_clip]#adding title and transition clip
    for comment_count, indiv in enumerate(img):
        comment_num = str(all_comments_names[comment_count].split('$')[1])
        clips.append(ImageClip(indiv).set_duration(durations[comment_count]))
        count += 1
        if count % num_comments_dict[comment_num] == 0:
            clips.append(transition_clip)
            count = 0
    concat_clip = concatenate_videoclips(clips, method="compose")
    return concat_clip


def init():
    #creating the temporary directory  
    try:
        os.makedirs("temp_files/comment_files")
        os.mkdir("temp_files/Images")
        os.mkdir("temp_files/title")
    except :
        print ("Creation of the directory failed / Directory already exists!")

    #clearing the temp directory
    for file in [img_file for img_file in glob.glob("temp_files/Images/*.png")]:
        os.remove(file)
    for file in [name for name in glob.glob("temp_files/comment_files/*.mp3")]:
        os.remove(file)

    #loading the reddit credentials
    with open('credentials.txt', 'r') as credfile:
        credentials = json.load(credfile)

    #creating an instance of reddit
    reddit = praw.Reddit(client_id=credentials['reddit']['client_id'],
                        client_secret=credentials['reddit']['client_secret'],
                        username=credentials['reddit']['username'],
                        password=credentials['reddit']['password'],
                        user_agent=credentials['reddit']['user_agent'])
    return reddit
def main(thread, total_num_comments, ca = ''):
    global top_level_comment
    global second_level_comment
    global third_level_comment
    reddit = init()
    
    #setting the thread and tts for title
    english = ['en-ca', 'en-uk', 'en-au', 'en-ie', 'en-nz']
    submission = reddit.submission(id=thread)
    submission.comment_sort = 'top'
    if not submission.stickied and not submission.is_video:
        tts = gTTS(text=submission.title, lang=choice(english))
        tts.save('temp_files/title/title.mp3')



    engine = pyttsx3.init()
    voices =  engine.getProperty('voices')
    weights = [0.7 if "DAVID" in voice.id else 0.15 for voice in voices]
    engine.setProperty('rate', 150)
    num_comments_dict = {}
    print("Getting Comments")
    draw_title(submission, ca)

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
                        make_comments(count, engine, weights, voices, third=True)
                        num_comments_dict[str(count)] = 3
                    else:
                        make_comments(count, engine, weights, voices, second=True)
                        num_comments_dict[str(count)] = 2
                else:
                    make_comments(count, engine, weights, voices, top=True)
                    num_comments_dict[str(count)] = 1

            elif valid_comment(4000, 1200, top=True):
                make_comments(count, engine, weights, voices, top=True)
                num_comments_dict[str(count)] = 1
            print(round(count*100/total_num_comments, 2), '%')
        except:pass

    lendict, title_dur, all_comments_names = create_audio_file(num_comments_dict)
    concat_clip = create_video_file(lendict, title_dur, all_comments_names, num_comments_dict)
    music = [music_name for music_name in glob.glob("music/*.mp3")]
    music_choice = choice(music)
    audio_foreground = AudioFileClip('comments/all.mp3')
    audio_background = AudioFileClip(music_choice).volumex(0.12)


    audio_ratio = ceil(audio_foreground.duration/audio_background.duration)
    audio_concat = concatenate_audioclips([audio_background]*audio_ratio)
    final_audio = CompositeAudioClip([audio_foreground, audio_concat])

    print("Writing Video")
    final_audio = final_audio.set_end(audio_foreground.duration+1)
    final = concat_clip.set_audio(final_audio)
    final.write_videofile("Comment Video.mp4", fps=24, threads=4)


    #clearing the temp directory
    for file in [img_file for img_file in glob.glob("temp_files/Images/*.png")]:
        os.remove(file)
    for file in [name for name in glob.glob("temp_files/comment_files/*.mp3")]:
        os.remove(file)
