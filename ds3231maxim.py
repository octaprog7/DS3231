"""мой "драйвер" часов DS3231. Я его написал, потому-что устал смотреть на ..."""
import micropython

from sensor_pack import bus_service
from sensor_pack.base_sensor import Device, Iterator

import sys


@micropython.native
def bcd_to_int(bcd) -> int:
    """convert bcd to int"""
    mask = 0x0F
    result = bcd & mask
    mask = mask << 4
    result += 10 * ((bcd & mask) >> 4)
    return result


def int_to_bcd(value: int) -> int:
    """convert int to bcd"""
    return int(str(value), base=16)


def to_bytes(num) -> bytearray:
    return num.to_bytes(1, sys.byteorder)


class DS3221(Device, Iterator):
    """Class for work with DS3231 clock from Maxim Integrated или как она сейчас называется!?"""
    @staticmethod
    def _convert_hours(hour_byte: int) -> int:
        hour = bcd_to_int(hour_byte)
        if hour_byte & 0x40:
            hour = bcd_to_int(hour_byte & 0x1F)
            if hour_byte & 0x20:
                hour = 12 + hour_byte
        return hour

    def __init__(self, adapter: bus_service.BusAdapter, address: int = 0x68, big_byte_order: bool = False):
        super().__init__(adapter, address, big_byte_order)
        self._tbuf = bytearray(7)
        self._alarm.buf = bytearray(3)

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
        buf, mask = self._tbuf, 0x1f
        self.adapter.read_buf_from_mem(self.address, 0, buf)
        for i, val in enumerate(buf):
            if i in (0, 1, 4, 6):
                buf[i] = bcd_to_int(val)
            if 2 == i:  # hours
                buf[i] = DS3221._convert_hours(val)
            if 5 == i:  # month
                buf[i] = bcd_to_int(val & mask)
        # -----         YY       MM      DD      HH      MM      SS    WDAY    no year day
        return 2_000 + buf[6], buf[5], buf[4], buf[2], buf[1], buf[0], buf[3], -1  #

    def set_time(self, local_time):
        """ГГГГ, ММ, ДД, ЧЧ, ММ, СС, день недели, день года
        это формат времени, возвращаемого функцией localtime()"""
        k = 5, 4, 3, 6, 2, 1, 0
        v = 3, 5, 6
        value = 0
        for ind in range(7):
            if ind not in v:
                value = to_bytes(int_to_bcd(local_time[k[ind]]))
            else:
                if 3 == ind:
                    value = to_bytes(int_to_bcd(local_time[k[ind]] + 1))
                if 5 == ind:
                    value = to_bytes(0x80 + int_to_bcd(local_time[k[ind]]))
                if 6 == ind:
                    value = to_bytes(int_to_bcd(local_time[k[ind]] - 2_000))

            self.adapter.write_buf_to_mem(self.address, ind, value)

    def get_alarm(self, first: bool = True) -> tuple:
        """return alarm as tupleL (day, hour, minutes)
        if first, then return firs alarm setup set, else return second alarm setup set
        if day in 1..7, then day - day of week.
        if day in 1..31, then day - day of month"""
        alarm_addr = 8
        if not first:
            alarm_addr += 3
        a_buf = self._alarm.buf
        self.adapter.read_buf_from_mem(self.address, alarm_addr, a_buf)
        minutes = bcd_to_int(a_buf[0])
        hour = a_buf[1]

    def __next__(self) -> tuple:
        """For support iterating."""
        return self.get_time()
