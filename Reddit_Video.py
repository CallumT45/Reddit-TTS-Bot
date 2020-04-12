import glob
import json
import os
import re
import textwrap
from math import ceil
from random import choice, choices

import praw
import pyttsx3
from gtts import gTTS
from moviepy.editor import (AudioFileClip, CompositeAudioClip, ImageClip,
                            VideoFileClip, concatenate_audioclips,
                            concatenate_videoclips)
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

class Reddit_Video():
    def __init__(self, thread, total_num_comments, Path, status):
        self.thread = thread
        self.total_num_comments = total_num_comments
        self.ca = Path
        self.status = status
        self.char_per_line = 65
        self.line_height = 30
        self.init()
        self.font_body = ImageFont.truetype(r"Open_Sans\OpenSans-Regular.ttf", 30)
        self.font_meta = ImageFont.truetype(r"Open_Sans\OpenSans-BoldItalic.ttf", 20)
        self.english = ['en-ca', 'en-uk', 'en-au', 'en-ie', 'en-nz']
        self.num_comments_dict = {}
     
        self.main()

    def remove_urls(self, text):
        text = re.sub('http[s]?://\S+', '', text, flags=re.MULTILINE)
        return(text)

    def draw_comment_sub(self, x, y, offset, author, score, body, draw):
        """
            Given an x and y, this function draws the comment author, score and body relative to the given a and y.
            Offset is used wehre the comment is second or third and must be further down the frame.
        """
        draw.text((x, y + offset), str(author), fill='rgb(0,191,255)', font=self.font_meta)
        author_pixel_size = draw.textsize(str(author), font = self.font_meta)
        draw.text((x + author_pixel_size[0] + 20, y + offset), str(score) + ' points', fill='rgb(211, 211, 211)', font=self.font_meta)
        draw.text((x, y + offset + 20), body, fill='rgb(255, 255, 255)', font=self.font_body)


    def draw_comment(self, count, second_level_comment_bool=False, third_level_comment_bool=False):
        img = Image.open(r'Images\commentbg.png')
        draw = ImageDraw.Draw(img)
        wrapper = textwrap.TextWrapper(width=65) 
        # draw the message on the background
        self.draw_comment_sub(80, 50, 0, self.top_level_comment.author.name, self.top_level_comment.score, wrapper.fill(text=self.top_level_comment.body), draw)
        img.save(f"temp_files/Images/${count}$atop_comment.png")
        if second_level_comment_bool:
            img = Image.open(r'Images\commentbg.png')
            draw = ImageDraw.Draw(img)
            top_body_pixel_size = ceil(len(str(self.top_level_comment.body))/self.char_per_line)*self.line_height
            self.draw_comment_sub(80, 50, 0, self.top_level_comment.author.name, self.top_level_comment.score, wrapper.fill(text=self.top_level_comment.body), draw)
            self.draw_comment_sub(125, 140, top_body_pixel_size, self.second_level_comment.author.name, self.second_level_comment.score, wrapper.fill(text=self.second_level_comment.body), draw)
            img.save(f"temp_files/Images/${count}$bsecond_comment.png")
        if third_level_comment_bool:
            img = Image.open(r'Images\commentbg.png')
            draw = ImageDraw.Draw(img)

            top_body_pixel_size = ceil(len(str(self.top_level_comment.body))/self.char_per_line)*self.line_height
            second_body_pixel_size = ceil(len(str(self.second_level_comment.body))/self.char_per_line)*self.line_height
            self.draw_comment_sub(80, 50, 0, self.top_level_comment.author.name, self.top_level_comment.score, wrapper.fill(text=self.top_level_comment.body), draw)
            self.draw_comment_sub(125, 140, top_body_pixel_size, self.second_level_comment.author.name, self.second_level_comment.score, wrapper.fill(text=self.second_level_comment.body), draw)
            self.draw_comment_sub(170, 230, (top_body_pixel_size + second_body_pixel_size), self.third_level_comment.author.name, self.third_level_comment.score, wrapper.fill(text=self.third_level_comment.body), draw)
            img.save(f"temp_files/Images/${count}$cthird_comment.png")

    def draw_title(self):
        wrapper = textwrap.TextWrapper(width=30) 
        string = wrapper.fill(text=self.submission.title) 
        img = Image.open(r'Images\background.png')

        if self.ca:
            clip_art = Image.open(self.ca).convert("RGBA")
            basewidth = 350
            wpercent = (basewidth/float(clip_art.size[0]))
            hsize = int((float(clip_art.size[1])*float(wpercent)))

            clip_art = clip_art.resize((basewidth,hsize), Image.ANTIALIAS)
            img.paste(clip_art, (800,250), clip_art)

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


    def make_comments(self, count, top=False, second=False, third=False):
        """
        Input boolean: top means only make top level comment, second means make second level comment and top, etc.
        Output: a frame corresponding to the comment and an mp3 file. For each comment voice choice determines if gtts or pyttsx3 will make the mp3 file.
        """
        self.draw_comment(count)
        voice_choice = choice([1,2])
        if voice_choice == 1:
            tts_1 = gTTS(text=self.top_level_comment.body, lang=choice(self.english))
            tts_1.save(f'temp_files/comment_files/${count}$atopComment.mp3')
        else:
            self.engine.setProperty('voice', choices(population=self.voices,weights=self.weights)[0].id)#Increasing liklihood of male voice
            self.engine.save_to_file(self.top_level_comment.body, f'temp_files/comment_files/${count}$atopComment.mp3')
            self.engine.runAndWait()
            
        if top: return

        self.draw_comment(count, True)#draw must go first, if deleted comment tts will work, but draw wont
        voice_choice = choice([1,2])    
        if voice_choice == 1:
            tts_2 = gTTS(text=self.second_level_comment.body, lang=choice(self.english))
            tts_2.save(f'temp_files/comment_files/${count}$bsecondComment.mp3')
        else:
            self.engine.setProperty('voice', choices(population=self.voices,weights=self.weights)[0].id)
            self.engine.save_to_file(self.second_level_comment.body, f'temp_files/comment_files/${count}$bsecondComment.mp3')
            self.engine.runAndWait()

        if second: return

        self.draw_comment(count, True, True)
        voice_choice = choice([1,2])
        if voice_choice == 1:
            tts_3 = gTTS(text=self.third_level_comment.body, lang=choice(self.english))
            tts_3.save(f'temp_files/comment_files/${count}$cthirdComment.mp3')
        else:
            self.engine.setProperty('voice', choices(population=self.voices,weights=self.weights)[0].id)
            self.engine.save_to_file(self.third_level_comment.body, f'temp_files/comment_files/${count}$cthirdComment.mp3')
            self.engine.runAndWait()        

        if third: return

    def valid_comment(self, score, length, top=False, second=False, third=False):
        """
        Input boolean: top means validate top level comment, second means validate second level comment, etc.
        Output boolean: True if comment meets requirements

        Requirements are the comment must exceed a certain score and be less than a certain length. author.name checks to see if the comment is deleted or not.
        And remove urls checks to see if the comment is just a link
        """
        if top:
            if self.top_level_comment.score > score and len(self.top_level_comment.body) < length and self.top_level_comment.author.name and self.remove_urls(self.top_level_comment.body):
                return True
        if second:
            if self.second_level_comment.score > score and len(self.second_level_comment.body) < length and self.second_level_comment.author.name and self.remove_urls(self.second_level_comment.body):
                return True
        if third:
            if self.third_level_comment.score > score and len(self.third_level_comment.body) < length and self.third_level_comment.author.name and self.remove_urls(self.third_level_comment.body):
                return True
        return False

    def create_audio_file(self):
        """ 
        Reads all the mp3 files in the comment_files directory and converts them to AudioFileClips, also sets up the transition audio.
        Loops through the comment names and appends them to a new list, whenever a comment and it replies ends a transition is added. The length of each clip is also recorded to
        a dictionary. All audio clips are combined and outputted to all.mp3.
        """
        all_comments = [AudioFileClip(mp3_file) for mp3_file in glob.glob("temp_files/comment_files/*.mp3")] 
        transition = AudioFileClip(r"transitions/bar_transition.mp3")
        self.all_comments_names = [name for name in glob.glob("temp_files/comment_files/*.mp3")]


        all_comments_final = []
        self.lendict = {}
        title = AudioFileClip('temp_files/title/title.mp3')
        self.title_dur = title.duration
        all_comments_final.append(title)
        all_comments_final.append(transition)
        count = 0
        # Make list with [title, transition, comment_top, comment_second, comment_third, transition, etc]
        for comment_count, indiv in enumerate(all_comments):
            comment_num = self.all_comments_names[comment_count].split('$')[1]
            all_comments_final.append(indiv)
            self.lendict[comment_num + str(count)] = indiv.duration
            count += 1
            if count % self.num_comments_dict[comment_num] == 0:
                self.lendict[comment_num + str(count-1)] = indiv.duration + 0.5
                count = 0
                all_comments_final.append(transition)

        self.status = "Writing Audio"
        print("Writing Audio")
        audio_concat = concatenate_audioclips(all_comments_final)
        audio_concat.write_audiofile("comments/all.mp3", 44100)


    def create_video_file(self):
        """
        Reads all the frames into a list and the durations for each frame. Creates a list with the title and transition then appends the next frame and sets it duration to the value 
        read from the length dictionary. Combines all the clips in the list.
        """
        imgs = [img_file for img_file in glob.glob("temp_files/Images/*.png")] 
        durations = [dur for dur in self.lendict.values()]
        transition_clip = VideoFileClip("transitions/TVColorBars.mp4")

        count = 0
        clips = [ImageClip([img_file for img_file in glob.glob("temp_files/title/*.png")][0]).set_duration(self.title_dur+0.5), transition_clip]#adding title and transition clip
        for comment_count, indiv in enumerate(imgs):
            comment_num = str(self.all_comments_names[comment_count].split('$')[1])
            clips.append(ImageClip(indiv).set_duration(durations[comment_count]))
            count += 1
            if count % self.num_comments_dict[comment_num] == 0:
                clips.append(transition_clip)
                count = 0
        self.concat_clip = concatenate_videoclips(clips, method="compose")



    def init(self):
        #creating the temporary directory  
        try:
            if not os.path.exists("temp_files/comment_files"):
                os.makedirs("temp_files/comment_files")
            if not os.path.exists("temp_files/Images"):
                os.makedirs("temp_files/Images") 
            if not os.path.exists("temp_files/title"):
                os.makedirs("temp_files/title")
        except :
            print ("Creation of the directory failed!")

        #clearing the temp directory
        for file in [img_file for img_file in glob.glob("temp_files/Images/*.png")]:
            os.remove(file)
        for file in [name for name in glob.glob("temp_files/comment_files/*.mp3")]:
            os.remove(file)

        #loading the reddit credentials
        with open('credentials.txt', 'r') as credfile:
            credentials = json.load(credfile)

        #creating an instance of reddit
        self.reddit = praw.Reddit(client_id=credentials['reddit']['client_id'],
                            client_secret=credentials['reddit']['client_secret'],
                            username=credentials['reddit']['username'],
                            password=credentials['reddit']['password'],
                            user_agent=credentials['reddit']['user_agent'])

    def main(self):
        #setting the thread and tts for title
        self.submission = self.reddit.submission(id=self.thread)
        self.submission.comment_sort = 'top'
        # If the submission is stickied or not a text post, then return nothing
        if self.submission.stickied or not self.submission.is_self:
            print("Error! Invalid submission")
            return
        tts = gTTS(text=self.submission.title, lang=choice(self.english))
        tts.save('temp_files/title/title.mp3')



        self.engine = pyttsx3.init()
        self.voices =  self.engine.getProperty('voices')
        # Making male voice more common
        self.weights = [0.7 if "DAVID" in voice.id else 0.15 for voice in self.voices]
        self.engine.setProperty('rate', 150)
        self.status = "Getting Comments"
        print("Getting Comments")
        self.draw_title()

        for count, self.top_level_comment in enumerate(tqdm(self.submission.comments[:self.total_num_comments], leave=False)):
            try:
                self.top_level_comment.body = self.remove_urls(self.top_level_comment.body)
                if self.valid_comment(1000, 600, top=True):#valid_comment(score, len)
                    self.second_level_comment = self.top_level_comment.replies[0]
                    self.second_level_comment.body = self.remove_urls(self.second_level_comment.body)
                    self.third_level_comment = self.second_level_comment.replies[0]
                    self.third_level_comment.body = self.remove_urls(self.third_level_comment.body)

                    if self.valid_comment((self.top_level_comment.score // 10), 400, second=True):
                        if self.valid_comment((self.top_level_comment.score // 12), 200, third=True):
                            self.make_comments(count, third=True)
                            self.num_comments_dict[str(count)] = 3
                        else:
                            self.make_comments(count, second=True)
                            self.num_comments_dict[str(count)] = 2
                    else:
                        self.make_comments(count, top=True)
                        self.num_comments_dict[str(count)] = 1

                elif self.valid_comment(4000, 1200, top=True):
                    self.make_comments(count, top=True)
                    self.num_comments_dict[str(count)] = 1
            except:pass

        self.create_audio_file()
        self.create_video_file()
        music = [music_name for music_name in glob.glob("music/*.mp3")]
        music_choice = choice(music)
        audio_foreground = AudioFileClip('comments/all.mp3')
        audio_background = AudioFileClip(music_choice).volumex(0.12)

        audio_ratio = ceil(audio_foreground.duration/audio_background.duration)
        audio_concat = concatenate_audioclips([audio_background]*audio_ratio)
        final_audio = CompositeAudioClip([audio_foreground, audio_concat])

        self.status = "Writing Video"
        print("Writing Video")
        final_audio = final_audio.set_end(audio_foreground.duration+1)
        final = self.concat_clip.set_audio(final_audio)
        final.write_videofile(f"{self.submission.id}.mp4", fps=24, threads=4)


        #clearing the temp directory
        for file in [img_file for img_file in glob.glob("temp_files/Images/*.png")]:
            os.remove(file)
        for file in [name for name in glob.glob("temp_files/comment_files/*.mp3")]:
            os.remove(file)
