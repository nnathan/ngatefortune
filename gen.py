#!/usr/bin/env python3

# this file has been automatically formatted with black

import datetime
import glob
import os
import subprocess
import sys
import textwrap

import bs4
import bs4.element
from bs4 import BeautifulSoup


def log(s):
    sys.stderr.write(f"{s}\n")


def parse_hackernews(raw_html):
    root = BeautifulSoup(raw_html, "lxml")
    pelems = root.find_all("p")

    # since some of the <p> tags contain other junk
    # we pare it down to just story links
    pelems = [
        p
        for p in pelems
        if hasattr(p.span, "attrs")
        and "class" in p.span.attrs
        and "storylink" in p.span["class"]
    ]

    headlines = []

    for i, p in enumerate(pelems):
        log(f"processing entry {i}")

        spans = p.find_all("span")

        # annoyance n-gate.com/hackernews/2016/10/21/0/index.html (just a storylink with no link or metadata)
        if len(spans) == 1:
            title = spans[0].text.strip()
            text = p.contents[-1].strip()
            headline = {
                "title": title,
                "titlelink": "",
                "date": "",
                "hnlink": "",
                "addendums": [],
                "context": [],
                "text": text,
            }
            yield headline
            continue

        # annoyance (injected metrics in a span):
        #       n-gate.com/hackernews/2018/10/31/0/index.html
        if len(spans) > 3:
            if "requests for" in spans[1].text or "request for" in spans[1].text:
                del spans[1]

        title = spans[0].a.text.strip()
        titlelink = spans[0].a["href"]
        date = spans[1].text
        hackernewslink = spans[2].a["href"]

        # annoyance (<ip> tag):
        #        n-gate.com/hackernews/2019/06/30/0/index.html
        if type(p.contents[-1]) == bs4.element.Tag:
            # this one is too hard to fix, let's skip it.
            continue

        # annoyance (intermixed html tags in text portion):
        #       n-gate.com/hackernews/2016/12/21/0/index.html
        #         - [Stroustrup's Rule and Layering Over Time in Rust]
        #       n-gate.com/hackernews/2016/10/07/0/index.html
        #         - [How being alone may be the key to rest]
        #         - [Police complaints drop over 90% after deploying body cameras]
        #       n-gate.com/hackernews/2017/01/31/0/index.html
        #         - [1.1B Taxi Rides on Kdb+/q and 4 Xeon Phi CPUs]
        #       n-gate.com/hackernews/2018/08/31/0/index.html
        #         - [Changing Our Approach to Anti-Tracking]
        #       n-gate.com/hackernews/2018/09/07/0/index.html
        #         - [Terry Davis has died]
        #       n-gate.com/hackernews/2018/04/31/0/index.html
        #         - [Hijack of Amazon’s domain service used to reroute web traffic for two hours]
        #       n-gate.com/hackernews/2018/11/30/0/index.html
        #         - [We are Google employees – Google must drop Dragonfly]
        #       n-gate.com/hackernews/2018/02/07/0/index.html
        #         - [U.S. consumer protection official puts Equifax probe on ice]
        #       n-gate.com/hackernews/2019/10/31/0/index.html
        #         - [Perfectly Cropped]
        #       and probably more in the future...

        # usually the trailing portion that contains the headline summary has no break tags,
        # so we can use it to identify where the trailing portion begins
        start = -1
        for i, v in enumerate(p.contents):
            if type(v) == bs4.element.Tag and v.name == "br":
                start = i + 1

        # untag will remove tags and return the summary portion plus any contextual links
        def untag(contents):
            out = []
            addendums = []
            context = []
            link_num = 0
            for v in contents:
                if type(v) == bs4.element.NavigableString:
                    out.append(v)
                    continue
                if type(v) == bs4.element.Tag and v.name == "a":
                    # annoyance (a tag with no href):
                    #       n-gate.com/hackernews/2018/12/21/0/index.html
                    #         - [The Yoda of Silicon Valley]
                    if "href" in v.attrs:
                        context.append(v["href"])
                        out.append(v.text + f"[{link_num}]")
                        link_num += 1
                        continue
                if type(v) == bs4.element.Tag and v.name == "sup":
                    # annoyance (footnote outside headline summary)
                    #       n-gate.com/hackernews/2016/10/07/0/index.html
                    #         - [Police complaints drop over 90% after deploying body cameras]
                    if (
                        title
                        == "Police complaints drop over 90% after deploying body cameras"
                    ):
                        addendums = [
                            "* - I'm kidding. A Hackernews would never set foot in the East Bay."
                        ]
                    elif title == "Who Are My Investors?":
                        addendums = ["* - never."]

                if title == "Golang SSH Security":
                    log("Golang SSH Security")
                    addendums = [
                        "* - Imagine that.  Vendor-related problems with Go.  For a change, this one couldn't have been trivially solved with plain old package management."
                    ]

                out.append(v.text)
            return out, addendums, context

        textparts, addendums, context = untag(p.contents[start:])
        text = "".join(textparts).strip()

        headline = {
            "title": title,
            "titlelink": titlelink,
            "date": date,
            "hnlink": hackernewslink,
            "addendums": addendums,
            "context": context,
            "text": text,
        }

        yield headline


def out(headline):
    title = headline["title"]
    text = headline["text"]
    date = headline["date"]
    hnlink = headline["hnlink"]
    link = headline["titlelink"]
    addendums = headline["addendums"]
    context = headline["context"]

    wraptext = textwrap.fill(
        text,
        width=75,
        drop_whitespace=True,
        fix_sentence_endings=True,
        break_long_words=True,
        break_on_hyphens=True,
    )

    # annoyance n-gate.com/hackernews/2016/10/21/0/index.html (just a storylink with no link or metadata)
    if hnlink == "":
        print(f"{title}\n\n{wraptext}")
        return

    print(f"{title}\n{date}\n\n{wraptext}\n")

    for a in addendums:
        wrapaddendum = textwrap.fill(
            a,
            width=75,
            drop_whitespace=True,
            fix_sentence_endings=True,
            break_long_words=True,
            break_on_hyphens=True,
        )

        print(wrapaddendum)

    if len(addendums) > 0:
        print("")

    for i, link in enumerate(context):
        print(f"[{i}]: {link}")

    if len(context) > 0:
        print("")

    print(f"Link: {link}\nComments: {hnlink}")


if __name__ == "__main__":
    if not os.path.exists("n-gate.com"):
        log("n-gate.com directory does not exist, exiting")
        sys.exit(1)

    htmlfiles = sorted(
        glob.glob("n-gate.com/hackernews/**/0/index.html", recursive=True)
    )
    for hf in htmlfiles:
        log(f"processing {hf}")
        with open(hf) as f:
            raw = f.read()
            for headline in parse_hackernews(raw):
                # to debug
                # from pprint import pprint
                # pprint(headline)
                out(headline)
                print("%")
