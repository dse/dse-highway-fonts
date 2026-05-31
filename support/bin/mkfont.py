#!/usr/bin/env -S fontforge -script
import fontforge, argparse, os, re, json

LETTERS   = "".join([chr(x) for x in range(65,91)])
DIGITS    = "".join([chr(x) for x in range(48,58)])
ALL_CHARS = LETTERS + DIGITS

PRECEDING_CLASSES = [
    "HIJMNU1",                  # 112 # (1)
    "BDGOPQRS2356890",          # 122 # (2)
    "CEFKXZ",                   # 223 # (2)
    "ALTVWY47",                 # 224 # (4)
]
FOLLOWING_CLASSES = [
    "BDEFHIKLMNPRU15",          # (1)
    "CGOQSXZ236890",            # (2)
    "AJTVWY47",                 # (4)
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("font_filename", type=str)
    parser.add_argument("data_filename", type=str)
    parser.add_argument("glyph_filenames", nargs="+")
    parser.add_argument("--metrics-2000", "--2000", action="store_true")
    args = parser.parse_args()
    font = fontforge.font()

    # SVG source files are based on these metrics.
    font.ascent = 960
    font.descent = 192

    for glyph_filename in args.glyph_filenames:
        (dirname, basename) = os.path.split(glyph_filename)
        (root, ext) = os.path.splitext(basename)
        if match := re.fullmatch(r'[0-9a-f]+', root, re.IGNORECASE):
            codepoint = int(root, 16)
        else:
            raise Exception("%s: invalid glyph filename: cannot extract codepoint from %s" % (glyph_filename, repr(root)))

        codepoints = [codepoint]
        if chr(codepoint).lower() != chr(codepoint):
            codepoints.append(codepoint + 32)

        for cp in codepoints:
            glyph = font.createChar(cp)
            font.strokedfont = True
            print("importing %s" % glyph_filename)
            glyph.importOutlines(glyph_filename, correctdir=True)
            font.strokedfont = False
            glyph.left_side_bearing = 0
            glyph.right_side_bearing = 0

    if args.metrics_2000:
        metrics = MetricsMaker2000(font, args.data_filename)
        metrics.run()
    else:
        metrics = MetricsMaker1966(font, args.data_filename)
        metrics.run()

    space_glyph = font.createChar(32)

    # https://mutcd.fhwa.dot.gov/shse/design.pdf:
    # > Spacing between words, words and arrow, a letter
    # > and arrow, or a word and number in a line copy
    # > should be approximately 1 to 1½ times the upper-
    # > case letter height used in that line of copy.
    space_glyph.width = round(font.capHeight)

    # The font authors of Roadgeek Fonts and OC Highway VAR both
    # disagree for narrower fonts.
    space_glyph.width = font[ord("E")].width

    # https://mutcd.fhwa.dot.gov/shse/design.pdf:
    # > Interline spacing should be approximately three-
    # > fourths the average of capital or uppercase letter
    # > heights in adjacent lines of letters.
    em = font.em
    font.ascent += round(font.em / 12)
    font.descent += round(font.em / 12)

    if args.font_filename.endswith(".sfd"):
        print("saving %s" % args.font_filename)
        font.save(args.font_filename)
    else:
        print("generating %s" % args.font_filename)
        font.generate(args.font_filename)

class MetricsMaker2000:
    """
    Set left- and right-side bearings based on 2000 font metric tables.
    """
    def __init__(self, font, data_filename):
        self.data_filename = data_filename
        self.font = font
        with open(data_filename) as fh:
            self.font_data = json.load(fh)
            self.metric_data = self.font_data["2000"]
            self.metrics = self.metric_data["metrics"]
            self.unit = self.font.capHeight / self.metric_data["letterHeightBasis"]
    def run(self):
        for char in ALL_CHARS:
            lsb = roundish(self.metrics[char][0] * self.unit)
            rsb = roundish(self.metrics[char][2] * self.unit)
            self.font[ord(char)].left_side_bearing = round(lsb)
            self.font[ord(char)].right_side_bearing = round(rsb)
            if char.lower() != char:
                self.font[ord(char.lower())].left_side_bearing = round(lsb)
                self.font[ord(char.lower())].right_side_bearing = round(rsb)

class MetricsMaker1966:
    """
    Set left- and right-side bearings based on 1966 code tables.
    This requires kerning classes.
    """
    def __init__(self, font, data_filename):
        self.data_filename = data_filename
        self.font = font
        with open("data/2/spacing.json") as fh:
            self.spacing_data = json.load(fh)
            self.code_numbers = self.spacing_data["codeNumbers"] #
            self.preceding_data = self.code_numbers["preceding"] # values are [1 to 4, 1 to 4, 1 to 4]
            self.following_data = self.code_numbers["following"] # values are 1 to 3
        with open(data_filename) as fh:
            self.font_data = json.load(fh)
            self.metrics = self.font_data["1966"]
            self.code_number_spacings = self.metrics["codeNumberSpacing"] # keys are "1" to "4", values are e.g. 1.5, 1.2, 0.8, 0.4
            self.unit = self.font.capHeight / self.metrics["letterHeightBasis"]
            self.lsbs = {}
            self.rsbs = {}
            self.metrics_2000 = self.font_data["2000"]

    def run(self):
        self.set_bearings(PRECEDING_CLASSES[0], FOLLOWING_CLASSES[0])
        self.set_bearings(PRECEDING_CLASSES[1], FOLLOWING_CLASSES[1])
        self.set_bearings(PRECEDING_CLASSES[2], FOLLOWING_CLASSES[1])
        self.set_bearings(PRECEDING_CLASSES[3], FOLLOWING_CLASSES[2])

        first_classes = tuple([tuple(x) for x in PRECEDING_CLASSES])
        second_classes = tuple([tuple(x) for x in FOLLOWING_CLASSES])
        offsets = []
        for preceding_class in [[], *PRECEDING_CLASSES]:
            rsbs = [self.rsbs[x] for x in preceding_class]
            if len(list(set(rsbs))) > 1:
                raise Exception("invalid PRECEDING_CLASS: %s" % repr(preceding_class))
            for following_class in [[], *FOLLOWING_CLASSES]:
                lsbs = [self.lsbs[x] for x in following_class]
                spacings = []
                if len(list(set(lsbs))) > 1:
                    raise Exception("invalid FOLLOWING_CLASS: %s" % repr(following_class))
                for pchar in preceding_class:
                    for fchar in following_class:
                        spacing = self.get_spacing(pchar , fchar)
                        spacings.append(spacing)
                if len(list(set(spacings))) > 1:
                    raise Exception("spacings not all equal: %s %s" % (repr(preceding_class), repr(following_class)))
                if len(spacings):
                    offsets.append(round(spacings[0] - lsbs[0] - rsbs[0]))
                else:
                    offsets.append(0)
                print(preceding_class, following_class)
        self.font.addLookup("'kern' Horizontal Kerning lookup 0", "gpos_pair", None, (("kern", (("cyrl", ("dflt", ), ),
                                                                                                ("grek", ("dflt", ), ),
                                                                                                ("latn", ("dflt", ), ), ), ), ))
        self.font.addKerningClass("'kern' Horizontal Kerning lookup 0", "'kern' Horizontal Kerning lookup 0 subtable",
                                  (None, *first_classes, *[x.lower() for x in first_classes]), (None, *second_classes, *[x.lower() for x in second_classes]), offsets)

    def set_bearings(self, preceding_chars, following_chars):
        for preceding_char in preceding_chars:
            for following_char in following_chars:
                pair = preceding_char + following_char
                spacing = self.get_spacing(preceding_char, following_char)
                bearing = roundish(spacing / 2)
                self.set_rsb(preceding_char, bearing, pair=pair)
                self.set_lsb(following_char, bearing, pair=pair)
                self.font[ord(preceding_char)].right_side_bearing = round(bearing)
                self.font[ord(following_char)].left_side_bearing = round(bearing)
                if preceding_char.lower() != preceding_char:
                    self.font[ord(preceding_char.lower())].right_side_bearing = round(bearing)
                if following_char.lower() != following_char:
                    self.font[ord(following_char.lower())].left_side_bearing = round(bearing)

    def get_code_number(self, preceding_char, following_char):
        return self.preceding_data[preceding_char][self.following_data[following_char] - 1]

    def get_spacing(self, preceding_char, following_char):
        code_number = self.get_code_number(preceding_char, following_char)
        return roundish(self.code_number_spacings[str(code_number)] * self.unit)

    def set_lsb(self, char, value, pair=None):
        if char in self.lsbs and not approx_equal(self.lsbs[char], value):
            raise Exception("lsb of %s is set to %g but was going to set it to %g" % (repr(char), repr(pair), repr(value), self.lsbs[char]))
        self.lsbs[char] = roundish(value)

    def set_rsb(self, char, value, pair=None):
        if char in self.rsbs and not approx_equal(self.rsbs[char], value):
            raise Exception("rsb of %s (of pair %s) is set to %g but was going to set it to %g" % (repr(char), repr(pair), value, self.rsbs[char]))
        self.rsbs[char] = roundish(value)

def roundish(x):
    return round(x * 10000) / 10000

def approx_equal(x, y):
    return abs(x - y) <= 0.0001

main()
