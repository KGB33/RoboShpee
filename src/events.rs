use crate::{Data, Error};
use poise::serenity_prelude as serenity;
use poise::serenity_prelude::{ChannelId, VoiceState};

pub async fn event_handler(
    ctx: &serenity::Context,
    event: &serenity::FullEvent,
    _framework: poise::FrameworkContext<'_, Data, Error>,
    _data: &Data,
) -> Result<(), Error> {
    #[allow(clippy::single_match)]
    match event {
        serenity::FullEvent::VoiceStateUpdate {
            old: Some(old),
            new,
        } => on_voice_leave(ctx, old, new).await?,
        _ => {}
    }
    Ok(())
}

async fn on_voice_leave(
    ctx: &serenity::Context,
    old: &VoiceState,
    new: &VoiceState,
) -> Result<(), Error> {
    // Skip events caused by self
    if [
        536718941964468245, // RoboShpee
        541500270438514688, // RoboShpeeTest
    ]
    .contains(&new.user_id.get())
    {
        return Ok(());
    }

    let guild_id = old
        .guild_id
        .expect("Voice Channels outside of guilds are unsupported.");

    let was_here = |old_chan: ChannelId| async move {
        // Join then leave to set the "___ Was Here"
        let manager = songbird::get(ctx).await.expect("Songbird not registered");
        let _ = manager.join(guild_id, old_chan).await;
        let _ = manager.remove(guild_id).await;
        Ok(())
    };

    // Only fire on events that change voice channels (leave/move)
    // Or leave events
    match (old.channel_id, new.channel_id) {
        (Some(old_chan), None) => was_here(old_chan).await,
        (Some(old_chan), Some(new_chan)) if old_chan != new_chan => was_here(old_chan).await,
        _ => Ok(()),
    }
}
