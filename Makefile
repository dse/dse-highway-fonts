default: dist/series-a.ttf dist/series-b.ttf

dist/%.ttf: src/%.sfd
	mkdir -p dist
	ffconvert "$<" "$@.tmp.ttf"
	mv "$@.tmp.ttf" "$@"
