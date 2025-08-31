from flask import Flask, Response

app = Flask(__name__)

client = """
import requests
import threading
import time
import uuid
import sys
import queue
import signal
import select
import tty
import termios

Provider = "https://realpegachat.onrender.com"

class Starexx:
    def __init__(self):
        self.user_id = f"{uuid.uuid4().hex[:6]}"
        self.chat_id = None
        self.last_message_id = None
        self.running = True
        self.messages = []
        self.input_buffer = ""
        self.message_queue = queue.Queue()
        self.screen_lock = threading.Lock()
        signal.signal(signal.SIGINT, self.signal_handler)
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        self.redraw_input()

    def signal_handler(self, sig, frame):
        self.leave()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
        sys.exit(0)

    def connect(self):
        while self.running:
            try:
                resp = requests.post(f"{Provider}/api/join", json={"userId": self.user_id}, timeout=5)
                data = resp.json()
                if data.get("connected"):
                    self.chat_id = data["chatId"]
                    self.messages.append("\033[1mSystem:\033[0m Connected!")
                    self.redraw_input()
                    return
                else:
                    self.waiting()
                    r = requests.post(f"{Provider}/api/retrieve", json={"userId": self.user_id}, timeout=5).json()
                    if r.get("connected"):
                        self.chat_id = r["chatId"]
                        self.messages.append("\033[1mSystem:\033[0m Partner found!")
                        self.redraw_input()
                        return
            except Exception:
                time.sleep(2)

    def waiting(self):
        for anim in ["[*] Realpega Connected ", "Waiting for partner.  ", "Waiting for partner.. ", "Waiting for partner..."]:
            if not self.running or self.chat_id:
                return
            self.redraw_input(wait_text=anim)
            time.sleep(0.5)

    def poll(self):
        while self.running and self.chat_id:
            try:
                resp = requests.post(
                    f"{Provider}/api/cli_status",
                    json={
                        "userId": self.user_id,
                        "chatId": self.chat_id,
                        "lastMessageId": self.last_message_id,
                    },
                    timeout=5
                )
                if resp.status_code != 200:
                    time.sleep(2)
                    continue
                data = resp.json()
                new_msgs = data.get("messages", [])
                for msg in new_msgs:
                    if msg["sender"] != self.user_id:
                        self.messages.append(f"\033[1mAnonymous:\033[0m {msg['text']}")
                        self.last_message_id = msg["id"]
                        self.message_queue.put(True)
            except Exception:
                pass
            time.sleep(2)

    def redraw_input(self, wait_text=None):
        with self.screen_lock:
            sys.stdout.write("\033[H\033[J")
            for m in self.messages[-20:]:
                print(m)
            print("\n" * 2, end="")
            if wait_text:
                sys.stdout.write(f"{wait_text}\n")
            sys.stdout.write(f"Send message: {self.input_buffer}")
            sys.stdout.flush()

    def msg(self):
        threading.Thread(target=self.message_listener, daemon=True).start()
        try:
            while self.running:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)
                    if char == '\n':
                        if self.input_buffer.lower() in ["exit", "quit"]:
                            self.leave()
                            break
                        if self.input_buffer and self.chat_id:
                            resp = requests.post(
                                f"{Provider}/api/sms",
                                json={
                                    "userId": self.user_id,
                                    "chatId": self.chat_id,
                                    "message": self.input_buffer,
                                },
                                timeout=5
                            )
                            data = resp.json()
                            if data.get("success"):
                                self.last_message_id = data["messageId"]
                                self.messages.append(f"\033[1mYou:\033[0m {self.input_buffer}")
                                self.input_buffer = ""
                                self.redraw_input()
                        else:
                            self.input_buffer = ""
                            self.redraw_input()
                    elif char == '\x7f':
                        self.input_buffer = self.input_buffer[:-1]
                        self.redraw_input()
                    elif char.isprintable():
                        self.input_buffer += char
                        self.redraw_input()
        except KeyboardInterrupt:
            self.leave()
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def message_listener(self):
        while self.running:
            try:
                self.message_queue.get(timeout=1)
                self.redraw_input()
            except queue.Empty:
                continue

    def leave(self):
        self.running = False
        if self.chat_id:
            try:
                requests.post(
                    f"{Provider}/api/leave",
                    json={"userId": self.user_id, "chatId": self.chat_id},
                    timeout=5
                )
            except Exception:
                pass

if __name__ == "__main__":
    client = Starexx()
    client.connect()
    threading.Thread(target=client.poll, daemon=True).start()
    client.msg()
"""

@app.route("/")
def show():
    return Response(client, mimetype='text/plain')

if __name__ == "__main__":
    app.run()
