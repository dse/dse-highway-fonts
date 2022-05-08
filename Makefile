default: dist/series-a.ttf

dist/%.ttf: src/%.sfd
	mkdir -p dist
	ffconvert $< $@
