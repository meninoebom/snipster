import reflex as rx

config = rx.Config(
    app_name="ui",
    api_url="https://snipster-reflex.fly.dev",
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
)
