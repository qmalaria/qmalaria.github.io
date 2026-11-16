"""
Define a `cite()` macro that converts DOIs to hyperlinked citations.

Citations are indexed by DOI and stored in a JSON cache file, to avoid having
to look up each DOI every time the site is updated.
"""

import json
import re
import tempfile
from pathlib import Path

import bibtexparser
import requests
import zensical
from citeproc import (
    Citation,
    CitationItem,
    CitationStylesBibliography,
    CitationStylesStyle,
    formatter,
)
from citeproc.source.bibtex import BibTeX


def load_items(cache_file: Path) -> dict[str, str]:
    """
    Restore saved items from a cache file (if it exists), otherwise return an
    empty dictionary.
    """
    if cache_file.exists():
        with open(cache_file, "r") as f:
            items: dict[str, str] = json.load(f)
    else:
        items = {}
    return items


def save_items(cache_file: Path, items: dict[str, str]) -> None:
    """
    Save items to a cache file, first sorting by key (DOI) to ensure that the
    items are always ordered consistently.
    """
    sorted_items = {
        key: items[key]
        for key in sorted(items.keys())
    }
    with open(cache_file, "w") as f:
        json.dump(sorted_items, f, indent=2)


def get_bib_for(doi: str) -> str:
    """
    Retrieve the BibTeX entry for a DOI.
    """
    url = f"https://doi.org/{doi}"
    headers = {"accept": "application/x-bibtex"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    text = str(resp.text).strip()
    return text


class BibTexSource:
    """
    Manage a collection of BibTeX entries.
    """

    def __init__(self, bib_file: Path) -> None:
        self.bib_file = bib_file
        self.bib_items = load_items(bib_file)

    def lookup(self, doi: str) -> str:
        """
        Return the BibTeX entry associated with a DOI.
        """
        if doi in self.bib_items:
            return self.bib_items[doi]
        print(f"Looking up {doi} ...")
        text = get_bib_for(doi)
        self.bib_items[doi] = text
        save_items(self.bib_file, self.bib_items)
        return text


class BibTexRendered:
    """
    Manage a collection of rendered citations.
    """

    def __init__(self, cache_file: Path, source: BibTexSource) -> None:
        self.cache_file = cache_file
        self.rendered_items = load_items(cache_file)
        self.source = source

    def render(self, doi: str, style: CitationStylesStyle) -> str:
        """
        Return the rendered citation for a DOI.
        """
        if doi in self.rendered_items:
            text = self.rendered_items[doi]
        else:
            src = self.source.lookup(doi)
            text = render_bibtex(src, style)
            self.rendered_items[doi] = text
            save_items(self.cache_file, self.rendered_items)
        return text


def clean_bib(text: str) -> bibtexparser.library.Library:
    """
    Parse a BibTeX entry, removing fields that are not supported by citeproc.
    """
    lib = bibtexparser.parse_string(
        text,
        append_middleware=[
            # Transforms {\"o} -> ö, removes curly braces, etc.
            bibtexparser.middlewares.LatexDecodingMiddleware(),
            bibtexparser.middlewares.MonthAbbreviationMiddleware(True),
            # Transforms apr -> 4 etc.
            bibtexparser.middlewares.MonthIntMiddleware(True),
        ],
    )

    if "doi" in lib.entries:
        lib.entries["DOI"] = "doi"
    if "url" in lib.entries:
        lib.entries["URL"] = "url"

    for entry in lib.entries:
        del entry["month"]
        del entry["editor"]
        del entry["doi"]
        del entry["url"]

    return lib


def citeproc_bibtex(lib: bibtexparser.library.Library) -> BibTeX:
    """
    Construct a citeproc bibliography for a parsed BibTeX entry.
    """
    text = bibtexparser.write_string(lib)
    with tempfile.NamedTemporaryFile(mode="w", delete_on_close=False) as f:
        f.write(text)
        f.close()
        b = BibTeX(f.name, encoding="utf-8")
    return b


def citeproc_render(bib: BibTeX, style: CitationStylesStyle) -> str:
    """
    Render a citeproc bibliography using the specified style.
    """
    keys = list(bib.keys())
    if len(keys) != 1:
        raise ValueError(keys)
    key = keys[0]
    library = CitationStylesBibliography(style, bib, formatter.html)
    item = CitationItem(key)
    library.register(Citation([item]))
    rendered_items: list[str] = library.style.render_bibliography([item])
    return rendered_items[0]


def render_bibtex(src: str, style: CitationStylesStyle) -> str:
    """
    Render a BibTeX entry usin the specified style, and convert the DOI into a
    Markdown hyperlink.
    """
    cleaned = clean_bib(src)
    csl_bib = citeproc_bibtex(cleaned)
    csl_mixed_string = citeproc_render(csl_bib, style)
    # NOTE: strip the leading citation number.
    text_fields = list(csl_mixed_string)[1:]
    text = "".join(text_fields)
    # NOTE: collapse whitespace and newlines.
    rendered = re.sub(r"\s+", " ", text)
    # NOTE: convert the DOI into a hyperlink.
    doi = str(cleaned.entries[0]["DOI"])
    text_out = rendered.replace(doi, f"[{doi}](https://doi.org/{doi})")
    return text_out


def bold_authors(text: str, authors: list[str]) -> str:
    """
    Highlight specific authors with bold text.
    """
    # NOTE: we use regular expressions so that we can handle, e.g., both
    # "Zaloumis S" and "Zaloumis SG".
    for author in authors:
        text = re.sub(f"({author})", "**\\1**", text)
    return text


def define_env(env: zensical.extensions.macros.MacroEnv) -> None:
    """
    Define the `cite()` macro for the given environment.
    """
    extra = env.variables["extra"]
    config = extra.get("doicite", {})
    authors = config.get("authors", [])
    bib_file = Path(config.get("bibtex_cache", "doicite-bibtex.json"))
    cache_file = Path(config.get("rendered_cache", "doicite-rendered.json"))
    csl_file = config.get("csl_file", "plos.csl")

    bib_src = BibTexSource(bib_file)
    bib_out = BibTexRendered(cache_file, bib_src)
    csl_style = CitationStylesStyle(csl_file)

    @env.macro
    def cite(doi: str, anchor: str | None = None) -> str:
        markdown_str = bib_out.render(doi, csl_style)
        bolded_str = bold_authors(markdown_str, authors)
        if anchor is None or anchor == "":
            return bolded_str
        else:
            return f'<span class="cite" id="{anchor}">{bolded_str}</span>'
