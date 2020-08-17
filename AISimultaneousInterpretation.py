import azure.cognitiveservices.speech as speechsdk
import time
from tkinter import *
from tkinter import ttk
import threading


# Set specified subscription key and service region.
# Replace with your own subscription key and region identifier from here: https://aka.ms/speech/sdkregion
speech_key, service_region = "73aabea889334e1fa1277dfd778d8f00", "westus"

# Set default from_language, to_language and output_voice
from_language, to_language, output_voice = "en-GB", "zh-Hans", "zh-CN-HuihuiRUS"



# GUI settings
tk = Tk()
tk.title('AI-simultaneous-interpretation')
tk.geometry('900x600')
tk.configure(bg='gray95')

# Set from_language_frame
frame_from = Frame(width=120, height=20, pady=15, bg='gray95')
frame_from.grid(row=0)
Label(frame_from, text='输入',font=('黑体',20), bg='gray95', fg='gray40').grid(row=0,sticky=W,padx=25)

my_from_language = StringVar()
from_language_chosen = ttk.Combobox(frame_from, width=12, textvariable=my_from_language)
from_language_chosen['values'] = ("英文-英国","英文-美国", "中文-普通话", "中文-粤语")
from_language_chosen.grid(row=0,sticky=E,padx=25)
from_language_chosen.current(0)  

from_text_area = Text(frame_from, width=120, height=15, bg='gray90', highlightcolor='gray95', highlightthickness=0)
from_text_area.grid(row=1,padx=25, pady=5)
           
# Set to_language_frame
frame_to = Frame(width=120,height=20, bg='gray95')
frame_to.grid(row=1)
Label(frame_to, text='输出', font=('黑体',20), bg='gray95', fg='gray40').grid(row=0,sticky=W,padx=25)

my_to_language = StringVar()
to_language_chosen = ttk.Combobox(frame_to, width=12, textvariable=my_to_language)
to_language_chosen['values'] = ("英文-英国","英文-美国", "中文-普通话", "中文-粤语")
to_language_chosen.grid(row=0,sticky=E,padx=25)
to_language_chosen.current(2) 

to_text_area = Text(frame_to, width=120, height=15, bg='gray90', highlightcolor='gray95', highlightthickness=0)
to_text_area.grid(row=1,padx=25, pady=5)

# Set button, click button to start or stop translation
start_img = PhotoImage(file='start.png')
start = start_img.subsample(3, 3)
stop_img = PhotoImage(file='stop.png')
stop = stop_img.subsample(3,3)
button_image = start
start_stop_button = None

def button():
    global start_stop_button
    start_stop_button = Button(tk, image=button_image, command=click_button, borderwidth=4)
    start_stop_button.grid(row=2, pady=20)



# Transfer Chinese choices in GUI to language code needed for speech to speech translation
def set_language(my_from_language, my_to_language):
    global from_language, to_language, output_voice
    from_language, to_language, output_voice = get_language(my_from_language, my_to_language)

# Dictionaries about Chinese choices in GUI and its corresponded language code
def get_language(from_la, to_la):
    # Dictionary of source languages.
    # Add more languages of your choice, from list found here: https://docs.microsoft.com/zh-cn/azure/cognitive-services/speech-service/language-support#speech-to-text
    dict_from = {
        "英文-英国" : "en-GB",
        "英文-美国" : "en-US",
        "中文-普通话" : "zh-CN",
        "中文-粤语" : "zh-HK"
    }

    # Dictionary of target languages.
    # Add more languages of your choice, from list found here: https://aka.ms/speech/sttt-languages
    dict_to = {
        "英文-英国" : "en",
        "英文-美国" : "en",
        "中文-普通话" : "zh-Hans",
        "中文-粤语" : "zh-Hant"
    }

    # Dictionary of synthesis output voice name.
    # Add more languages of your choice, from list found here: https://aka.ms/speech/tts-languages
    dict_output_voice = {
        # Uncommentted lines below are dictionary of Standard voices which are available to most region but with less result
        "英文-英国" : "en-GB-Susan-Apollo",
        "英文-美国" : "en-US-ZiraRUS",
        "中文-普通话" : "zh-CN-HuihuiRUS",
        "中文-粤语" : "zh-HK-Tracy-Apollo"
        # Commentted lines below are dicitonary of Neural voices
        # Note that Neural voices are not available in some service region
        # More information about regions could be found here: https://docs.microsoft.com/zh-cn/azure/cognitive-services/speech-service/regions#standard-and-neural-voices
        # "英文-英国" : "en-GB-LibbyNeural",
        # "英文-美国" : "en-US-AriaNeural",
        # "中文-普通话" : "zh-CN-XiaoxiaoNeural",
        # "中文-粤语" : "zh-HK-HiuGaaiNeural"
    }

    from_l = dict_from[from_la]
    to_l = dict_to[to_la]
    output_v = dict_output_voice[to_la]
    return from_l, to_l, output_v


# Set translate speech to speech, more information about Microsoft Speech to Speech SDK could be found here: https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/index-speech-translation
done = False

def translate_speech_to_speech():
    global done
    # Creates an instance of a speech translation config with specified subscription key and service region.
    translation_config = speechsdk.translation.SpeechTranslationConfig(subscription=speech_key, region=service_region)

    # Creates an instance of a speech config with specified subscription key and service region.
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

    # Sets source and target languages.
    translation_config.speech_recognition_language = from_language
    translation_config.add_target_language(to_language)
    
    # Sets the synthesis output voice name.
    speech_config.speech_synthesis_voice_name = output_voice

    # Creates a translation recognizer using and audio file as input.
    recognizer = speechsdk.translation.TranslationRecognizer(translation_config=translation_config)

    # Creates a speech synthesizer using the default speaker as audio output and sets its language 
    speech_config.speech_synthesis_language = to_language
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

    # Starts continuous translation
    print("Say something...")

    # return recognized text
    def get_text(evt):
        return evt.result.text

    # return translated text
    def get_translation(evt):
        return evt.result.translations[to_language]

    recognizer.start_continuous_recognition()
    recognizer.recognized.connect(lambda evt: from_text_area.insert("end", get_text(evt) + "\n"))
    recognizer.recognized.connect(lambda evt: to_text_area.insert("end", get_translation(evt) + "\n"))
    recognizer.recognized.connect(lambda evt: speech_synthesizer.speak_text_async(get_translation(evt)))
    
    while not done:
        time.sleep(.5)

#  open another thread
def thread_it(func, *args):
    t = threading.Thread(target=func, args=args) 
    t.setDaemon(True) 
    t.start()

# click button to 1. change the img from started mode to stopped mode; 2. start or stop translation
flag = False
def click_button():
    global flag, start_stop_button, done
    flag = not flag
    if flag:
        start_stop_button['image'] = stop
        done = False
        set_language(my_from_language.get(), my_to_language.get())
        #  use another thread to run time consumed function: translate_speech_to_speech, to prevent GUI being stuck
        thread_it(translate_speech_to_speech)
    else:
        done = True
        start_stop_button['image'] = start
    tk.update()

# create button
button()

# mainloop of tkinter
tk.mainloop()


