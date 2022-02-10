# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
from ..device import Device, AReg32


ENABLE_BITS = {
    # AHB1
    'GPDMA1'        : (0x88,  0),
    'CORDIC'        : (0x88,  1),
    'FMAC'          : (0x88,  2),
    'MDF1'          : (0x88,  3),
    'FLASH'         : (0x88,  8),
    'CRC'           : (0x88, 12),
    'TSC'           : (0x88, 16),
    'RAMCFG'        : (0x88, 17),
    'DMA2D'         : (0x88, 18),
    'GTZC1'         : (0x88, 24),
    'BKPSRAM'       : (0x88, 28),
    'DCACHE1'       : (0x88, 30),
    'SRAM1'         : (0x88, 31),

    # AHB2.1
    'GPIOA'         : (0x8C,  0),
    'GPIOB'         : (0x8C,  1),
    'GPIOC'         : (0x8C,  2),
    'GPIOD'         : (0x8C,  3),
    'GPIOE'         : (0x8C,  4),
    'GPIOF'         : (0x8C,  5),
    'GPIOG'         : (0x8C,  6),
    'GPIOH'         : (0x8C,  7),
    'GPIOI'         : (0x8C,  8),
    'ADC1'          : (0x8C, 10),
    'DCMI_PSSI'     : (0x8C, 12),
    'OTG'           : (0x8C, 14),
    'AES'           : (0x8C, 16),
    'HASH'          : (0x8C, 17),
    'RNG'           : (0x8C, 18),
    'PKA'           : (0x8C, 19),
    'SAES'          : (0x8C, 20),
    'OCTOSPIM'      : (0x8C, 21),
    'OTFDEC1'       : (0x8C, 23),
    'OTFDEC2'       : (0x8C, 24),
    'SDMMC1'        : (0x8C, 27),
    'SDMMC2'        : (0x8C, 28),
    'SRAM2'         : (0x8C, 30),
    'SRAM3'         : (0x8C, 31),

    # AHB2.2
    'FSMC'          : (0x90, 0),
    'OCTOSPI1'      : (0x90, 4),
    'OCTOSPI2'      : (0x90, 8),

    # AHB3
    'LPGPIO1'       : (0x94,  0),
    'PWR'           : (0x94,  2),
    'ADC4'          : (0x94,  5),
    'DAC1'          : (0x94,  6),
    'LPDMA1'        : (0x94,  9),
    'ADF1'          : (0x94, 10),
    'GTZC2'         : (0x94, 12),
    'SRAM4'         : (0x94, 31),

    # APB1.1
    'TIM2'          : (0x9C,  0),
    'TIM3'          : (0x9C,  1),
    'TIM4'          : (0x9C,  2),
    'TIM5'          : (0x9C,  3),
    'TIM6'          : (0x9C,  4),
    'TIM7'          : (0x9C,  5),
    'WWDG'          : (0x9C, 11),
    'SPI2'          : (0x9C, 14),
    'USART2'        : (0x9C, 17),
    'USART3'        : (0x9C, 18),
    'UART4'         : (0x9C, 19),
    'UART5'         : (0x9C, 20),
    'I2C1'          : (0x9C, 21),
    'I2C2'          : (0x9C, 22),
    'CRS'           : (0x9C, 24),

    # APB1.2
    'I2C4'          : (0xA0,  1),
    'LPTIM2'        : (0xA0,  5),
    'FDCAN1'        : (0xA0,  9),
    'UCPD1'         : (0xA0, 23),

    # APB2
    'TIM1'          : (0xA4, 11),
    'SPI1'          : (0xA4, 12),
    'TIM8'          : (0xA4, 13),
    'USART1'        : (0xA4, 14),
    'TIM15'         : (0xA4, 16),
    'TIM16'         : (0xA4, 17),
    'TIM17'         : (0xA4, 18),
    'SAI1'          : (0xA4, 21),
    'SAI2'          : (0xA4, 22),

    # APB3.
    'SYSCFG'        : (0xA8,  1),
    'SPI3'          : (0xA8,  5),
    'LPUART1'       : (0xA8,  6),
    'I2C3'          : (0xA8,  7),
    'LPTIM1'        : (0xA8, 11),
    'LPTIM3'        : (0xA8, 12),
    'LPTIM4'        : (0xA8, 13),
    'OPAMP'         : (0xA8, 14),
    'COMP'          : (0xA8, 15),
    'VREF'          : (0xA8, 20),
    'RTCAPB'        : (0xA8, 21),
    }


