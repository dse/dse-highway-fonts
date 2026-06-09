#!/usr/bin/env -S fontforge -script
import fontforge, argparse, os
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("font_filename", type=str, nargs='+')
    args = parser.parse_args()
    for filename in args.font_filename:
        font = fontforge.open(filename)
        space_glyph = font[32]
        print("%s: %d / %d = %g (em = %d)" % (filename, space_glyph.width, font.capHeight, space_glyph.width / font.capHeight, font.em))
        font.close()
main()


# Series A: 185/670
# Series B: 200/670 = .299  256/1000 = .256
# Series C: 215/670 = .321  428/1000 = .428
# Series D: 230/670 = .343  599/1000 = .599
# Series E: 245/670 = .366  599/1000 = .599
# Series F: 260/670 = .388  984/1000 = .984


# ../my-private-highway-fonts/highway-var/static/OCHighwayVAR2-Series1.otf: 200 / 670 = 0.298507 (em = 1000)
# ../my-private-highway-fonts/highway-var/static/OCHighwayVAR2-Series2.otf: 208 / 670 = 0.310448 (em = 1000)
# ../my-private-highway-fonts/highway-var/static/OCHighwayVAR2-Series3.otf: 215 / 670 = 0.320896 (em = 1000)
# ../my-private-highway-fonts/highway-var/static/OCHighwayVAR2-Series4.otf: 224 / 670 = 0.334328 (em = 1000)
# ../my-private-highway-fonts/highway-var/static/OCHighwayVAR2-Series5.otf: 230 / 670 = 0.343284 (em = 1000)
# ../my-private-highway-fonts/highway-var/static/OCHighwayVAR2-Series6.otf: 238 / 670 = 0.355224 (em = 1000)
# ../my-private-highway-fonts/highway-var/static/OCHighwayVAR2-Series7.otf: 245 / 670 = 0.365672 (em = 1000)
# ../my-private-highway-fonts/highway-var/static/OCHighwayVAR2-Series8.otf: 253 / 670 = 0.377612 (em = 1000)
# ../my-private-highway-fonts/highway-var/static/OCHighwayVAR2-Series9.otf: 260 / 670 = 0.38806 (em = 1000)
# ../my-private-highway-fonts/roadgeek-fonts/RG2014B.ttf: 256 / 1000 = 0.256 (em = 1750)
# ../my-private-highway-fonts/roadgeek-fonts/RG2014C.ttf: 428 / 1000 = 0.428 (em = 1750)
# ../my-private-highway-fonts/roadgeek-fonts/RG2014D.ttf: 599 / 1000 = 0.599 (em = 1750)
# ../my-private-highway-fonts/roadgeek-fonts/RG2014E.ttf: 599 / 1000 = 0.599 (em = 1750)
# ../my-private-highway-fonts/roadgeek-fonts/RG2014EEM.ttf: 599 / 1000 = 0.599 (em = 1750)
# ../my-private-highway-fonts/roadgeek-fonts/RG2014EM.ttf: 866 / 1000 = 0.866 (em = 1750)
# ../my-private-highway-fonts/roadgeek-fonts/RG2014F.ttf: 984 / 1000 = 0.984 (em = 1750)
