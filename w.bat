rem @echo off
 set target=build\stm32vld
 arm-none-eabi-objcopy.exe -O ihex %target%.elf tmp.hex    
 rem python tools\avr\bin\fwriter\fwriter.py -cst-link tmp.hex 
 "G:\STM32_ST-LINK_Utility\ST-LINK Utility\ST-LINK_CLI.exe" -c SWD -P tmp.hex  -Rst 
