# VEE - Virtual Electronic Entity

![VEE Desktop Buddy](buddy.png)

VEE is an interactive desktop companion application that provides entertainment, helpful notifications, and engagement while you work. It features a customizable desktop buddy that responds to your activities, offers mini-games for breaks, and adds a touch of personality to your computing experience.

## Features

- **Interactive Desktop Buddy**: Responds to your activities with personalized speech bubbles
- **Multiple Themes**: Choose from default, dark, or pastel color schemes
- **Application Awareness**: Detects when you switch between applications and responds accordingly
- **System Resource Monitoring**: Alerts you when CPU or memory usage is high
- **Mini-Games**: Take a break with four built-in games
- **Easter Eggs**: Discover hidden responses by typing certain keywords
- **Idle Detection**: VEE notices when you've been away and will comment when you return
- **Customizable Appearance**: Switch between different buddy images
- **System Tray Integration**: Easy access to settings and features
- **Drawing Tool**: Create and save quick sketches

## Installation

1. Make sure you have Python 3.8+ installed on your system
2. Clone this repository or download the source files
3. Create a virtual environment (recommended):
   ```
   python -m venv env
   ```
4. Activate the virtual environment:
   - Windows: `env\Scripts\activate`
   - macOS/Linux: `source env/bin/activate`
5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python vee.py
   ```

2. VEE will appear on your desktop with a welcome message
3. Right-click on VEE to access the menu with games and settings
4. Drag VEE to position it anywhere on your desktop
5. VEE will stay on top of other windows but you can minimize it to the system tray

## Configuration

VEE uses a configuration file (`vee_config.json`) that stores your preferences:

- Buddy images
- High scores for games
- Theme preferences
- Notification settings
- Startup message toggle

The configuration is automatically created on first launch and updated when you change settings.

## Mini-Games

VEE includes four mini-games to help you take productive breaks:

1. **Catch the Cookie**: Test your reflexes by catching a falling cookie
2. **Guess the Emoji**: A simple emoji quiz game
3. **Draw Mode**: Express your creativity with a simple drawing tool (saves drawings automatically)
4. **Rapid Click Challenge**: Test your clicking speed in 5 seconds

Access games by right-clicking on VEE and selecting from the Games menu.

## Easter Eggs

VEE responds to certain keywords and phrases when typed anywhere on your system, including:

- Common expressions: "lol", "bruh", "omg", etc.
- Special topics: "cat", "python", "love", etc.
- Secret commands: Try typing "themeswap" for a surprise!

## System Requirements

- Windows OS (primary support)
- Python 3.8 or higher
- Dependencies (automatically installed):
  - PyQt5: UI framework
  - pynput: For keyboard and mouse tracking
  - psutil: For system resource monitoring
  - pygetwindow: For detecting active applications

## Contributing

Feel free to fork this project and submit pull requests with improvements or bug fixes.

## License

[MIT License](LICENSE) - Feel free to use and modify this project for personal or commercial purposes.

## Screenshots

The repository includes several screenshots of VEE in action:
- VEE's normal appearance
- Drawing tool examples
- Different themes and buddy images

---

Made with ❤️ by L1ght | April 2025 | Virtual Electronic Entity Project