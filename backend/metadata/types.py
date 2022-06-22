from typing import DefaultDict, Dict, List, Optional

from mypy_extensions import TypedDict


class _GenderForenames(TypedDict):
    latinSpelling: List[str]
    nativeSpelling: Optional[List[str]]


class SubstitutionForenamesMap(TypedDict):
    maleForenames: _GenderForenames
    femaleForenames: _GenderForenames
    demonym: Optional[str]
    country: str


DefaultForenamesTranslations = Optional[Dict[str, List[str]]]


class _Translations(TypedDict):
    letsGo: Optional[str]
    constitutionQuery: Optional[List[str]]
    defaultForenames: DefaultForenamesTranslations


class _Properties(TypedDict):
    usesLatinScript: bool


class _LanguageMetadataValue(TypedDict):
    sentenceDataDownloadLinks: Dict[str, str]
    properties: _Properties
    countriesEmployedIn: List[str]
    translations: Dict[str, _Translations]


LanguageMetadata = DefaultDict[str, _LanguageMetadataValue]
CountryMetadata = Dict[str, Optional[SubstitutionForenamesMap]]
