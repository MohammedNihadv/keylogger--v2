# Advanced Keylogger Tool V2

A powerful and flexible keylogger tool with modular architecture. It tracks user activity, Capture photos, system performance, and hardware status, while ensuring security, maintainability, and flexibility for various use cases such as security testing, system monitoring, and educational purposes.

```
 _                 _                                       ______  
| |               | |                                     (_____ \ 
| |  _ _____ _   _| | ___   ____  ____ _____  ____    _   _ ____) )
| |_/ ) ___ | | | | |/ _ \ / _  |/ _  | ___ |/ ___)  | | | / ____/ 
|  _ (| ____| |_| | | |_| ( (_| ( (_| | ____| |       \ V / (_____ 
|_| \_)_____)\__  |\_)___/ \___ |\___ |_____)_|        \_/|_______)
            (____/        (_____(_____|


```
---

## Installation

Follow these steps to get the **Advanced System Monitoring Tool V2** up and running.

### Prerequisites

Ensure you have **Python 3.8+** installed on your system. Additionally, you'll need to install **pip** to manage dependencies.

### Step 1: Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/MohammedNihadv/keylogger--v2
cd keylogger--v2
```
### Step 2: Telegram Settings
**To configure the Telegram integration, you need to set up your Telegram bot and chat ID.**

Steps to Configure Telegram:

**Create a Telegram Bot:**

```Open the @BotFather on Telegram and follow the instructions to create a new bot. You will receive a token for your bot.```

**Find Your Chat ID:**

```To get your chat ID, You can use a bot like @userinfobot to quickly get your chat ID Also can use the Alernatives.```

**Configure Telegram Settings:**

Open the keylogger.py script and update the following settings with your bot's token and your chat ID:

**# Telegram settings : LINE 66**
```
        self.telegram_token = "YOUR_BOT_TOKEN"
        self.telegram_chat_id = YOUR_CHAT_ID  # Remove quotes, should be an integer
        self.upload_interval = 60  # seconds
