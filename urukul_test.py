from artiq.coredevice.urukul2 import (
    urukul_sta_drover,
    urukul_sta_ifc_mode,
    urukul_sta_pll_lock,
    urukul_sta_proto_rev,
    urukul_sta_rf_sw,
    urukul_sta_smp_err,
)
from artiq.experiment import *


class Urukul_Testing(EnvExperiment):
    """Urukul Testing"""

    def build(self):
        self.setattr_device("core")
        self.setattr_device("urukul1_ch0")
        self.setattr_device("urukul1_cpld")
        # self.setattr_device("urukul1_ch1")
        self.setattr_device("urukul1_ch3")

    @kernel
    def status_register(self):
        self.core.reset()
        self.urukul1_cpld.init()

        ## Retreive STATUS register
        sta = self.urukul1_cpld.sta_read()
        rf_sw = urukul_sta_rf_sw(sta)
        smp_err = urukul_sta_smp_err(sta)
        pll_lock = urukul_sta_pll_lock(sta)
        drover = urukul_sta_drover(sta)
        ifc_mode = urukul_sta_ifc_mode(sta)
        proto_rev = urukul_sta_proto_rev(sta)
        print(rf_sw, smp_err, pll_lock, drover, ifc_mode, proto_rev)

    @kernel
    def channel_0_3_io_update_device(self):
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
        """Required device_db DDS's to not have io_update_device
        field set so that CFG.IO_UPDATE is used instead.
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
        self.urukul1_ch0.set(freq, amplitude=amp)
        self.urukul1_ch3.set(freq, amplitude=amp)
        # Set MASK_NU to trigger CFG.IO_UPDATE
        self.urukul1_ch0.cfg_mn(True)
        self.urukul1_ch3.cfg_mn(True)
        # Switch on waveforms
        self.urukul1_ch0.cfg_sw(True)
        self.urukul1_ch3.cfg_sw(True)

        delay(10 * s)

        # Switch off waveforms
        self.urukul1_ch0.cfg_sw(False)
        self.urukul1_ch3.cfg_sw(False)

    @kernel
    def channel_0_3_cfg_io_update_toggle_profiles(self):
        """Toggle CFG.PROFILES[0:2] for channel 0 and 3.

        Required device_db DDS's to not have io_update_device
        field set so that CFG.IO_UPDATE is used instead.
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

        # Set MASK_NU to trigger CFG.IO_UPDATE
        self.urukul1_ch0.cfg_mn(True)
        self.urukul1_ch3.cfg_mn(True)

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
    def run(self):
        # self.status_register()
        # io_update_device must not be set for DDS's in device_db
        # self.channel_0_3_cfg_io_update()
        self.channel_0_3_cfg_io_update_toggle_profiles()

        ## Test urukul0 (v1.3) by reading the CPLD STATUS register twice in a row without ending the SPI transaction to see how it responds to multiple 24 bit transactions....

        ## PROFILES
        ## Set 8 different profiles and use the SPI interface to toggle them

        ## DRG
