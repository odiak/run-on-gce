# run_on_gce.py

run_on_gce.py runs Python program on Google Compute Engine.
It copies all related files to specified GCE instance, install dependencies via Poetry, and runs specified commands.

## Install

```console
poetry add --dev git+https://github.com/odiak/run-on-gce.git
```

## Example

```python
from run_on_gce import run_on_gce

run_on_gce(
    projec="my-project-999999",
    instance="dev-server-3",
    location="asia-northeast1-a",
    project_dir="~/src/github.com/user/project",
    filter_rules=(
        "- .venv",
        "H build",
        "+ */",
        "+ *.py",
        "+ pyproject.toml",
        "+ poetry.lock",
        "+ .python-version",
        "H *",
    ),
    args=("poetry", "run", "python", "my_program.py"),
)
```

# License

MIT License.