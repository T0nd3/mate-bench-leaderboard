# mate-bench-leaderboard

Community leaderboard for [MATE — Model AI Throughput Evaluator](https://github.com/T0nd3/mate-bench).

## Leaderboard

**[t0nd3.github.io/mate-bench-leaderboard](https://t0nd3.github.io/mate-bench-leaderboard/)**

## How it works

Results are submitted by the community using the `mate` CLI:

```bash
pip install mate-bench mate-engine-ollama mate-workload-llm
mate run llm --profile quick
mate submit
```

This repository contains a GitHub Action that queries the submission database every hour and regenerates `leaderboard.json`. GitHub Pages serves the static leaderboard site from the root of this repository.

## Data

- `leaderboard.json` — auto-generated, do not edit manually
- `index.html` — leaderboard frontend
- `scripts/build_leaderboard.py` — Action script that fetches from Cloudflare D1

## Notes

- Only results without throttling detected are shown
- Each GPU chip is represented by its best result per profile and model
- Full-profile submissions are not shown (tokens/s is not a single value)
- Submissions are anonymous — no personal data is collected

## License

MIT — see [mate-bench](https://github.com/T0nd3/mate-bench/blob/main/LICENSE)
