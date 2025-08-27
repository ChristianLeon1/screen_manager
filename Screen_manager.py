#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AÑO: 2025 CREADOR: Christian Yael Ramírez León

import subprocess 
import dmenu 
import json
import os

def default_dmenu(optns: list[str], prompt: str, lines = None):  
    # Configuration of color and size for dmenu
    selected_option = dmenu.show(optns, font='Hack Nerd Font-12', background='#474747', foreground='#E0E0E0', foreground_selected='#0F0F0F', background_selected='#878787', prompt=prompt, case_insensitive=True, lines=lines) 
    return selected_option

def run_xrandr(instruction: list[str], disconnected_outputs: list[str]) -> None: 
    for output in disconnected_outputs: 
        instruction.append('--output') 
        instruction.append(output) 
        instruction.append('--off')
    subprocess.run(instruction) 
    subprocess.run(['feh', '--bg-fill', '~/Documentos/WallPapers/wall_gemini.jpeg']) # Update WallPaper 

def xrandr_instruction(configuration: dict[str, dict[str, str]]) -> list[str]: 
    instruction = ['xrandr'] 
    for output in configuration.keys(): 
        if configuration[output]['status'] == 'off': 
            instruction.extend(['--output', output, '--off']) 
            continue
        instruction.extend(['--output', output, '--mode', configuration[output]['resolution'], '--rotate', configuration[output]['orientation']]) 
        if len(configuration[output]['position'].split()) == 1: 
            instruction.append(configuration[output]['position'])
        else: 
            instruction.extend(configuration[output]['position'].split())

        instruction.extend(['--scale', configuration[output]['scale']]) 

    return instruction

# -------------------------------------------
#
# Load configuration json
#
# -------------------------------------------

def load_config():
    """
    Loads a saved configuration from the 'saved_config.json' file,
    presents a list of available configurations to the user via dmenu,
    and returns the selected configuration's xrandr instruction.
    """

    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saved_config.json')

    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        default_dmenu(['exit'], 'No configurations saved in the file.')
        return None

    try:
        with open(filename, 'r') as f:
            all_configs = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        default_dmenu(['exit'], 'No configurations saved in the file.')
        return None

    config_names = list(all_configs.keys())
    if not config_names:
        default_dmenu(['exit'], 'No configurations saved in the file.')
        return None

    # Use dmenu to let the user choose a configuration
    selected_name = default_dmenu(config_names, 'Select a configuration to load:')
    
    # Get the xrandr instruction for the selected configuration
    selected_config = all_configs.get(selected_name)
    if selected_config:
        instruction = xrandr_instruction(selected_config) 
        run_xrandr(instruction, disconnected_outputs) 
        if selected_name == 'Escritorio Casa': 
            subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch_2.sh'])
    else:
        print("Selected configuration not found in the file.")
        return None

# -------------------------------------------
#
# Advanced configuration 
#
# -------------------------------------------

