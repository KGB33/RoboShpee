import dagger
from dagger import object_type, function, dag

PREFIX = "dagger"


@object_type
class Actions:
    @function
    def workflows(self) -> dagger.Directory:
        """
        Usage, from the root of the repo: `dagger call generate-ci workflows -o .`
        """
        return (
            dag.gha(dagger_version="v0.12.6")
            # Test on PRs
            .with_pipeline(
                name="Test",
                command="test",
                lfs=True,
                on_pull_request=True,
                on_push_branches=["main"],
            )
            # Publish
            .with_pipeline(
                name="Publish",
                command="--is-dev=false publish --ghcr-token env:GITHUB_TOKEN",
                lfs=True,
                secrets=["GITHUB_TOKEN"],
                on_push_branches=["main"],
            )
            # Generate config
            .config()
        )
