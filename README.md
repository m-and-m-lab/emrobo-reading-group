# Embodiment Reading Group

Website for the Embodiment Reading Group, a weekly hybrid research reading group at the University of Michigan on embodiment representations and embodied skill learning.

**Live site:** https://m-and-m-lab.github.io/emrobo-reading-group/

The site is a plain [Jekyll](https://jekyllrb.com) site built by GitHub Pages. There is nothing to install to update it; edit files on GitHub and the site rebuilds in a minute or two.

## Common tasks

### Add a session

Add an entry to [`_data/sessions.yml`](_data/sessions.yml):

```yaml
- date: 2026-11-05
  semester: Fall 2026
  type: paper              # paper | invited | tooling | special
  theme: Tactile representations
  title: "Paper title"
  authors: Last et al.
  venue: CoRL 2024
  paper_url: https://arxiv.org/abs/xxxx.xxxxx
  presenter: Your Name
```

The session appears on the home page, the schedule, and the subscribable calendar automatically. Remove `tentative: true` once a date is confirmed.

### After a session

Add the links to the same entry:

```yaml
  slides: https://...
  video: https://www.youtube.com/watch?v=...
  notes: https://...
```

Recordings with a `video` link also show up under "Recent recordings" on the home page.

### Start a new semester

Change `current_semester` in [`_config.yml`](_config.yml). Sessions from earlier semesters move to the archive page.

### Fill in logistics

Everything about time, room, and links lives in [`_config.yml`](_config.yml) under `meeting:` and `links:`. Empty links render as "soon" on the site. Keep `zoom_join` empty unless the meeting has a passcode; share the link via the mailing list and calendar instead.

### Add to the reading list

Add papers to [`_data/reading_list.yml`](_data/reading_list.yml) under a topic. Set `session:` to a session id (`YYYY-MM-DD-type`, e.g. `2026-10-01-paper`) to link a paper to the session that covers it.

### Organizers, tools

- [`_data/organizers.yml`](_data/organizers.yml): current and past organizers.
- [`_data/resources.yml`](_data/resources.yml): tools listed on the tooling page.

## Contributions from members

Paper suggestions, tooling session proposals, and speaker nominations come in through GitHub issue forms in [`.github/ISSUE_TEMPLATE`](.github/ISSUE_TEMPLATE).

## Local preview (optional)

```bash
bundle install
bundle exec jekyll serve
```

Then open http://localhost:4000/emrobo-reading-group/.

## Publishing

In the repository settings, under **Pages**, choose **Deploy from a branch**, branch `main`, folder `/ (root)`. The repository must be public. If the repository is renamed, update `baseurl` in `_config.yml` to match.