class RCC(Device):
    '''
    Driver for the STM32U5 Reset and Clock Control (RCC) device.
    '''
    REGS = [AReg32('CR',            0x000, [('MSION',           0),
                                            ('MSIKERON',        1),
                                            ('MSISRDY',         2),
                                            ('MSIPLLEN',        3),
                                            ('MSIKON',          4),
                                            ('MSIKRDY',         5),
                                            ('MSIPLLSEL',       6),
                                            ('MSIPLLFAST',      7),
                                            ('HSION',           8),
                                            ('HSIKERON',        9),
                                            ('HSIRDY',          10),
                                            ('HSI48ON',         12),
                                            ('HSI48RDY',        13),
                                            ('SHSION',          14),
                                            ('SHSIRDY',         15),
                                            ('HSEON',           16),
                                            ('HSERDY',          17),
                                            ('HSEBYP',          18),
                                            ('CSSON',           19),
                                            ('HSEEXT',          20),
                                            ('PLL1ON',          24),
                                            ('PLL1RDY',         25),
                                            ('PLL2ON',          26),
                                            ('PLL2RDY',         27),
                                            ('PLL3ON',          28),
                                            ('PLL3RDY',         29),
                                            ]),
            AReg32('ICSCR1',        0x008, [('MSICAL3',         0,  4),
                                            ('MSICAL2',         5,  9),
                                            ('MSICAL1',         10, 14),
                                            ('MSICAL0',         15, 19),
                                            ('MSIBIAS',         22),
                                            ('MSIRGSEL',        23),
                                            ('MSIKRANGE',       24, 27),
                                            ('MSISRANGE',       28, 31),
                                            ]),
            AReg32('ICSCR2',        0x00C, [('MSITRIM3',        0,  4),
                                            ('MSITRIM2',        5,  9),
                                            ('MSITRIM1',        10, 14),
                                            ('MSITRIM0',        15, 19),
                                            ]),
            AReg32('ICSCR3',        0x010, [('HSICAL',          0,  11),
                                            ('HSITRIM',         16, 20),
                                            ]),
            AReg32('CRRCR',         0x014, [('HSI48CAL',        0,  8),
                                            ]),
            AReg32('CFGR1',         0x01C, [('SW',              0,  1),
                                            ('SWS',             2,  3),
                                            ('STOPWUCK',        4),
                                            ('STOPKERWUCK',     5),
                                            ('MCOSEL',          24, 27),
                                            ('MCOPRE',          28, 30),
                                            ]),
            AReg32('CFGR2',         0x020, [('HPRE',            0,  3),
                                            ('PPRE1',           4,  6),
                                            ('PPRE2',           8,  10),
                                            ('AHB1DIS',         16),
                                            ('AHB2DIS1',        17),
                                            ('AHB2DIS2',        18),
                                            ('APB1DIS',         19),
                                            ('APB2DIS',         20),
                                            ]),
            AReg32('CFGR3',         0x024, [('PPRE3',           4,  6),
                                            ('AHB3DIS',         16),
                                            ('APB3DIS',         17),
                                            ]),
            AReg32('PLL1CFGR',      0x028, [('PLL1SRC',         0,  1),
                                            ('PLL1RGE',         2,  3),
                                            ('PLL1FRACEN',      4),
                                            ('PLL1M',           8,  11),
                                            ('PLL1MBOOST',      12, 15),
                                            ('PLL1PEN',         16),
                                            ('PLL1QEN',         17),
                                            ('PLL1REN',         18),
                                            ]),
            AReg32('PLL2CFGR',      0x02C, [('PLL2SRC',         0,  1),
                                            ('PLL2RGE',         2,  3),
                                            ('PLL2FRACEN',      4),
                                            ('PLL2M',           8,  11),
                                            ('PLL2PEN',         16),
                                            ('PLL2QEN',         17),
                                            ('PLL2REN',         18),
                                            ]),
            AReg32('PLL3CFGR',      0x030, [('PLL3SRC',         0,  1),
                                            ('PLL3RGE',         2,  3),
                                            ('PLL3FRACEN',      4),
                                            ('PLL3M',           8,  11),
                                            ('PLL3PEN',         16),
                                            ('PLL3QEN',         17),
                                            ('PLL3REN',         18),
                                            ]),
            AReg32('PLL1DIVR',      0x034, [('PLL1N',           0,  8),
                                            ('PLL1P',           9,  15),
                                            ('PLL1Q',           16, 22),
                                            ('PLL1R',           24, 30),
                                            ]),
            AReg32('PLL1FRACR',     0x038, [('PLL1FRACN',       3,  15),
                                            ]),
            AReg32('PLL2DIVR',      0x03C, [('PLL2N',           0,  8),
                                            ('PLL2P',           9,  15),
                                            ('PLL2Q',           16, 22),
                                            ('PLL2R',           24, 30),
                                            ]),
            AReg32('PLL2FRACR',     0x040, [('PLL2FRACN',       3,  15),
                                            ]),
            AReg32('PLL3DIVR',      0x044, [('PLL3N',           0,  8),
                                            ('PLL3P',           9,  15),
                                            ('PLL3Q',           16, 22),
                                            ('PLL3R',           24, 30),
                                            ]),
            AReg32('PLL3FRACR',     0x048, [('PLL3FRACN',       3,  15),
                                            ]),
            AReg32('CIER',          0x050, [('LSIRDYIE',        0),
                                            ('LSERDYIE',        1),
                                            ('MSISRDYIE',       2),
                                            ('HSIRDYIE',        3),
                                            ('HSERDYIE',        4),
                                            ('HSI48RDYIE',      5),
                                            ('PLL1RDYIE',       6),
                                            ('PLL2RDYIE',       7),
                                            ('PLL3RDYIE',       8),
                                            ('MSIKRDYIE',       11),
                                            ('SHSIRDYIE',       12),
                                            ]),
            AReg32('CIFR',          0x054, [('LSIRDYF',         0),
                                            ('LSERDYF',         1),
                                            ('MSISRDYF',        2),
                                            ('HSIRDYF',         3),
                                            ('HSERDYF',         4),
                                            ('HSI48RDYF',       5),
                                            ('PLL1RDYF',        6),
                                            ('PLL2RDYF',        7),
                                            ('PLL3RDYF',        8),
                                            ('CSSF',            10),
                                            ('MSIKRDYF',        11),
                                            ('SHSIRDYF',        12),
                                            ]),
            AReg32('CICR',          0x058, [('LSIRDYC',         0),
                                            ('LSERDYC',         1),
                                            ('MSISRDYC',        2),
                                            ('HSIRDYC',         3),
                                            ('HSERDYC',         4),
                                            ('HSI48RDYC',       5),
                                            ('PLL1RDYC',        6),
                                            ('PLL2RDYC',        7),
                                            ('PLL3RDYC',        8),
                                            ('CSSC',            10),
                                            ('MSIKRDYC',        11),
                                            ('SHSIRDYC',        12),
                                            ]),
            AReg32('AHB1RSTR',      0x060, [('GPDMA1RST',       0),
                                            ('CORDICRST',       1),
                                            ('FMACRST',         2),
                                            ('MDF1RST',         3),
                                            ('CRCRST',          12),
                                            ('TSCRST',          16),
                                            ('RAMCFGRST',       17),
                                            ('DMA2DRST',        18),
                                            ]),
            AReg32('AHB2RSTR1',     0x064, [('GPIOARST',        0),
                                            ('GPIOBRST',        1),
                                            ('GPIOCRST',        2),
                                            ('GPIODRST',        3),
                                            ('GPIOERST',        4),
                                            ('GPIOFRST',        5),
                                            ('GPIOGRST',        6),
                                            ('GPIOHRST',        7),
                                            ('GPIOIRST',        8),
                                            ('ADC1RST',         10),
                                            ('DCMI_PSSIRST',    12),
                                            ('OTGRST',          14),
                                            ('AESRST',          16),
                                            ('HASHRST',         17),
                                            ('RNGRST',          18),
                                            ('PKARST',          19),
                                            ('SAESRST',         20),
                                            ('OCTOSPIMRST',     21),
                                            ('OTFDEC1RST',      23),
                                            ('OTFDEC2RST',      24),
                                            ('SDMMC1RST',       27),
                                            ('SDMMC2RST',       28),
                                            ]),
            AReg32('AHB2RSTR2',     0x068, [('FSMCRST',         0),
                                            ('OCTOSPI1RST',     4),
                                            ('OCTOSPI2RST',     8),
                                            ]),
            AReg32('AHB3RSTR',      0x06C, [('LPGPIO1RST',      0),
                                            ('ADC4RST',         5),
                                            ('DAC1RST',         6),
                                            ('LPDMA1RST',       9),
                                            ('ADF1RST',         10),
                                            ]),
            AReg32('APB1RSTR1',     0x074, [('TIM2RST',         0),
                                            ('TIM3RST',         1),
                                            ('TIM4RST',         2),
                                            ('TIM5RST',         3),
                                            ('TIM6RST',         4),
                                            ('TIM7RST',         5),
                                            ('SPI2RST',         14),
                                            ('USART2RST',       17),
                                            ('USART3RST',       18),
                                            ('UART4RST',        19),
                                            ('UART5RST',        20),
                                            ('I2C1RST',         21),
                                            ('I2C2RST',         22),
                                            ('CRSRST',          24),
                                            ]),
            AReg32('APB1RSTR2',     0x078, [('I2C4RST',         1),
                                            ('LPTIM2RST',       5),
                                            ('FDCAN1RST',       9),
                                            ('UCPD1RST',        23),
                                            ]),
            AReg32('APB2RSTR',      0x07C, [('TIM1RST',         11),
                                            ('SPI1RST',         12),
                                            ('TIM8RST',         13),
                                            ('USART1RST',       14),
                                            ('TIM15RST',        16),
                                            ('TIM16RST',        17),
                                            ('TIM17RST',        18),
                                            ('SAI1RST',         21),
                                            ('SAI2RST',         22),
                                            ]),
            AReg32('APB3RSTR',      0x080, [('SYSCFGRST',       1),
                                            ('SPI3RST',         5),
                                            ('LPUART1RST',      6),
                                            ('I2C3RST',         7),
                                            ('LPTIM1RST',       11),
                                            ('LPTIM3RST',       12),
                                            ('LPTIM4RST',       13),
                                            ('OPAMPRST',        14),
                                            ('COMPRST',         15),
                                            ('VREFRST',         20),
                                            ]),
            AReg32('AHB1ENR',       0x088, [('GPDMA1EN',        0),
                                            ('CORDICEN',        1),
                                            ('FMACEN',          2),
                                            ('MDF1EN',          3),
                                            ('FLASHEN',         8),
                                            ('CRCEN',           12),
                                            ('TSCEN',           16),
                                            ('RAMCFGEN',        17),
                                            ('DMA2DEN',         18),
                                            ('GTZC1EN',         24),
                                            ('BKPSRAMEN',       28),
                                            ('DCACHE1EN',       30),
                                            ('SRAM1EN',         31),
                                            ]),
            AReg32('AHB2ENR1',      0x08C, [('GPIOAEN',         0),
                                            ('GPIOBEN',         1),
                                            ('GPIOCEN',         2),
                                            ('GPIODEN',         3),
                                            ('GPIOEEN',         4),
                                            ('GPIOFEN',         5),
                                            ('GPIOGEN',         6),
                                            ('GPIOHEN',         7),
                                            ('GPIOIEN',         8),
                                            ('ADC1EN',          10),
                                            ('DCMI_PSSIEN',     12),
                                            ('OTGEN',           14),
                                            ('AESEN',           16),
                                            ('HASHEN',          17),
                                            ('RNGEN',           18),
                                            ('PKAEN',           19),
                                            ('SAESEN',          20),
                                            ('OCTOSPIMEN',      21),
                                            ('OTFDEC1EN',       23),
                                            ('OTFDEC2EN',       24),
                                            ('SDMMC1EN',        27),
                                            ('SDMMC2EN',        28),
                                            ('SRAM2EN',         30),
                                            ('SRAM3EN',         31),
                                            ]),
            AReg32('AHB2ENR2',      0x090, [('FSMCEN',          0),
                                            ('OCTOSPI1EN',      4),
                                            ('OCTOSPI2EN',      8),
                                            ]),
            AReg32('AHB3ENR',       0x094, [('LPGPIO1EN',       0),
                                            ('PWREN',           2),
                                            ('ADC4EN',          5),
                                            ('DAC1EN',          6),
                                            ('LPDMA1EN',        9),
                                            ('ADF1EN',          10),
                                            ('GTZC2EN',         12),
                                            ('SRAM4EN',         31),
                                            ]),
            AReg32('APB1ENR1',      0x09C, [('TIM2EN',          0),
                                            ('TIM3EN',          1),
                                            ('TIM4EN',          2),
                                            ('TIM5EN',          3),
                                            ('TIM6EN',          4),
                                            ('TIM7EN',          5),
                                            ('WWDGEN',          11),
                                            ('SPI2EN',          14),
                                            ('USART2EN',        17),
                                            ('USART3EN',        18),
                                            ('UART4EN',         19),
                                            ('UART5EN',         20),
                                            ('I2C1EN',          21),
                                            ('I2C2EN',          22),
                                            ('CRSEN',           24),
                                            ]),
            AReg32('APB1ENR2',      0x0A0, [('I2C4EN',          1),
                                            ('LPTIM2EN',        5),
                                            ('FDCAN1EN',        9),
                                            ('UCPD1EN',         23),
                                            ]),
            AReg32('APB2ENR',       0x0A4, [('TIM1EN',          11),
                                            ('SPI1EN',          12),
                                            ('TIM8EN',          13),
                                            ('USART1EN',        14),
                                            ('TIM15EN',         16),
                                            ('TIM16EN',         17),
                                            ('TIM17EN',         18),
                                            ('SAI1EN',          21),
                                            ('SAI2EN',          22),
                                            ]),
            AReg32('APB3ENR',       0x0A8, [('SYSCFGEN',        1),
                                            ('SPI3EN',          5),
                                            ('LPUART1EN',       6),
                                            ('I2C3EN',          7),
                                            ('LPTIM1EN',        11),
                                            ('LPTIM3EN',        12),
                                            ('LPTIM4EN',        13),
                                            ('OPAMPEN',         14),
                                            ('COMPEN',          15),
                                            ('VREFEN',          20),
                                            ('RTCAPBEN',        21),
                                            ]),
            AReg32('AHB1SMENR',     0x0B0, [('GPDMA1SMEN',      0),
                                            ('CORDICSMEN',      1),
                                            ('FMACSMEN',        2),
                                            ('MDF1SMEN',        3),
                                            ('FLASHSMEN',       8),
                                            ('CRCSMEN',         12),
                                            ('TSCSMEN',         16),
                                            ('RAMCFGSMEN',      17),
                                            ('DMA2DSMEN',       18),
                                            ('GTZC1SMEN',       24),
                                            ('BKPSRAMSMEN',     28),
                                            ('ICACHESMEN',      29),
                                            ('DCACHE1SMEN',     30),
                                            ('SRAM1SMEN',       31),
                                            ]),
            AReg32('AHB2SMENR1',    0x0B4, [('GPIOASMEN',       0),
                                            ('GPIOBSMEN',       1),
                                            ('GPIOCSMEN',       2),
                                            ('GPIODSMEN',       3),
                                            ('GPIOESMEN',       4),
                                            ('GPIOFSMEN',       5),
                                            ('GPIOGSMEN',       6),
                                            ('GPIOHSMEN',       7),
                                            ('GPIOISMEN',       8),
                                            ('ADC1SMEN',        10),
                                            ('DCMI_PSSISMEN',   12),
                                            ('OTGSMEN',         14),
                                            ('AESSMEN',         16),
                                            ('HASHSMEN',        17),
                                            ('RNGSMEN',         18),
                                            ('PKASMEN',         19),
                                            ('SAESSMEN',        20),
                                            ('OCTOSPIMSMEN',    21),
                                            ('OTFDEC1SMEN',     23),
                                            ('OTFDEC2SMEN',     24),
                                            ('SDMMC1SMEN',      27),
                                            ('SDMMC2SMEN',      28),
                                            ('SRAM2SMEN',       30),
                                            ('SRAM3SMEN',       31),
                                            ]),
            AReg32('AHB2SMENR2',    0x0B8, [('FSMCSMEN',        0),
                                            ('OCTOSPI1SMEN',    4),
                                            ('OCTOSPI2SMEN',    8),
                                            ]),
            AReg32('AHB3SMENR',     0x0BC, [('LPGPIO1SMEN',     0),
                                            ('PWRSMEN',         2),
                                            ('ADC4SMEN',        5),
                                            ('DAC1SMEN',        6),
                                            ('LPDMA1SMEN',      9),
                                            ('ADF1SMEN',        10),
                                            ('GTZC2SMEN',       12),
                                            ('SRAM4SMEN',       31),
                                            ]),
            AReg32('APB1SMENR1',    0x0C4, [('TIM2SMEN',        0),
                                            ('TIM3SMEN',        1),
                                            ('TIM4SMEN',        2),
                                            ('TIM5SMEN',        3),
                                            ('TIM6SMEN',        4),
                                            ('TIM7SMEN',        5),
                                            ('WWDGSMEN',        11),
                                            ('SPI2SMEN',        14),
                                            ('USART2SMEN',      17),
                                            ('USART3SMEN',      18),
                                            ('UART4SMEN',       19),
                                            ('UART5SMEN',       20),
                                            ('I2C1SMEN',        21),
                                            ('I2C2SMEN',        22),
                                            ('CRSSMEN',         24),
                                            ]),
            AReg32('APB1SMENR2',    0x0C8, [('I2C4SMEN',        1),
                                            ('LPTIM2SMEN',      5),
                                            ('FDCAN1SMEN',      9),
                                            ('UCPD1SMEN',       23),
                                            ]),
            AReg32('APB2SMENR',     0x0CC, [('TIM1SMEN',        11),
                                            ('SPI1SMEN',        12),
                                            ('TIM8SMEN',        13),
                                            ('USART1SMEN',      14),
                                            ('TIM15SMEN',       16),
                                            ('TIM16SMEN',       17),
                                            ('TIM17SMEN',       18),
                                            ('SAI1SMEN',        21),
                                            ('SAI2SMEN',        22),
                                            ]),
            AReg32('APB3SMENR',     0x0D0, [('SYSCFGSMEN',      1),
                                            ('SPI3SMEN',        5),
                                            ('LPUART1SMEN',     6),
                                            ('I2C3SMEN',        7),
                                            ('LPTIM1SMEN',      11),
                                            ('LPTIM3SMEN',      12),
                                            ('LPTIM4SMEN',      13),
                                            ('OPAMPSMEN',       14),
                                            ('COMPSMEN',        15),
                                            ('VREFSMEN',        20),
                                            ('RTCAPBSMEN',      21),
                                            ]),
            AReg32('SRDAMR',        0x0D8, [('SPI3AMEN',        5),
                                            ('LPUART1AMEN',     6),
                                            ('I2C3AMEN',        7),
                                            ('LPTIM1AMEN',      11),
                                            ('LPTIM3AMEN',      12),
                                            ('LPTIM4AMEN',      13),
                                            ('OPAMPAMEN',       14),
                                            ('COMPAMEN',        15),
                                            ('VREFAMEN',        20),
                                            ('RTCAPBAMEN',      21),
                                            ('ADC4AMEN',        25),
                                            ('LPGPIO1AMEN',     26),
                                            ('DAC1AMEN',        27),
                                            ('LPDMA1AMEN',      28),
                                            ('ADF1AMEN',        29),
                                            ('SRAM4AMEN',       31),
                                            ]),
            AReg32('CCIPR1',        0x0E0, [('USART1SEL',       0,  1),
                                            ('USART2SEL',       2,  3),
                                            ('USART3SEL',       4,  5),
                                            ('UART4SEL',        6,  7),
                                            ('UART5SEL',        8,  9),
                                            ('I2C1SEL',         10, 11),
                                            ('I2C2SEL',         12, 13),
                                            ('I2C4SEL',         14, 15),
                                            ('SPI2SEL',         16, 17),
                                            ('LPTIM2SEL',       18, 19),
                                            ('SPI1SEL',         20, 21),
                                            ('SYSTICKSEL',      22, 23),
                                            ('FDCAN1SEL',       24, 25),
                                            ('ICLKSEL',         26, 27),
                                            ('TIMICSEL',        29, 31),
                                            ]),
            AReg32('CCIPR2',        0x0E4, [('MDF1SEL',         0,  2),
                                            ('SAI1SEL',         5,  7),
                                            ('SAI2SEL',         8,  10),
                                            ('SAESSEL',         11),
                                            ('RNGSEL',          12, 13),
                                            ('SDMMCSEL',        14),
                                            ('OCTOSPISEL',      20, 21),
                                            ]),
            AReg32('CCIPR3',        0x0E8, [('LPUART1SEL',      0,  2),
                                            ('SPI3SEL',         3,  4),
                                            ('I2C3SEL',         6,  7),
                                            ('LPTIM34SEL',      8,  9),
                                            ('LPTIM1SEL',       10, 11),
                                            ('ADCDACSEL',       12, 14),
                                            ('DAC1SEL',         15),
                                            ('ADF1SEL',         16, 18),
                                            ]),
            AReg32('BDCR',          0x0F0, [('LSEON',           0),
                                            ('LSERDY',          1),
                                            ('LSEBYP',          2),
                                            ('LSEDRV',          3,  4),
                                            ('LSECSSON',        5),
                                            ('LSECSSD',         6),
                                            ('LSESYSEN',        7),
                                            ('RTCSEL',          8,  9),
                                            ('LSESYSRDY',       11),
                                            ('LSECFGON',        12),
                                            ('RTCEN',           15),
                                            ('BDRST',           16),
                                            ('LSCOEN',          24),
                                            ('LSCOSEL',         25),
                                            ('LSION',           26),
                                            ('LSIRDY',          27),
                                            ('LSIPREDIV',       28),
                                            ]),
            AReg32('CSR',           0x0F4, [('MSIKSRANGE',      8,  11),
                                            ('MSISSRANGE',      12, 15),
                                            ('RMVF',            23),
                                            ('OBLRSTF',         25),
                                            ('PINRSTF',         26),
                                            ('BORRSTF',         27),
                                            ('SFTRSTF',         28),
                                            ('IWDGRSTF',        29),
                                            ('WWDGRSTF',        30),
                                            ('LPWRRSTF',        31),
                                            ]),
            AReg32('SECCFGR',       0x110, [('HSISEC',          0),
                                            ('HSESEC',          1),
                                            ('MSISEC',          2),
                                            ('LSISEC',          3),
                                            ('LSESEC',          4),
                                            ('SYSCLKSEC',       5),
                                            ('PRESCSEC',        6),
                                            ('PLL1SEC',         7),
                                            ('PLL2SEC',         8),
                                            ('PLL3SEC',         9),
                                            ('ICLKSEC',         10),
                                            ('HSI48SEC',        11),
                                            ('RMVFSEC',         12),
                                            ]),
            AReg32('PRIVCFGR',      0x114, [('SPRIV',           0),
                                            ('NSPRIV',          1),
                                            ]),
            ]

    def __init__(self, target, ap, name, addr, **kwargs):
        super().__init__(target, ap, addr, name, RCC.REGS, **kwargs)

    def enable_device(self, name):
        offset, bit = ENABLE_BITS[name]
        if self._get_field(1, bit, offset) == 0:
            self._set_field(1, 1, bit, offset)
