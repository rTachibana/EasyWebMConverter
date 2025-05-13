import os
import sys
import datetime
import subprocess
import time
import re
import locale
import platform

# Get script root directory
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add src directory to path so we can import config
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.append(src_dir)

# Now import config
import config

# Check platform
is_windows = platform.system() == "Windows"

# Set FFmpeg path based on platform
if is_windows:
    FFMPEG_PATH = os.path.join(script_dir, 'ffmpeg', 'bin', 'ffmpeg.exe')
else:
    FFMPEG_PATH = os.path.join(script_dir, 'ffmpeg', 'bin', 'ffmpeg')

# Get system encoding
SYSTEM_ENCODING = locale.getpreferredencoding()

# Presets
SIZE_PRESETS = {
    "1": {"name": "Original", "value": "original"},
    "2": {"name": "HD (1280p max)", "value": "1280:-1"},
    "3": {"name": "SD (720p max)", "value": "720:-1"},
    "4": {"name": "Small (480p max)", "value": "480:-1"},
    "5": {"name": "Tiny (360p max)", "value": "360:-1"}
}

BITRATE_PRESETS = {
    "1": {"name": "Auto (Quality-based)", "value": "auto"},
    "2": {"name": "High Quality (2Mbps)", "value": "2M"},
    "3": {"name": "Standard (1Mbps)", "value": "1M"},
    "4": {"name": "Low Quality (500kbps)", "value": "500k"}
}

FORMAT_PRESETS = {
    "1": {"name": "MP4 (H.264)", "ext": "mp4", "codec": "libx264"},
    "2": {"name": "WebM (VP9)", "ext": "webm", "codec": "libvpx-vp9"}
}

def ensure_output_dir():
    """Ensure output directory exists"""
    # 設定ファイルから出力ディレクトリを取得
    output_dir = config.get_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def get_output_filename(ext):
    """Generate output filename with timestamp"""
    # 設定ファイルからファイル名テンプレートを使用
    return config.get_output_filename(ext)

def parse_duration(ffmpeg_output):
    """Parse video duration from FFmpeg output"""
    duration_match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})", ffmpeg_output)
    if duration_match:
        hours, minutes, seconds, centiseconds = map(int, duration_match.groups())
        return hours * 3600 + minutes * 60 + seconds + centiseconds / 100
    return 0

def parse_time(time_str):
    """Parse current time from FFmpeg progress output"""
    time_match = re.search(r"time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})", time_str)
    if time_match:
        hours, minutes, seconds, centiseconds = map(int, time_match.groups())
        return hours * 3600 + minutes * 60 + seconds + centiseconds / 100
    return 0

def get_video_info(input_file):
    """Get video information including width, height"""
    if not os.path.exists(input_file):
        return None
    
    try:
        cmd = [FFMPEG_PATH, "-i", input_file]
        startupinfo = None
        if is_windows:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            encoding=SYSTEM_ENCODING,
            startupinfo=startupinfo
        )
        _, stderr = process.communicate()
        
        # Parse video dimensions
        video_pattern = re.search(r"Stream .* Video:.* (\d+)x(\d+)", stderr)
        if video_pattern:
            width = int(video_pattern.group(1))
            height = int(video_pattern.group(2))
            return {"width": width, "height": height}
    except Exception as e:
        print(f"Warning: Could not determine video dimensions: {str(e)}")
    
    return None

