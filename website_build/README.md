# simplescamprotection.com - static website

Plain HTML/CSS/JS. No server, database or build step needed to host it.

## Publish
Upload **everything inside the `static_site` folder** (including the hidden `.htaccess`) to the web root of your host, then point
`www.simplescamprotection.com` at it (your host's DNS instructions - usually a CNAME for `www` and an A record or
redirect for the bare domain). Turn on HTTPS at your host.

## Download buttons
They link to the latest GitHub release of `trcmsp/simple-scam-protection`:
`https://github.com/trcmsp/simple-scam-protection/releases/latest/download/SimpleScamProtectionSetup.exe` (and `.msi`, `.exe`).
If your repository has a different name, search-and-replace `trcmsp/simple-scam-protection` in `index.html`.
A release is created automatically when you push a tag such as `v1.3.0` (see `.github/workflows/build-windows.yml`).

## Editing
Edit `index.html` / `assets/site.js`. If you add new Tailwind classes, rebuild the CSS with `website_build/build_site.sh`
(it also re-exports the link-checker rules from the Windows app and verifies the website gives identical answers).
