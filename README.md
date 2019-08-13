# How to create a bot plugin

## Git

Create a dedicated root directory for antibot dev, and associate a python virtualenv to it.

Clone projects `antibot`, `template`, `k8s` and optionally `jirahandler`

Install `cookiecutter`

Install `antibot` in editable mode

## Serveo
You should use [serveo](https://serveo.net/) to expose your dev environement to outside.

`ssh -R <name>:80:localhost:5001 serveo.net`

## Slack

Create an app on https://api.slack.com/apps

Enable the following features :
 * interactive components
 * slash commands
 * bots
 * permissions
 
In `Interactive components` use `https://name.serveo.net/action` as url

Install the bot

## Your plugin

Use `cookiecutter template/` to create your project. Then push it as a new project under `https://scm.mrs.antidot.net/antibot`

## Testing

Create a `env.list` file in the root antibot directory with the following content :

    VERIFICATION_TOKEN=<verification-token>
    SLACK_API_TOKEN=<bot-user-access-token>
    SIGNING_SECRET=<signing-secret>
    WS_API_KEY=d77cd9810f6b2189a52c12bd525730e516df81b1
    WS_IP_RESTRICTIONS=
    JIRA_URL=https://jira.antidot.net/
    JIRA_USER=product-bot
    JIRA_PASSWORD=<jira-password>
    PPROD_RN_URL=https://doc-interne.antidot.net/
    PPROD_RN_USER=root@fluidtopics.com
    PPROD_RN_PASSWORD=
    PROD_RN_URL=https://doc.antidot.net/
    PROD_RN_USER=bot@fluidtopics.com
    PROD_RN_PASSWORD=
    
You may skip some of these variables if you don't need them.

in `k8s` project, launch `./test/run.py`

## Prod

Check that your plugin is mentionned in the k8s Dockerfile.

Once your gitlab pipeline is successful, launch a k8s pipeline on master.

## Coding

There is lot of stuff you can do, check the other projects for examples.

Use `@command("/myplugin/route")` to react to slash command (don't forget to create the correspond command in slack).

Always use the block api from `antibot.slack.messages_v2` when creating messages.

Use `@block_action(action_id="...")` to react to interactive components on messages.

Use `@ws("/myplugin/route)` to create a raw endpoint.

Use `@jira_hook(project="...")` from `jirahandle` to react to events in jira.
