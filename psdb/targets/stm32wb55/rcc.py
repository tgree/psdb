# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
import time

from ..device import Device, Reg32


ENABLE_BITS = {
    # AHB1
    'DMA1'    : (0x048,  0),
    'DMA2'    : (0x048,  1),
    'DMAMUX'  : (0x048,  2),
    'CRC'     : (0x048, 12),
    'TSC'     : (0x48,  16),

    # AHB2
    'GPIOA'   : (0x04C,  0),
    'GPIOB'   : (0x04C,  1),
    'GPIOC'   : (0x04C,  2),
    'GPIOD'   : (0x04C,  3),
    'GPIOE'   : (0x04C,  4),
    'GPIOH'   : (0x04C,  7),
    'ADC'     : (0x04C, 13),
    'AES'     : (0x04C, 16),

    # AHB3/4
    'QUADSPI' : (0x50,   8),
    'PKA'     : (0x50,  16),
    'AES2'    : (0x50,  17),
    'RNG'     : (0x50,  18),
    'HSEM'    : (0x50,  19),
    'IPCC'    : (0x50,  20),
    'FLASH'   : (0x50,  25),

    # APB1.1
    'TIM2'    : (0x58,   0),
    'LCD'     : (0x58,   9),
    'RTCAPB'  : (0x58,  10),
    'WWDG'    : (0x58,  11),
    'SPI2'    : (0x58,  14),
    'I2C1'    : (0x58,  21),
    'I2C3'    : (0x58,  23),
    'CRS'     : (0x58,  24),
    'USB'     : (0x58,  26),
    'LPTIM1'  : (0x58,  31),

    # APB1.2
    'LPUART1' : (0x5C,   0),
    'LPTIM2'  : (0x5C,   5),

    # APB2
    'TIM1'    : (0x60,  11),
    'SPI1'    : (0x60,  12),
    'USART1'  : (0x60,  14),
    'TIM16'   : (0x60,  17),
    'TIM17'   : (0x60,  18),
    'SAI1'    : (0x60,  21),
    }

HPRE_MAP = {
    1   : 0,
    2   : 8,
    3   : 1,
    4   : 9,
    5   : 2,
    6   : 5,
    8   : 10,
    10  : 6,
    16  : 11,
    32  : 7,
    64  : 12,
    128 : 13,
    256 : 14,
    512 : 15,
    }

PPRE_MAP = {
    1  : 0,
    2  : 4,
    4  : 5,
    8  : 6,
    16 : 7,
    }


