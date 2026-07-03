# Adaptive Smart Grain Storage using STM32

## Overview
Adaptive Smart Grain Storage is a monitoring system designed to observe grain storage conditions in real time using STM32. The system measures environmental parameters and calculates the Crop Storage Risk Index (CSRI) to determine the storage condition.

## Features
- Temperature monitoring (DHT22)
- Humidity monitoring
- Grain moisture monitoring
- CO₂ monitoring
- CSRI calculation
- LCD 16x2 display
- LED and buzzer warning
- Relay control
- UART communication
- Real-time visualization using Python and GNUPlot
- Proteus simulation

## Hardware
- STM32F103C8T6
- DHT22
- LCD 16x2 I2C
- Relay Module
- LED Indicators
- Buzzer

## Software
- Keil uVision
- Proteus 8 Professional
- Python 3
- GNUPlot

## Project Structure

```
Firmware/
├── Smart_Storage_main.c
└── Smart_Storage_I2c.c

Proteus_GNUPlot/
└── plot.py

Proteus/
└── smart.pdsprj
```

## How to Run

1. Compile the STM32 firmware using Keil.
2. Open the Proteus project.
3. Load the generated HEX file.
4. Run the Proteus simulation.
5. Execute `plot.py` to display the real-time monitoring graph.

## Author

Gigan Arka