```

### Step 3: Install Dependencies

Once inside the project directory, install all the required dependencies using **pip**. This will automatically install all the necessary Python packages to support the tool's functionalities:

```bash
pip install pynput==1.7.6 Pillow==10.0.0 pyaudio==0.2.13 psutil==5.9.5 rich==13.5.2 watchdog==3.0.0 python-telegram-bot==20.7 opencv-python==4.8.0
```

Alternatively, you can install the dependencies from the **requirements.txt** file by using:

```bash
pip install -r requirements.txt
```

### Step 4: Run the Tool

Once the dependencies are installed, you can start using the system monitoring tool.

To launch the tool with all default features enabled:

```bash
python keylogger.py
```
### Step 5: Stop From Running

```
Press ESC
or 
Ctrl + C To Cancel
```

You can customize the behavior using command-line options as mentioned in the **Usage** section.

---

## Features

### Core Monitoring
- **Keystroke Logging**: Records all keyboard inputs, including timestamps.
- **Screenshot Capture**: Periodically takes screenshots with customizable intervals.
- **Webcam Capture**: Captures high-quality webcam photos at set intervals.
- **Audio Recording**: Captures audio in 50-second chunks, saving in WAV format.
- **Mouse Tracking**: Monitors mouse movements, clicks, and scrolling actions.
- **Filesystem Monitoring**: Tracks file system changes, including file creation, modification, and deletions.
- **System Information**: Gathers essential system and hardware information (CPU, memory, etc.).
- **Telegram Integration**: Seamless integration with Telegram for automatic file upload.

### Advanced Features
- **Change Detection**: Takes screenshots only when screen content changes.
- **Active Window Tracking**: Capture only the active window's content.
- **Performance Metrics**: Monitors CPU, memory, and disk usage for resource tracking.
- **Configurable Settings**: Fine-tune the system through extensive command-line options.
- **Rich Console Interface**: Real-time monitoring displayed on the terminal.
- **Auto-Recovery**: Ensures system recovery after failure with automatic retries.

---

## Project Structure

```bash
system-monitor/
├── keylogger.py         # Main monitoring script
├── modules/             # Modular components like keystroke logger, webcam capture, etc.
├── logs/                # Output directory for logs and captured data
├── config.json          # Config file for tool customization
├── utils.py             # Helper utilities
└── README.md            # Documentation
```

---

## Usage

### Basic Command
Run the tool with all default monitoring features enabled:
```bash
python keylogger.py
```

### Command Line Options
You can customize your monitoring preferences using the following options:

```bash
python keylogger.py [OPTIONS]
```

**Available Options:**

- `-k, --no-keylog`: Disable keylogging
- `-s, --no-screenshots`: Disable screenshot capture
- `-a, --no-audio`: Disable audio recording
- `-c, --no-camera`: Disable webcam capture
- `-i, --interval <seconds>`: Set the screenshot capture interval (default: 10)
- `--camera-interval <seconds>`: Set the webcam capture interval (default: 30)
- `--camera-resolution <width>x<height>`: Configure webcam resolution (default: 1280x720)
- `--output-dir <directory>`: Specify a custom output directory
- `--stealth`: Enable stealth mode (runs without showing console output)
- `--mouse`: Enable mouse tracking
- `--filesystem`: Enable filesystem monitoring
- `--performance`: Enable performance monitoring (CPU, memory, disk usage)
- `--screenshot-changes`: Only capture screenshots when the screen content changes
- `--active-window`: Capture only the active window

### Example Commands

#### Run with all features enabled:
```bash
python keylogger.py --mouse --filesystem --performance
```

#### Custom webcam settings:
```bash
python keylogger.py --camera-interval 60 --camera-resolution 1920x1080
```

#### Stealth mode, with keylogging and other features disabled:
```bash
python keylogger.py --stealth --no-screenshots --no-audio --no-camera
```

---

## Output Directory Structure

The data generated by the tool will be saved in the `monitoring_output/` directory.

```bash
monitoring_output/
├── screenshots/
│   ├── screenshot_YYYY-MM-DD_HH-MM-SS.png
│   └── change_YYYY-MM-DD_HH-MM-SS.png
├── camera/
│   └── camera_YYYY-MM-DD_HH-MM-SS.jpg
├── audio/
│   └── audio_YYYY-MM-DD_HH-MM-SS.wav
├── key_log.txt
├── mouse_log.txt
├── file_changes.log
├── performance.log
└── system_info.json
```

- **screenshots/**: Stores screenshots (both periodic and content-based).
- **camera/**: Stores captured webcam images.
- **audio/**: Stores recorded audio files.
- **key_log.txt**: Logs keystrokes captured by the keylogger.
- **mouse_log.txt**: Logs mouse movement, clicks, and scroll actions.
- **file_changes.log**: Logs file and directory changes detected by the filesystem monitoring.
- **performance.log**: Logs system resource metrics (CPU, memory, disk usage).
- **system_info.json**: Contains detailed information about the system configuration.

---

## Features in Detail

### Keystroke Logging
- Records all keystrokes, including special keys (Ctrl, Alt, Shift).
- Can handle key event timestamps.
- Customizable log file location.

### Screenshot Capture
- Periodic screenshots or change-based screenshot captures.
- Supports capturing the entire screen or only the active window.
- Adjustable capture interval.

### Webcam Capture
- HD webcam photos (default 1280x720 resolution).
- Configurable resolution and capture intervals.
- Efficient error recovery and minimal resource consumption.

### Audio Recording
- Records audio in 50-second intervals.
- Stores audio in WAV format.
- Customizable chunk size for audio recording.

### Mouse Tracking
- Logs mouse movements (coordinates), clicks, and scrolls.
- Captures the timestamp of each event.

### Filesystem Monitoring
- Tracks file and directory creation, deletion, and modification events.
- Supports recursive directory monitoring.

### Telegram Integration
- Automatically uploads captured files to a specified Telegram channel or bot.
- Configurable upload interval and progress tracking.

### Performance Monitoring
- Monitors CPU usage, memory consumption, and disk usage in real-time.
- Collects detailed resource data to assist in performance analysis.

---

## Legal Notice

This tool is intended for ethical purposes only, including:
- **Security Testing**
- **System Monitoring**
- **Parental Control**
- **Educational Purposes**

**Important**: Always obtain explicit consent before deploying this tool. Unauthorized surveillance or data collection may violate privacy laws.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
