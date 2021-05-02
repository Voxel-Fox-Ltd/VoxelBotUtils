.. raw:: html

   <style>
      .class > dt > .property {
         display: none !important;
      }
   </style>

Bot Config File
===========================

.. class:: BotConfig

   .. attribute:: token
   .. attribute:: owners
   .. attribute:: dm_uncaugh_errors
   .. attribute:: user_agent
   .. attribute:: default_prefix
   .. attribute:: support_guild_id
   .. attribute:: bot_support_role_id
   .. attribute:: guild_settings_prefix_column
   .. attribute:: cached_messages

   .. class:: event_webhook

         .. attribute:: event_webhook_url

         .. class:: events

            .. attribute:: guild_join
            .. attribute:: guild_remove
            .. attribute:: shard_connect
            .. attribute:: shard_disconnect
            .. attribute:: shard_ready
            .. attribute:: bot_ready
            .. attribute:: unhandled_error

   .. class:: intents

      .. attribute:: guilds
      .. attribute:: members
      .. attribute:: bans
      .. attribute:: emojis
      .. attribute:: integrations
      .. attribute:: webhooks
      .. attribute:: invites
      .. attribute:: voice_states
      .. attribute:: presences
      .. attribute:: guild_messages
      .. attribute:: dm_messages
      .. attribute:: guild_reactions
      .. attribute:: dm_reactions
      .. attribute:: guild_typing
      .. attribute:: dm_typing

   .. class:: help_command

      .. attribute:: dm_help
      .. attribute:: content

   .. class:: bot_listing_api_keys

      .. attribute:: topgg_token
      .. attribute:: discordbotlist_token

   .. class:: command_data

      .. attribute:: website_link
      .. attribute:: guild_invite
      .. attribute:: github_link
      .. attribute:: donate_link
      .. attribute:: echo_command_enabled
      .. attribute:: stats_command_enabled
      .. attribute:: vote_command_enabled
      .. attribute:: updates_channel_id
      .. attribute:: info

   .. class:: oauth

      .. attribute:: enabled
      .. attribute:: base
      .. attribute:: response_type
      .. attribute:: redirect_uri
      .. attribute:: client_id
      .. attribute:: scope
      .. attribute:: permissions

   .. class:: database

      .. attribute:: enabled
      .. attribute:: user
      .. attribute:: password
      .. attribute:: database
      .. attribute:: host
      .. attribute:: port

   .. class:: redis

      .. attribute:: enabled
      .. attribute:: host
      .. attribute:: port
      .. attribute:: db

   .. class:: embed

      .. attribute:: enabled
      .. attribute:: content
      .. attribute:: colour
      .. attribute:: footer
         :type: list

      .. class:: author

         .. attribute:: enabled
         .. attribute:: name
         .. attribute:: url

   .. class:: presence

      .. attribute:: activity_type
      .. attribute:: text
      .. attribute:: status
      .. attribute:: include_shard_id

      .. class:: streaming

         .. attribute:: twitch_usernames
         .. attribute:: twitch_client_id
         .. attribute:: twitch_client_secret

   .. class:: upgrade_chat

      .. attribute:: client_id
      .. attribute:: client_secret

   .. class:: statsd

      .. attribute:: host
      .. attribute:: port

      .. class:: constant_tags

         .. attribute:: service