def encode_video(input_file, size_preset, bitrate_preset, format_preset, progress_callback=None):
    """Encode video"""
    if not os.path.exists(input_file):
        return False, f"Input file not found: {input_file}"
    
    if not os.path.exists(FFMPEG_PATH):
        return False, f"FFmpeg not found at: {FFMPEG_PATH}\nPlease run setup script"
    
    # 設定ファイルから出力ディレクトリを取得
    output_dir = ensure_output_dir()
    output_file = get_output_filename(format_preset["ext"])
    
    # Get video duration and info
    try:
        duration_cmd = [FFMPEG_PATH, "-i", input_file]
        # Use subprocess with proper shell handling for multibyte characters
        # Create process with proper encoding handling
        startupinfo = None
        if is_windows:
            # Hide console window on Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        duration_process = subprocess.Popen(
            duration_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            encoding=SYSTEM_ENCODING,
            startupinfo=startupinfo
        )
        _, stderr = duration_process.communicate()
        
        duration = parse_duration(stderr)
        if progress_callback and duration > 0:
            progress_callback(f"Video duration: {int(duration // 60)}m {int(duration % 60)}s")
    except Exception as e:
        print(f"Warning: Could not determine video duration: {str(e)}")
        duration = 0
    
    # Build command
    cmd = [FFMPEG_PATH, "-i", input_file, "-v", "warning", "-stats"]
    
    # Size setting
    if size_preset != "original":
        # Handle special size presets that maintain aspect ratio
        if ":-1" in size_preset:
            # Format is either "width:-1" or "-1:height"
            parts = size_preset.split(":")
            if parts[0] != "-1":  # Width is specified
                cmd.extend(["-vf", f"scale={parts[0]}:{parts[1]}:force_original_aspect_ratio=decrease"])
            else:  # Height is specified
                cmd.extend(["-vf", f"scale={parts[0]}:{parts[1]}:force_original_aspect_ratio=decrease"])
        else:
            # For backward compatibility - fixed resolution (not recommended)
            cmd.extend(["-s", size_preset])
    
    # Format-specific settings
    if format_preset["ext"] == "webm":
        # WebM settings
        cmd.extend(["-c:v", format_preset["codec"]])
        
        # Use CRF for auto bitrate, otherwise specify bitrate
        if bitrate_preset == "auto":
            cmd.extend(["-crf", "30"])  # Default quality for VP9
        else:
            cmd.extend(["-b:v", bitrate_preset, "-crf", "30"])
            
        # Copy audio if possible, otherwise convert to Vorbis
        cmd.extend(["-c:a", "libvorbis"])
    else:
        # MP4 settings
        cmd.extend(["-c:v", format_preset["codec"]])
        
        # Use CRF for auto bitrate, otherwise specify bitrate
        if bitrate_preset == "auto":
            cmd.extend(["-crf", "23"])  # Default quality for H.264
        else:
            cmd.extend(["-b:v", bitrate_preset, "-crf", "23"])
            
        # Copy audio if possible, otherwise convert to AAC
        cmd.extend(["-c:a", "aac"])
    
    # Output file settings
    cmd.extend(["-f", format_preset["ext"], output_file])
    
    try:
        # Execute FFmpeg with proper encoding handling
        startupinfo = None
        if is_windows:
            # Hide console window on Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,  # Redirect stderr to stdout to capture progress
            universal_newlines=True,
            bufsize=1,
            encoding=SYSTEM_ENCODING,
            startupinfo=startupinfo
        )
        
        if progress_callback:
            progress_callback("Encoding started...")
        
        # Read and update progress in real-time
        for line in iter(process.stdout.readline, ''):
            if progress_callback and "time=" in line:
                current_time = parse_time(line)
                if duration > 0:
                    progress_pct = min(100, int((current_time / duration) * 100))
                    progress_callback(f"Progress: {progress_pct}% - {format_preset['name']} encoding")
                else:
                    progress_callback(f"Encoding in progress... {format_preset['name']}")
        
        process.stdout.close()
        return_code = process.wait()
        
        if return_code != 0:
            return False, f"Encoding failed with return code {return_code}"
        
        if progress_callback:
            progress_callback("Encoding complete")

        return True, f"Encoding complete. Output file: {os.path.basename(output_file)}"
    except Exception as e:
        return False, f"Error during encoding: {str(e)}"

def check_ffmpeg():
    """Check if FFmpeg is available"""
    if not os.path.exists(FFMPEG_PATH):
        if is_windows:
            setup_script = "setup.bat"
        else:
            setup_script = "./setup.sh"
        
        print(f"ERROR: FFmpeg not found at: {FFMPEG_PATH}")
        print(f"Please run {setup_script} to automatically download FFmpeg.")
        return False
    return True

def print_header():
    """Print application header"""
    print("=" * 50)
    print("MP4/WebM Encoder")
    print("=" * 50)
    print("This tool helps you convert video files to WebM or MP4 format.")
    output_dir = config.get_output_dir()
    print(f"Output files will be saved to: {output_dir}")
    print("=" * 50)
    print()

def print_menu(menu_items, title, default=None):
    """Print menu and get user selection"""
    print(f"\n{title}:")
    for key, item in menu_items.items():
        default_mark = " (Default)" if key == default else ""
        print(f"{key}. {item['name']}{default_mark}")
    
    choice = input("Enter your choice: ").strip()
    if choice == "" and default:
        return menu_items[default]
    
    while choice not in menu_items:
        print("Invalid choice. Please try again.")
        choice = input("Enter your choice: ").strip()
        if choice == "" and default:
            return menu_items[default]
    
    return menu_items[choice]

