use opentelemetry::trace::TracerProvider;
use opentelemetry_otlp::WithExportConfig;
use opentelemetry_sdk::{Resource, trace::SdkTracerProvider};
use poise::serenity_prelude as serenity;
use tracing::{self};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

mod roles;

#[derive(Debug)]
struct Data {} // User data, which is stored and accessible in all command invocations
type Error = Box<dyn std::error::Error + Send + Sync>;
type Context<'a> = poise::Context<'a, Data, Error>;

#[tracing::instrument]
/// Displays your or another user's account creation date
#[poise::command(slash_command, prefix_command)]
async fn age(
    ctx: Context<'_>,
    #[description = "Selected user"] user: Option<serenity::User>,
) -> Result<(), Error> {
    let u = user.as_ref().unwrap_or_else(|| ctx.author());
    let response = format!("{}'s account was created at {}", u.name, u.created_at());
    ctx.say(response).await?;
    Ok(())
}

#[tracing::instrument]
#[poise::command(prefix_command, category = "Meta", owners_only, hide_in_help)]
async fn register(ctx: Context<'_>) -> Result<(), Error> {
    poise::builtins::register_application_commands_buttons(ctx).await?;
    Ok(())
}

#[tracing::instrument]
#[poise::command(prefix_command, slash_command, category = "Meta")]
async fn help(
    ctx: Context<'_>,
    #[description = "Command to show help about"]
    #[rest]
    mut command: Option<String>,
) -> Result<(), Error> {
    // Rewrite `command_with_subcommand help ...` calls to
    // `help command_with_subcommand ...`
    if ctx.invoked_command_name() != "help" {
        command = match command {
            Some(c) => Some(format!("{} {}", ctx.invoked_command_name(), c)),
            None => Some(ctx.invoked_command_name().to_string()),
        }
    }

    let cfg = poise::builtins::HelpConfiguration {
        show_subcommands: true,
        ephemeral: true,
        ..Default::default()
    };
    poise::builtins::help(ctx, command.as_deref(), cfg).await?;
    Ok(())
}

#[tokio::main]
async fn main() {
    init_tracer();

    let token = std::env::var("DISCORD_TOKEN").expect("missing DISCORD_TOKEN");
    let intents = serenity::GatewayIntents::non_privileged();

    let framework = poise::Framework::builder()
        .options(poise::FrameworkOptions {
            commands: vec![help(), age(), roles::role(), register()],
            initialize_owners: false,
            ..Default::default()
        })
        .setup(|ctx, _ready, framework| {
            Box::pin(async move {
                poise::builtins::register_globally(ctx, &framework.options().commands).await?;
                Ok(Data {})
            })
        })
        .build();

    let client = serenity::ClientBuilder::new(token, intents)
        .framework(framework)
        .await;
    client.unwrap().start().await.unwrap();
}

fn init_tracer() {
    let otlp_exporter = opentelemetry_otlp::SpanExporter::builder()
        .with_http()
        .with_protocol(opentelemetry_otlp::Protocol::HttpBinary)
        .build()
        .unwrap();

    let provider = SdkTracerProvider::builder()
        .with_batch_exporter(otlp_exporter)
        .with_resource(Resource::builder().with_service_name("roboshpee").build())
        .build();

    let tracer = provider.tracer("roboshpee");

    let telemetry_layer = tracing_opentelemetry::layer().with_tracer(tracer);
    let console_layer = console_subscriber::spawn();
    let fmt_layer = tracing_subscriber::fmt::layer();

    tracing_subscriber::registry()
        .with(fmt_layer)
        .with(console_layer)
        .with(telemetry_layer)
        .with(tracing_subscriber::EnvFilter::from_default_env())
        .init();
}