class RCC(Device):
    '''
    Driver for the STM Reset and Clock Control (RCC) device.
    '''
    REGS = [Reg32('CR',             0x000, [('MSION',           1),
                                            ('MSIRDY',          1),
                                            ('MSIPLLEN',        1),
                                            ('',                1),
                                            ('MSIRANGE',        4),
                                            ('HSION',           1),
                                            ('HSIKERON',        1),
                                            ('HSIRDY',          1),
                                            ('HSIASFS',         1),
                                            ('HSIKERDY',        1),
                                            ('',                3),
                                            ('HSEON',           1),
                                            ('HSERDY',          1),
                                            ('',                1),
                                            ('CSSON',           1),
                                            ('HSEPRE',          1),
                                            ('',                3),
                                            ('PLLON',           1),
                                            ('PLLRDY',          1),
                                            ('PLLSA1ON',        1),
                                            ('PLLSA1RDY',       1),
                                            ]),
            Reg32('ICSCR',          0x004, [('MSICAL',          8),
                                            ('MSITRIM',         8),
                                            ('HSICAL',          8),
                                            ('HSITRIM',         7),
                                            ]),
            Reg32('CFGR',           0x008, [('SW',              2),
                                            ('SWS',             2),
                                            ('HPRE',            4),
                                            ('PPRE1',           3),
                                            ('PPRE2',           3),
                                            ('',                1),
                                            ('STOPWUCH',        1),
                                            ('HPREF',           1),
                                            ('PPRE1F',          1),
                                            ('PPRE2F',          1),
                                            ('',                5),
                                            ('MCOSEL',          4),
                                            ('MCOPRE',          3),
                                            ]),
            Reg32('PLLCFGR',        0x00C, [('PLLSRC',          2),
                                            ('',                2),
                                            ('PLLM',            3),
                                            ('',                1),
                                            ('PLLN',            7),
                                            ('',                1),
                                            ('PLLPEN',          1),
                                            ('PLLP',            5),
                                            ('',                2),
                                            ('PLLQEN',          1),
                                            ('PLLQ',            3),
                                            ('PLLREN',          1),
                                            ('PLLR',            3),
                                            ]),
            Reg32('PLLSAI1CFGR',    0x010, [('',                8),
                                            ('PLLN',            7),
                                            ('',                1),
                                            ('PLLPEN',          1),
                                            ('PLLP',            5),
                                            ('',                2),
                                            ('PLLQEN',          1),
                                            ('PLLQ',            3),
                                            ('PLLREN',          1),
                                            ('PLLR',            3),
                                            ]),
            Reg32('CIER',           0x018, [('LSIR1DYIE',       1),
                                            ('LSERDYIE',        1),
                                            ('MSIRDYIE',        1),
                                            ('HSIRDYIE',        1),
                                            ('HSERDYIE',        1),
                                            ('PLLRDYIE',        1),
                                            ('PLLSAI1RDYIE',    1),
                                            ('',                2),
                                            ('LSECSSIE',        1),
                                            ('HSI48RDYIE',      1),
                                            ('LSI2RDYIE',       1),
                                            ]),
            Reg32('CIFR',           0x01C, [('LSI1RDYF',        1),
                                            ('LSERDYF',         1),
                                            ('MSIRDYF',         1),
                                            ('HSIRDYF',         1),
                                            ('HSERDYF',         1),
                                            ('PLLRDYF',         1),
                                            ('PLLSAI1RDYF',     1),
                                            ('',                1),
                                            ('CSSF',            1),
                                            ('LSECSSF',         1),
                                            ('HSI48RDYF',       1),
                                            ('LSI2RDYF',        1),
                                            ]),
            Reg32('CICR',           0x020, [('LSI1RDYC',        1),
                                            ('LSERDYC',         1),
                                            ('MSIRDYC',         1),
                                            ('HSIRDYC',         1),
                                            ('HSERDYC',         1),
                                            ('PLLRDYC',         1),
                                            ('PLLSAI1RDYC',     1),
                                            ('',                1),
                                            ('CSSC',            1),
                                            ('LSECSSC',         1),
                                            ('HSI48RDYC',       1),
                                            ('LSI2RDYC',        1),
                                            ]),
            Reg32('SMPSCR',         0x024, [('SMPSSEL',         2),
                                            ('',                2),
                                            ('SMPSDIV',         2),
                                            ('',                2),
                                            ('SMPSSWS',         2),
                                            ]),
            Reg32('AHB1RSTR',       0x028, [('DMA1RST',         1),
                                            ('DMA2RST',         1),
                                            ('DMAMUX1RST',      1),
                                            ('',                9),
                                            ('CRCRST',          1),
                                            ('',                3),
                                            ('TSCRST',          1),
                                            ]),
            Reg32('AHB2RSTR',       0x02C, [('GPIOARST',        1),
                                            ('GPIOBRST',        1),
                                            ('GPIOCRST',        1),
                                            ('GPIODRST',        1),
                                            ('GPIOERST',        1),
                                            ('',                2),
                                            ('GPIOHRST',        1),
                                            ('',                5),
                                            ('ADCRST',          1),
                                            ('',                2),
                                            ('AES1RST',         1),
                                            ]),
            Reg32('AHB3RSTR',       0x030, [('',                8),
                                            ('QSPIRST',         1),
                                            ('',                7),
                                            ('PKARST',          1),
                                            ('AES2RST',         1),
                                            ('RNGRST',          1),
                                            ('HSEMRST',         1),
                                            ('IPCCRST',         1),
                                            ('',                4),
                                            ('FLASHRST',        1),
                                            ]),
            Reg32('APB1RSTR1',      0x038, [('TIM2RST',         1),
                                            ('',                8),
                                            ('LCDRST',          1),
                                            ('',                4),
                                            ('SPI2RST',         1),
                                            ('',                6),
                                            ('I2C1RST',         1),
                                            ('',                1),
                                            ('I2C3RST',         1),
                                            ('CRSRST',          1),
                                            ('',                1),
                                            ('USBRST',          1),
                                            ('',                4),
                                            ('LPTIM1RST',       1),
                                            ]),
            Reg32('APB1RSTR2',      0x03C, [('LPUART1RST',      1),
                                            ('',                4),
                                            ('LPTIM2RST',       1),
                                            ]),
            Reg32('APB2RSTR',       0x040, [('',                11),
                                            ('TIM1RST',         1),
                                            ('SPI1RST',         1),
                                            ('',                1),
                                            ('USART1RST',       1),
                                            ('',                2),
                                            ('TIM16RST',        1),
                                            ('TIM17RST',        1),
                                            ('',                2),
                                            ('SAI1RST',         1),
                                            ]),
            Reg32('APB3RSTR',       0x044, [('RFRST',           1),
                                            ]),
            Reg32('AHB1ENR',        0x048, [('DMA1EN',          1),
                                            ('DMA2EN',          1),
                                            ('DMAMUX1EN',       1),
                                            ('',                9),
                                            ('CRCEN',           1),
                                            ('',                3),
                                            ('TSCEN',           1),
                                            ]),
            Reg32('AHB2ENR',        0x04C, [('GPIOAEN',         1),
                                            ('GPIOBEN',         1),
                                            ('GPIOCEN',         1),
                                            ('GPIODEN',         1),
                                            ('GPIOEEN',         1),
                                            ('',                2),
                                            ('GPIOHEN',         1),
                                            ('',                5),
                                            ('ADCEN',           1),
                                            ('',                2),
                                            ('AES1EN',          1),
                                            ]),
            Reg32('AHB3ENR',        0x050, [('',                8),
                                            ('QSPIEN',          1),
                                            ('',                7),
                                            ('PKAEN',           1),
                                            ('AES2EN',          1),
                                            ('RNGEN',           1),
                                            ('HSEMEN',          1),
                                            ('IPCCEN',          1),
                                            ('',                4),
                                            ('FLASHEN',         1),
                                            ]),
            Reg32('APB1ENR1',       0x058, [('TIM2EN',          1),
                                            ('',                8),
                                            ('LCDEN',           1),
                                            ('RTCAPBEN',        1),
                                            ('WWDGEN',          1),
                                            ('',                2),
                                            ('SPI2EN',          1),
                                            ('',                6),
                                            ('I2C1EN',          1),
                                            ('',                1),
                                            ('I2C3EN',          1),
                                            ('CRSEN',           1),
                                            ('',                1),
                                            ('USBEN',           1),
                                            ('',                4),
                                            ('LPTIM1EN',        1),
                                            ]),
            Reg32('APB1ENR2',       0x05C, [('LPUART1EN',       1),
                                            ('',                4),
                                            ('LPTIM2EN',        1),
                                            ]),
            Reg32('APB2ENR',        0x060, [('',                11),
                                            ('TIM1EN',          1),
                                            ('SPI1EN',          1),
                                            ('',                1),
                                            ('USART1EN',        1),
                                            ('',                2),
                                            ('TIM16EN',         1),
                                            ('TIM17EN',         1),
                                            ('',                2),
                                            ('SAI1EN',          1),
                                            ]),
            Reg32('AHB1SMENR',      0x068, [('DMA1SMEN',        1),
                                            ('DMA2SMEN',        1),
                                            ('DMAMUX1SMEN',     1),
                                            ('',                6),
                                            ('SRAM1SMEN',       1),
                                            ('',                2),
                                            ('CRCSMEN',         1),
                                            ('',                3),
                                            ('TSCSMEN',         1),
                                            ]),
            Reg32('AHB2SMENR',      0x06C, [('GPIOASMEN',       1),
                                            ('GPIOBSMEN',       1),
                                            ('GPIOCSMEN',       1),
                                            ('GPIODSMEN',       1),
                                            ('GPIOESMEN',       1),
                                            ('',                2),
                                            ('GPIOHSMEN',       1),
                                            ('',                5),
                                            ('ADC',             1),
                                            ('',                2),
                                            ('AES1SMEN',        1),
                                            ]),
            Reg32('AHB3SMENR',      0x070, [('',                8),
                                            ('QSPISMEN',        1),
                                            ('',                7),
                                            ('PKAEN',           1),
                                            ('AES2SMEN',        1),
                                            ('RNGSMEN',         1),
                                            ('',                5),
                                            ('SRAM2SMEN',       1),
                                            ('FLASHSMEN',       1),
                                            ]),
            Reg32('APB1SMENR1',     0x078, [('TIM2SMEN',        1),
                                            ('',                8),
                                            ('LCDSMEN',         1),
                                            ('RTCAPBSMEN',      1),
                                            ('WWDGSMEN',        1),
                                            ('',                2),
                                            ('SPI2SMEN',        1),
                                            ('',                6),
                                            ('I2C1SMEN',        1),
                                            ('',                1),
                                            ('I2C3SMEN',        1),
                                            ('CRSSMEN',         1),
                                            ('',                1),
                                            ('USBSMEN',         1),
                                            ('',                4),
                                            ('LPTIM1SMEN',      1),
                                            ]),
            Reg32('APB1SMENR2',     0x07C, [('LPUART1SMEN',     1),
                                            ('',                4),
                                            ('LPTIM2SMEN',      1),
                                            ]),
            Reg32('APB2SMENR',      0x080, [('',                11),
                                            ('TIM1SMEN',        1),
                                            ('SPI1SMEN',        1),
                                            ('',                1),
                                            ('USART1SMEN',      1),
                                            ('',                2),
                                            ('TIM16SMEN',       1),
                                            ('TIM17SMEN',       1),
                                            ('',                2),
                                            ('SAI1SMEN',        1),
                                            ]),
            Reg32('CCIPR',          0x088, [('USART1SEL',       2),
                                            ('',                8),
                                            ('LPUART1SEL',      2),
                                            ('I2C1SEL',         2),
                                            ('',                2),
                                            ('I2C3SEL',         2),
                                            ('LPTIM1SEL',       2),
                                            ('LPTIM2SEL',       2),
                                            ('SAI1SEL',         2),
                                            ('',                2),
                                            ('CLK48SEL',        2),
                                            ('ADCSEL',          2),
                                            ('RNGSEL',          2),
                                            ]),
            Reg32('BDCR',           0x090, [('LSEON',           1),
                                            ('LSERDY',          1),
                                            ('LSEBYP',          1),
                                            ('LSEDRV',          2),
                                            ('LSECSSON',        1),
                                            ('LSECSSD',         1),
                                            ('',                1),
                                            ('RTCSEL',          2),
                                            ('',                5),
                                            ('RTCEN',           1),
                                            ('BDRST',           1),
                                            ('',                7),
                                            ('LSCOEN',          1),
                                            ('LSCOSEL',         1),
                                            ]),
            Reg32('CSR',            0x094, [('LSI1ON',          1),
                                            ('LSI1RDY',         1),
                                            ('LSI2ON',          1),
                                            ('LSI2RDY',         1),
                                            ('',                4),
                                            ('LSI2TRIM',        4),
                                            ('',                2),
                                            ('RFWKPSEL',        2),
                                            ('RFRSTS',          1),
                                            ('',                6),
                                            ('RMVF',            1),
                                            ('',                1),
                                            ('OBLRSTF',         1),
                                            ('PINRSTF',         1),
                                            ('BORRSTF',         1),
                                            ('SFTRSTF',         1),
                                            ('IWDGRSTF',        1),
                                            ('WWDGRSTF',        1),
                                            ('LPWRRSTF',        1),
                                            ]),
            Reg32('CRRCR',          0x098, [('HSI48ON',         1),
                                            ('HSI48RDY',        1),
                                            ('',                5),
                                            ('HSI48CAL',        9),
                                            ]),
            Reg32('HSECR',          0x09C, [('UNLOCKED',        1),
                                            ('',                2),
                                            ('HSES',            1),
                                            ('HSEGMC',          3),
                                            ('',                1),
                                            ('HSETUNE',         6),
                                            ]),
            Reg32('EXTCFGR',        0x108, [('SHDHPRE',         4),
                                            ('C2HPRE',          4),
                                            ('',                8),
                                            ('SHDHPREF',        1),
                                            ('C2HPREF',         1),
                                            ('',                2),
                                            ('RFCSS',           1),
                                            ]),
            Reg32('C2AHB1ENR',      0x148, [('DMA1EN',          1),
                                            ('DMA2EN',          1),
                                            ('DMAMUX1EN',       1),
                                            ('',                6),
                                            ('SRAM1EN',         1),
                                            ('',                2),
                                            ('CRCEN',           1),
                                            ('',                3),
                                            ('TSCEN',           1),
                                            ]),
            Reg32('C2AHB2ENR',      0x14C, [('GPIOAEN',         1),
                                            ('GPIOBEN',         1),
                                            ('GPIOCEN',         1),
                                            ('GPIODEN',         1),
                                            ('GPIOEEN',         1),
                                            ('',                2),
                                            ('GPIOHEN',         1),
                                            ('',                5),
                                            ('ADCEN',           1),
                                            ('',                2),
                                            ('AES1EN',          1),
                                            ]),
            Reg32('C2AHB3ENR',      0x150, [('',                16),
                                            ('PKAEN',           1),
                                            ('AES2EN',          1),
                                            ('RNGEN',           1),
                                            ('HSEMEN',          1),
                                            ('IPCCEN',          1),
                                            ('',                4),
                                            ('FLASHEN',         1),
                                            ]),
            Reg32('C2APB1ENR1',     0x158, [('TIM2EN',          1),
                                            ('',                8),
                                            ('LCDEN',           1),
                                            ('RTCAPBEN',        1),
                                            ('',                3),
                                            ('SPI2EN',          1),
                                            ('',                6),
                                            ('I2C1EN',          1),
                                            ('',                1),
                                            ('I2C3EN',          1),
                                            ('CRSEN',           1),
                                            ('',                1),
                                            ('USBEN',           1),
                                            ('',                4),
                                            ('LPTIM1EN',        1),
                                            ]),
            Reg32('C2APB1ENR2',     0x15C, [('LPUART1EN',       1),
                                            ('',                4),
                                            ('LPTIM2EN',        1),
                                            ]),
            Reg32('C2APB2ENR',      0x160, [('',                11),
                                            ('TIM1EN',          1),
                                            ('SPI1EN',          1),
                                            ('',                1),
                                            ('USART1EN',        1),
                                            ('',                2),
                                            ('TIM16EN',         1),
                                            ('TIM17EN',         1),
                                            ('',                2),
                                            ('SAI1EN',          1),
                                            ]),
            Reg32('C2APB3ENR',      0x164, [('BLEEN',           1),
                                            ('802EN',           1),
                                            ]),
            Reg32('C2AHB1SMENR',    0x168, [('DMA1SMEN',        1),
                                            ('DMA2SMEN',        1),
                                            ('DMAMUX1SMEN',     1),
                                            ('',                6),
                                            ('SRAM1SMEN',       1),
                                            ('',                2),
                                            ('CRCSMEN',         1),
                                            ('',                3),
                                            ('TSCSMEN',         1),
                                            ]),
            Reg32('C2AHB2SMENR',    0x16C, [('GPIOASMEN',       1),
                                            ('GPIOBSMEN',       1),
                                            ('GPIOCSMEN',       1),
                                            ('GPIODSMEN',       1),
                                            ('GPIOESMEN',       1),
                                            ('',                2),
                                            ('GPIOHSMEN',       1),
                                            ('',                5),
                                            ('ADC',             1),
                                            ('',                2),
                                            ('AES1SMEN',        1),
                                            ]),
            Reg32('C2AHB3SMENR',    0x170, [('',                16),
                                            ('PKAEN',           1),
                                            ('AES2SMEN',        1),
                                            ('RNGSMEN',         1),
                                            ('',                5),
                                            ('SRAM2SMEN',       1),
                                            ('FLASHSMEN',       1),
                                            ]),
            Reg32('C2APB1SMENR1',   0x178, [('TIM2SMEN',        1),
                                            ('',                8),
                                            ('LCDSMEN',         1),
                                            ('RTCAPBSMEN',      1),
                                            ('',                3),
                                            ('SPI2SMEN',        1),
                                            ('',                6),
                                            ('I2C1SMEN',        1),
                                            ('',                1),
                                            ('I2C3SMEN',        1),
                                            ('CRSSMEN',         1),
                                            ('',                1),
                                            ('USBSMEN',         1),
                                            ('',                4),
                                            ('LPTIM1SMEN',      1),
                                            ]),
            Reg32('C2APB1SMENR2',   0x17C, [('LPUART1SMEN',     1),
                                            ('',                4),
                                            ('LPTIM2SMEN',      1),
                                            ]),
            Reg32('C2APB2SMENR',    0x180, [('',                11),
                                            ('TIM1SMEN',        1),
                                            ('SPI1SMEN',        1),
                                            ('',                1),
                                            ('USART1SMEN',      1),
                                            ('',                2),
                                            ('TIM16SMEN',       1),
                                            ('TIM17SMEN',       1),
                                            ('',                2),
                                            ('SAI1SMEN',        1),
                                            ]),
            Reg32('C2APB3SMENR',    0x184, [('BLESMEN',         1),
                                            ('802SMEN',         1),
                                            ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super(RCC, self).__init__(target, ap, addr, name, RCC.REGS, **kwargs)
        self.target = target

    def enable_device(self, name):
        offset, bit = ENABLE_BITS[name]
        if self._get_field(1, bit, offset) == 0:
            self._set_field(1, 1, bit, offset)

    def enable_hse(self):
        self._CR.HSEON = 1
        while self._CR.HSERDY == 0:
            time.sleep(0.01)

    def enable_hsi(self):
        self._CR.HSION = 1
        while self._CR.HSIRDY == 0:
            time.sleep(0.01)

    def enable_lse(self):
        self._BDCR.LSEON = 1
        while self._BDCR.LSERDY == 0:
            time.sleep(0.01)

    def apply_hse_tuning(self):
        id0_data = self.target.flash.get_st_otp_data_from_key(0x00)
        assert id0_data is not None

        hse_tuning = id0_data[6]
        self._HSECR         = 0xCAFECAFE
        self._HSECR.HSETUNE = hse_tuning

    def set_lse_drive_capability(self, val):
        self._BDCR.LSEDRV = val

    def reset_backup_domain(self):
        self._BDCR.BDRST = 1
        self._BDCR.BDRST = 0

    def set_hpre(self, divider):
        '''
        Sets the CPU1 HPRE divider (HCLK1).  Valid values are:

            1, 2, 3, 4, 5, 6, 8, 10, 16, 32, 64, 128, 256, 512
        '''
        self._CFGR.HPRE = HPRE_MAP[divider]
        while self._CFGR.HPREF == 0:
            time.sleep(0.01)

    def set_c2hpre(self, divider):
        '''
        Sets the CPU2 HPRE divider (HCLK2).  Valid values are:

            1, 2, 3, 4, 5, 6, 8, 10, 16, 32, 64, 128, 256, 512
        '''
        self._EXTCFGR.C2HPRE = HPRE_MAP[divider]
        while self._EXTCFGR.C2HPREF == 0:
            time.sleep(0.01)

    def set_shdhpre(self, divider):
        '''
        Sets the shared HCLK4 divider.  Valid values are:

            1, 2, 3, 4, 5, 6, 8, 10, 16, 32, 64, 128, 256, 512
        '''
        self._EXTCFGR.SHDHPRE = HPRE_MAP[divider]
        while self._EXTCFGR.SHDHPREF == 0:
            time.sleep(0.01)

    def set_ppre1(self, divider):
        '''
        Sets the PPRE1 divider (PCLK1 low-speed prescaler).  Valid values are:

            1, 2, 4, 8, 16
        '''
        self._CFGR.PPRE1 = PPRE_MAP[divider]
        while self._CFGR.PPRE1F == 0:
            time.sleep(0.01)

    def set_ppre2(self, divider):
        '''
        Sets the PPRE2 divider (PCLK2 high-speed prescaler).  Valid values are:

            1, 2, 4, 8, 16
        '''
        self._CFGR.PPRE2 = PPRE_MAP[divider]
        while self._CFGR.PPRE2F == 0:
            time.sleep(0.01)

    def set_sysclock_source(self, sw):
        '''
        Selects the SYSCLOCK source as follows:

                SW | Source
                ---+-------
                0  | MSI
                1  | HSI16
                2  | HSE
                3  | PLL
                ---+-------
        '''
        self._CFGR.SW = sw
        while self._CFGR.SWS != sw:
            time.sleep(0.01)

    def set_rtcclock_source(self, rtcsel):
        '''
        Selects the RTC clock source as follows:

                RTCSEL | Source
                -------+-------
                0      | None
                1      | LSE
                2      | LSI
                3      | HSE/32
                -------+-------

        Note that the backup domain must be reset to change the RTCSEL value
        from anything other than "None".
        '''
        assert self._BDCR.RTCSEL == 0
        self._BDCR.RTCSEL = rtcsel

    def set_usart1clock_source(self, usart1sel):
        '''
        Selects the USART1 clock source as follows:

                USART1SEL | Source
                ----------+-------
                0         | PCLK
                1         | SYSCLK
                2         | HSI16
                3         | LSE
                ----------+-------
        '''
        self._CCIPR.USART1SEL = usart1sel

    def set_lpuartclock_source(self, lpuart1sel):
        '''
        Selects the LPUART1 clock source as follows:

                LPUART1SEL | Source
                -----------+-------
                0          | PCLK
                1          | SYSCLK
                2          | HSI16
                3          | LSE
                -----------+-------
        '''
        self._CCIPR.LPUART1SEL = lpuart1sel

    def set_rfwakeupclock_source(self, rfwkpsel):
        '''
        Selects the RF system wakeup clock source as follows:

                RFWKPSEL | Source
                ---------+---------
                0        | None
                1        | LSE
                3        | HSE/1024
                ---------+---------
        '''
        assert rfwkpsel in (0, 1, 3)
        self._CSR.RFWKPSEL = rfwkpsel

    def set_smps_div(self, smpsdiv):
        self._SMPSCR.SMPSDIV = smpsdiv

    def set_smpsclock_source(self, smpssel):
        '''
        Selects the SMPS clock source as follows:

                SMPSSEL | Source
                --------+-------
                0       | HSI16
                1       | MSI
                2       | HSE
                --------+-------
        '''
        assert smpssel in (0, 1, 2)
        self._SMPSCR.SMPSSEL = smpssel
