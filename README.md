# discordbot-giveaway
A simple, flawed, bot for hosting giveaways that I had coded for me. I'm too cheap to pay for premium github so I have it public.

Okay here is the bot. It runs on Python 3.6 and needs the Discord.py module.
First it has a .ini file there you need to put your bot-token, the role that are allowed to create and manage giveaways (modrole), user-idnumbers to people allowed to dm the bot, and user-idnumbers to people that are allowed to use the undocumented rigging feature.

You can get the basic steps for creating a giveaway by typing !help giveaway or !help g, further commands can be seen by typing !help

Example steps:
!g time 10
!g emoji :gift:
!g prize glory and honor
!g channel general
!g start

It would create a giveway for 10 seconds in the channel general where people need to react with the heart, winner would get a dm from the bot with the prize
Rigging works like this, !g rig set Simon and it would rig it to make the user Simon win. Simon still needs to react to the message. To clear rigging !g rig clear

All command except prize are saved between each created giveway so you don't need to retype everything

Whitelist and Blacklist got both roles and user features
They work something like this !g blacklist user add Simon and Simon would not be able to win

!g message Custom message to set a custom message instead of the default one

to do all steaps at once, except changing the message, use this command !g doall :heart: 10 "item to win" general

It also has a blacklisting and whitelisting feature

!giveaway whitelist user add
!giveaway whitelist user remove
!giveaway whitelist group add
!giveaway whitelist group remove

blacklist works the same
