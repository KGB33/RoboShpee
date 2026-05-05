use crate::{Context, Error};
use std::random::random;

#[tracing::instrument]
/// Translates a duration into taco time
#[poise::command(slash_command, prefix_command)]
pub async fn taco_time(
    ctx: Context<'_>,
    #[description = "Duration in minutes"] delta: Option<f64>,
) -> Result<(), Error> {
    let media_files = [
        "JustOneMin.webm",
        "taco_time.png",
        "wow_in_a_few.png",
        "wow_tacos.png",
    ];
    let chosen = &media_files[random::<usize>(..) % media_files.len()];
    let url = format!(
        "https://media.githubusercontent.com/media/KGB33/RoboShpee/main/roboshpee/static/{chosen}"
    );

    let message = match delta {
        Some(d) => {
            let r = random::<u32>(..) as f64 / u32::MAX as f64;
            let scaled = (r + 1.0) * d;
            format!("The estimated taco time is about {scaled:.1}mins\n{url}")
        }
        None => url,
    };

    ctx.send(poise::CreateReply::default().content(message))
        .await?;
    Ok(())
}