def advanced_config(connected_outputs: list[str], disconnected_outputs: list[str], resolutions: dict[str, list[str]], opt_resolution: dict[str, str]) -> None: 

    """
    Constructs an xrandr command interactively for monitor configuration
    and provides an option to save the configuration to a JSON file.

    Args:
        connected_outputs (list[str]): List of currently connected outputs.
        disconnected_outputs (list[str]): List of currently disconnected outputs.
        resolutions (dict[str, list[str]]): Dictionary mapping outputs to their available resolutions.
        opt_resolution (dict[str, str]): Dictionary mapping outputs to their optimal resolution.
    """

    monitors = {} 
    selected_optn= ''
    same_monitors = []
    for i, output in enumerate(connected_outputs):  
        
        optns = ['status (ON / OFF)', 'resolution', 'position', 'orientation', 'save', 'exit'] 
        config_monitor = {'resolution': opt_resolution[output],
                          'position': '--primary' if i == 0 else '',
                          'orientation': 'normal', 
                          'scale': '1x1',
                          'status': 'on'}   
        
        while selected_optn != 'exit':  
            selected_optn = default_dmenu(optns[1:] if i == 0 else optns, f'{connected_outputs[i]}: configuration') 

            if selected_optn == 'status (ON / OFF)': 
                config_monitor['status'] = default_dmenu(['on','off'],'Select status:')
            elif selected_optn == 'resolution':
                config_monitor['resolution'] = default_dmenu(resolutions[connected_outputs[i]], 'Select resolution:', lines=5) 
            elif selected_optn == 'position': 
                position = default_dmenu(['primary','right-of', 'left-of', 'above', 'below', 'same-as'], 'Select position:')  
                if position != 'primary': 
                    temp_connected = connected_outputs[:] 
                    temp_connected.pop(i)
                    output_position = default_dmenu(temp_connected, 'Select in output for position:')
                    config_monitor['position'] = f'--{position} {output_position}'
                    if position == 'same-as': 
                        same_monitors.extend([output, output_position])
                else: 
                    config_monitor['position'] = '--primary' 
            elif selected_optn == 'orientation': 
                config_monitor['orientation'] = default_dmenu(['normal', 'left', 'right', 'inverted'], 'Select orientation:')  
            elif selected_optn == 'save': 
                break
            elif selected_optn == 'exit':
                return None 
    
        monitors[output] = config_monitor 
    
    # Compare if was selected the option same_monitor
    same_monitors = list(set(same_monitors))   
    if len(same_monitors) > 1: 
        same_monitors.sort(key=lambda m: int(monitors[m]['resolution'].split('x')[0]), reverse=False)    

        for i, output in enumerate(same_monitors):  
            if i == 0: 
                monitors[output]['scale'] = '1x1'
                width, height = monitors[output]['resolution'].split('x')
                width, height = int(width), int(height)
                continue 
            width_1, height_1 = monitors[output]['resolution'].split('x')
            width_1, height_1 = int(width_1), int(height_1)
            monitors[output]['scale'] = f'{round(width / width_1, 3)}x{round(height / height_1, 3)}'
    
    # save configuration in a json file
    save_option = default_dmenu(['yes', 'no'], 'Save configuration?')
    if save_option == 'yes':
        config_name = default_dmenu([], 'Enter a name for this configuration:')
        if config_name:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(script_dir, 'saved_config.json')
            
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                try:
                    with open(filename, 'r') as f:
                        all_configs = json.load(f)
                except (json.JSONDecodeError, IOError):
                    all_configs = {}
            else:
                all_configs = {}
            
            all_configs[config_name] = monitors
            
            try:
                with open(filename, 'w') as f:
                    json.dump(all_configs, f, indent=4)
            except Exception as e:  
                pass
    
    instruction = xrandr_instruction(monitors) 
    run_xrandr(instruction, disconnected_outputs) 

    # polybar configuration change if different configuration 
    if len(connected_outputs) == 1: 
        subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch.sh'])
    elif len(connected_outputs) == 2: 
        if len(same_monitors) == 0: 
            subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch_2.sh'])
        else: 
            subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch_3.sh']) 
    elif len(connected_outputs) == 3: 
            subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch_3.sh'])   
    
    return None 

# --------------------------------------------------------
#
#   Main program 
#
# --------------------------------------------------------

xrandr_output = subprocess.run(['xrandr'], capture_output=True).stdout.decode().split('\n')
available_outputs = [line.split()[0] for line in xrandr_output if 'connected' in line]
connected_outputs = [line.split()[0] for line in xrandr_output if ' connected' in line] 
disconnected_outputs = [line.split()[0] for line in xrandr_output if 'disconnected' in line] 

resolutions = {} 
opt_resolution = {}
for output in connected_outputs: 
    resolutions[output] = [] 

i = 0
flag = False
index_available = available_outputs.index(connected_outputs[i]) + 1
for line in xrandr_output: 
    if connected_outputs[i] in line: 
        flag = True 
        continue

    if not flag: 
        continue

    if len(available_outputs) == index_available: 
        resolutions[connected_outputs[i]].append(line) 
    elif available_outputs[index_available] not in line: 
        resolutions[connected_outputs[i]].append(line) 
    else: 
        flag = False 
        i = i + 1 
        if i == len(connected_outputs): 
            break
        elif available_outputs[index_available] == connected_outputs[i]: 
            flag = True 

for output in connected_outputs: 
    for i, line in enumerate(resolutions[output]): 
        try: 
            resolutions[output][i] = line.split()[0] 
        except:
            pass
        if '+' in line: 
            opt_resolution[output]= resolutions[output][i]

# ---------------------------------------
#
#   Configuration one monitor
#
# ---------------------------------------

if len(connected_outputs) == 1: 
    selected_option = default_dmenu(['Normal', 'Advanced', 'Saved Configuration'], 'Display settings: 1 Display connected') 

    if selected_option == 'Normal': 
        instruction = ['xrandr', '--output', f'{connected_outputs[0]}', '--primary', '--mode', f'{opt_resolution[connected_outputs[0]]}', '--pos', '0x0', '--scale', '1x1', '--rotate', 'normal']  
        run_xrandr(instruction,disconnected_outputs)
        subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch.sh']) # Change directory 

    elif selected_option == 'Advanced': 
        advanced_config(connected_outputs, disconnected_outputs, resolutions, opt_resolution)

    elif selected_option == 'Saved Configuration': 
        load_config() 

# ---------------------------------------
#
#   Configuration two monitors
#
# ---------------------------------------

