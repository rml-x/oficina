from machine import Pin
from time import sleep, localtime
from network import WLAN, STA_IF
from ntptime import settime
from umqtt.robust import MQTTClient
from json import dumps
import dht

sensor = dht.DHT22(Pin(4))

topico = 'ifrs\pav10\lab1'
broker = 'broker.hivemq.com'
clientID = 'esp32'

def conectaWiFi(nomerede, senharede):
    rede = WLAN(STA_IF)
    rede.active(True)
    if not rede.isconnected():
        rede.connect(nomerede, senharede)
        tentativas = 0
        while not rede.isconnected() and tentativas < 20:
            sleep(7)
            tentativas += 1
    return rede, rede.isconnected()

conectado = conectaWiFi(nomerede='Wokwi-GUEST', senharede='')


if conectado:
    print(localtime())
    settime()
    mqtt = MQTTClient(clientID, broker)
    mqtt.connect()
    print("Conectado ao MQTT")


dicDados = {
    'timestamp': '',
    'temperatura': 0,
    'umidade': 0
}

while True:
    #leitura dados
    try:
        sensor.measure()
        dicDados['temperatura'] = int(sensor.temperature())
        dicDados['umidade'] = int(sensor.humidity())
    except Exception as e:
        print(f"Erro ao ler o sensor: {e}")
        continue

    t = localtime() #data e hora no leitor
    dicDados['timestamp'] = f'{t[0]}-{t[1]}-{t[2]}T{t[3]}:{t[4]}:{t[5]}'

    if conectado: #manda os dados pro mqtt
        msg = dumps(dicDados)
        mqtt.publish(topico, msg.encode())
        print(dicDados)

    sleep(10)