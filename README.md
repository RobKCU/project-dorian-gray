# Project Dorian Gray

Project Dorian Gray is an ongoing Bluesky bot and image project. Each day, the bot posts a portrait: first as an untouched base image, then as an image that changes gradually over time. The project imagines the portrait as a surface that absorbs traces of digital life.

Inspired by Oscar Wilde's *The Picture of Dorian Gray*, this version turns toward browsers, platforms, automation, image processing, and generative systems. The public feed remains spare: one image, one caption, one daily mark.

## What the bot does

The bot posts one image per day to Bluesky.

The first post is the base portrait. It is not a neutral starting point or a lack of transformation; it is the first act of exposure. From there, the portrait is updated gradually, accumulating a visible history of daily contact with networked life.

The changes are cumulative rather than episodic. Each new image is generated from the original portrait plus the current accumulated state. The bot does not simply edit yesterday's image again; it returns to the base portrait and asks what the accumulated condition should now look like.

## How the program works

The bot reads a local, privacy-preserving summary of browser activity for a completed day. It does not use page contents, private messages, search text, email subjects, or raw browsing details in the public post.

The daily activity is classified into broad patterns: work, reference, generative AI, social platforms, video, news, search, entertainment, health, finance, and other forms of digital activity. The program also looks for temporal patterns: late-night use, repeated checking, long feed sessions, switching between domains, research chains, task focus, social connection, and other rhythms of attention.

Those signals are translated into a set of cumulative portrait axes. The axes are not moral judgments and they are not simple opposites. They are independent tendencies that can coexist in the same day:

- **Directedness / Drift**: focus, purpose, wandering, diffusion.
- **Public / Private**: exposure to the world, withdrawal, enclosure.
- **Self / Others**: self-reference, relation, correspondence, attention to other people.
- **Vitality / Gloom**: restoration, depletion, warmth, shadow.
- **AI Mediation / Direct Engagement**: synthetic assistance, direct encounter, delegated or unmediated attention.

Each day nudges these axes rather than replacing them. Some effects fade; others leave residue. Over time the portrait develops a cumulative state: not a literal log of websites visited, but a symbolic pressure field built from repeated patterns.

That state is then translated into visual instructions: changes to gaze, skin, posture, light, texture, atmosphere, and painterly handling. The portrait should not show browser windows, logos, screens, or literal evidence. The transformation is meant to remain embodied.

## Captions

Each post uses a brief caption in the form:

```text
The jpeg absorbs a day of [BLANK].
```

The blank is chosen from a controlled vocabulary of allusive terms: words related to digital mediation, decay, display, circulation, memory, attention, and drift.

Examples include terms such as mediation, scrolling, compression, display, telemetry, synthesis, circulation, fragmentation, latency, forgetting, and repetition. The captions are deliberately ambiguous. They are not meant as literal summaries of the day, but as small verbal pressure marks beside the image.

## The local archive

The public bot posts only the image and its brief caption.

Alongside the public feed, the project maintains a fuller local archive: the current portrait, day-by-day image files, metadata, transformation rationales, axis scores, prompt text, and an HTML document for reviewing the day's state. That archive is part of the working system, but it is not posted publicly by the bot.

The public image is therefore only the visible edge of a larger private record.

## Conceptual note

Wilde's portrait held what the visible person would not show. Project Dorian Gray moves that premise into a world of digital traces, automated interpretation, and mediated selfhood. The portrait does not illustrate websites or reproduce data directly. Instead, it becomes a daily threshold between private activity and public display: a face altered by patterns of attention, repetition, synthesis, exposure, and withdrawal.

The result is neither a diary nor a data visualization exactly. It is a portrait under technological weather.

## What this repo contains

This repository contains the public materials and working code for the Bluesky bot version of Project Dorian Gray. At a high level, it includes:

- the bot logic that prepares a daily portrait post;
- local browser-history summarization and classification code;
- the cumulative axis/state system;
- the controlled caption vocabulary and caption selection logic;
- image-generation and Bluesky posting utilities;
- local archive/report generation;
- scheduling and runtime support for daily operation;
- project documentation.

The exact implementation may change as the project develops. The central structure remains the same: one portrait, one daily transformation, one brief caption.

## Status

Project Dorian Gray is a work in progress and an ongoing bot project. The portrait is still accumulating.
