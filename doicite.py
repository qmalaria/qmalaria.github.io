"""
Define a `cite()` macro that converts DOIs to hyperlinked citations.

Citations are indexed by DOI and stored in a JSON cache file, to avoid having
to look up each DOI every time the site is updated.
"""

import dataclasses
import json
import urllib.parse
from pathlib import Path

import requests


@dataclasses.dataclass
class Citation:
    """
    A formatted citation for a published work.

    :param doi: The DOI associated with the published work.
    :param url: The URL for resolving the DOI.
    :param text: The citation text.
    """

    doi: str
    url: str
    text: str

    def link(self) -> str:
        """
        Return a hyperlinked citation for this work in Markdown format.
        """
        return f"[{self.text}]({self.url})"


def load_citations(cache_file: Path) -> dict[str, Citation]:
    """
    Load citations from a JSON cache file.
    """
    if cache_file.exists():
        with open(cache_file, "r") as f:
            cache_data = json.load(f)
        citations = {
            doi: Citation(**cite_dict)
            for doi, cite_dict in cache_data.items()
        }
    else:
        citations = {}

    return citations


def save_citations(cache_file: Path, citations: dict[str, Citation]) -> None:
    """
    Save citations to a JSON cache file.
    """
    # NOTE: we sort by DOI to preserve the citation order in the event that
    # the cache file is removed and recreated.
    cite_dicts = {
        doi: dataclasses.asdict(cite)
        for (doi, cite) in sorted(citations.items(), key=lambda item: item[0])
    }
    with open(cache_file, "w") as f:
        json.dump(cite_dicts, f, indent=2)


class Bibliography:
    """
    A bibliography that stores cited works in a cache file.

    :param cache_file: The JSON file in which to cache formatted citations.
    :param style: The citation style.
    :param lang: The language/locale to use for the citation.
    """
    def __init__(self, cache_file: Path, style: str, lang: str) -> None:
        self.cache_file: Path = cache_file
        self.style = style
        self.lang = lang
        self.citations: dict[str, Citation] = load_citations(cache_file)


    def lookup(self, doi: str) -> Citation:
        """
        Return a formatted citation associated with the given DOI.
        """
        if doi in self.citations:
            citation = self.citations[doi]
        else:
            print(f"Looking up {doi} ...")
            cite_text = get_citation(doi, self.style, self.lang)
            citation = Citation(
                doi=doi,
                url=get_url(doi),
                text=cite_text,
            )
            self.citations[doi] = citation
            save_citations(self.cache_file, self.citations)

        return citation


def get_citation(doi: str, style: str, lang: str) -> str:
    """
    Format the citation for a published work.

    :param doi: The DOI assigned to the published work.
    :param style: The citation style.
    :param lang: The language/locale to use for the citation.

    See https://citation.doi.org/api-docs.html for details.
    """
    url = "https://citation.doi.org/format"
    params = {"doi": doi, "style": style, "lang": lang}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    text = resp.text.strip().removeprefix("1.").strip()
    return text


def get_url(doi: str) -> str:
    """
    Return the URL for resolving a DOI.

    :param doi: The DOI assigned to the published work.
    """
    doi_enc: str = urllib.parse.quote(doi)
    return f"https://doi.org/{doi_enc}"


def define_env(env):
    """
    Define the `cite()` macro for the given environment.
    """
    extra = env.variables["extra"]
    config = extra.get("doicite", {})
    style = config.get("style", "plos")
    lang = config.get("lang", "en-US")
    cache_file = config.get("cache_file", "bibliography.json")

    bib = Bibliography(Path(cache_file), style=style, lang=lang)

    @env.macro
    def cite(doi: str) -> str:
        citation = bib.lookup(doi)
        return citation.link()
