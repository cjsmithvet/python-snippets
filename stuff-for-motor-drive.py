# At the top

# USED ONLY FOR WORKING AT HOME
# Nest 0: 10.0.0.166, 10.0.0.101, 10.0.0.120, 10.0.0.125.
# Nest X: 10.0.0.113.  (Others do not appear to be on 10.0.0.)
KOLLMORGEN_SINGLE_DRIVE_DEFAULT_ADDRESS = "10.0.0.166"

# In KollmorgenDriveInterface.discover_drives:

        message = bytearray([0x12, 0xaf, 0x12, 0xaf, 0x00, 0x00, 0x00, 0x00,
                             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                             0x00, 0x32, 0x35, 0x35, 0x2e, 0x32, 0x35, 0x35,
                             0x2e, 0x30, 0x2e, 0x30, 0x00, 0x00, 0x00, 0x00,
                             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                             0x00, 0xa4, 0x03, 0x00, 0x00])
        # USE SINGLE ADDRESS FOR WORKING AT HOME
        # server_address = (KOLLMORGEN_SINGLE_DRIVE_DEFAULT_ADDRESS, KOLLMORGEN_DISCOVERY_PORT)
        server_address = (KOLLMORGEN_DISCOVERY_ADDRESS, KOLLMORGEN_DISCOVERY_PORT)

# In RecoveryDriveService.run:

                    # QQQ Testing the rediscovery of drives
                    # global KOLLMORGEN_SINGLE_DRIVE_DEFAULT_ADDRESS
                    # if KOLLMORGEN_SINGLE_DRIVE_DEFAULT_ADDRESS == "10.0.0.166":
                    #     KOLLMORGEN_SINGLE_DRIVE_DEFAULT_ADDRESS = "10.0.0.113"
                    # else:
                    #     KOLLMORGEN_SINGLE_DRIVE_DEFAULT_ADDRESS = "10.0.0.166"

# At the very end, instead of full parsing of the rest server argument:
    rs = RestServer(("", 40000), "Recovery Drive Service",
                    "Provides realtime status data from motor drives")
