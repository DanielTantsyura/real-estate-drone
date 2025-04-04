#!/usr/bin/env python3
"""
Launch Chrome browser with settings required for DroneBlocks Tello Simulator
"""

import os
import json
import subprocess
import sys
import platform
import argparse
from pathlib import Path

def get_chrome_path():
    """
    Get the path to the Chrome browser based on the current OS
    
    Returns:
        str: Path to Chrome browser or None if not found
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chrome.app/Contents/MacOS/Chrome"
        ]
    elif system == "Windows":
        chrome_paths = [
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google\\Chrome\\Application\\chrome.exe")
        ]
    elif system == "Linux":
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]
    else:
        print(f"Unsupported operating system: {system}")
        return None
    
    # Find the first path that exists
    for path in chrome_paths:
        if os.path.exists(path):
            return path
    
    print("Chrome browser not found. Please install Chrome or specify the path manually.")
    return None

def load_config(config_path=None):
    """
    Load configuration from file
    
    Args:
        config_path (str, optional): Path to the config file
        
    Returns:
        dict: Configuration dictionary
    """
    # Default configuration
    default_config = {
        "simulator": {
            "enabled": True,
            "simulator_key": "",
            "chrome_settings": {
                "allow_insecure_content": True,
                "simulator_url": "https://sim.droneblocks.io/"
            }
        }
    }
    
    # If no config path provided, check some default locations
    if config_path is None:
        possible_paths = [
            "config/config.json",
            os.path.join(os.path.dirname(__file__), "../config/config.json"),
            os.path.join(os.path.expanduser("~"), ".tello/config.json")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                config_path = path
                break
    
    # Load config if it exists
    config = default_config
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                # Try to access simulator config
                if 'simulator' in loaded_config:
                    config['simulator'] = loaded_config['simulator']
        except Exception as e:
            print(f"Error loading config from {config_path}: {e}")
            print("Using default configuration")
    else:
        print("No config file found, using default configuration")
        
    return config

def launch_chrome(config, chrome_path=None, user_data_dir=None):
    """
    Launch Chrome with the necessary settings for DroneBlocks Simulator
    
    Args:
        config (dict): Configuration dictionary
        chrome_path (str, optional): Path to Chrome executable
        user_data_dir (str, optional): Path to Chrome user data directory
        
    Returns:
        subprocess.Popen: Process object for the launched Chrome instance
    """
    if not chrome_path:
        chrome_path = get_chrome_path()
        if not chrome_path:
            print("Chrome executable not found. Please specify the path manually.")
            return None
    
    # Define Chrome arguments
    chrome_args = [chrome_path]
    
    # Add user data directory if specified
    if user_data_dir:
        chrome_args.extend(['--user-data-dir', user_data_dir])
    
    # Add simulator URL
    chrome_config_key = 'chrome_settings' if 'chrome_settings' in config['simulator'] else 'chrome'
    simulator_url = config['simulator'][chrome_config_key]['simulator_url']
    chrome_args.append(simulator_url)
    
    # Add flags for allowing insecure content if enabled
    if config['simulator'][chrome_config_key]['allow_insecure_content']:
        chrome_args.extend([
            '--allow-running-insecure-content',
            '--disable-web-security',
            '--ignore-certificate-errors'
        ])
    
    # Launch Chrome
    try:
        print(f"Launching Chrome for DroneBlocks Simulator at {simulator_url}")
        print(f"Chrome command: {' '.join(chrome_args)}")
        
        chrome_process = subprocess.Popen(chrome_args)
        print(f"Chrome launched with PID: {chrome_process.pid}")
        return chrome_process
    except Exception as e:
        print(f"Error launching Chrome: {e}")
        return None

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Launch Chrome with settings for DroneBlocks Tello Simulator')
    parser.add_argument('--config', help='Path to config file')
    parser.add_argument('--chrome-path', help='Path to Chrome executable')
    parser.add_argument('--user-data-dir', help='Path to Chrome user data directory')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Launch Chrome
    chrome_process = launch_chrome(config, args.chrome_path, args.user_data_dir)
    
    if chrome_process:
        print("Chrome launched successfully for DroneBlocks Simulator")
        print("You can now run your simulator missions")
        print("\nPress Ctrl+C to exit this script (Chrome will continue running)")
        try:
            # Wait for user to press Ctrl+C
            chrome_process.wait()
        except KeyboardInterrupt:
            print("\nScript terminated by user")
            print("Chrome will continue running")
    else:
        print("Failed to launch Chrome")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 