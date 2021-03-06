## Quickstart

These are offensive fortunes and so they will live in the offensive fortune directory.

Download [ngatehackersnews](https://git.sr.ht/~nnathan/ngatefortune/blob/master/ngatehackernews) fortune file.

Run `strfile ngatehackernews` and copy `ngatehackernews` and `ngatehackernews.dat` to `/usr/local/share/games/fortunes/off/`.  Or `/usr/share/games/fortunes/off/`. Or wherever the fortune file should live, consult your `fortune(6)` manpage which will specify where. You can also place them in a local directory such as `~/.fortune`.

Then run `fortune -o ngatehackernews` to get a random n-gate headline summary. Neat huh? Maybe chuck it in your bash profile to brighten your day.

This is what I do:

```bash
# copy ngatehackernews{,.dat} to ~/.fortune
if shopt -q login_shell; then
    [ -d ~/.fortune ] && fortune ~/.fortune
fi
```

[Thanks skeeto.](https://nullprogram.com/blog/2016/12/01/)

## When will the latest fortune file become available?

I will keep the fortune file up to date, so the link that lives in master will hopefully contain the latest updates.

## How do I generate the fortune file?

You will need python3 and a few dependencies, make, and wget.

To install python3 dependencies run: `pip3 install --user -r requirements.txt`.

Then run `make` and it will mirror n-gate.com and generate the fortune files `ngatehackernews` and `ngatehackernews.dat`.

`make clean` will clean the fortune files and `make cleanall` will clean fortune files and the n-gate.com mirror.

There is no guarantee to work if new weird HTML oddities are introduced in headline summaries. Parsing all the HTML entries was a bit of a headache to begin with.

An attempt has been made to ensure the resulting fortune file is generated deterministically by sorting the input file pathnames in lexical order. This has the desired side-effect of having the quotes generated in ascending order by date.

## License

All the content from n-gate.com and anything inside `ngatehackernews` fortune file is copyright the original n-gate.com author, whoever (s)he is.

Everything else in this repository is licensed under the [CC0 1.0 Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/).
