use poise::serenity_prelude::Role;

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
    #[description = "Role to add"] role_name: String,
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
    ctx.say(format!("Added {:?}", role.name)).await?;
    Ok(())
}

/// Removes a role
#[tracing::instrument]
#[poise::command(slash_command, prefix_command, track_edits, category = "Roles")]
async fn remove(
    ctx: Context<'_>,
    #[description = "Role to remove"] role_name: String,
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
async fn create(ctx: Context<'_>) -> Result<(), Error> {
    ctx.say("Just ping KGB33.").await?;
    Ok(())
}

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
