"""мой "драйвер" часов DS3231. Я его написал, потому-что устал смотреть на ..."""
from sensor_pack import bus_service
from sensor_pack.base_sensor import Device, Iterator

import sys


def bcd2dec(bcd) -> int:
    return ((bcd & 0xf0) >> 4) * 10 + (bcd & 0x0f)


def dec2bcd(dec) -> int:
    tens, units = divmod(dec, 10)
    return (tens << 4) + units


class DS3221(Device):
    """Class for work with DS3231 clock from Maxim Integrated или как она сейчас называется!?"""

    def __init__(self, adapter: bus_service.BusAdapter, address: int, big_byte_order: bool):
        super().__init__(adapter, address, big_byte_order)
        self._tbuf = bytearray(7)

    def _read_register(self, reg_addr, bytes_count=2) -> bytes:
        """считывает из регистра датчика значение.
        bytes_count - размер значения в байтах"""
        return self.adapter.read_register(self.address, reg_addr, bytes_count)

    def _write_register(self, reg_addr, value: int, bytes_count=2) -> int:
        """записывает данные value в датчик, по адресу reg_addr.
        bytes_count - кол-во записываемых данных"""
        byte_order = self._get_byteorder_as_str()[0]
        return self.adapter.write_register(self.address, reg_addr, value, bytes_count, byte_order)

    def get_status(self) -> int:
        """Чтение регистра состояния 0x0F"""
        return self._read_register(0x0F, 1)[0]

    def get_temperature(self) -> float:
        """возвращает температуру микросхемы часов в градусах Цельсия"""
        hi, low = self._read_register(0x11, 2)
        return self.unpack("b", hi.to_bytes(1, sys.byteorder))[0] + 0.25 * (low >> 6)

    def get_aging_offset(self) -> int:
        return self._read_register(0x10, 1)[0]
    
    def get_time(self) -> tuple:
        """возвращает время, как в виде кортежа (как localtime())
        (year, month, mday, hour, minute, second, weekday, yearday)"""
        buf = self._tbuf
        self.adapter.read_buf(self.address, 0, buf)
        for i, val in enumerate(buf):
            if i in (0, 1, 4, 6):
                buf[i] = bcd2dec(val)
            if 2 == i:
                if val & 0x40:
                    buf[i] = bcd2dec(val & 0x1f)
                if val & 0x20:
                    buf[i] += 12
            
            if 5 == i:
                buf[i] = bcd2dec(val & 0x1f)
    
        return buf[6], buf[5], buf[4], buf[2], buf[1], buf[0], buf[3], -1, 0  # 
    
    def set_time(self, local_time : tuple):
        pass