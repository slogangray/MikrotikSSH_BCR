# MikrotikSSH_BCR
Mikrotik ssh batch command runer. Python script.
v 1.0

Скрипт создан для автоматизации выполнения команд cli на удаленных устройствах Mikrotik.
В опубликованном примере он выполняет пакетное обновление роутеров (RouterOS + firmware) из списка **ip_list.txt**.
Основные параметры конфигурации задаются в файле **config.conf**.

Подключение происходит через протокол SSH используя rsa-key авторизацию.

Для настройки авторизации на устройстве необходимо:  

1) Включить простокол SSH.  
2) Создать пользователя для подключения.  
3) Поместить публичный ключ на устройство. Выполнить импорт публичного ключа через winbox **System--->Users--->SSH Keys--->Import SSH Key** выбрав созданного пользователя и файл ключа.  
4) Устройство готово. Для дополнительной безопасности можно настроить port knocking.  

*Сгенерировать пару ключей без использования сторонних программ можно при помощи указания аргумента **g** при запуске скрипта.  

Для настройки выполнения скрипта необходимо:  

1) В файле конфигурации указать имя созданного пользователя на устройстве, параметр "Login". Пути к публичному и приватному ключам, параметры для сохранения сгенерированных скриптом ключей. **private_key_file, save_private_key_file, save_public_key_file**.
Также можно указать нужен ли port knocking в параметре "portknoking".
2) Внутри скрипта указать необходимый набор команд   

cmd0 ="system routerboard settings set auto-upgrade=yes"  
cmd1 ="system package update check-for-updates"  
cmd2 ="system package update download"  
cmd3 ="system reboot"  

и паузы **time.sleep(2)** между ними.  

3) Запустить скрипт и следить за процессом обновления.

Логика работы скрипта:  

1) Выбираем адрес и порт подключения устройства из списка.  
2) Пингуем. Если пингуется то пробуем подключаться, если не пингуется то выбираем следующее устройства из списка.  
3) Подключились, выполняем команды, проверяем что после выполнения устройство пингуется. В случае если пинг пропал останавливаем работу скрипта. Если пинг есть, переходим к следующему устройству.  
4) После окончания выполнения выводится время работы скрипта.  