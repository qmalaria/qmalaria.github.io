# qMalaria

This website is generated using [Zensical](https://zensical.org/).

To edit and preview the website on your own computer, make a local copy of this repository.
You will need to have [Python](www.python.org/) version 3.10 or later installed.

## Initial setup

Make a local copy of this repository.
For example:

```sh
git clone git@github.com:qmalaria/qmalaria.github.io.git
cd qmalaria.github.io
```

Then create a Python [virtual environment](https://docs.python.org/3/tutorial/venv.html) in the directory `./venv` and install the required Python packages:

```sh
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```

**You only need to do this once.**

## Live preview

Ensure that you've activated the virtual environment in `./venv`, and then run `zensical` to preview the website:

```sh
source ./venv/bin/activate
zensical serve --open
```

**This preview will automatically update** when you modify the pages in the `./docs` directory.
