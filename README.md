# Project Dorian Gray

Project Dorian Gray is an ongoing Bluesky bot and image project. Each day, the bot posts a portrait: first as an untouched base image, then as an image that changes gradually over time. The project imagines the portrait as a surface that absorbs traces of digital life.

Inspired by Oscar Wilde's *The Picture of Dorian Gray*, this version turns toward browsers, platforms, automation, image processing, and generative systems. The public feed remains spare: one image, one caption, one daily mark.

## What the bot does

The bot posts one image per day to Bluesky.

The first post is the base portrait. It is not a neutral starting point or a lack of transformation; it is the first act of exposure. From there, the portrait is updated gradually, accumulating a visible history of daily contact with networked life.

The changes are cumulative in the most literal way: each day's image is made by editing the previous day's JPEG. Nothing is restored. Small daily alterations compound, and the artefacts of repeated machine processing (compression, smoothing, re-interpretation) are allowed to accumulate along with them. It is, after all, a JPEG and not an oil painting.

## How the program works

The bot reads a local, privacy-preserving summary of browser activity for a completed day: only which sites were visited and when. It never reads page contents, private messages, search text or email subjects. All classification happens on the machine where the bot runs. The image model receives yesterday's picture and a short instruction describing the day's edit, never any browsing data.

The daily activity is classified into broad patterns: work, reference, generative AI, social platforms, video, news, search, entertainment, health, finance, and other forms of digital activity. The program also looks for temporal patterns: late-night use, repeated checking, long feed sessions, switching between domains, research chains, task focus, social connection, and other rhythms of attention.

Those signals are translated into a set of portrait axes. The axes are not moral judgments and they are not simple opposites. They are independent tendencies that can coexist in the same day:

- **Directedness / Drift**: focus, purpose, wandering, diffusion.
- **Public / Private**: exposure to the world, withdrawal, enclosure, entrapment.
- **Self / Others**: self-reference, relation, correspondence, attention to other people.
- **Vitality / Gloom**: restoration, depletion, warmth, shadow.
- **AI Mediation / Direct Engagement**: synthetic assistance, direct encounter, delegated or unmediated attention.

There is no hidden score that the portrait is drawn from. The image is its own memory: whatever happened to it yesterday is still there today, and each day only adds to it. Repeated patterns therefore leave deeper marks, not because a number climbs, but because the same kinds of edit keep landing on an already altered face.

Each day, only a few of these tendencies are allowed to act. They act on different parts of the picture in turn (composition, background, light, posture, gaze, mouth, skin, surface, depth, and faint traces of the world and of other people), so the change wanders across the whole image rather than settling on one feature. A pattern that breaks with the recent past is noticed first. Days spent largely away from the browser count toward vitality: redemption is possible, but it has to be earned edit by edit.

The portrait should not show browser windows, logos, screens, or literal evidence. The transformation is meant to remain embodied.

## Captions

Each post uses a brief caption in the form:

```text
The jpeg absorbs a day of [BLANK].
```

The blank is chosen from a controlled vocabulary of allusive terms, keyed to whichever tendency led that day's edit. A word is not repeated within a dozen posts.

Examples include drift, latency, exposure, withdrawal, self-regard, correspondence, renewal, sediment, synthesis, interpolation, grain, telemetry, insomnia, and compression. The captions are deliberately ambiguous. They are not meant as literal summaries of the day, but as small verbal pressure marks beside the image.

## The local archive

The public bot posts only the image and its brief caption.

Alongside the public feed, the project maintains a fuller local archive: every frame in the image lineage, the day's scores, the edits chosen and the prompt sent, and an HTML page for reviewing the run. That archive is part of the working system, but it is not posted publicly by the bot.

The public image is therefore only the visible edge of a larger private record.

## Conceptual note

Wilde's portrait held what the visible person would not show. Project Dorian Gray moves that premise into a world of digital traces, automated interpretation, and mediated selfhood. The portrait does not illustrate websites or reproduce data directly. Instead, it becomes a daily threshold between private activity and public display: a face altered by patterns of attention, repetition, synthesis, exposure, and withdrawal.

The result is neither a diary nor a data visualization exactly. It is a portrait under technological weather.

## What this repo contains

This repository contains the public materials and working code for the Bluesky bot version of Project Dorian Gray. At a high level, it includes:

- the bot logic that prepares a daily portrait post;
- local browser-history summarization and classification code;
- the daily selection of edits across eleven parts of the picture;
- the controlled caption vocabulary and caption selection logic;
- image-generation and Bluesky posting utilities;
- local archive/report generation;
- scheduling and runtime support for daily operation;
- project documentation.

The exact implementation may change as the project develops. The central structure remains the same: one portrait, one daily transformation, one brief caption.

## Status

The current run began on 11 October 2026 with the unaltered base photograph. An earlier version of the bot, which re-rendered the original photograph each day, ran from June to September 2026 and has been retired. The portrait is still accumulating.

## Running it

```bash
bash scripts/install.sh                         # installs to ~/.dorian_gray_bot and schedules the daily run (makes + posts)
cd ~/.dorian_gray_bot
.venv/bin/python -m dorian_bot.bot --status      # where things stand
.venv/bin/python -m dorian_bot.bot --dry-run     # preview tomorrow's edit; nothing generated or saved
.venv/bin/python -m dorian_bot.bot --post-latest # post anything not yet posted (the daily run does this itself)
python scripts/simulate.py 2026-06-01 2026-09-30 # replay history through the selection logic, no images
```

Settings such as the image model and quality can be overridden in `.env` (`DORIAN_IMAGE_MODEL`, `DORIAN_IMAGE_QUALITY`).
