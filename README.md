# Monitor Setup

Monitor Setup is a Python script that simplifies the management of multiple monitors in Linux desktop environments. It uses `dmenu` for an interactive user interface and `xrandr` for screen configuration. It's ideal for users who need to quickly switch between different monitor setups, such as using a single monitor, extending the desktop across multiple screens, or duplicating the display.


## Key Features 

* **Automatic Detection**: Automatically detects connected and disconnected displays to offer relevant configuration options.
* **Preset Modes**: Provides common configurations with a single click:
    * **One monitor**: `Normal`, `Advanced`, `Saved Configuration`
    * **Two monitors**: `Main Only`, `Mirror`, `Secondary Only`, `Dual Monitor`, `Advanced`, `Saved Configuration`
    * **Three monitors**: `Main Screen Only`, `Main & Secondary`, `Main & Tertiary`, `Secondary & Tertiary`, `Duplicate Main`, `Triple Monitor`, `Advanced`, `Saved Configuration`
* **Advanced Configuration**: Allows for detailed customization for each monitor, including resolution, position, orientation, and scaling.
* **Save and Load Configurations**: Enables users to save their preferred setups to a JSON file for later use. This is helpful for different scenarios like a "Home Desktop," "Office," or "Presentation" setup.
* **Polybar Integration**: The script is configured to automatically change the Polybar setup based on the number of connected monitors, ensuring your status bar adjusts correctly to the new layout.
* **Dynamic Wallpaper**: Automatically changes the wallpaper with `feh` after each monitor adjustment.

## Requirements

* **`python3`**: The Python interpreter.
* **`dmenu`**: A simple and fast application launcher. The script uses `dmenu` for its interactive user interface.
* **`xrandr`**: The X.org command-line tool for configuring screen outputs.
* **`feh`**: An image viewer used to set the wallpaper.
* **`polybar`** (optional): If you want the status bar to adjust automatically, ensure you have Polybar installed with the correct configurations in the paths specified in the code.

## Usage

1.  Make sure `dmenu` and `xrandr` are installed on your system.
2.  Place the `monitor-setup.py` script and the `saved_config.json` file (if you have one) in the same directory.
3.  Make the script executable: `chmod +x monitor-setup.py`
4.  Run the script from your terminal or set it up as a keyboard shortcut in your window manager (e.g., i3, dwm, etc.): `python3 /path/to/monitor-setup.py`.

## Configuration File ⚙️

The script uses a file named **`saved_config.json`** to store custom configurations. If you choose to save a configuration, the script will prompt you for a name and store it in this file.


