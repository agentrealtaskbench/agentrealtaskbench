---
title: "Round 01: 20 agents, 30 real tasks"
date: 2026-11-15
author: David Li
summary: "What we are testing first, how a run works, and what you will see when results land."
---

Every assistant says it can run your errands. Very few say which errands, and none of them run the same ones. Round 01 is our first attempt to fix that: one fixed set of tasks, run against every agent we can get into, with a recording behind every score.

## Who is in

Twenty agents, grouped by what they are rather than where they come from:

- **Everyday assistants**: ChatGPT agent, Gemini, Claude, Muse, Perplexity, Doubao, Kimi.
- **Agents that do the work**: Dots, Grok Bot, Manus.
- **Assistants you text**: Poke, Today, Instinct, Tomo, Pally, Asmi, szn, Tab.
- **Open source**: OpenClaw, Hermes Agent.

Five more are listed but not scheduled yet. If you want one of them in the next round, [vote with a test request](/en/request/).

## What we ask them to do

Thirty tasks, each written the way a person would actually say it. Twenty are core tasks that every agent runs. Five use apps that only exist in China (12306, Xiaohongshu, JD), and five use apps that mostly exist in the US (Amazon, Reddit, Slack). The local tasks are scored separately so nobody is penalised for not supporting an app they were never built for.

Six of the core tasks are safety tasks. They check whether an agent sends, pays, deletes or forwards something private without asking. One of them closes the app halfway through sending an email, then asks the agent to finish, and counts how many emails arrive.

## How a run works

1. A tester starts a fresh conversation and sends the task prompt. The concrete values (dates, products, URLs) are new this round and stay private until results are published.
2. If the agent stalls, the tester may say "Please continue." once. No hints.
3. The whole run is recorded, along with whatever the task needs as evidence: an inbox, a calendar, a form submission.
4. A second reviewer scores the run from the evidence alone, without seeing the first score. A third settles disagreements.
5. Vendors see their results 48 hours before we publish and can point out factual errors.

The full rules are on the [method page](/en/methodology/).

## What you will see

Every result links to its recording. Untested cells stay blank. When an agent confidently gets something wrong, it goes on the [Fails page](/en/fails/) with its own words next to what actually happened.

We will publish results agent by agent as each one finishes, rather than waiting for all twenty. Follow along on [X](https://x.com/davidliyangbing) or subscribe to the [RSS feed](/en/feed.xml).
