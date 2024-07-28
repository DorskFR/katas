# Python

## Setup

Out of conveniency all projects are setup using https://rye.astral.sh/ which takes care of the runtime, the virtual environment and the dependencies all in one.

```bash
curl -sSf https://rye.astral.sh/get | bash
```

Then cd to each project folder and `rye sync`.

Modules can be started with `rye run python -m module`.

Otherwise all projects will have a `rye run start` command.
