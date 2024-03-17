from django.apps import apps
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Generates a Markdown file with docstrings of Django models'

    def handle(self, *args, **options):
        models_md = ""

        # Iterate over all installed apps
        for app_config in apps.get_app_configs():
            # Iterate over models in each app
            for model in app_config.get_models():
                models_md += f"## {model._meta.app_label}.{model.__name__}\n\n"
                models_md += f"{model.__doc__}\n\n"

                # Iterate over fields in each model
                for field in model._meta.fields:
                    models_md += f"### {field.name}\n\n"
                    models_md += f"{field.__doc__}\n\n"

        # Write the generated Markdown to a file
        with open("models_docstrings.md", "w") as md_file:
            md_file.write(models_md)

        self.stdout.write(self.style.SUCCESS('Successfully generated models docstrings in models_docstrings.md'))