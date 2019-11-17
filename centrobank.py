import time
import smtplib
from email import encoders
from os import remove
from selenium import webdriver
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from webdriver_manager.chrome import ChromeDriverManager
from os import path

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('http://www.google.com/')                                # Зашли на сайт google.ru

search_box = driver.find_element_by_name('q')                       # Проверили, что появилось поле “поиск”
assert search_box is not None
search_box.send_keys('Центральный банк РФ')                         # Ввели в поле поиск значение Центральный банк РФ
search_box.submit()                                                 # Нажали на кнопку поиск в google

continue_link = driver.find_element_by_partial_link_text('cbr.ru')  # Нашли ссылку “cbr.ru”

assert continue_link is not None
continue_link.click()                                               # Нажали на ссылку cbr.ru

assert 'www.cbr.ru' == driver.current_url.split('/')[2]             # Проверили, что открыт нужный сайт

for i in ['Интернет-приемная', 'Написать благодарность']:           # Нажали на ссылку Интернет-приемная
    continue_link = driver.find_element_by_link_text(i)             # и открыли раздел Написать благодарность
    assert continue_link is not None
    continue_link.click()

search_box = driver.find_element_by_name('MessageBody')
search_box.send_keys('случайный текст')                             # В поле Ваша благодарность ввели “случайный текст”

checkbox = driver.find_element_by_id('_agreementFlag')
checkbox.click()                                                    # Поставили галочку “Я согласен”
pic1 = driver.get_screenshot_as_file('screenshot_one.png')          # Сделали скриншот

burger = driver.find_element_by_class_name('burger')                # Нажали на кнопку “Три полоски”
burger.click()
time.sleep(1)

continue_link = driver.find_element_by_partial_link_text('О сайте')
continue_link.click()                                               # Нажали на раздел О сайте
time.sleep(1)

continue_link = driver.find_element_by_partial_link_text('Предупреждение')
continue_link.click()                                               # Нажали на ссылку предупреждение
t1 = driver.find_element_by_id('content')
text1 = t1.text                                                     # Запомнили текст предупреждения
time.sleep(1)

continue_link = driver.find_element_by_link_text('EN')
continue_link.click()                                               # Сменили язык страницы на en
t2 = driver.find_element_by_id('content')
text2 = t2.text
assert text1 is not text2                                           # Проверили, что текст отличается от сохраненного
pic2 = driver.get_screenshot_as_file('screenshot_two.png')          # Сделали скриншот

smtpObj = smtplib.SMTP('smtp.mail.ru', 587)                         # Отправляем скрины на почту
smtpObj.starttls()
smtpObj.login('any@mail.ru','123')

msg = MIMEMultipart()                                               # создали сообщение
msg['From'] = 'any@mail.ru'
msg['To'] = 'any@mail.ru'
msg['Subject'] = 'Скрины экрана'

def attach_file(msg, files):
    for file in files:
        filename = path.basename(file)
        try:
            with open(file, 'rb') as fp:
                file = MIMEImage(fp.read())
                fp.close()
            encoders.encode_base64(file)                            # Кодируем как Base64
            file.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(file)                                        # добавляем файл в сообщение
        except FileNotFoundError:
            print('файл {} не найден'.format(filename))

files = ['screenshot_one.png', 'screenshot_two.png']
attach_file(msg, files)
smtpObj.send_message(msg)                                           # Отправляем сообщение
smtpObj.quit()                                                      # Выходим

try:
    remove('screenshot_one.png')                                    # удаляем скриншоты
    remove('screenshot_two.png')
except OSError:
    print('ошибка при удалении')

time.sleep(2)
driver.quit()
