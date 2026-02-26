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

## Website structure

Each page corresponds to a Markdown file in the `./docs` directory:

- `./docs/index.md` is the homepage ("Welcome to qMalaria");
- `./docs/our-team/index.md` is the "Our Team" page;
    - Each profile page is a separate Markdown file in the `./docs/our-team` directory;
- `./docs/projects/index.md` is the "Projects" page;
    - Each project page is a separate Markdown file in the `./docs/resources` directory;
- `./docs/resources/index.md` is the "Resources" page.

## How to add a new page

1. Create a new Markdown file in the `./docs` directory, or and sub-directory inside `./docs`.
2. Create a heading that defines the page title, and add the page content below:

    ```md
    # Page title

    Content goes here ...
    ```
3. Consider defining a page icon (e.g., search the [Lucide icon set](https://lucide.dev/icons/) for a suitable icon):

    ```md
    ---
    icon: lucide/icon-name
    ---

    # Page title

    Content goes here ...
    ```

4. Add the Markdown file to the navigation table in the [zensical.toml](./zensical.toml) file (see the [navigation documentation](https://zensical.org/docs/setup/navigation/) for further details):

    ```toml
    nav = [
      # ...
      "my-new-page.md",
      # ...
    ]
    ```

    **Important:** don't include the `./docs` part of the filename in the navigation table.

5. Build the updated website and check that the new page is displayed as intended:

    ```sh
    source ./venv/bin/activate
    zensical serve --open
    ```

6. Save ("commit") your changes and upload ("push") them to the website repository:

    ```sh
    git add zensical.toml docs/my-new-page.md
    git commit -m "Add a page about XXX"
    git push
    ```

## How to add a project

1. Add a project image to the `./docs/images` directory (e.g., `project-xyz.png`);

2. Create a project page in the `./docs/projects` directory (e.g., `./docs/projects/xyz.md`; see [How to add a new page](#how-to-add-a-new-page));

3. Add a new tile to the projects page (`./docs/projects/index.md`) that links to this new project page:

    ```md
    - Project title goes here
        {: .project .title }

        ![Project title goes here](../images/project-xyz.png)

        ---

        A brief description of the project goes here.

        [:lucide-arrow-right: Read more](xyz.md)

    ```

4. Add the new project page to the navigation table, under "Projects":

    ```toml
    nav = [
      # ...
      { "Projects" = [
        "projects/index.md",
        # ...
        "projects/xyz.md",
      ] },
      # ...
    ]
    ```

5. Build the updated website and check that the new project page and project tile are both displayed as intended:

    ```sh
    source ./venv/bin/activate
    zensical serve --open
    ```

6. Save ("commit") your changes and upload ("push") them to the website repository:

    ```sh
    git add zensical.toml
    git add docs/projects/index.md docs/projects/xyz.md
    git add docs/images/project-xyz.png
    git commit -m "Add a project page for XYZ"
    git push
    ```

## How to add a team member profile

1. Add a profile photo to the `./docs/images` directory (e.g., `some-person.jpg`);

2. Create a profile page in the `./docs/our-team` directory (e.g., `./docs/our-team/some-person.md`; see [How to add a new page](#how-to-add-a-new-page)):

    ```md
    ---
    icon: lucide/square-user-round
    ---

    # Some Person

    Profile text goes here

    [Link text](other-website-URL-here){ .md-button .md-button--primary }
    ```
3. Add a new tile to the team page (`./docs/our-team/index.md`) that links to this new profile page:

    ```md
    - ![Some Person](../images/some-person.jpg){ .person }

        [Some Person](some-person.md)
        {: .person .title}

    ```

4. Add the new profile page to the navigation table, under "Our Team":

    ```toml
    nav = [
      # ...
      { "Our Team" = [
        "our-team/index.md",
        # ...
        "our-team/some-person.md",
      ] },
      # ...
    ]
    ```

5. Build the updated website and check that the new project page and project tile are both displayed as intended:

    ```sh
    source ./venv/bin/activate
    zensical serve --open
    ```

6. Save ("commit") your changes and upload ("push") them to the website repository:

    ```sh
    git add zensical.toml
    git add docs/our-team/index.md docs/our-team/some-person.md
    git add docs/images/some-person.png
    git commit -m "Add a profile for Some Person"
    git push
    ```
