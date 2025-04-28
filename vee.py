import sys
import random
import time
import json
import os
import psutil
import pygetwindow as gw
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QMenu, QMessageBox, QSystemTrayIcon, QVBoxLayout, QHBoxLayout, QPushButton, QColorDialog, QFrame
from PyQt5.QtGui import QPixmap, QFont, QIcon, QPainter, QPen, QColor, QImage
from PyQt5.QtCore import Qt, QTimer, QPoint, QEvent, QPropertyAnimation, QEasingCurve
from pynput import keyboard, mouse

# ---------- Configuration and Settings ----------
CONFIG_FILE = "vee_config.json"
DEFAULT_CONFIG = {
    "buddy_image": "buddy2.png",
    "alternate_image": "buddy.png",
    "high_scores": {
        "cookie_game": 0,
        "rapid_click": 0
    },
    "theme": "default",
    "notification_level": "normal",
    "startup_message": True
}

# Themes
THEMES = {
    "default": {
        "positive_bubble": "#fff6c1",
        "negative_bubble": "#cde4ff",
        "neutral_bubble": "#ffffff",
        "text_color": "#333333"
    },
    "dark": {
        "positive_bubble": "#4a4a00",
        "negative_bubble": "#002244",
        "neutral_bubble": "#2d2d2d",
        "text_color": "#ffffff"
    },
    "pastel": {
        "positive_bubble": "#ffcccc",
        "negative_bubble": "#ccccff",
        "neutral_bubble": "#ccffcc",
        "text_color": "#333333"
    }
}

# Triggers
trigger_words = [
    "lol", "bruh", "omg", "sheesh", "huh", "sus", "fr", "no cap", "rizz", "sleep", "study"
]
vs_code_names = ["Code", "code", "visual studio code"]
browser_names = ["chrome", "firefox", "brave", "edge"]

# Messages
focus_msgs = {
    "code": [
        "Back to VS Code? Let's pretend to be productive.",
        "Coding time. Don't mess this up.",
        "Lines of code or lines of errors? Let's find out!",
    ],
    "browser": [
        "Surfing the web? Don't fall into the void.",
        "Research or Reddit? 👀",
        "Information superhighway or distraction avenue?",
    ],
    "other": [
        "Still here. Still judging.",
        "Hmm, you're switching around a lot.",
        "I see you changing windows... interesting.",
    ]
}

trigger_replies = {
    "lol": ["You're not actually laughing.", "LOL - Lots of Laziness"],
    "bruh": ["bruh indeed.", "Bruh moment detected."],
    "omg": ["Classic reaction.", "OMG indeed!"],
    "sheesh": ["Chillll. That was extra.", "Sheeeeeesh!"],
    "huh": ["confused? same.", "I'm as puzzled as you are."],
    "sus": ["That's suspicious...", "Among Us reference in 2025? Sus."],
    "fr": ["for real for real.", "Fr fr no cap on god."],
    "no cap": ["Facts only.", "Zero cap detected."],
    "rizz": ["Bro thinks he's HIM.", "Rizz level: undefined."],
    "sleep": ["It's sleep o'clock.", "Close your eyes, not your IDE."],
    "study": ["Go study. I'll wait.", "Books > screens sometimes."]
}

# --- Mood and personality additions ---
MOOD_MAX = 10
MOOD_MIN = -10
MOOD_POSITIVE = 4
MOOD_NEGATIVE = -4

idle_msgs = [
    "You alive over there?",
    "Don't make me do all the work.",
    "Wake up! Or are you napping?",
    "Idle detected. Should I nap too?"
]

easter_eggs = {
    "cat": [
        "Did someone say cat? \U0001F431",
        "Meow! You summoned the feline overlord.",
        "Purr-fect timing!"
    ],
    "love": [
        "Aww, love is in the air! \u2764\ufe0f",
        "Sending virtual hugs!",
        "You are loved!"
    ],
    "uwu": [
        "uwu what's this?",
        "So soft. So cute. uwu~",
        "(*^\u03C9^) uwu!"
    ],
    "python": [
        "Python: where indentation actually matters!",
        "Ssssssnake language detected!",
        "A wild Python appeared!"
    ],
    "friday": [
        "Friday mode activated! Weekend incoming!",
        "It's Friday! Time to pretend to work!",
        "Friday = my favorite F word."
    ]
}

