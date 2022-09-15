# DS3231
MicroPython module for DS3231 Maxim Integrated Extremely Accurate I2C RTC.

Just connect your DS3231 module board to Arduino, ESP or any other board with MicroPython firmware.

Supply voltage DS3231 3.3 Volts or 5V! If you use lithium (Li-Ion) backup battery CR2032,
supply your DS3231 board from 3.3 V only! If the supply voltage is greater than
3.3 Volts, the СR2032 Li-Ion battery will become unusable due to the recharging circuit
located on the board.

1. VCC
2. GND
3. SDA
4. SCL

Upload micropython firmware to the NANO(ESP, etc) board, and then two files: main.py,
ds3231maxim.py and folder sensor_pack. Then open main.py in your IDE and run it.

# Warning

In this project, I use the second hardware I2C port of the RP2040 Connect board. 
See calling the I2C class instance constructor. You must select the I2С port you need! 
Don't forget the 4K7 pull-up resistors!

# Pictures

## IDE
![alt text](https://github.com/octaprog7/ds3131/blob/master/ide3231.png)
## Breadboard
![alt text](https://github.com/octaprog7/ds3131/blob/master/board3231.jpg)

