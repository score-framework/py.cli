from pkg_resources import iter_entry_points
from .ui import default as default_ui


def main():
    installers = [entrypoint.load()(entrypoint.dist.project_name)
                  for entrypoint in iter_entry_points(group='score.cli.setup')]
    default_ui(installers)


if __name__ == '__main__':
    main()
