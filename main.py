import network
import socket
from machine import Pin
import time
from secrets import SSID, PASSWORD

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
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body {{
          font-family: Arial, sans-serif;
          text-align: center;
          background: linear-gradient(135deg, #1e3c72, #2a5298);
          color: white;
          padding: 20px;
        }}
        h2 {{
          margin-top: 30px;
          font-size: 28px;
          font-weight: bold;
        }}
        .status {{
          font-size: 22px;
          margin-bottom: 25px;
        }}
        button {{
          background: white;
          color: #2a5298;
          border: none;
          padding: 16px 28px;
          margin: 10px;
          font-size: 20px;
          border-radius: 12px;
          box-shadow: 0 4px 10px rgba(0,0,0,0.3);
          width: 80%;
          max-width: 220px;
          cursor: pointer;
          transition: 0.2s;
        }}
        button:hover {{
          transform: scale(1.05);
        }}
        .footer {{
          margin-top: 30px;
          font-size: 14px;
          opacity: 0.8;
        }}
      </style>
    </head>
    <body>
      <h2>Pico W LED Control</h2>
      <p class="status">LED is <strong>{state}</strong></p>
      <a href="/on"><button>Turn ON</button></a><br>
      <a href="/off"><button>Turn OFF</button></a>
      <p class="footer">Made with ❤️ on MicroPython</p>
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
