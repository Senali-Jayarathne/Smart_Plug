import network
import socket
from machine import Pin
import time

# WiFi credentials
SSID = "Dialog 4G 563"
PASSWORD = "be6F0F9F"

# Onboard LED
led = Pin("LED", Pin.OUT)

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Connecting to WiFi...", end="")
while not wlan.isconnected():
    print(".", end="")
    time.sleep(1)

print("\nConnected!")
print("IP:", wlan.ifconfig()[0])

# HTML page
def webpage(state):
    return f"""
    <html>
    <body>
        <h2>Pico W LED Control</h2>
        <p>LED is <strong>{state}</strong></p>
        <a href="/on"><button>Turn ON</button></a>
        <a href="/off"><button>Turn OFF</button></a>
    </body>
    </html>
    """

# Web server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print("Web server running...")

while True:
    client, addr = s.accept()
    request = client.recv(1024).decode()
    print("Request:", request)

    if "/on" in request:
        led.value(1)
    elif "/off" in request:
        led.value(0)

    state = "ON" if led.value() else "OFF"
    response = webpage(state)

    client.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
    client.send(response)
    client.close()

