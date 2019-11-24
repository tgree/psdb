# Copyright (c) 2018-2019 Phase Advanced Sensor Systems, Inc.
MATCHERS = []


class Matcher(object):
    def __init__(self, cls, cidr, pidr, cidr_mask=0xFFFFFFFF,
                 pidr_mask=0xFFFFFFFFFFFFFFFF, subtype=''):
        self.cls       = cls
        self.cidr      = cidr
        self.cidr_mask = cidr_mask
        self.pidr      = pidr
        self.pidr_mask = pidr_mask
        self.subtype   = subtype
        MATCHERS.append(self)

    def _cidr_match(self, c):
        return (self.cidr & self.cidr_mask) == (c.cidr & self.cidr_mask)

    def _pidr_match(self, c):
        return (self.pidr & self.pidr_mask) == (c.pidr & self.pidr_mask)

    def score(self, c):
        return 100 if self._cidr_match(c) and self._pidr_match(c) else 0


class StaticMatcher(Matcher):
    def __init__(self, cls, apsel, addr, cidr, pidr, **kwargs):
        super(StaticMatcher, self).__init__(cls, cidr, pidr, **kwargs)
        self.apsel = apsel
        self.addr  = addr

    def score(self, c):
        if self.apsel != c.ap.ap_num or self.addr != c.addr:
            return 0
        return super(StaticMatcher, self).score(c)*2


def match(c):
    scores = [(m.score(c), m) for m in MATCHERS]
    scores.sort(key=lambda s: s[0])
    if scores and scores[-1][0] > 0:
        m = scores[-1][1]
        return m.cls(c, m.subtype)
    return c