if len(connected_outputs) == 2: 
    selected_option = default_dmenu(['Main Only', 
                                     'Mirror',
                                     'Secondary Only', 
                                     'Dual Monitor',
                                     'Advanced', 
                                     'Saved Configuration'], 
                                    'Display settings: 2 Display connected') 
    
    # Main Only
    if selected_option == 'Main Only':  
        instruction = ['xrandr', '--output', f'{connected_outputs[0]}', '--primary', '--mode', f'{opt_resolution[connected_outputs[0]]}', '--pos', '0x0', '--scale', '1x1', '--rotate', 'normal', '--output', f'{connected_outputs[1]}', '--off']  
        run_xrandr(instruction, disconnected_outputs)
        subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch.sh']) # Change directory 
    
    # Secondary Only
    elif selected_option == 'Secondary Only': 
        instruction = ['xrandr', '--output', f'{connected_outputs[1]}', '--primary', '--mode', f'{opt_resolution[connected_outputs[1]]}', '--pos', '0x0', '--scale', '1x1', '--rotate', 'normal', '--output', f'{connected_outputs[0]}', '--off']  
        run_xrandr(instruction, disconnected_outputs)
        subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch_3.sh']) # Change directory  
    
    # Mirror 
    elif selected_option == 'Mirror': 
        principal_res = opt_resolution[connected_outputs[0]].split('x')
        second_res = opt_resolution[connected_outputs[1]].split('x') 
        scale = [round(int(second_res[0]) / int(principal_res[0]),3), round(int(second_res[1]) / int(principal_res[1]), 3)] 
        instruction = ['xrandr', '--output', f'{connected_outputs[0]}', '--primary', 
                       '--mode', f'{opt_resolution[connected_outputs[0]]}', 
                       '--pos', '0x0', 
                       '--scale', f'{scale[0]}x{scale[1]}' if principal_res[0] >= second_res[0] else '1x1', 
                       '--rotate', 'normal', 
                       '--output', f'{connected_outputs[1]}', 
                       '--mode', f'{opt_resolution[connected_outputs[1]]}', 
                       '--same-as', f'{connected_outputs[0]}', 
                       '--scale', f'{scale[0]}x{scale[1]}' if principal_res[0] < second_res[0] else '1x1', 
                       '--rotate', 'normal']
        run_xrandr(instruction, disconnected_outputs) 
        subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch_3.sh'])
    
    # Dual monitor
    elif selected_option == 'Dual Monitor': 
        instruction = ['xrandr', '--output', f'{connected_outputs[0]}', '--primary', 
                       '--mode', f'{opt_resolution[connected_outputs[0]]}', 
                       '--pos', '0x0', 
                       '--scale', '1x1', 
                       '--rotate', 'normal', 
                       '--output', f'{connected_outputs[1]}', 
                       '--mode', f'{opt_resolution[connected_outputs[1]]}', 
                       '--right-of', f'{connected_outputs[0]}', 
                       '--scale', f'1x1', 
                       '--rotate', 'normal']  
        run_xrandr(instruction, disconnected_outputs)
        subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch_2.sh'])

    elif selected_option == 'Advanced': 
        advanced_config(connected_outputs,disconnected_outputs,resolutions,opt_resolution)

    elif selected_option == 'Saved Configuration': 
        load_config() 

