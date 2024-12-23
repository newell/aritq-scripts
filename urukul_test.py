import artiq.coredevice.spi2 as spi
from artiq.coredevice.ad9910 import (
    _AD9910_REG_ASF,
    _AD9910_REG_RAMP_LIMIT,
    _AD9910_REG_RAMP_RATE,
    _AD9910_REG_RAMP_STEP,
)
from artiq.coredevice.urukul import (
    CS_CFG,
    SPI_CONFIG,
    SPIT_CFG_RD,
    urukul_sta_drover,
    urukul_sta_ifc_mode,
    urukul_sta_pll_lock,
    urukul_sta_proto_rev,
    urukul_sta_rf_sw,
    urukul_sta_smp_err,
)
from artiq.experiment import *
from numpy import int64


class Urukul_Testing(EnvExperiment):
    """Urukul Testing"""

    def build(self):
        self.setattr_device("core")
        self.setattr_device("urukul0_cpld")
        self.setattr_device("urukul1_cpld")
        self.setattr_device("urukul1_ch0")
        # self.setattr_device("urukul1_ch1")
        self.setattr_device("urukul1_ch3")

    # @kernel
    # def read_twice_sta(self):
    #     """Test if Urukulv1.3 and what happens if we blah blah"""
    #     self.core.reset()
    #     self.urukul0_cpld.init()

    #     ## Retreive STATUS register
    #     self.urukul0_cpld.bus.set_config_mu(
    #         SPI_CONFIG | spi.SPI_INPUT, 24, SPIT_CFG_RD, CS_CFG
    #     )
    #     self.urukul0_cpld.bus.write(((self.urukul0_cpld.cfg_reg >> 24) & 0xFFFFFF) << 8)
    #     self.urukul0_cpld.bus.set_config_mu(
    #         SPI_CONFIG | spi.SPI_END | spi.SPI_INPUT, 24, SPIT_CFG_RD, CS_CFG
    #     )
    #     self.urukul0_cpld.bus.write((self.urukul0_cpld.cfg_reg & 0xFFFFFF) << 8)
    #     hi = self.urukul0_cpld.bus.read()
    #     lo = self.urukul0_cpld.bus.read()
    #     print(hi, lo)
    #     # sta = (int64(hi) << 24) | lo  # I think this will work
    #     # print(sta)
    #     ## THE ABOVE WAS FOR TESTING HOW OLD HW WORKS WITH NEWER DRIVER METHODS

    #     ## THE BELOW WORKS
    #     # # sta = self.urukul0_cpld.sta_read()
    #     # rf_sw = urukul_sta_rf_sw(sta)
    #     # smp_err = urukul_sta_smp_err(sta)
    #     # pll_lock = urukul_sta_pll_lock(sta)
    #     # drover = urukul_sta_drover(sta)
    #     # ifc_mode = urukul_sta_ifc_mode(sta)
    #     # proto_rev = urukul_sta_proto_rev(sta)
    #     # print(rf_sw, smp_err, pll_lock, drover, ifc_mode, proto_rev)

    @kernel
    def status_register(self):
        self.core.reset()
        self.urukul1_cpld.init()

        ## Read STATUS register
        sta = self.urukul1_cpld.sta_read()
        rf_sw = urukul_sta_rf_sw(sta)
        smp_err = urukul_sta_smp_err(sta)
        pll_lock = urukul_sta_pll_lock(sta)
        ifc_mode = urukul_sta_ifc_mode(sta)
        proto_rev = urukul_sta_proto_rev(sta)
        drover = urukul_sta_drover(sta)
        print(rf_sw, smp_err, pll_lock, ifc_mode, proto_rev, drover, sta)

    @kernel
    def channel_0_3_cfg(self, io_update_device=True):
        """Required device_db DDS's to have io_update_device field set."""
        self.core.reset()
        self.urukul1_cpld.init()
        # # Set ATT_EN
        # self.urukul1_ch0.cfg_att_en(True)
        # self.urukul1_ch3.cfg_att_en(True)
        # if not io_update_device:
        #     # Set MASK_NU to trigger CFG.IO_UPDATE
        #     self.urukul1_ch0.cfg_mask_nu(True)
        #     self.urukul1_ch3.cfg_mask_nu(True)

        self.urukul1_ch0.init()
        self.urukul1_ch3.init()

        delay(10 * ms)

        freq = 100 * MHz
        amp = 1.0
        attenuation = 1.0

        self.urukul1_ch0.set(freq, amplitude=amp)
        self.urukul1_ch3.set(freq, amplitude=amp)

        # Switch on waveforms
        self.urukul1_ch0.cfg_sw(True)
        self.urukul1_ch3.cfg_sw(True)

        self.urukul1_ch0.set_att(attenuation)
        self.urukul1_ch3.set_att(attenuation)

        delay(5 * s)

        # Switch off waveforms
        self.urukul1_ch0.cfg_sw(False)
        self.urukul1_ch3.cfg_sw(False)

        # if not io_update_device:
        #     # Set MASK_NU to trigger CFG.IO_UPDATE
        #     self.urukul1_ch0.cfg_mask_nu(False)
        #     self.urukul1_ch3.cfg_mask_nu(False)

        # # UnSet ATT_EN
        # self.urukul1_ch0.cfg_att_en(False)
        # self.urukul1_ch3.cfg_att_en(False)

    @kernel
    def channel_0_3_toggle_profiles(self, io_update_device=True):
        """Toggle CFG.PROFILES[0:2] for channel 0 and 3.

        Required device_db DDS's to have io_update_device
        field set so that CFG.IO_UPDATE is not used instead.
        """
        self.core.reset()
        self.urukul1_cpld.init()
        # Set ATT_EN
        self.urukul1_ch0.cfg_att_en(True)
        self.urukul1_ch3.cfg_att_en(True)
        if not io_update_device:
            # Set MASK_NU to trigger CFG.IO_UPDATE
            self.urukul1_ch0.cfg_mask_nu(True)
            self.urukul1_ch3.cfg_mask_nu(True)

        self.urukul1_ch0.init()
        self.urukul1_ch3.init()

        delay(10 * ms)

        freq = 100 * MHz
        amp = 1.0
        attenuation = 1.0

        ## SET SINGLE-TONE PROFILES
        # Set Profile 7 (default)
        self.urukul1_ch0.set(freq, amplitude=amp)
        self.urukul1_ch3.set(freq, amplitude=amp)
        # Set Profile 6 (default)
        self.urukul1_ch0.set(freq + 25 * MHz, amplitude=amp, profile=6)
        self.urukul1_ch3.set(freq + 25 * MHz, amplitude=amp, profile=6)
        # Set Profile 5 (default)
        self.urukul1_ch0.set(freq + 50 * MHz, amplitude=amp, profile=5)
        self.urukul1_ch3.set(freq + 50 * MHz, amplitude=amp, profile=5)
        # Set Profile 4 (default)
        self.urukul1_ch0.set(freq + 75 * MHz, amplitude=amp, profile=4)
        self.urukul1_ch3.set(freq + 75 * MHz, amplitude=amp, profile=4)

        delay(1 * s)  # slack

        # Set Profile 3 (default)
        self.urukul1_ch0.set(freq + 100 * MHz, amplitude=amp, profile=3)
        self.urukul1_ch3.set(freq + 100 * MHz, amplitude=amp, profile=3)
        # Set Profile 2 (default)
        self.urukul1_ch0.set(freq + 125 * MHz, amplitude=amp, profile=2)
        self.urukul1_ch3.set(freq + 125 * MHz, amplitude=amp, profile=2)
        # Set Profile 1 (default)
        self.urukul1_ch0.set(freq + 150 * MHz, amplitude=amp, profile=1)
        self.urukul1_ch3.set(freq + 150 * MHz, amplitude=amp, profile=1)
        # Set Profile 0 (default)
        self.urukul1_ch0.set(freq + 175 * MHz, amplitude=amp, profile=0)
        self.urukul1_ch3.set(freq + 175 * MHz, amplitude=amp, profile=0)

        # Switch on waveforms -- Profile 7 (default)
        self.urukul1_ch0.cfg_sw(True)
        self.urukul1_ch3.cfg_sw(True)
        self.urukul1_ch0.set_att(attenuation)
        self.urukul1_ch3.set_att(attenuation)
        delay(2 * s)
        # Switch off waveforms
        self.urukul1_ch0.cfg_sw(False)
        self.urukul1_ch3.cfg_sw(False)

        # Iterate over Profiles 6 to 0
        for i in range(6, -1, -1):
            # Switch channels 0 and 3 to Profile i
            self.urukul1_cpld.set_profile(0, i)
            self.urukul1_cpld.set_profile(3, i)
            self.urukul1_ch0.cfg_sw(True)
            self.urukul1_ch3.cfg_sw(True)
            delay(2 * s)
            # Switch off waveforms
            self.urukul1_ch0.cfg_sw(False)
            self.urukul1_ch3.cfg_sw(False)

        if not io_update_device:
            # Set MASK_NU to trigger CFG.IO_UPDATE
            self.urukul1_ch0.cfg_mask_nu(False)
            self.urukul1_ch3.cfg_mask_nu(False)

        # UnSet ATT_EN
        self.urukul1_ch0.cfg_att_en(False)
        self.urukul1_ch3.cfg_att_en(False)

    @kernel
    def osk(self, io_update_device=True):
        self.core.reset()
        self.urukul1_cpld.init()
        # Set ATT_EN
        self.urukul1_ch0.cfg_att_en(True)
        if not io_update_device:
            # Set MASK_NU to trigger CFG.IO_UPDATE
            self.urukul1_ch0.cfg_mask_nu(True)

        self.urukul1_ch0.init()

        delay(10 * ms)

        freq = 100 * MHz
        amp = 1.0
        attenuation = 1.0

        self.urukul1_ch0.set(freq, amplitude=amp)
        self.urukul1_ch0.set_cfr1(manual_osk_external=1, osk_enable=1)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)
        self.urukul1_ch0.set_asf(0x3FFF)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)

        # Switch on waveform, then set attenuation
        self.urukul1_ch0.cfg_sw(True)
        self.urukul1_ch0.set_att(attenuation)
        for _ in range(10):
            # Toggle output via OSK
            self.urukul1_ch0.cfg_osk(True)
            delay(1 * s)
            self.urukul1_ch0.cfg_osk(False)
            delay(1 * s)
        # Switch off waveform
        self.urukul1_ch0.cfg_sw(False)

        if not io_update_device:
            # Set MASK_NU to trigger CFG.IO_UPDATE
            self.urukul1_ch0.cfg_mask_nu(False)

        # UnSet ATT_EN
        self.urukul1_ch0.cfg_att_en(False)

    @kernel
    def osk_auto(self, io_update_device=True):
        self.core.reset()
        self.urukul1_cpld.init()
        # Set ATT_EN
        self.urukul1_ch0.cfg_att_en(True)
        if not io_update_device:
            # Set MASK_NU to trigger CFG.IO_UPDATE
            self.urukul1_ch0.cfg_mask_nu(True)

        self.urukul1_ch0.init()

        delay(10 * ms)

        freq = 100 * MHz
        amp = 1.0
        attenuation = 1.0

        self.urukul1_ch0.set(freq, amplitude=amp)
        self.urukul1_ch0.set_cfr1(osk_enable=1, select_auto_osk=1)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)
        self.urukul1_ch0.write32(_AD9910_REG_ASF, 0xFFFF << 16 | 0x3FFF << 2 | 0b11)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)

        # Switch on waveform, then set attenuation
        self.urukul1_ch0.cfg_sw(True)
        self.urukul1_ch0.set_att(attenuation)
        for _ in range(10):
            self.urukul1_ch0.cfg_osk(True)
            delay(1 * s)
            self.urukul1_ch0.cfg_osk(False)
            delay(1 * s)
        # Switch off waveform
        self.urukul1_ch0.cfg_sw(False)

        if not io_update_device:
            # Set MASK_NU to trigger CFG.IO_UPDATE
            self.urukul1_ch0.cfg_mask_nu(False)

        # UnSet ATT_EN
        self.urukul1_ch0.cfg_att_en(False)

    @kernel
    def drg_ramp_generator_normal(self, io_update_device=True):
        self.core.reset()
        self.urukul1_cpld.init()
        # Set ATT_EN
        self.urukul1_ch0.cfg_att_en(True)
        if not io_update_device:
            # Set MASK_NU to trigger CFG.IO_UPDATE
            self.urukul1_ch0.cfg_mask_nu(True)

        self.urukul1_ch0.init()

        delay(10 * ms)

        freq = 100 * MHz
        amp = 1.0
        attenuation = 1.0

        self.urukul1_ch0.frequency_to_ftw(100 * MHz)
        # cfr2 21:20 destination, 19 drg enable, no-dwell high, no-dwell low,
        self.urukul1_ch0.set(freq, amplitude=amp)
        self.urukul1_ch0.set_cfr2(drg_enable=1)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)
        self.urukul1_ch0.write64(
            _AD9910_REG_RAMP_LIMIT,
            self.urukul1_ch0.frequency_to_ftw(130 * MHz),
            self.urukul1_ch0.frequency_to_ftw(70 * MHz),
        )
        # The larger the values, the slower the update happens
        self.urukul1_ch0.write32(_AD9910_REG_RAMP_RATE, 0x004F004F)
        # The smaller the value it is, the smaller the frequency step
        self.urukul1_ch0.write64(_AD9910_REG_RAMP_STEP, 0xF0, 0xF0)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)

        # Switch on waveform, then set attenuation
        self.urukul1_ch0.cfg_sw(True)
        self.urukul1_ch0.set_att(attenuation)
        for _ in range(10):
            self.urukul1_ch0.cfg_drctl(True)
            delay(0.5 * s)
            self.urukul1_ch0.cfg_drctl(False)
            delay(0.5 * s)
        # Switch off waveform
        self.urukul1_ch0.cfg_sw(False)

        if not io_update_device:
            # Set MASK_NU to trigger CFG.IO_UPDATE
            self.urukul1_ch0.cfg_mask_nu(False)

        # UnSet ATT_EN
        self.urukul1_ch0.cfg_att_en(False)

    @kernel
    def drg_ramp_generator_normal_with_hold(self, io_update_device=True):
        self.core.reset()
        self.urukul1_cpld.init()
        # Set ATT_EN
        self.urukul1_ch0.cfg_att_en(True)
        if not io_update_device:
            # Set MASK_NU to trigger CFG.IO_UPDATE
            self.urukul1_ch0.cfg_mask_nu(True)

        self.urukul1_ch0.init()

        delay(10 * ms)

        freq = 100 * MHz
        amp = 1.0
        attenuation = 1.0

        self.urukul1_ch0.frequency_to_ftw(100 * MHz)
        # cfr2 21:20 destination, 19 drg enable, no-dwell high, no-dwell low,
        self.urukul1_ch0.set(freq, amplitude=amp)
        self.urukul1_ch0.set_cfr2(drg_enable=1)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)
        self.urukul1_ch0.write64(
            _AD9910_REG_RAMP_LIMIT,
            self.urukul1_ch0.frequency_to_ftw(130 * MHz),
            self.urukul1_ch0.frequency_to_ftw(70 * MHz),
        )
        # The larger the values, the slower the update happens
        self.urukul1_ch0.write32(_AD9910_REG_RAMP_RATE, 0x004F004F)
        # The smaller the value it is, the smaller the frequency step
        self.urukul1_ch0.write64(_AD9910_REG_RAMP_STEP, 0xF0, 0xF0)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)

        # Switch on waveform, then set attenuation
        self.urukul1_ch0.cfg_sw(True)
        self.urukul1_ch0.set_att(attenuation)
        for _ in range(10):
            self.urukul1_ch0.cfg_drctl(True)
            delay(0.25 * s)
            self.urukul1_ch0.cfg_drhold(True)
            delay(0.25)
            self.urukul1_ch0.cfg_drhold(False)
            delay(0.25)
            self.urukul1_ch0.cfg_drctl(False)
            delay(0.25)
            self.urukul1_ch0.cfg_drhold(True)
            delay(0.25)
            self.urukul1_ch0.cfg_drhold(False)
            delay(0.25)
        # Switch off waveform
        self.urukul1_ch0.cfg_sw(False)

        if not io_update_device:
            # Set MASK_NU to trigger CFG.IO_UPDATE
            self.urukul1_ch0.cfg_mask_nu(False)

        # UnSet ATT_EN
        self.urukul1_ch0.cfg_att_en(False)

    @kernel
    def drg_ramp_generator_nodwell(self, io_update_device=True):
        self.core.reset()
        self.urukul1_cpld.init()
        # Set ATT_EN
        self.urukul1_ch0.cfg_att_en(True)
        if not io_update_device:
            # Set MASK_NU to trigger CFG.IO_UPDATE
            self.urukul1_ch0.cfg_mask_nu(True)

        self.urukul1_ch0.init()

        delay(10 * ms)

        freq = 100 * MHz
        amp = 1.0
        attenuation = 1.0

        self.urukul1_ch0.frequency_to_ftw(100 * MHz)
        # cfr2 21:20 destination, 19 drg enable, no-dwell high, no-dwell low,
        self.urukul1_ch0.set(freq, amplitude=amp)
        self.urukul1_ch0.set_cfr2(drg_enable=1, drg_nodwell_high=1, drg_nodwell_low=1)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)
        self.urukul1_ch0.write64(
            _AD9910_REG_RAMP_LIMIT,
            self.urukul1_ch0.frequency_to_ftw(130 * MHz),
            self.urukul1_ch0.frequency_to_ftw(70 * MHz),
        )
        # The larger the values, the slower the update happens
        self.urukul1_ch0.write32(_AD9910_REG_RAMP_RATE, 0x004F004F)
        # The smaller the value it is, the smaller the frequency step
        self.urukul1_ch0.write64(_AD9910_REG_RAMP_STEP, 0xF0, 0xF0)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)

        # Switch on waveform, then set attenuation
        self.urukul1_ch0.cfg_sw(True)
        self.urukul1_ch0.set_att(attenuation)

        delay(10 * s)
        # Switch off waveform
        self.urukul1_ch0.cfg_sw(False)

        if not io_update_device:
            # Set MASK_NU to trigger CFG.IO_UPDATE
            self.urukul1_ch0.cfg_mask_nu(False)

        # UnSet ATT_EN
        self.urukul1_ch0.cfg_att_en(False)

    @kernel
    def att_channel_0_3(self, io_update_device=True):
        self.core.reset()
        self.urukul1_cpld.init()
        # Set ATT_EN
        self.urukul1_ch0.cfg_att_en(True)
        self.urukul1_ch3.cfg_att_en(True)
        if not io_update_device:
            # Set MASK_NU to trigger CFG.IO_UPDATE
            self.urukul1_ch0.cfg_mask_nu(True)
            self.urukul1_ch3.cfg_mask_nu(True)

        self.urukul1_ch0.init()
        self.urukul1_ch3.init()

        delay(10 * ms)

        freq = 100 * MHz
        amp = 1.0

        self.urukul1_ch0.set(freq, amplitude=amp)
        self.urukul1_ch3.set(freq, amplitude=amp)

        delay(1 * ms)

        # Switch on waveforms
        self.urukul1_ch0.cfg_sw(True)
        self.urukul1_ch3.cfg_sw(True)

        # This must be set AFTER cfg_sw set to truw for some reason
        # Also, if not set, then the attenuators have a default attenuation
        # and this needs to be set....
        self.urukul1_ch0.set_att(0.0 * dB)
        self.urukul1_ch3.set_att(0.0 * dB)

        delay(5 * s)

        self.urukul1_ch0.set_att(10.0)
        self.urukul1_ch3.set_att(10.0)

        delay(5 * s)

        self.urukul1_ch0.set_att(20.0)
        self.urukul1_ch3.set_att(20.0)

        delay(5 * s)

        self.urukul1_ch0.set_att(30.0)
        self.urukul1_ch3.set_att(30.0)

        delay(5 * s)

        # Switch off waveforms
        self.urukul1_ch0.cfg_sw(False)
        self.urukul1_ch3.cfg_sw(False)

        if not io_update_device:
            # Set MASK_NU to trigger CFG.IO_UPDATE
            self.urukul1_ch0.cfg_mask_nu(False)
            self.urukul1_ch3.cfg_mask_nu(False)

        # UnSet ATT_EN
        self.urukul1_ch0.cfg_att_en(False)
        self.urukul1_ch3.cfg_att_en(False)

    @kernel
    def run(self):
        ## TEST v1.3 with new version read_sta
        # self.read_twice_sta()

        ## STATUS REGISTER
        # self.status_register()

        ## SINGLE-TONE PROFILE
        self.channel_0_3_cfg()
        # self.channel_0_3_cfg(io_update_device=False)

        ## PROFILES
        # self.channel_0_3_toggle_profiles()
        # self.channel_0_3_toggle_profiles(io_update_device=False)

        ## OSK
        # self.osk()
        # self.osk(io_update_device=False)
        # self.osk_auto()
        # self.osk_auto(io_update_device=False)

        ## DRG
        # self.drg_ramp_generator_normal()
        # self.drg_ramp_generator_normal(io_update_device=False)
        # self.drg_ramp_generator_normal_with_hold()
        # self.drg_ramp_generator_normal_with_hold(io_update_device=False)
        # self.drg_ramp_generator_nodwell()
        # self.drg_ramp_generator_nodwell(io_update_device=False)

        ## ATT
        # self.att_channel_0_3()
        # self.att_channel_0_3(io_update_device=False)
