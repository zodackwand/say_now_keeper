import speech_recognition as sr
from pydub import AudioSegment

def recognize_speech_from_file(file_path: str) -> str:
    # Инициализируем распознаватель
    recognizer = sr.Recognizer()

    # Конвертируем аудиофайл в формат WAV
    audio = AudioSegment.from_file(file_path)
    wav_path = file_path.replace('.ogg', '.wav')
    audio.export(wav_path, format='wav')

    # Загружаем аудиофайл
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)

    # Распознаем речь в аудиофайле
    try:
        result = recognizer.recognize_google(audio_data, language='ru-RU', show_all=True)
        if 'alternative' in result:
            transcript = result['alternative'][0]['transcript']
            return transcript
        else:
            return "Не удалось распознать речь"
    except sr.UnknownValueError:
        return "Не удалось распознать речь"
    except sr.RequestError as e:
        return f"Ошибка сервиса распознавания речи: {e}"

if __name__ == "__main__":
    file_path = "test.ogg"
    recognized_text = recognize_speech_from_file(file_path)
    print(recognized_text)