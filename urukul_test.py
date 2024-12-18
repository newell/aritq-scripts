import artiq.coredevice.spi2 as spi
from artiq.coredevice.ad99102 import _AD9910_REG_ASF
from artiq.coredevice.urukul import CS_CFG, SPI_CONFIG, SPIT_CFG_RD
from artiq.coredevice.urukul2 import (
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

    @kernel
    def read_twice_sta(self):
        """Test if Urukulv1.3 and what happens if we blah blah"""
        self.core.reset()
        self.urukul0_cpld.init()

        ## Retreive STATUS register
        self.urukul0_cpld.bus.set_config_mu(
            SPI_CONFIG | spi.SPI_INPUT, 24, SPIT_CFG_RD, CS_CFG
        )
        self.urukul0_cpld.bus.write(((self.urukul0_cpld.cfg_reg >> 24) & 0xFFFFFF) << 8)
        self.urukul0_cpld.bus.set_config_mu(
            SPI_CONFIG | spi.SPI_END | spi.SPI_INPUT, 24, SPIT_CFG_RD, CS_CFG
        )
        self.urukul0_cpld.bus.write((self.urukul0_cpld.cfg_reg & 0xFFFFFF) << 8)
        hi = self.urukul0_cpld.bus.read()
        lo = self.urukul0_cpld.bus.read()
        print(hi, lo)
        # sta = (int64(hi) << 24) | lo  # I think this will work
        # print(sta)
        ## THE ABOVE WAS FOR TESTING HOW OLD HW WORKS WITH NEWER DRIVER METHODS

        ## THE BELOW WORKS
        # # sta = self.urukul0_cpld.sta_read()
        # rf_sw = urukul_sta_rf_sw(sta)
        # smp_err = urukul_sta_smp_err(sta)
        # pll_lock = urukul_sta_pll_lock(sta)
        # drover = urukul_sta_drover(sta)
        # ifc_mode = urukul_sta_ifc_mode(sta)
        # proto_rev = urukul_sta_proto_rev(sta)
        # print(rf_sw, smp_err, pll_lock, drover, ifc_mode, proto_rev)

    @kernel
    def status_register(self):
        self.core.reset()
        self.urukul1_cpld.init()

        # INFO:worker(923,urukul_test.py):print:0
        # The above is returned when proto_rev 0x09 hw tries to use the previous sta_read
        # INFO:worker(923,urukul_test.py):print:140737497792512
        # The above is returned when first trying the 0x08 way of doing it and then the new way of doing it
        # INFO:dashboard:artiq.dashboard.experiments:Submitted 'repo:Urukul Testing', RID is 924
        # INFO:worker(924,urukul_test.py):print:9437184
        # The above is returned when the new way of doing it is done.

        # self.urukul1_cpld.bus.set_config_mu(
        #     SPI_CONFIG | spi.SPI_END | spi.SPI_INPUT, 24, SPIT_CFG_RD, CS_CFG
        # )
        # self.urukul1_cpld.bus.write(self.urukul1_cpld.cfg_reg << 8)
        # print(self.urukul1_cpld.bus.read())
        # # return self.bus.read()
        # delay(1 * s)

        ## Retreive STATUS register
        sta = self.urukul1_cpld.sta_read()
        rf_sw = urukul_sta_rf_sw(sta)
        smp_err = urukul_sta_smp_err(sta)
        pll_lock = urukul_sta_pll_lock(sta)
        drover = urukul_sta_drover(sta)
        ifc_mode = urukul_sta_ifc_mode(sta)
        proto_rev = urukul_sta_proto_rev(sta)
        # print(sta)
        print(rf_sw, smp_err, pll_lock, drover, ifc_mode, proto_rev, sta)
        # The above outputs 0 0 0 0 0 9 9437184
        # The reason I am documenting the above is because in the event that they think I should keep the same urukul/ad9910 drivers then
        # we can either have the user pass something init (I would need to move where self.cfg_reg is initialized into init (unless can get it from call to setattr call))
        # or we can use the above hack.  In the event they are okay with different driver versions I would need to update how template_dbb and eem are creating things
        # for the device db etc.  I can worry about this after the fact.
        # Howver, the fact that I moved io_update_device to ad9910...this may be a breaking change that requires different driver versions.

    @kernel
    def channel_0_3_cfg_io_update_device(self):
        """Required device_db DDS's to have io_update_device field set."""
        self.core.reset()
        self.urukul1_cpld.init()
        self.urukul1_ch0.init()
        self.urukul1_ch3.init()

        delay(10 * ms)

        freq = 100 * MHz
        amp = 1.0
        attenuation = 1.0

        self.urukul1_ch0.set_att(attenuation)
        self.urukul1_ch3.set_att(attenuation)
        self.urukul1_ch0.set(freq, amplitude=amp)
        self.urukul1_ch3.set(freq, amplitude=amp)
        # Switch on waveforms
        self.urukul1_ch0.cfg_sw(True)
        self.urukul1_ch3.cfg_sw(True)

        delay(10 * s)

        # Switch off waveforms
        self.urukul1_ch0.cfg_sw(False)
        self.urukul1_ch3.cfg_sw(False)

    @kernel
    def channel_0_3_cfg_io_update(self):
        """To test this remove io_update_device from CPLD in
        device_db.py so that CFG.IO_UPDATE is used instead.
        """
        self.core.reset()
        self.urukul1_cpld.init()
        # Set MASK_NU to trigger CFG.IO_UPDATE
        self.urukul1_ch0.cfg_mask_nu(True)
        self.urukul1_ch3.cfg_mask_nu(True)

        self.urukul1_ch0.init()
        self.urukul1_ch3.init()

        delay(10 * ms)

        freq = 200 * MHz
        amp = 1.0
        attenuation = 1.0

        self.urukul1_ch0.set_att(attenuation)
        self.urukul1_ch3.set_att(attenuation)
        self.urukul1_ch0.set(freq, amplitude=amp)
        self.urukul1_ch3.set(freq, amplitude=amp)
        # Switch on waveforms
        self.urukul1_ch0.cfg_sw(True)
        self.urukul1_ch3.cfg_sw(True)

        delay(10 * s)

        # Switch off waveforms
        self.urukul1_ch0.cfg_sw(False)
        self.urukul1_ch3.cfg_sw(False)

    @kernel
    def channel_0_3_io_update_device_toggle_profiles(self):
        """Toggle CFG.PROFILES[0:2] for channel 0 and 3.

        Required device_db DDS's to have io_update_device
        field set so that CFG.IO_UPDATE is not used instead.
        """
        self.core.reset()
        self.urukul1_cpld.init()
        self.urukul1_ch0.init()
        self.urukul1_ch3.init()

        delay(10 * ms)

        freq = 100 * MHz
        amp = 1.0
        attenuation = 1.0

        self.urukul1_ch0.set_att(attenuation)
        self.urukul1_ch3.set_att(attenuation)

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

    @kernel
    def channel_0_3_io_update_toggle_profiles(self):
        """Toggle CFG.PROFILES[0:2] for channel 0 and 3.

        Required device_db DDS's to not have io_update_device
        field set so that CFG.IO_UPDATE is used instead.
        """
        self.core.reset()
        self.urukul1_cpld.init()
        # Set MASK_NU to trigger CFG.IO_UPDATE
        self.urukul1_ch0.cfg_mask_nu(True)
        self.urukul1_ch3.cfg_mask_nu(True)
        self.urukul1_ch0.init()
        self.urukul1_ch3.init()

        delay(10 * ms)

        freq = 100 * MHz
        amp = 1.0
        attenuation = 1.0

        self.urukul1_ch0.set_att(attenuation)
        self.urukul1_ch3.set_att(attenuation)

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

    @kernel
    def osk(self):
        self.core.reset()
        self.urukul1_cpld.init()
        self.urukul1_ch0.init()

        delay(10 * ms)

        freq = 100 * MHz
        amp = 1.0
        attenuation = 1.0

        self.urukul1_ch0.set_att(attenuation)
        self.urukul1_ch0.set(freq, amplitude=amp)
        self.urukul1_ch0.set_cfr1(manual_osk_external=1, osk_enable=1)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)
        self.urukul1_ch0.set_asf(0x3FFF)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)

        # Switch off waveform
        self.urukul1_ch0.cfg_sw(True)
        for _ in range(10):
            # Toggle output via OSK
            self.urukul1_ch0.cfg_osk(True)
            delay(1 * s)
            self.urukul1_ch0.cfg_osk(False)
            delay(1 * s)
        # Switch off waveform
        self.urukul1_ch0.cfg_sw(False)

    @kernel
    def osk_no_io_update_device(self):
        self.core.reset()
        self.urukul1_cpld.init()
        # Set MASK_NU to trigger CFG.IO_UPDATE
        self.urukul1_ch0.cfg_mask_nu(True)
        self.urukul1_ch0.init()

        delay(10 * ms)

        freq = 200 * MHz
        amp = 1.0
        attenuation = 1.0

        self.urukul1_ch0.set_att(attenuation)
        self.urukul1_ch0.set(freq, amplitude=amp)
        self.urukul1_ch0.set_cfr1(manual_osk_external=1, osk_enable=1)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)
        self.urukul1_ch0.set_asf(0x3FFF)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)

        # Switch off waveform
        self.urukul1_ch0.cfg_sw(True)
        for _ in range(10):
            # Toggle output via OSK
            self.urukul1_ch0.cfg_osk(True)
            delay(1 * s)
            self.urukul1_ch0.cfg_osk(False)
            delay(1 * s)
        # Switch off waveform
        self.urukul1_ch0.cfg_sw(False)

    @kernel
    def osk_auto_no_io_update_device(self):
        self.core.reset()
        self.urukul1_cpld.init()
        # Set MASK_NU to trigger CFG.IO_UPDATE
        self.urukul1_ch0.cfg_mask_nu(True)
        self.urukul1_ch0.init()

        delay(10 * ms)

        freq = 100 * MHz
        amp = 1.0
        attenuation = 1.0

        self.urukul1_ch0.set_att(attenuation)
        self.urukul1_ch0.set(freq, amplitude=amp)
        self.urukul1_ch0.set_cfr1(osk_enable=1, select_auto_osk=1)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)
        self.urukul1_ch0.write32(_AD9910_REG_ASF, 0xFFFF << 16 | 0x3FFF << 2 | 0b11)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)

        # Switch off waveform
        self.urukul1_ch0.cfg_sw(True)
        for _ in range(10):
            self.urukul1_ch0.cfg_osk(True)
            delay(1 * s)
            self.urukul1_ch0.cfg_osk(False)
            delay(1 * s)
        # Switch off waveform
        self.urukul1_ch0.cfg_sw(False)

    @kernel
    def drg(self):
        self.core.reset()
        self.urukul1_cpld.init()
        # Set MASK_NU to trigger CFG.IO_UPDATE
        self.urukul1_ch0.cfg_mask_nu(True)
        self.urukul1_ch0.init()

        delay(10 * ms)

        freq = 100 * MHz
        amp = 1.0
        attenuation = 1.0

        # cfr2 21:20 destination, 19 drg enable, no-dwell high, no-dwell low,
        self.urukul1_ch0.set_att(attenuation)
        self.urukul1_ch0.set(freq, amplitude=amp)
        self.urukul1_ch0.set_cfr1(osk_enable=1, select_auto_osk=1)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)
        self.urukul1_ch0.write32(_AD9910_REG_ASF, 0xFFFF << 16 | 0x3FFF << 2 | 0b11)
        self.urukul1_ch0.cpld.io_update.pulse(1 * ms)

        # Switch off waveform
        self.urukul1_ch0.cfg_sw(True)
        for _ in range(10):
            self.urukul1_ch0.cfg_osk(True)
            delay(1 * s)
            self.urukul1_ch0.cfg_osk(False)
            delay(1 * s)
        # Switch off waveform
        self.urukul1_ch0.cfg_sw(False)

    @kernel
    def run(self):
        ## TEST v1.3 with new version read_sta
        # self.read_twice_sta()

        ## STATUS REGISTER READ
        # self.status_register()

        ## SINGLE-TONE PROFILE, 2 CHANNELS
        # self.channel_0_3_cfg_io_update_device()

        ## SINGLE-TONE PROFILE, 2 CHANNELS, NO IO_UPDATE_DEVICE
        # self.channel_0_3_cfg_io_update()

        ## PROFILES
        # self.channel_0_3_io_update_device_toggle_profiles()

        ## PROFILES, NO IO_UPDATE_DEVICE
        # self.channel_0_3_io_update_toggle_profiles()

        ## OSK
        # self.osk()

        ## OSK NO IO_UPDATE_DEVICE
        # self.osk_no_io_update_device()

        ## OSK AUTO
        self.osk_auto_no_io_update_device()

        ## DRG
        # self.drg()
