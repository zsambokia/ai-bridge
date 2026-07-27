# Provider registry proof

Migration `0011_executionprovider_providerauditevent` creates and seeds the registry. `python manage.py migrate --check` and `python manage.py makemigrations --check` passed on the final workspace.

Safe MCP discovery is exposed through `provider.list`, `provider.get`, `provider.capabilities`, and `provider.health`. These responses exclude configuration, credential bindings, command lines, and raw exceptions.
