#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AÑO: 2024 CREADOR: Christian Yael Ramírez León

import subprocess 
import dmenu # It will be changed in the future for rofi 

# Available inputs monitors in the order shown by xrandr command
monitor_inputs = ['eDP-1', 'DP-1', 'HDMI-1', 'DP-2', 'HDMI-2']
connected_inputs = []
disconnected_inputs = []

monitor_specs = subprocess.run(['xrandr', '-q'],capture_output=True)
monitor_specs = monitor_specs.stdout.decode().split('\n')

resolutions = {}
optimal_resolution = {}

def AddDisctonectedMon (instruction = [], disconnected_inputs = []): 
    for i in disconnected_inputs: 
        instruction.append('--output')
        instruction.append(i)
        instruction.append('--off')
    return instruction

# Add connected inputs. 
j = 0 

for i in range(len(monitor_specs)): 
    if j >= len(monitor_inputs):
        break 

    if monitor_specs[i].find(monitor_inputs[j]) != -1: 
        if monitor_specs[i].find('disconnected') == -1: 
            connected_inputs.append(monitor_inputs[j])  
            resolutions[monitor_inputs[j]] = []

            while(i < len(monitor_specs) - 1): 
                i = i + 1 
                if j + 1 >= len(monitor_inputs):
                    resolutions[monitor_inputs[j]].append(monitor_specs[i].strip().split(' ')[0].split('x'))
                    if monitor_specs[i].find('+') != -1: 
                        optimal_resolution[monitor_inputs[j]] = monitor_specs[i].strip().split(' ')[0].split('x')
                elif monitor_specs[i].find(monitor_inputs[j + 1]) == -1:
                    resolutions[monitor_inputs[j]].append(monitor_specs[i].strip().split(' ')[0].split('x'))
                    if monitor_specs[i].find('+') != -1: 
                        optimal_resolution[monitor_inputs[j]] = monitor_specs[i].strip().split(' ')[0].split('x')
                else: 
                    break
        else: 
            disconnected_inputs.append(monitor_inputs[j])
        j = j + 1


if len(connected_inputs) == 1: 
    selected_option = dmenu.show(['Configuración Normal','Configuración Avanzada'], font='Hack Nerd Font-12', background='#000000', foreground_selected='#000000', prompt='Configuración de pantalla: 1 pantalla conectada', case_insensitive=True) 

    if selected_option == 'Configuración Normal': 
        instruction = ['xrandr', '--output', f'{connected_inputs[0]}', '--primary', '--mode', f'{optimal_resolution[connected_inputs[0]][0]}x{optimal_resolution[connected_inputs[0]][1]}', '--pos', '0x0', '--rotate', 'normal'] 
        for i in disconnected_inputs: 
            instruction.append('--output')
            instruction.append(i)
            instruction.append('--off') 
        subprocess.run(instruction)
        subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch.sh']) 
        with open('config_1_monitor.txt', 'w') as file: 
            for i in instruction:
                file.write(f"{i} ")
            file.write("&& bash /home/enigma/.config/polybar/colorblocks/launch.sh")

    elif selected_option == 'Configuración Avanzada': 
        pass 

elif len(connected_inputs) == 2: 
    selected_option = dmenu.show(['Duplicar','Solo Pantalla Principal', 'Solo Pantalla Secundaria', 'Ampliar', 'Avanzado'], font='Hack Nerd Font-12', background='#000000', foreground_selected='#000000', prompt='Configuración de pantalla: 2 pantallas conectadas', case_insensitive=True) 

    if selected_option == 'Duplicar': 
        pass 

    elif selected_option == 'Solo Pantalla Principal': 
        instruction = ['xrandr', '--output', f'{connected_inputs[0]}', '--primary', '--mode', f'{optimal_resolution[connected_inputs[0]][0]}x{optimal_resolution[connected_inputs[0]][1]}', '--pos', '0x0', '--rotate', 'normal', '--output', f'{connected_inputs[1]}', '--off'] 
        instruction = AddDisctonectedMon(instruction, disconnected_inputs)
        subprocess.run(instruction)
        subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch.sh'])
        with open('config_2_monitor.txt', 'w') as file: 
            for i in instruction:
                file.write(f"{i} ")
            file.write("&& bash /home/enigma/.config/polybar/colorblocks/launch.sh")



    elif selected_option == 'Solo Pantalla Secundaria': 
        instruction = ['xrandr', '--output', f'{connected_inputs[0]}', '--off', '--output', f'{connected_inputs[1]}', '--primary', '--mode', f'{optimal_resolution[connected_inputs[1]][0]}x{optimal_resolution[connected_inputs[1]][1]}', '--pos', '0x0', '--rotate', 'normal'] 
        instruction = AddDisctonectedMon(instruction, disconnected_inputs)
        subprocess.run(instruction)

    elif selected_option == 'Ampliar': 
        instruction = ['xrandr', '--output', f'{connected_inputs[0]}', '--primary', '--mode', f'{optimal_resolution[connected_inputs[0]][0]}x{optimal_resolution[connected_inputs[0]][1]}', '--rotate', 'normal', '--output', f'{connected_inputs[1]}', '--pos', '0x0', '--right-of', f'{connected_inputs[0]}', '--mode', f'1600x900'] # Specific resolution for second monitor. 

        # instruction = ['xrandr', '--output', f'{connected_inputs[0]}', '--primary', '--mode', f'{optimal_resolution[connected_inputs[0]][0]}x{optimal_resolution[connected_inputs[0]][1]}', '--rotate', 'normal', '--output', f'{connected_inputs[1]}', '--pos', '0x0', '--right-of', f'{connected_inputs[0]}', '--mode', f'{optimal_resolution[connected_inputs[1]][0]}x{optimal_resolution[connected_inputs[1]][1]}']  
        for i in disconnected_inputs: 
            instruction.append('--output')
            instruction.append(i)
            instruction.append('--off') 
        subprocess.run(instruction)
        subprocess.run(['bash', '/home/enigma/.config/polybar/colorblocks/launch_2.sh']) # Dual monitor config for polybar 

    elif selected_option == 'Avanzado': 
        pass 