roast_msgs = [
    "You call that productivity? My grandma types faster.",
    "Bro, even Clippy would be disappointed.",
    "You need help. Like, actual help.",
    "I'm not mad, just disappointed. Actually, I'm mad too.",
    "You fumbled the bag again."
]
hype_msgs = [
    "YOOO, you're on fire! 🔥",
    "Absolute legend. Keep going!",
    "Nobody does it like you!",
    "You are HIM. Or HER. Or THEM. ICONIC!",
    "Let's GOOOO!"
]
calm_down_msgs = [
    "Okay, let's chill for a sec...",
    "Take a breather, superstar.",
    "Deep breaths. Even legends need a break."
]

resource_warning_msgs = [
    "Your CPU is working hard. Maybe close some tabs?",
    "Memory usage is high. Time to reboot?",
    "Your PC is sweating. Give it a break!",
    "System resources looking stretched. Might want to check that."
]

late_night_msgs = [
    "It's 11PM. Sleep mode activated.",
    "You should be in bed!",
    "Late night grind, huh?"
]
shutdown_msgs = [
    "It's after 2AM. I'm shutting down, goodnight.",
    "Nope. Too late. Bye!",
    "Sleep is important. See you tomorrow!"
]

secret_combos = {
    "kittycode": "You unlocked: Kitty Mode! 🐾",
    "nour": "Nour detected. The legend herself!",
    "hello!": "Hi there, secret agent!",
    "themeswap": "Theme swapper activated. Right-click for options!",
    "matrix": "You've entered the Matrix. There is no spoon.",
    "42": "The answer to life, the universe, and everything!"
}
recent_combo = None
recent_combo_time = 0

