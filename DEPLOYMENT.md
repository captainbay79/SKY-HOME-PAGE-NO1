# Deployment

This repository publishes only the new 키다리스카이차 website.

- GitHub: captainbay79/SKY-HOME-PAGE-NO1, branch main
- Cloudflare account: 8e930a539f3915a2c13d80a617f96404
- Worker: sky-home-page-no1
- URL: https://sky-home-page-no1.captainbay79.workers.dev

After each user-approved website change, validate it, commit and push to this repository, package with `python tools/build_deploy.py`, and run `pnpm exec wrangler deploy`. Confirm the live main page, representative regional pages, images and region data after deployment.

Do not modify captainbay79/KIDARI-SKY-HOME-PAGE, the kidari-sky Pages project or kidarisky.shop. Keep source photos, review previews, tools, dependencies and local logs outside the public deployment package. Never commit credentials.