# ---------------------------------------
#
#   Configuration three monitors
#
# ---------------------------------------

    elif len(connected_outputs) == 3:
        selected_option = default_dmenu(['Main Screen Only',
                                         'Main & Secondary',
                                         'Main & Tertiary',
                                         'Secondary & Tertiary',
                                         'Duplicate Main',
                                         'Triple Monitor',
                                         'Advanced', 
                                         'Saved Configuration'],
                                         'Display settings: 3 Displays connected')

        # Main Screen Only (first monitor active)
        if selected_option == 'Main Screen Only':
            instruction = ['xrandr', '--output', f'{connected_outputs[0]}', '--primary', '--mode', f'{opt_resolution[connected_outputs[0]]}', '--pos', '0x0', '--scale', '1x1', '--rotate', 'normal', '--output', f'{connected_outputs[1]}', '--off', '--output', f'{connected_outputs[2]}', '--off']
            run_xrandr(instruction, disconnected_outputs)
            subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch.sh'])

        # Main & Secondary (first and second monitors active)
        elif selected_option == 'Main & Secondary':
            instruction = ['xrandr', '--output', f'{connected_outputs[0]}', '--primary', '--mode', f'{opt_resolution[connected_outputs[0]]}', '--pos', '0x0', '--scale', '1x1', '--rotate', 'normal', '--output', f'{connected_outputs[1]}', '--mode', f'{opt_resolution[connected_outputs[1]]}', '--right-of', f'{connected_outputs[0]}', '--scale', '1x1', '--rotate', 'normal', '--output', f'{connected_outputs[2]}', '--off']
            run_xrandr(instruction, disconnected_outputs)
            subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch.sh'])

        # Main & Tertiary (first and third monitors active)
        elif selected_option == 'Main & Tertiary':
            instruction = ['xrandr', '--output', f'{connected_outputs[0]}', '--primary', '--mode', f'{opt_resolution[connected_outputs[0]]}', '--pos', '0x0', '--scale', '1x1', '--rotate', 'normal', '--output', f'{connected_outputs[2]}', '--mode', f'{opt_resolution[connected_outputs[2]]}', '--right-of', f'{connected_outputs[0]}', '--scale', '1x1', '--rotate', 'normal', '--output', f'{connected_outputs[1]}', '--off']
            run_xrandr(instruction, disconnected_outputs)
            subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch.sh'])

        # Secondary & Tertiary (second and third monitors active)
        elif selected_option == 'Secondary & Tertiary':
            instruction = ['xrandr', '--output', f'{connected_outputs[1]}', '--primary', '--mode', f'{opt_resolution[connected_outputs[1]]}', '--pos', '0x0', '--scale', '1x1', '--rotate', 'normal', '--output', f'{connected_outputs[2]}', '--mode', f'{opt_resolution[connected_outputs[2]]}', '--right-of', f'{connected_outputs[1]}', '--scale', '1x1', '--rotate', 'normal', '--output', f'{connected_outputs[0]}', '--off']
            run_xrandr(instruction, disconnected_outputs)
            subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch.sh'])

        # Duplicate Main (all three monitors showing the same content, scaled to the smallest)
        elif selected_option == 'Duplicate Main':
            # Assuming the first monitor is the main source for duplication
            principal_res = opt_resolution[connected_outputs[0]].split('x')
            second_res = opt_resolution[connected_outputs[1]].split('x')
            third_res = opt_resolution[connected_outputs[2]].split('x')

            # Find the smallest resolution width and height to scale to
            min_width = min(int(principal_res[0]), int(second_res[0]), int(third_res[0]))
            min_height = min(int(principal_res[1]), int(second_res[1]), int(third_res[1]))
            
            # Calculate scale factors for each monitor relative to the main
            scale1 = [round(min_width / int(principal_res[0]), 3), round(min_height / int(principal_res[1]), 3)]
            scale2 = [round(min_width / int(second_res[0]), 3), round(min_height / int(second_res[1]), 3)]
            scale3 = [round(min_width / int(third_res[0]), 3), round(min_height / int(third_res[1]), 3)]

            instruction = ['xrandr', '--output', f'{connected_outputs[0]}', '--primary',
                           '--mode', f'{opt_resolution[connected_outputs[0]]}',
                           '--pos', '0x0',
                           '--scale', f'{scale1[0]}x{scale1[1]}',
                           '--rotate', 'normal',
                           '--output', f'{connected_outputs[1]}',
                           '--mode', f'{opt_resolution[connected_outputs[1]]}',
                           '--same-as', f'{connected_outputs[0]}',
                           '--scale', f'{scale2[0]}x{scale2[1]}',
                           '--rotate', 'normal',
                           '--output', f'{connected_outputs[2]}',
                           '--mode', f'{opt_resolution[connected_outputs[2]]}',
                           '--same-as', f'{connected_outputs[0]}',
                           '--scale', f'{scale3[0]}x{scale3[1]}',
                           '--rotate', 'normal']
            run_xrandr(instruction, disconnected_outputs)

        # Triple Monitor (all three monitors as a single extended desktop)
        elif selected_option == 'Triple Monitor':
            instruction = ['xrandr', '--output', f'{connected_outputs[0]}', '--primary',
                           '--mode', f'{opt_resolution[connected_outputs[0]]}',
                           '--pos', '0x0',
                           '--scale', '1x1',
                           '--rotate', 'normal',
                           '--output', f'{connected_outputs[1]}',
                           '--mode', f'{opt_resolution[connected_outputs[1]]}',
                           '--right-of', f'{connected_outputs[0]}',
                           '--scale', '1x1',
                           '--rotate', 'normal',
                           '--output', f'{connected_outputs[2]}',
                           '--mode', f'{opt_resolution[connected_outputs[2]]}',
                           '--right-of', f'{connected_outputs[1]}',
                           '--scale', '1x1',
                           '--rotate', 'normal']
            run_xrandr(instruction, disconnected_outputs)

        elif selected_option == 'Advanced':
            advanced_config(connected_outputs, disconnected_outputs, resolutions, opt_resolution) 

        elif selected_option == 'Saved Configuration': 
            load_config() 

