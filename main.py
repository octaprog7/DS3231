from machine import I2C
from ds3231maxim import DS3221
from sensor_pack.bus_service import I2cAdapter
import utime

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    i2c = I2C(id=1, freq=400_000)  # on Arduino Nano RP2040 Connect tested
    adaptor = I2cAdapter(i2c)
    clock = DS3221(adapter=adaptor, address=0x68, big_byte_order=False)

    while True:
        tmp = clock.get_temperature()
        stat = clock.get_status()
        ao = clock.get_aging_offset()
        tr = clock.get_time()
        print(f"Temperature: {tmp}\tstatus: {hex(stat)}\taging offset: {hex(ao)}")
        print(f"Local time: {tr}")
        utime.sleep_ms(1000)
