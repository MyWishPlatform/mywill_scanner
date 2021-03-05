# Setup scanner

### Add config
* Create `.yaml` config
* Add env variable `CONFIG` with full path to your config file
* According to `config.example.yaml` in `settings` directory fill your config
---
### Start project
Before start make sure your workdir is project root and you setup config.

Scanner starting from `networks/networks_scan_entrypoint.py`.

Scanner using `poetry`, to install poetry you need run command:
```
pip install poetry
```

After this, poetry will be used as package manager.

To install dependencies, run:
```
poetry install
```

To start project, run:
```
poetry run python main.py
```