# Antibot

## Introduction

This is a python framework to create slack bots.

It abstract most of the boilerplate code to interact with slack and encapsulate slack json data in nice native classes.


## How to run

You need to create a new app on https://api.slack.com/apps.
You need to activate `interactive components`, `slash commands` provide at least the following permissions to the bot :
 * users:read
 * users:read.email
 * files:write
 
You also need a way for slack to contact you server.
In development you can use http://localhost.run/ although you will need to reconfigure `interactive components` and `slash commands` regularly.

You also need a virtualenv where you will install `antibot` and all of your plugins.

The following environment variables are mandatory for antibot to run :
 * SLACK_BOT_USER_TOKEN : can be found under `Bot User OAuth Access Token` in `OAuth & Permissions` page
 * SIGNING_SECRET : can be found in the `Basic Information` page
 * WS_API_KEY : is a random secret of you choice to call non-slack related api on your bot
 * MONGO_URI : an accessible mongo instance
 * DEV=true while in development


## How to create a plugin

Use [cookiecutter](https://github.com/cookiecutter/cookiecutter) on https://github.com/JGiard/Antibot-plugins-template

## Coding

There is lot of stuff you can do, check the other projects for examples.

Use `@command("/myplugin/route")` to react to slash command (don't forget to create the correspond command in slack).

Always use the block api from `antibot.slack.messages` when creating messages.

Use `@block_action(action_id="...")` to react to interactive components on messages.

Use `@ws("/myplugin/route)` to create a raw endpoint.
