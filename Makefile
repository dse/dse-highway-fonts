FONTS := series-a.sfd series-b.sfd series-b-type2.sfd

default: $(FONTS)

dist/%.ttf: src/%.sfd
	mkdir -p dist
	ffconvert "$<" "$@.tmp.ttf"
	mv "$@.tmp.ttf" "$@"

series-a.sfd: Makefile support/bin/mkfont.py src/vector/series-a/*.svg
	support/bin/mkfont.py "$@" seriesA src/vector/series-a/*.svg

series-b.sfd: Makefile support/bin/mkfont.py src/vector/series-b/*.svg
	support/bin/mkfont.py "$@" seriesB src/vector/series-b/*.svg

series-b-type2.sfd: Makefile support/bin/mkfont.py src/vector/series-b/*.svg
	support/bin/mkfont.py --2000 "$@" seriesB src/vector/series-b/*.svg

.PHONY: FORCE
