#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AÑO: 2025 CREADOR: Christian Yael Ramírez León

import subprocess 
import dmenu 

def default_dmenu(optns: list, prompt: str):  
    selected_option = dmenu.show(optns, font='Hack Nerd Font-12', background='#000000', foreground_selected='#000000', prompt=prompt, case_insensitive=True) 
    return selected_option

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

# Configuration 1 Display 

if len(connected_outputs) == 1: 
    selected_option = default_dmenu(['Normal', 'Advanced'], 'Display settings: 1 Display connected') 

    if selected_option == 'Normal': 
        instruction = ['xrandr', '--output', f'{connected_outputs[0]}', '--primary', '--mode', f'{opt_resolution[connected_outputs[0]]}', '--pos', '0x0', '--rotate', 'normal']  
        for output in disconnected_outputs: 
            instruction.append('--output') 
            instruction.append(output) 
            instruction.append('--off')
        subprocess.run(instruction) 
        subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch.sh']) # Change directory 

    if selected_option == 'Advanced': 
        pass 

# Configuration 2 Display 

if len(connected_outputs) == 2: 
    selected_option = default_dmenu(['Main Screen Only', 
                                     'Duplicate',
                                     'Secondary Screen Only', 
                                     'Dual Monitor',
                                     'Advanced'], 
                                    'Display settings: 2 Display connected') 

    if selected_option == 'Main Screen Only':  

        instruction = ['xrandr', '--output', f'{connected_outputs[0]}', '--primary', '--mode', f'{opt_resolution[connected_outputs[0]]}', '--pos', '0x0', '--rotate', 'normal']  
        for output in disconnected_outputs: 
            instruction.append('--output') 
            instruction.append(output) 
            instruction.append('--off')
        subprocess.run(instruction) 
        subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch.sh']) # Change directory 

    if selected_option == 'Secondary Screen Only': 
        instruction = ['xrandr', '--output', f'{connected_outputs[0]}', '--primary', '--mode', f'{opt_resolution[connected_outputs[0]]}', '--pos', '0x0', '--rotate', 'normal']  
        for output in disconnected_outputs: 
            instruction.append('--output') 
            instruction.append(output) 
            instruction.append('--off')
        subprocess.run(instruction) 
        subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch.sh']) # Change directory 


