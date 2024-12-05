import os
import subprocess
import pyautogui
import cv2
import pyaudio
import wave
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для управления ПК.\n"
        "Доступные команды:\n"
        "/start - Начать работу\n"
        "/shutdown - Выключить ПК\n"
        "/reboot - Перезагрузить ПК\n"
        "/run <путь> - Запустить программу\n"
        "/browser_open - Открыть браузер\n"
        "/browser_close - Закрыть браузер\n"
        "/volume <0-100> - Установить громкость\n"
        "/screenshot - Сделать скриншот\n"
        "/youtube - Открыть YouTube\n"
        "/vk - Открыть ВКонтакте\n"
        "/camera - Сделать снимок с камеры\n"
        "/record - Начать запись звука (10 секунд)"
    )

# Функция для выключения ПК
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выключаю компьютер...")
    os.system("shutdown /s /t 1")

# Функция для перезагрузки ПК
async def reboot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Перезагружаю компьютер...")
    os.system("shutdown /r /t 1")

# Функция для запуска программ
async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        path = " ".join(context.args)
        try:
            subprocess.Popen(path, shell=True)
            await update.message.reply_text(f"Запустил: {path}")
        except Exception as e:
            await update.message.reply_text(f"Ошибка при запуске: {e}")
    else:
        await update.message.reply_text("Укажите путь к программе. Пример:\n/run C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")

# Функция для открытия браузера (Opera GX)
async def browser_open(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        subprocess.Popen("start opera", shell=True)
        await update.message.reply_text("Opera GX открыт.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при открытии Opera GX: {e}")

# Функция для закрытия браузера (Opera GX)
async def browser_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        os.system("taskkill /IM opera.exe /F")
        await update.message.reply_text("Opera GX закрыт.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при закрытии Opera GX: {e}")

# Функция для управления громкостью
async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            volume_level = int(context.args[0])
            if 0 <= volume_level <= 100:
                os.system(f"nircmd.exe setsysvolume {int(65535 * (volume_level / 100))}")
                await update.message.reply_text(f"Громкость установлена на {volume_level}%.")
            else:
                await update.message.reply_text("Введите значение от 0 до 100.")
        except ValueError:
            await update.message.reply_text("Укажите числовое значение громкости (0-100).")
    else:
        await update.message.reply_text("Пример команды: /volume 50")

# Функция для создания скриншота
async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    screenshot_path = "screenshot.png"
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        await update.message.reply_photo(photo=open(screenshot_path, 'rb'))
        os.remove(screenshot_path)  # Удаляем файл после отправки
    except Exception as e:
        await update.message.reply_text(f"Ошибка при создании скриншота: {e}")

# Функция для открытия YouTube в Opera GX
async def youtube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        os.system("start opera https://www.youtube.com")
        await update.message.reply_text("Открыл YouTube в Opera GX.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при открытии YouTube: {e}")

# Функция для открытия ВКонтакте в Opera GX
async def vk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        os.system("start opera https://vk.com")
        await update.message.reply_text("Открыл ВКонтакте в Opera GX.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при открытии ВКонтакте: {e}")

# Функция для захвата изображения с камеры
async def camera(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            await update.message.reply_text("Не удалось получить доступ к камере.")
            return

        ret, frame = camera.read()
        if ret:
            image_path = "camera_image.jpg"
            cv2.imwrite(image_path, frame)
            camera.release()
            await update.message.reply_photo(photo=open(image_path, 'rb'))
            os.remove(image_path)  # Удаляем файл после отправки
        else:
            await update.message.reply_text("Ошибка при получении изображения с камеры.")
            camera.release()
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# Функция для записи звука
async def record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio_path = "recorded_audio.wav"
    try:
        # Параметры записи
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 60

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        await update.message.reply_text("Начинаю запись звука на 10 секунд...")
        frames = []
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        # Останавливаем запись
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Сохраняем аудиофайл
        wf = wave.open(audio_path, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        # Отправляем аудиофайл
        await update.message.reply_audio(audio=open(audio_path, 'rb'))
        os.remove(audio_path)  # Удаляем файл после отправки
    except Exception as e:
        await update.message.reply_text(f"Ошибка при записи звука: {e}")

# Основная функция для запуска бота
def main():
    TOKEN = "8167944967:AAGmb14BsOt04Y2wy6bzWdrPs2O_9rxw4kA"
    app = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("reboot", reboot))
    app.add_handler(CommandHandler("run", run))
    app.add_handler(CommandHandler("browser_open", browser_open))
    app.add_handler(CommandHandler("browser_close", browser_close))
    app.add_handler(CommandHandler("volume", volume))
    app.add_handler(CommandHandler("screenshot", screenshot))
    app.add_handler(CommandHandler("youtube", youtube))
    app.add_handler(CommandHandler("vk", vk))
    app.add_handler(CommandHandler("camera", camera))
    app.add_handler(CommandHandler("record", record))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()



   