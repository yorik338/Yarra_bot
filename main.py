import speech_recognition as sr
import random
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import subprocess
import os
from openai import OpenAI
import httpx

OPENAI_API_KEY = OpenApiKey

openai = OpenAI(
    api_key=OPENAI_API_KEY,
    http_client=httpx.Client(
        proxies=PROXY),
)


def generate_response(vopros):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[{"role": "user", "content": vopros}],
        max_tokens=1000,
    )

    return response.choices[0].message.content


def listen():
    with sr.Microphone() as source:
        voice_recognizer = sr.Recognizer()

        print("Скажите что-то >>> ")
        try:
            audio = voice_recognizer.listen(source, timeout=4)
            voice_text = voice_recognizer.recognize_google(audio,
                                                           language="ru")
            print(f"Вы сказали: {voice_text}")
            return voice_text
        except sr.UnknownValueError:
            return "ошибка распознание"
        except sr.RequestError:
            return "ошибка запроса"


def say(text):
    voice = gTTS(text, lang="ru")
    unique_file = "audio_" + str(random.randint(0, 10000)) + ".mp3"
    voice.save(unique_file)

    try:
        sound = AudioSegment.from_mp3(unique_file)
        play(sound)
    except Exception as e:
        print(f"Error playing sound: {e}")

    os.remove(unique_file)
    print(f"Ассистент: {text}")


def handle_command(command):
    command = command.lower()

    if command == "привет":
        say("Привет-привет")
    elif command == "пока":
        stop()
    elif "интернет" in command:
        query = command.replace("интернет", "").strip()
        search_query(query)
    elif command != "ошибка распознание" and command != "ошибка запроса":
        otvet = generate_response(command)
        print(otvet)
        say(otvet)

    else:
        say("Ошибка распознания повторите запрос")


def search_query(query):
    search_url = f"https://www.google.com/search?q={query}"
    browser_command = "firefox"  # Change this to your browser command if it's different

    try:
        subprocess.Popen([browser_command, search_url])
    except Exception as e:
        print(f"Error opening browser: {e}")


def stop():
    say("До скорого")
    exit()


def start():
    print("Запуск ассистента...")

    while True:
        command = listen()
        handle_command(command)


try:
    start()
except KeyboardInterrupt:
    stop()
