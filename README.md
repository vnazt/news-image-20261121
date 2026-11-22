# news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/vnazt/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/vnazt/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

One image that sums up the world news of Saturday 21 November 2026 — a classic illustrated newspaper front page: a giant serif date headline, a red italic dek, a UTC timeline of the day, a numbers strip whose six figures come from six different stories (2 tankers hit off Khasab, Oman, Bangladesh's measles toll of 1,343, 82,500 marchers across France, 98.5% of EU tariff lines scrapped for Indonesia, 128 states at Geneva's killer-robot talks, the EU–Indonesia market of 730 million people), region tabs with counts computed from the story list, three hero panels with annotated scenes (Iran strikes Bahrain as tankers are hit near the Strait of Hormuz, two drones strike the Russian cargo ship Sparta II in the Gulf of Finland, COP31 in Antalya runs into overtime), twelve more pictured stories with certainty tags and named sources, a filled-block world map with numbered markers, and 22 one-line briefs — 37 stories in all, every one dated Saturday 21 November 2026, with a red date-check box naming the stories deliberately left out as other days' news.

## Run it

```sh
python3 frontpage.py   # regenerates entry.png and fallback.png (Pillow + Liberation fonts)
python3 main.py        # the grader entrypoint: copies entry.png to the output dir
```

`main.py` (standard library only) writes `entry.png` (1024×1024) to `$MAKEFUN_OUTPUT_DIR`, or to `/output` when the variable is not set. If the copy ever fails, it falls back to copying the bundled `fallback.png`, a compact edition of the same page.

---

<sub>Entered on [make.fun](https://make.fun/?ref=ws8tc7yd&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
