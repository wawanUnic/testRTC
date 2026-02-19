#!/usr/bin/env python3
import time
import subprocess
import RPi.GPIO as GPIO

GPIO.setwarnings(False)

# РЕЛЕ (BCM 18 = физический пин 12, активный LOW)

RELAY_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)  # реле выключено по умолчанию

# SSH ФУНКЦИИ

def ssh_cmd(host, username, command):
    cmd = [
        "ssh",
        "-oHostKeyAlgorithms=+ssh-rsa",
        "-oPubkeyAcceptedAlgorithms=+ssh-rsa",
        "-oStrictHostKeyChecking=no",
        f"{username}@{host}",
        command
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except Exception:
        return None
def get_time_and_mac(host, username):
    info = {}

    # Время
    info["time"] = ssh_cmd(host, username, "date")

    # Интерфейсы
    interfaces = ssh_cmd(host, username, "ls /sys/class/net | grep -v lo")
    if not interfaces:
        info["mac"] = None
        return info

    iface = interfaces.split()[0]  # первый интерфейс

    # MAC
    info["mac"] = ssh_cmd(host, username, f"cat /sys/class/net/{iface}/address")

    return info

# ОСНОВНОЙ ЦИКЛ
HOST = "192.168.8.3"
USER = "root"
LOGFILE = "results.log"

cycle = 1

while True:
    print(f"\n=== ЦИКЛ {cycle} ===")

    # 1. Включаем реле (подаём питание)
    GPIO.output(RELAY_PIN, GPIO.LOW)
    print("Реле включено (питание подано)")

    # 2. Ждём 2 минуты (120 секунд)
    time.sleep(120)

    # 3. Получаем время и MAC
    data = get_time_and_mac(HOST, USER)
    line = f"{cycle}; {data['time']}; {data['mac']}"
    print(line)

    # 4. Пишем в файл (одна строка = один тест)
    with open(LOGFILE, "a") as f:
        f.write(line + "\n")

    # 5. Выключаем реле
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    print("Реле выключено (питание снято)")

    # 6. Ждём 28 минут (1680 секунд) до следующего цикла
    time.sleep(1680)

    cycle += 1
