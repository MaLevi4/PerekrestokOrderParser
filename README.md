# PerekrestokOrderParser

Скрипт для получения информации о каждом купленном вами товаре в онлайн-магазине "Перекрёсток Впрок".

### Зачем нужен?
- Можно посчитать как менялись цены товаров, которые вы покупали
- Можно выявить самый часто покупаемый вами товар
- Можно выявить самый дорогой товар, который вы покупали
- Можно посмотреть на какие категории товаров вы потратили больше всего денег

Скрипт предоставляет возможность **только** выгрузить данные. Дальнейшую обработку вам необходимо запрограммировать самостоятельно в соответствии с вашими целями.

### Как пользоваться?
1. Получить авторизационную cookie
    1. Авторизоваться на сайте vprok.ru
    2. С помощью расширений браузера (например "EditThisCookie" или "Cookie Editor" для Google Chrome) найти cookie с названием, начинающимся с "remember_xo-fo"
    3. Скопировать название и значение этой cookie
2. Скачать репозиторий и установить python
    1. Если у вас не установлен python, вы можете скачать его с официального сайта (www.python.org). Для корректной работы необходима версия python не ниже 3.7
    2. Скачать репозиторий используя команду `git clone` или скачать .zip-архив с сайта github.
    3. Установить дополнитeльные библиотеки python, выполнив в директории проекта команду `python -m pip install -r requirements.txt`
3. Запустить скрипт. В качестве входных данных необходимо передать название и значение авторизационной cookie. Они могут передаваться через переменные окружения (*PEREKRESTOK_COOKIE_NAME* и *PEREKRESTOK_COOKIE_VALUE*) или как первый и второй аргументы командной строки (значения в переменных окружения имеют приоритет).

Пример использования на Windows (командная строка открыта в директории проекта):
```
python main.py remember_xo-fo_4546ffd47bc4accc5866998d8b gfGDGy842jh6f0jfgtj4s6g54sdgd0tvT1ZD6G3VkU4542132540sdgWY1Y0VFUm8wMDJZenc9PSIsInZhb4grggRGgfd45g4df875487484506sDGsdgsdg845gDSGdg84g53sd1gsd8gsd24d2gsd4gsd8gsd1ge8gs4dg35s1grg48sdg53g48r74g30g465dSGHDFHRGsdgsdg4UWhEb2lXUDFORHRZaUpQUStBZGE3QXRjWFE9IiwibWFjIjoiZjhiMTAxMGFlZDE2YzhmZDc2NWY2N4874635uyyu140684SDGSDGdgdsggsdgrgewij45
```
Пример использования на Windows с передачей данных через переменные окружения (командная строка открыта в директории проекта):
```
set PEREKRESTOK_COOKIE_NAME=remember_xo-fo_4546ffd47bc4accc5866998d8b
set PEREKRESTOK_COOKIE_VALUE=gfGDGy842jh6f0jfgtj4s6g54sdgd0tvT1ZD6G3VkU4542132540sdgWY1Y0VFUm8wMDJZenc9PSIsInZhb4grggRGgfd45g4df875487484506sDGsdgsdg845gDSGdg84g53sd1gsd8gsd24d2gsd4gsd8gsd1ge8gs4dg35s1grg48sdg53g48r74g30g465dSGHDFHRGsdgsdg4UWhEb2lXUDFORHRZaUpQUStBZGE3QXRjWFE9IiwibWFjIjoiZjhiMTAxMGFlZDE2YzhmZDc2NWY2N4874635uyyu140684SDGSDGdgdsggsdgrgewij45
python main.py
```
Результат работы будет сохранён в файл `exported_data.json`.

Результатом работы является список словарей: 1 словарь - 1 позиция в заказе. Каждый словарь содержит следующую информацию:
- Внутренний ID товара (`id`)
- Название товара (`title`)
- Ссылку на товар в интернет-магазине (`link`)
- Ссылку на картинку товара (`img`)
- Цену, которую вы заплатили за единицу товара (`price`)
- Количество (`amount`)
- Единица измерения количества: шт\кг (`amount_unit`)
- № заказа (`order_id`)
- Дата заказа (`date`)
- Категория товара (`category`)

#### License: MIT