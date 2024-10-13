class Config:
    TESTING = False
    DEBUG = False

    notify_method = 'EMAIL'  # see supported_notify_methods

    smtp_server = 'mail.yourisp.com:465'
    smtp_user = 'user'
    smtp_pass = 'pass'
    email_from = 'noreply@mail.yourisp.com'
    email_to = 'sysadmin@mail.yourisp.com'
    # Define the MQTT broker settings
    mqtt_broker = "mqttserver.local"
    mqtt_port = 1883
    mqtt_user = "mosquitto"
    mqtt_password = "pass"
    mqtt_topic = "notify/android/t"
    backup_paths = ['/path/to/repository1',
            '/path/to/repository2',
            ]
    cmds = {
            '1':
                { 'cmd': 'duplicacy backup -stats -threads 10',
                },
            '2':
                { 'cmd': 'duplicacy check',
                },
            '3':
                { 'cmd': 'duplicacy prune -keep 0:80 -exclusive',
                },
            }

