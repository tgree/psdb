#!/usr/bin/env python3
# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
import argparse
import struct
import math
import sys

import psdb.probes


USE_HSE = True

def autoint(v):
    return int(v, 0)


def main(rv):
    # Validate DAC values.
    if rv.amplitude < 0 or rv.amplitude > 0x0800:
        raise Exception('--amplitude out of range')
    if rv.bias < 0 or rv.bias > 0x0FFF:
        raise Exception('--bias out of range')

    # Dump all debuggers if requested.
    if rv.dump_debuggers:
        psdb.probes.dump_probes()

    # Probe the specified serial number (or find the default if no serial number
    # was specified.
    probe = psdb.probes.find_default(usb_path=rv.usb_path)
    f     = probe.set_tck_freq(rv.probe_freq)
    print('Probing with SWD frequency at %.3f MHz' % (f/1.e6))

    # Use the probe to detect a target platform.
    target = probe.probe(verbose=rv.verbose, connect_under_reset=True)
    f      = target.set_max_tck_freq()
    print('Set SWD frequency to %.3f MHz' % (f/1.e6))

    # Find the various devices we need.
    rcc     = target.devs['RCC_M7']
    pwr     = target.devs['PWR']
    syscfg  = target.devs['SYSCFG']
    sram1   = target.devs['SRAM1']
    dac     = target.devs['DAC1']
    dmamux1 = target.devs['DMAMUX1']
    dma1    = target.devs['DMA1']
    tim6    = target.devs['TIM6']

    # Set the PWR mode.
    pwr.set_mode_ldo()

    # Configure the RCC dividers.  The clocks will be as follows:Z
    #   SYSCLK     - 480 MHz
    #   CPU1CLK    - 480 MHz
    #   CPU2CLK    - 240 MHz
    #   AHB clocks - 240 MHz
    #   APB clocks - 120 MHz
    rcc.set_d1cpre(1)       # CPU1           - 480 MHz
    rcc.set_hpre(2)         # AHB, AXI, CPU2 - 240 MHz
    rcc.set_d1ppre(2)       # APB3           - 120 MHz
    rcc.set_d2ppre1(2)      # APB1           - 120 MHz
    rcc.set_d2ppre2(2)      # APB2           - 120 MHz
    rcc.set_d3ppre(2)       # APB4           - 120 MHz

    # Measure HSE.
    f_hse = target.enable_and_measure_hse()
    f_hse = ((f_hse + 500000) // 1000000) * 1000000
    rcc.set_f_hse(f_hse)

    # Configure for 480 MHz operation.
    if USE_HSE:
        M, N, P, VOS = rcc.get_pll_mnpv(480, rcc.f_hse)
    else:
        M, N, P, VOS = rcc.get_pll_mnpv(480, rcc.f_hsi)
    print('M, N, P, VOS = (%u, %u, %u, %u)' % (M, N, P, VOS))
    print('          f_hse: %7.3f MHz' % (rcc.f_hse / 1e6))
    print('       f_sysclk: %7.3f MHz' % (rcc.f_sysclk / 1e6))
    print('----------------------------------')
    pwr.set_vos(VOS)
    if USE_HSE:
        rcc.set_pll_source(2)
    else:
        rcc.set_pll_source(0)
    rcc.configure_pll_p_clk(M, N, P)
    rcc.set_sysclock_source(3)
    print('       f_sysclk: %7.3f MHz' % (rcc.f_sysclk / 1e6))
    print('f_sys_d1cpre_ck: %7.3f MHz' % (rcc.f_sys_d1cpre_ck / 1e6))
    print('         f_hclk: %7.3f MHz' % (rcc.f_hclk / 1e6))
    print('        f_pclk1: %7.3f MHz' % (rcc.f_pclk1 / 1e6))
    print('        f_pclk2: %7.3f MHz' % (rcc.f_pclk2 / 1e6))
    print('        f_pclk3: %7.3f MHz' % (rcc.f_pclk3 / 1e6))
    print('        f_pclk4: %7.3f MHz' % (rcc.f_pclk4 / 1e6))
    print('  f_timx_ker_ck: %7.3f MHz' % (rcc.f_timx_ker_ck / 1e6))
    print('  f_timy_ker_ck: %7.3f MHz' % (rcc.f_timy_ker_ck / 1e6))

    # Configure TIM15 to toggle at 1/1000th the timer kernel clock frequency
    # if requested.
    if rv.enable_tim15:
        # Enable PE5 as TIM15_CH1.
        rcc.enable_device('GPIOE')
        pe                  = target.devs['GPIOE']
        pe._AFRL.AFSEL5     = 4
        pe._MODER.MODE5     = 2
        pe._OTYPER.OT5      = 0
        pe._OSPEEDR.OSPEED5 = 3
        pe._PUPDR.PUPD5     = 0

        # Set up the timer.
        rcc.enable_device('TIM15')
        tim15        = target.devs['TIM15']
        tim15._SMCR  = 0
        tim15._CCER  = 0
        tim15._CR1   = 0
        ccmr         = tim15._CCMR1.read()
        ccmr        &= ~0x00010070
        ccmr        |= 0x00000030
        tim15._CCMR1 = ccmr
        tim15._CCR1  = 0
        tim15._CCER  = 0x00000001
        tim15._CR1   = 0
        tim15._PSC   = 0
        tim15._ARR   = (1000 // 2) - 1
        tim15._CNT   = 0
        tim15._BDTR  = 0x00008000
        tim15._CR1   = 0x00000001

    # Prepare a 16-bit sine wave in SRAM1.
    zap     = struct.pack('<H', 0x800) * 65536
    sram1.ap.write_bulk(zap, sram1.dev_base)
    npoints = 480
    wave    = b''
    for i in range(npoints):
        v = 0x800 + rv.amplitude * math.sin((i + 1) * 2 * math.pi / npoints)
        wave += struct.pack('<H', int(v))
    sram1.ap.write_bulk(wave, sram1.dev_base)

    # Enable both DAC channels.  Set the bias output as a constant value
    # on DAC1.1 and configure DAC1.2 to fetch the sine wave using DMA.
    rcc.enable_device('DAC1')
    dac._CR      = 0x00000000   # Zap everything
    dac._MCR     = 0x00020002   # External pin with buffer disabled
    dac._CR      = 0x10160000   # DAC1.2 DMA TRIG5 (TIM6), DAC1.1 manual
    dac._CR      = 0x10170001   # Enable.
    dac._DHR12R1 = rv.bias
    dac._DHR12R2 = 0x800

    # Configure TIM6 to trigger every 10 cycles (24 MHz update rate) but don't
    # start it yet.  We do this before enabling DMA in order to clear any stale
    # DMA requests from TIM6.  The H7 doesn't seem to be capable of going
    # faster than once every 10 cycles.
    rcc.enable_device('TIM6')
    tim6._CR1     = 0x00000000
    tim6._CR2     = (2 << 4)        # TRGO on UPDATE
    tim6._DIER    = 0
    tim6._ARR     = (10 - 1)
    tim6._CNT     = 0
    tim6._PSC     = 0
    tim6._SR      = 0

    # Configura DMAMUX1 channel 0 to service DAC1.2.
    dmamux1._C0CR = 68

    # Configure DMA1 to transfer SRAM1 as a circular buffer to DHR12R2.
    # Use burst mode.
    rcc.enable_device('DMA1')
    dma1._S0CR = 0x00000000
    while dma1._S0CR.read() & 1:
        pass
    dma1._LIFCR  = 0x0000003D
    dma1._S0CR   = 0x00802D40
    dma1._S0NDTR = npoints
    dma1._S0PAR  = dac._DHR12R2.addr
    dma1._S0M0AR = sram1.dev_base
    dma1._S0M1AR = 0x00000000
    dma1._S0FCR  = 0x00000005
    dma1._S0CR   = 0x00802D41

    # Finally, start TIM6 to trigger DAC updates and DMA transfers.
    tim6._CR1 = 0x00000001


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump-debuggers', '-d', action='store_true')
    parser.add_argument('--usb-path')
    parser.add_argument('--probe-freq', type=int, default=1000000)
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--enable-tim15', action='store_true')
    parser.add_argument('--amplitude', '-a', type=autoint, default=0x0800)
    parser.add_argument('--bias', '-b', type=autoint, default=0x0800)
    rv = parser.parse_args()

    try:
        main(rv)
    except psdb.ProbeException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    _main()
