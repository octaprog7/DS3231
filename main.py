from machine import I2C
from ds3231maxim import DS3221
from sensor_pack.bus_service import I2cAdapter
import utime

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    i2c = I2C(id=1, freq=400_000)  # on Arduino Nano RP2040 Connect tested
    adaptor = I2cAdapter(i2c)
    clock = DS3221(adapter=adaptor)

    print(f"Call get_time() method")
    tr = clock.get_time()
    print(f"Local time: {tr}")

    tmp = clock.get_temperature()
    stat = clock.get_status()
    ao = clock.get_aging_offset()
    print(f"Temperature: {tmp}\tstatus: {hex(stat)}\taging offset: {hex(ao)}")

    print("Alarm times:")
    print("First:", clock.get_alarm())
    print("Second:", clock.get_alarm(False))

    print(f"Using iterator...")
    for ltime in clock:
        print(f"Local time: {ltime}")
        utime.sleep_ms(1000)
