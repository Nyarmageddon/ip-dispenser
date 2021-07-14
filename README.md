# IP Dispenser

Небольшое приложение для выдачи IP-адресов из подсетей.
Написано на Python + Django.


### Установка

В виртуальном окружении:

* `git clone https://github.com/Nyarmageddon/ip-dispenser.git .`
* `cd app && pip install -r requirements.txt`
* `cp ip_dispenser/settings_local.dist.py ip_dispenser/settings_local.py`
* отредактировать настройки в `ip_dispenser/settings_local.py`
* `python manage.py migrate`
* добавить админ-аккаунт для работы:
`python manage.py createsuperuser`

### Начало работы

После установки нужно авторизоваться и перейти в админку /admin/, чтобы добавить хотя бы одну подсеть.
После этого пользователи могут получать IP-адреса из неё в личном кабинете.


IP-адреса выдаются из случайной доступной подсети.
Приоритет отдаётся IP, которые уже выдавались пользователям.
Если таких нет, то система добавляет в базу следующий IP по порядку.


По адресу /dashboard/ есть кривенькая админка, но лучше пользоваться Django-админкой /admin/ .


### Разное

Текст на главной странице написан Балабобой.