def load_config():
    """Load configuration from file or create default if not exists"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        else:
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")

def get_time_period():
    """Get the current time period (morning, afternoon, night)"""
    import datetime
    now = datetime.datetime.now().time()
    if now < datetime.time(11, 0):
        return "morning"
    elif now >= datetime.time(20, 0):
        return "night"
    else:
        return "afternoon"

def personalize(msg):
    """Add time-based emoji to message"""
    period = get_time_period()
    if period == "morning":
        return f"\U0001F305 {msg}"
    elif period == "afternoon":
        return f"\u2600\ufe0f {msg}"
    elif period == "night":
        return f"\U0001F319 {msg}"
    return msg

def check_system_resources():
    """Check system CPU and memory usage"""
    try:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        
        if cpu > 80 or memory > 85:
            return True, random.choice(resource_warning_msgs)
        return False, None
    except:
        return False, None

# ---------- Game Classes ----------
class CatchTheCookieGame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Catch the Cookie")
        self.setFixedSize(400, 400)
        self.cookie_radius = 30
        self.cookie_x = random.randint(self.cookie_radius, self.width() - self.cookie_radius)
        self.cookie_y = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.drop_cookie)
        self.timer.start(20)
        self.caught = False
        
        from PyQt5.QtWidgets import QPushButton
        self.exit_btn = QPushButton("Exit", self)
        self.exit_btn.setGeometry(200, 360, 80, 30)
        self.exit_btn.clicked.connect(self.close)

        self.show()

    def drop_cookie(self):
        self.cookie_y += 4
        if self.cookie_y > self.height():
            self.timer.stop()
            QMessageBox.information(self, "Result", "You missed it! 😾")
            self.close()
        self.update()

    def mousePressEvent(self, event):
        dx = event.x() - self.cookie_x
        dy = event.y() - self.cookie_y
        if dx * dx + dy * dy <= self.cookie_radius * self.cookie_radius:
            self.caught = True
            self.timer.stop()
            # Update high score
            config = load_config()
            score = int(time.time() * 10) % 100 + 50  # Simple score based on timing
            if score > config["high_scores"]["cookie_game"]:
                config["high_scores"]["cookie_game"] = score
                save_config(config)
                QMessageBox.information(self, "Result", f"New high score: {score}! 🍪")
            else:
                QMessageBox.information(self, "Result", f"You win with {score} points! 🍪")
            self.close()

    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QColor, QBrush, QRadialGradient
        painter = QPainter(self)
        
        # Draw cookie with gradient for better appearance
        gradient = QRadialGradient(
            self.cookie_x, self.cookie_y, self.cookie_radius
        )
        gradient.setColorAt(0, QColor(180, 100, 60))
        gradient.setColorAt(1, QColor(140, 70, 30))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            self.cookie_x - self.cookie_radius, 
            self.cookie_y - self.cookie_radius, 
            self.cookie_radius * 2, 
            self.cookie_radius * 2
        )
        
        # Draw chocolate chips
        painter.setBrush(QColor(50, 25, 0))
        for i in range(5):
            chip_x = self.cookie_x + (random.random() - 0.5) * self.cookie_radius
            chip_y = self.cookie_y + (random.random() - 0.5) * self.cookie_radius
            chip_size = random.randint(3, 8)
            painter.drawEllipse(
                int(chip_x - chip_size/2),
                int(chip_y - chip_size/2),
                chip_size,
                chip_size
            )

class GuessTheEmojiGame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guess the Emoji")
        self.setFixedSize(400, 300)
        self.emoji_data = [
            ("This emoji is shy and pink. What is it?", ["😊", "🥺", "😳"], 2),
            ("Which one is the party emoji?", ["🎉", "😴", "🍎"], 0),
            ("Which is the cat?", ["🐶", "🐱", "🐭"], 1),
            ("Which emoji represents laughter?", ["😂", "😢", "😡"], 0),
            ("Which emoji shows surprise?", ["😴", "😮", "😎"], 1),
            ("Which emoji is about food?", ["🏠", "🚗", "🍕"], 2),
        ]
        self.qidx = random.randint(0, len(self.emoji_data)-1)
        self.desc, self.options, self.answer = self.emoji_data[self.qidx]
        from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLabel, QHBoxLayout
        layout = QVBoxLayout()
        self.label = QLabel(self.desc)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        btns = QHBoxLayout()
        for i, emoji in enumerate(self.options):
            btn = QPushButton(emoji)
            btn.setFont(QFont("Arial", 24))
            btn.clicked.connect(lambda checked, idx=i: self.check(idx))
            btns.addWidget(btn)
        layout.addLayout(btns)
        self.setLayout(layout)
        self.show()
    def check(self, idx):
        if idx == self.answer:
            QMessageBox.information(self, "Result", "Correct! 🎉")
        else:
            QMessageBox.information(self, "Result", "Nope! The answer was: " + self.options[self.answer])
        self.close()

class DrawModeGame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Draw Mode")
        self.setFixedSize(600, 400)
        self.setStyleSheet("background-color: white;")
        
        # Drawing properties
        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = Qt.black
        self.pen_width = 4
        
        # Create a QImage for direct drawing (more reliable than QPixmap for this use case)
        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Timer label
        self.timer_label = QLabel("Time left: 30s")
        self.timer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.timer_label)
        
        # Add spacer to push controls to bottom
        layout.addStretch()
        
        # Bottom controls
        controls_layout = QHBoxLayout()
        
        # Color button
        color_btn = QPushButton("Change Color")
        color_btn.clicked.connect(self.change_color)
        
        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_drawing)
        
        # Save button
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_drawing)
        
        controls_layout.addWidget(color_btn)
        controls_layout.addWidget(clear_btn)
        controls_layout.addWidget(save_btn)
        
        layout.addLayout(controls_layout)
        self.setLayout(layout)
        
        # Timer setup - 30 seconds
        self.time_left = 30
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        
        # Show drawing instructions
        QTimer.singleShot(500, lambda: QMessageBox.information(
            self, "Draw Mode", "Click and drag to draw. You have 30 seconds!"))
    
    def update_timer(self):
        """Update the countdown timer"""
        self.time_left -= 1
        self.timer_label.setText(f"Time left: {self.time_left}s")
        if self.time_left <= 0:
            self.timer.stop()
            self.save_drawing_prompt()
    
    def save_drawing_prompt(self):
        """Ask user if they want to save the drawing when time is up"""
        reply = QMessageBox.question(
            self, "Time's up!",
            "Your drawing time has ended! Would you like to save your artwork?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
        if reply == QMessageBox.Yes:
            self.save_drawing()
        self.close()
    
    def change_color(self):
        """Open color dialog to change pen color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.pen_color = color
    
    def save_drawing(self):
        """Save the drawing to a file"""
        try:
            from datetime import datetime
            from os.path import join, dirname, abspath
            
            # Use absolute path in the current directory
            dir_path = dirname(abspath(__file__))
            filename = join(dir_path, f"vee_drawing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
            # Save with error handling
            if self.image.save(filename, "PNG"):
                QMessageBox.information(self, "Saved", f"Artwork saved as {filename}")
            else:
                QMessageBox.warning(self, "Error", "Could not save the image")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not save: {str(e)}")
    
    def clear_drawing(self):
        """Clear the canvas"""
        self.image.fill(Qt.white)
        self.update()  # Trigger repaint
    
    def mousePressEvent(self, event):
        """Handle mouse press events for drawing"""
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for drawing"""
        if self.drawing and event.buttons() & Qt.LeftButton:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.pen_color, self.pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.last_point, event.pos())
            
            # Update the last point
            self.last_point = event.pos()
            
            # Update only the rectangle that needs to be redrawn
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events for drawing"""
        if event.button() == Qt.LeftButton:
            self.drawing = False
    
    def paintEvent(self, event):
        """Paint the canvas onto the widget"""
        canvas_painter = QPainter(self)
        canvas_painter.drawImage(0, 0, self.image)

class RapidClickGame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rapid Click Challenge")
        self.setFixedSize(400, 220)
        self.clicks = 0
        
        # Get high score from config
        config = load_config()
        self.high_score = config["high_scores"]["rapid_click"]
        
        self.running = False
        from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLabel
        layout = QVBoxLayout()
        self.label = QLabel("How many times can you click in 5 seconds?")
        self.label.setAlignment(Qt.AlignCenter)
        self.score_label = QLabel(f"Clicks: 0 | High Score: {self.high_score}")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.btn = QPushButton("Start!")
        self.btn.clicked.connect(self.start_game)
        layout.addWidget(self.label)
        layout.addWidget(self.score_label)
        layout.addWidget(self.btn)
        self.setLayout(layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.end_game)
        self.show()
    def start_game(self):
        self.clicks = 0
        self.score_label.setText(f"Clicks: 0 | High Score: {self.high_score}")
        self.btn.setText("Click me!")
        self.btn.clicked.disconnect()
        self.btn.clicked.connect(self.count_click)
        self.running = True
        self.timer.start(5000)
    def count_click(self):
        if self.running:
            self.clicks += 1
            self.score_label.setText(f"Clicks: {self.clicks} | High Score: {self.high_score}")
    def end_game(self):
        self.running = False
        self.btn.setText("Start!")
        self.btn.clicked.disconnect()
        self.btn.clicked.connect(self.start_game)
        msg = f"You got {self.clicks} clicks! "
        
        # Update high score in config if necessary
        config = load_config()
        if self.clicks > self.high_score:
            self.high_score = self.clicks
            config["high_scores"]["rapid_click"] = self.clicks
            save_config(config)
            msg += "New high score! 🥳"
        else:
            msg += random.choice(["Try again!", "You can do better!", "Not bad!"])
        QMessageBox.information(self, "Result", msg)
        self.close()

# ---------- Main Desktop Buddy Class ----------
class DesktopBuddy(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        
        self.setWindowTitle("Desktop Buddy Plus")
        self.setAttribute(Qt.WA_QuitOnClose, False)  # Prevent quitting when game closes
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(240, 270)

        # System tray icon
        self.setup_tray_icon()

        # --- Drag Bar (transparent, easy drag) ---
        self.drag_bar = QLabel(self)
        self.drag_bar.setGeometry(0, 200, 240, 30)
        self.drag_bar.setStyleSheet("background: rgba(0,0,0,0.01);")
        self.drag_bar.setCursor(Qt.OpenHandCursor)
        self.drag_bar.lower()

        # --- Image ---
        self.label = QLabel(self)
        self.update_buddy_image(self.config["buddy_image"])
        self.label.setGeometry(20, 10, 200, 200)

        # --- Speech Bubble (bigger, word wrap, dynamic font) ---
        self.text = QLabel("", self)
        # Fix: Properly position the speech bubble
        self.text.setGeometry(10, 210, 220, 50)
        self.apply_theme()
        self.text.setFont(QFont("Arial", 11))
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setWordWrap(True)

        # For dragging
        self.drag_pos = None

        # Mood meter
        self.mood = 0

        # Timer to check active app - more frequent checks (1.5s instead of 3s)
        self.last_check = ""
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_foreground_window)
        self.timer.start(1500)

        # Resource monitor
        self.resource_timer = QTimer()
        self.resource_timer.timeout.connect(self.monitor_resources)
        self.resource_timer.start(30000)  # Check every 30 seconds

        # Idle detection
        self.last_activity = time.time()
        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self.check_idle)
        self.idle_timer.start(30000)  # Check every 30 seconds

        # Fix: Reset and restart keyboard listener to ensure it works
        try:
            # Create a new keyboard listener with error handling
            self.listener = None  # Release any existing listener
            self.listener = keyboard.Listener(on_press=self.on_keypress)
            self.listener.daemon = True  # Allow clean exit
            self.listener.start()
        except Exception as e:
            print(f"Error setting up keyboard listener: {e}")
            # Fallback method
            self.keyboard_timer = QTimer()
            self.keyboard_timer.timeout.connect(self.check_keyboard_fallback)
            self.keyboard_timer.start(100)  # Poll frequently
            
        self.typed_buffer = ""
        self.easter_buffer = ""

        # Fix: Reset and restart mouse listener
        try:
            self.mouse_listener = None  # Release any existing listener
            self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move, on_click=self.on_mouse_click)
            self.mouse_listener.daemon = True  # Allow clean exit
            self.mouse_listener.start()
        except Exception as e:
            print(f"Error setting up mouse listener: {e}")

        # Animation setup
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setEasingCurve(QEasingCurve.OutBounce)
        self.animation.setDuration(1000)

        # Install event filter for mouse clicks on buddy
        self.installEventFilter(self)
        
        # Show welcome message on startup if enabled
        if self.config["startup_message"]:
            QTimer.singleShot(1000, lambda: self.say("Hello! Desktop Buddy is active!"))
            
        # Verify functionality by showing a test message
        QTimer.singleShot(2000, lambda: self.say("Reactive messages activated!"))

    def update_buddy_image(self, image_path):
        """Update the buddy's image"""
        try:
            pixmap = QPixmap(image_path).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)
        except Exception as e:
            print(f"Error loading image: {e}")
            # Try to load default image as fallback
            try:
                pixmap = QPixmap("buddy2.png").scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.label.setPixmap(pixmap)
            except:
                pass

    def apply_theme(self):
        """Apply the current theme to UI elements"""
        theme_name = self.config.get("theme", "default")
        theme = THEMES.get(theme_name, THEMES["default"])
        
        # Set neutral state initially
        self.text.setStyleSheet(
            f"color: {theme['text_color']}; "
            f"background: {theme['neutral_bubble']}; "
            f"border-radius: 12px; "
            f"padding: 8px;"
        )

    def setup_tray_icon(self):
        """Set up system tray icon and menu"""
        try:
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon("buddy.png"))
            
            tray_menu = QMenu()
            show_action = tray_menu.addAction("Show Buddy")
            show_action.triggered.connect(self.show_and_raise)
            
            theme_menu = tray_menu.addMenu("Themes")
            for theme in THEMES:
                theme_action = theme_menu.addAction(theme.capitalize())
                theme_action.triggered.connect(lambda checked, t=theme: self.change_theme(t))
            
            toggle_startup_message = tray_menu.addAction("Toggle Startup Message")
            toggle_startup_message.triggered.connect(self.toggle_startup_message)
            
            switch_image = tray_menu.addAction("Switch Buddy Image")
            switch_image.triggered.connect(self.toggle_buddy_image)
            
            exit_action = tray_menu.addAction("Exit")
            exit_action.triggered.connect(self.exit_app)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
        except Exception as e:
            print(f"Error setting up tray icon: {e}")

    def show_and_raise(self):
        """Show and raise the buddy window"""
        self.show()
        self.raise_()
        self.activateWindow()

    def change_theme(self, theme_name):
        """Change the theme"""
        if theme_name in THEMES:
            self.config["theme"] = theme_name
            save_config(self.config)
            self.apply_theme()
            self.say(f"Theme changed to {theme_name}!")

    def toggle_startup_message(self):
        """Toggle startup message setting"""
        self.config["startup_message"] = not self.config["startup_message"]
        save_config(self.config)
        status = "enabled" if self.config["startup_message"] else "disabled"
        self.say(f"Startup message {status}!")

    def toggle_buddy_image(self):
        """Toggle between buddy images"""
        current = self.config["buddy_image"]
        alternate = self.config["alternate_image"]
        self.config["buddy_image"] = alternate
        self.config["alternate_image"] = current
        save_config(self.config)
        self.update_buddy_image(self.config["buddy_image"])
        self.say("Image changed!")

    def monitor_resources(self):
        """Check system resources and warn if high"""
        warning_needed, message = check_system_resources()
        if warning_needed:
            self.say(message)

    def do_animation(self):
        """Perform a bounce animation"""
        current_pos = self.pos()
        self.animation.setStartValue(current_pos)
        self.animation.setEndValue(QPoint(current_pos.x(), current_pos.y() - 20))
        self.animation.start()
        QTimer.singleShot(500, lambda: self.animation.setEndValue(current_pos))

    def say(self, msg=None):
        """Display a message in the speech bubble with mood-based styling"""
        if not msg:
            return
            
        # Get current theme
        theme_name = self.config.get("theme", "default")
        theme = THEMES.get(theme_name, THEMES["default"])
        
        # Mood-based personality
        now = time.localtime()
        hour = now.tm_hour
        if hour >= 23 and hour < 24:
            if not msg in late_night_msgs:
                msg = random.choice(late_night_msgs)
        elif hour >= 2 and hour < 5:
            if not msg in shutdown_msgs:
                msg = random.choice(shutdown_msgs)
        elif self.mood <= -7:
            if not msg in roast_msgs:
                msg = random.choice(roast_msgs)
            # Calm down cooldown
            QTimer.singleShot(4000, lambda: self.text.setText(random.choice(calm_down_msgs)))
        elif self.mood >= 7:
            if not msg in hype_msgs:
                msg = random.choice(hype_msgs)
            QTimer.singleShot(4000, lambda: self.text.setText(random.choice(calm_down_msgs)))
            
        # Set bubble color based on mood
        if self.mood >= MOOD_POSITIVE:
            bg = theme["positive_bubble"]
        elif self.mood <= MOOD_NEGATIVE:
            bg = theme["negative_bubble"]
        else:
            bg = theme["neutral_bubble"]
            
        # Apply the styling to make sure the bubble is visible
        self.text.setStyleSheet(
            f"color: {theme['text_color']}; "
            f"background: {bg}; "
            f"border-radius: 12px; "
            f"padding: 8px;"
        )
        
        # Dynamic font size for long messages
        if len(msg) > 60:
            self.text.setFont(QFont("Arial", 9))
        else:
            self.text.setFont(QFont("Arial", 11))
        
        # Set the text and make sure speech bubble is properly positioned
        self.text.setText(personalize(msg))
        self.text.adjustSize()
        self.text.setGeometry(10, 210, 220, 50)
        self.text.show()
        self.text.raise_()
        
        # Perform animation to draw attention
        self.do_animation()
        
        # Auto-clear message after delay
        QTimer.singleShot(4000, lambda: self.text.setText(""))

    def check_foreground_window(self):
        """Check the currently active window and respond accordingly"""
        try:
            # Get active window more reliably
            win = None
            try:
                win = gw.getActiveWindow()
            except:
                try:
                    # Alternative method to get active window
                    windows = gw.getAllWindows()
                    for window in windows:
                        if window.isActive:
                            win = window
                            break
                except:
                    pass

            if win:
                # Convert to lowercase with error handling
                try:
                    title = win.title.lower() if hasattr(win, 'title') else ""
                except:
                    title = ""
                    
                app = "other"
                
                # Check for code editors
                for name in vs_code_names:
                    if name.lower() in title:
                        app = "code"
                        break
                        
                # Check for browsers
                for name in browser_names:
                    if name.lower() in title:
                        app = "browser"
                        break
                        
                # Only trigger if application focus has changed
                if app != self.last_check:
                    self.last_check = app
                    msg = random.choice(focus_msgs.get(app, focus_msgs["other"]))
                    self.say(msg)
                    # Mood logic
                    if app == "code":
                        self.change_mood(2)
                    elif app == "browser":
                        self.change_mood(-2)
                    else:
                        self.change_mood(-1)
        except Exception as e:
            print(f"Error checking window: {e}")
    
    def check_keyboard_fallback(self):
        """Fallback method if pynput keyboard listener fails"""
        import ctypes
        keys = [
            0x08, # BACKSPACE
            0x0D, # ENTER
            0x20, # SPACE
            0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, # 0-9
            0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A, 0x4B, 0x4C,
            0x4D, 0x4E, 0x4F, 0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58,
            0x59, 0x5A # A-Z
        ]
        
        for key in keys:
            is_pressed = ctypes.windll.user32.GetAsyncKeyState(key) & 0x8000 != 0
            if is_pressed:
                char = chr(key) if key >= 0x30 and key <= 0x5A else ""
                if char:
                    self.typed_buffer += char.lower()
                    self.typed_buffer = self.typed_buffer[-20:]
                    self.easter_buffer += char.lower()
                    self.easter_buffer = self.easter_buffer[-20:]
                    self.last_activity = time.time()
                    
                    # Check for trigger words
                    self.process_typed_text()
                    return

    def process_typed_text(self):
        """Process the typed buffer for triggers and easter eggs"""
        global recent_combo, recent_combo_time
        
        # Secret combos
        for combo in secret_combos:
            if combo in self.typed_buffer.lower():
                recent_combo = combo
                recent_combo_time = time.time()
                self.say(secret_combos[combo])
                self.typed_buffer = ""
                return
                
        # Easter egg triggers
        for egg in easter_eggs:
            if egg in self.easter_buffer.lower():
                self.say(random.choice(easter_eggs[egg]))
                self.easter_buffer = ""
                return
                
        # Normal triggers
        for word in trigger_words:
            if word in self.typed_buffer.lower():
                reply = random.choice(trigger_replies.get(word, ["..."]))
                self.say(reply)
                self.change_mood(1)
                self.typed_buffer = ""
                return

    def on_keypress(self, key):
        """Process keyboard input for triggers and easter eggs"""
        try:
            if hasattr(key, 'char') and key.char:
                c = key.char
                self.typed_buffer += c
                self.typed_buffer = self.typed_buffer[-20:]
                self.easter_buffer += c
                self.easter_buffer = self.easter_buffer[-20:]
                # Reset idle timer
                self.last_activity = time.time()
                
                # Process the typed text for triggers
                self.process_typed_text()
        except Exception as e:
            print(f"Error processing keypress: {e}")

    def on_mouse_move(self, x, y):
        """Update activity timestamp on mouse movement"""
        self.last_activity = time.time()

    def on_mouse_click(self, x, y, button, pressed):
        """Update activity timestamp on mouse click"""
        if pressed:
            self.last_activity = time.time()

    def check_idle(self):
        """Check for user inactivity"""
        idle_threshold = 120  # 2 minutes
        if time.time() - self.last_activity > idle_threshold:
            self.say(random.choice(idle_msgs))
            self.change_mood(-2)
            self.last_activity = time.time()  # Prevent spamming

    def change_mood(self, delta):
        """Update mood value within limits"""
        old_mood = self.mood
        self.mood = max(MOOD_MIN, min(MOOD_MAX, self.mood + delta))
        
        # Apply theme if mood crossed a threshold
        if (old_mood >= 0 and self.mood < 0) or (old_mood <= 0 and self.mood > 0):
            self.apply_theme()

    def eventFilter(self, obj, event):
        """Handle events for the entire widget"""
        # Make entire window right-clickable for menu
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.RightButton:
                self.show_menu(event.globalPos())
                return True
            # Click on buddy image still cheers
            if event.button() == Qt.LeftButton and self.label.geometry().contains(event.pos()):
                self.change_mood(1)
                self.say("Hey! Thanks for the click.")
                self.do_animation()
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.RightButton:
            self.show_menu(event.globalPos())
        elif event.button() == Qt.LeftButton:
            # Allow drag from anywhere or drag bar
            if self.drag_bar.geometry().contains(event.pos()) or self.label.geometry().contains(event.pos()) or self.text.geometry().contains(event.pos()):
                self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move events for dragging"""
        if self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        self.drag_pos = None

    def show_menu(self, pos):
        """Show the right-click context menu"""
        menu = QMenu()
        
        # Games submenu
        games_menu = menu.addMenu("Games")
        cookie_action = games_menu.addAction("Catch the Cookie")
        emoji_action = games_menu.addAction("Guess the Emoji")
        draw_action = games_menu.addAction("Draw Mode")
        rapid_action = games_menu.addAction("Rapid Click Challenge")
        
        # Settings submenu
        settings_menu = menu.addMenu("Settings")
        
        # Theme selection
        theme_menu = settings_menu.addMenu("Themes")
        for theme_name in THEMES:
            theme_action = theme_menu.addAction(theme_name.capitalize())
            theme_action.triggered.connect(lambda checked, t=theme_name: self.change_theme(t))
        
        # Image toggle
        image_action = settings_menu.addAction("Switch Buddy Image")
        image_action.triggered.connect(self.toggle_buddy_image)
        
        # Toggle startup message
        msg_action = settings_menu.addAction("Toggle Startup Message")
        msg_action.triggered.connect(self.toggle_startup_message)
        
        # Secret menu if combo recently typed
        global recent_combo, recent_combo_time
        if recent_combo and time.time() - recent_combo_time < 30:
            secret_action = menu.addAction("Reveal Secret")
        else:
            secret_action = None
            
        exit_action = menu.addAction("Exit Buddy")
        
        action = menu.exec_(pos)
        
        # Process menu selection
        if action == cookie_action:
            self.launch_mini_game('cookie')
        elif action == emoji_action:
            self.launch_mini_game('emoji')
        elif action == draw_action:
            self.launch_mini_game('draw')
        elif action == rapid_action:
            self.launch_mini_game('rapid')
        elif secret_action and action == secret_action:
            self.say(secret_combos[recent_combo])
            recent_combo = None
        elif action == exit_action:
            self.exit_app()

    def exit_app(self):
        """Clean exit of the application"""
        try:
            self.listener.stop()
            self.mouse_listener.stop()
            QApplication.quit()
        except:
            QApplication.quit()
    
    def launch_mini_game(self, which):
        """Launch a mini game with improved error handling"""
        try:
            print(f"Attempting to launch game: {which}")
            game_window = None
            
            if which == 'cookie':
                game_window = CatchTheCookieGame(None)
            elif which == 'emoji':
                game_window = GuessTheEmojiGame(None)
            elif which == 'draw':
                # Debug info to trace potential issues
                print("Starting Draw Mode Game")
                game_window = DrawModeGame(None)
                print("Draw Mode Game initialized")
            elif which == 'rapid':
                game_window = RapidClickGame(None)
            
            if game_window:
                game_window.setAttribute(Qt.WA_DeleteOnClose, True)
                self.game_window = game_window  # Keep reference to prevent garbage collection
                self.game_window.show()
                print(f"Game '{which}' launched successfully")
            else:
                print(f"Game window for '{which}' could not be created")
                self.say(f"Couldn't start {which} game!")
                
        except Exception as e:
            import traceback
            print(f"Error launching {which} game: {e}")
            print(traceback.format_exc())
            self.say(f"Oops! Couldn't start the {which} game.")

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)

        global persistent_buddy_window
        persistent_buddy_window = DesktopBuddy()
        persistent_buddy_window.setWindowFlag(Qt.Window, True)
        persistent_buddy_window.setAttribute(Qt.WA_QuitOnClose, False)
        persistent_buddy_window.raise_()
        persistent_buddy_window.activateWindow()
        persistent_buddy_window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Critical error: {e}")
        sys.exit(1)
