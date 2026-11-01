# shuzhao.me

Source of [shuzhao.me](https://shuzhao.me/), Shu Zhao's personal homepage.

The site is plain static HTML. GitHub Pages serves it from `main`, and its default Jekyll pass only copies the files, since nothing here uses a theme or layout.

## What's here

| Path | What it is |
| --- | --- |
| `index.html` | The homepage |
| `assets/css/pixel.css` | All homepage styles |
| `assets/img/` | Images: the photo, plus the pixel-art tree and favicons in `pixel/` |
| `assets/files/cv.pdf` | The CV linked from the homepage |
| `r2s/` | Self-contained project page for R2S (*Capable Teacher, Myopic Scorer*) |
| `_tools/pixel_sprites.py` | Draws the pixel-art sprites and favicons (needs Pillow); `--inject index.html` updates the inline SVG symbols |

Folders that start with `_` are not published.

## Preview and publish

- Preview: open `index.html` in a browser.
- Check the exact GitHub Pages output: `bundle install`, then `bundle exec jekyll build`, and look in `_site/`.
- Publish: push to `main`. The site updates in about a minute.
