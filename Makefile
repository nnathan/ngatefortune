.POSIX:

.PHONY:
all: ngatehackernews.dat

n-gate.com:
	-wget -U ngatefortune -m http://n-gate.com

ngatehackernews: n-gate.com
	./gen.py > ngatehackernews

ngatehackernews.dat: ngatehackernews
	strfile ngatehackernews

.PHONY:
clean:
	@rm -f ngatehackernews ngatehackernews.dat

.PHONY:
cleanall: clean
	@rm -rf n-gate.com
