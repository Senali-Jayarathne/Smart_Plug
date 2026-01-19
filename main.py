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

# HTML page generator
def webpage(state):
    # Lighter background for ON, darker for OFF
    if state == "ON":
        bg = "linear-gradient(45deg, #ff9f43, #feca57, #48dbfb, #1dd1a1)"
    else:
        bg = "linear-gradient(45deg, #222831, #393e46, #222831, #393e46)"

    return f"""
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        @keyframes bgMove {{
          0% {{ background-position: 0% 50%; }}
          50% {{ background-position: 100% 50%; }}
          100% {{ background-position: 0% 50%; }}
        }}
        body {{
          font-family: Arial, sans-serif;
          text-align: center;
          background: {bg};
          background-size: 400% 400%;
          animation: bgMove 12s infinite ease;
          color: white;
          padding: 20px;
        }}
        h2 {{
          margin-top: 30px;
          font-size: 32px;
          font-weight: bold;
          white-space: nowrap; /* Keep in one line */
          animation: floatTitle 3s infinite ease-in-out;
        }}
        @keyframes floatTitle {{
          0% {{ transform: translateY(0px); }}
          50% {{ transform: translateY(-12px); }}
          100% {{ transform: translateY(0px); }}
        }}
        .status {{
          font-size: 26px;
          margin-bottom: 25px;
          animation: glow 1.6s infinite;
        }}
        @keyframes glow {{
          0% {{ text-shadow: 0 0 4px #fff; opacity: 0.7; }}
          50% {{ text-shadow: 0 0 18px #fff; opacity: 1; }}
          100% {{ text-shadow: 0 0 4px #fff; opacity: 0.7; }}
        }}
        button {{
          background: rgba(255,255,255,0.9);
          color: #222;
          border: none;
          padding: 18px 30px;
          margin: 12px;
          font-size: 22px;
          font-weight: bold;
          border-radius: 18px;
          box-shadow: 0 0 12px rgba(255,255,255,0.7);
          width: 80%;
          max-width: 260px;
          cursor: pointer;
          transition: transform 0.25s, box-shadow 0.25s;
        }}
        button:hover {{
          transform: scale(1.12);
          box-shadow: 0 0 20px rgba(255,255,255,0.9);
        }}
        button:active {{
          transform: scale(0.95);
        }}
        a {{ text-decoration: none; }}
        .footer {{
          margin-top: 40px;
          font-size: 15px;
          opacity: 0;
          animation: fadeFoot 4s forwards;
        }}
        @keyframes fadeFoot {{
          from {{ opacity: 0; }}
          to {{ opacity: 0.85; }}
        }}
      </style>
    </head>
    <body>
      <h2>Pico W Magic LED ✨</h2>
      <p class="status">LED is <strong>{state}</strong></p>
      <a href="/on"><button>💡 Turn ON</button></a><br>
      <a href="/off"><button>🌙 Turn OFF</button></a>
      <p class="footer">Made with ❤️ + ✨ MicroPython ✨</p>
    </body>
    </html>
    """

# Web server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print("Web server running...")

while True:
    client, addr = s.accept()
    request = client.recv(1024).decode("utf-8")
    print("Request:", request)

    if "/on" in request:
        led.value(1)
    elif "/off" in request:
        led.value(0)

    state = "ON" if led.value() else "OFF"
    response = webpage(state)

    client.send("HTTP/1.0 200 OK\r\nContent-type: text/html; charset=utf-8\r\n\r\n")
    client.send(response.encode("utf-8"))
    client.close()