def get_input_file():
    """Get input file path from user"""
    while True:
        input_file = input("\nEnter the path to the video file: ").strip()
        
        # Remove quotes if present
        if input_file.startswith('"') and input_file.endswith('"'):
            input_file = input_file[1:-1]
        
        if not input_file:
            print("No file specified. Please enter a valid file path.")
            continue
        
        # Convert to absolute path to handle relative paths
        input_file = os.path.abspath(input_file)
        
        # Handle Unicode paths properly
        try:
            if not os.path.exists(input_file):
                print(f"File not found: {input_file}")
                continue
        except UnicodeEncodeError:
            print("Error with file path encoding. Please try copying the full path directly.")
            continue
        
        return input_file

def print_progress(message):
    """Print progress message"""
    # Use carriage return to update the same line
    print(f"\r{message}".ljust(80), end="", flush=True)

def process_video():
    """Process a single video file"""
    try:
        # Get input file
        input_file = get_input_file()
        
        # Get video information
        video_info = get_video_info(input_file)
        if video_info:
            print(f"Video dimensions: {video_info['width']}x{video_info['height']}")
        
        # Get format preset (設定ファイルからデフォルト値を取得)
        format_preset = print_menu(FORMAT_PRESETS, "Select output format", default=config.get_default_format())
        
        # Get size preset (設定ファイルからデフォルト値を取得)
        size_preset = print_menu(SIZE_PRESETS, "Select output size (aspect ratio will be preserved)", default=config.get_default_size())
        
        # Get bitrate preset (設定ファイルからデフォルト値を取得)
        bitrate_preset = print_menu(BITRATE_PRESETS, "Select bitrate", default=config.get_default_bitrate())
        
        # Start encoding
        print("\nStarting encoding...")
        print(f"Input file: {input_file}")
        print(f"Output format: {format_preset['name']}")
        output_dir = config.get_output_dir()
        print(f"Output directory: {output_dir}")
        
        # Run encoding
        success, message = encode_video(
            input_file, 
            size_preset["value"], 
            bitrate_preset["value"], 
            format_preset,
            progress_callback=print_progress
        )
        
        # Show result
        print("\n")  # Add newline after progress updates
        if success:
            print(f"SUCCESS: {message}")
            print(f"File saved to: {output_dir}")
            
            # 設定ファイルの設定に基づいて出力ディレクトリを開くかどうか確認
            if config.should_show_output_dir_prompt():
                open_dir = input("\nOpen output directory? (y/n): ").strip().lower()
                if open_dir == 'y':
                    try:
                        # Use platform-specific method to open file explorer
                        if is_windows:
                            os.startfile(output_dir)
                        elif platform.system() == "Darwin":  # macOS
                            subprocess.call(['open', output_dir])
                        else:  # Linux
                            subprocess.call(['xdg-open', output_dir])
                    except Exception as e:
                        print(f"Could not open directory: {str(e)}")
        else:
            print(f"ERROR: {message}")
        
        return True
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return False
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        return False

def setup_unicode():
    """Set up Unicode support for the console"""
    if is_windows:
        # Set console code page to UTF-8 on Windows
        try:
            # Try to set console code page to UTF-8
            os.system('chcp 65001 > nul')
        except:
            pass

def main():
    # Setup proper Unicode handling
    setup_unicode()
    
    # 設定ファイルが存在しない場合は作成
    config.create_default_config_if_not_exists()
    
    if not check_ffmpeg():
        sys.exit(1)
    
    print_header()
    
    try:
        continue_processing = True
        
        while continue_processing:
            # Process a video
            process_video()
            
            # 設定ファイルの設定に基づいて次のファイル処理に進むかどうか確認
            if config.should_ask_for_next_file():
                print("\n" + "=" * 50)
                choice = input("Do you want to process another video? (y/n): ").strip().lower()
                continue_processing = choice == 'y'
                
                if continue_processing:
                    print("\n" + "=" * 50)
                    print("Processing next video...")
            # else:
                # 設定でask_for_next_fileがFalseの場合は自動的に終了
                # continue_processing = False
                # 代わりに常に次のファイル処理に進む
        
        print("\nThank you for using MP4/WebM Encoder. Press Enter to exit.")
        input()
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 