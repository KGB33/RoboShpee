use futures::{Stream, StreamExt};
use log;
use poise::serenity_prelude::{Mention, Role};

use crate::{Context, Error};

/// Role specific commands
#[tracing::instrument]
#[poise::command(
    slash_command,
    prefix_command,
    track_edits,
    subcommand_required,
    subcommands("add", "remove", "create", "list"),
    category = "Roles"
)]
pub async fn role(ctx: Context<'_>) -> Result<(), Error> {
    Ok(())
}

/// Adds a role
#[tracing::instrument]
#[poise::command(slash_command, prefix_command, track_edits, category = "Roles")]
async fn add(
    ctx: Context<'_>,
    #[description = "Role to add"]
    #[autocomplete = "autocomplete_role"]
    role_name: String,
) -> Result<(), Error> {
    let Some(role) = get_roles(&ctx)
        .unwrap()
        .into_iter()
        .find(|r| r.name == role_name)
    else {
        return ctx
            .say(format!(
                "The role '{role_name}' does not exist or cannot be managed."
            ))
            .await
            .map(|_| Ok(()))?;
    };
    ctx.author_member()
        .await
        .unwrap()
        .add_role(ctx.http(), role.id)
        .await?;
    log::info!(
        "Added role '{:?}' to user '{:?}'",
        role.name,
        ctx.author().name
    );
    ctx.say(format!("Added {:?}", role.name)).await?;
    Ok(())
}

/// Removes a role
#[tracing::instrument]
#[poise::command(slash_command, prefix_command, track_edits, category = "Roles")]
async fn remove(
    ctx: Context<'_>,
    #[description = "Role to remove"]
    #[autocomplete = "autocomplete_role"]
    role_name: String,
) -> Result<(), Error> {
    let Some(role) = get_roles(&ctx)
        .unwrap()
        .into_iter()
        .find(|r| r.name == role_name)
    else {
        return ctx
            .say(format!(
                "The role '{role_name}' does not exist or cannot be managed."
            ))
            .await
            .map(|_| Ok(()))?;
    };
    ctx.author_member()
        .await
        .unwrap()
        .remove_role(ctx.http(), role.id)
        .await?;
    ctx.say(format!("Removed {:?}", role.name)).await?;
    Ok(())
}

/// Shows all available roles
#[tracing::instrument]
#[poise::command(
    slash_command,
    prefix_command,
    track_edits,
    category = "Roles",
    ephemeral
)]
async fn list(ctx: Context<'_>) -> Result<(), Error> {
    let roles = get_roles(&ctx).unwrap();
    let resp = format!(
        "Roles:\n{}",
        roles
            .into_iter()
            .map(|e| { format!("{}\n", e.name) })
            .collect::<String>()
    );
    ctx.say(resp).await?;
    Ok(())
}

/// Starts a vote to create a new role
#[tracing::instrument]
#[poise::command(slash_command, prefix_command, track_edits, category = "Roles")]
async fn create(
    ctx: Context<'_>,
    #[description = "Role to create"] role_name: String,
) -> Result<(), Error> {
    ctx.reply(format!(
        "{}, {} wants to create role `{}`.",
        Mention::from(ctx.guild().map_or(ctx.author().id, |g| g.owner_id)),
        Mention::from(ctx.author().id),
        role_name
    ))
    .await?;
    Ok(())
}

#[tracing::instrument]
fn get_roles<'a>(ctx: &'a Context<'a>) -> Option<Vec<Role>> {
    ctx.guild().map(|g| g.to_owned().roles).map(|rs| {
        let mut rs = rs
            .into_values()
            .filter(|e| e.colour.hex() == "206694")
            .collect::<Vec<Role>>();
        rs.sort_by(|a, b| a.name.cmp(&b.name));
        rs
    })
}

#[tracing::instrument]
async fn autocomplete_role<'a>(ctx: Context<'_>, partial: &'a str) -> impl Stream<Item = String> {
    let partial_lower = partial.to_lowercase();
    futures::stream::iter(get_roles(&ctx).unwrap())
        .filter(move |r| futures::future::ready(r.name.to_lowercase().starts_with(&partial_lower)))
        .map(|r| r.name)
}
