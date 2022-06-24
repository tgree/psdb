# Copyright (c) 2022 Phase Advanced Sensor Systems, Inc.
from .xtswd import XTSWD, Status, Opcode, Command, Response


RSP_EP  = 0x81
CMD_EP  = 0x02
IMON_EP = 0x83


class XTSWD_096(XTSWD):
    def __init__(self, usb_dev):
        super().__init__(usb_dev, CMD_EP, RSP_EP, IMON_EP)
        self.njunk_bytes = self._synchronize()

    def _synchronize(self):
        '''
        Recover the connection if it was interrupted previously.  There could
        be a bunch of data posted on the RSP EP from a previous lifetime, so
        we post illegal commands to the probe until we get a 32-byte response.
        However, that 32-byte response could be the end of the previous life's
        transfer, so do a final illegal command and then check for the expected
        opcode and tag.
        '''
        tag  = self._alloc_tag()
        cmd  = Command(opcode=Opcode.BAD_OPCODE, tag=tag)
        data = cmd.pack()
        junk = 0
        while True:
            self.usb_dev.write(CMD_EP, data)
            rsp = self.usb_dev.read(RSP_EP, 64)
            if len(rsp) == 32:
                break

            junk += len(rsp)

        self.usb_dev.write(CMD_EP, data)
        data = self.usb_dev.read(RSP_EP, 64)
        assert len(data) == 32

        rsp = Response.unpack(data)
        assert rsp.tag    == tag
        assert rsp.opcode == Opcode.BAD_OPCODE
        assert rsp.status == Status.BAD_OPCODE

        return junk

    def _decode_rsp(self, data):
        rsp     = Response.unpack(data[-Response._STRUCT.size:])
        rx_data = bytes(data[:-Response._STRUCT.size])
        return rsp, rx_data
