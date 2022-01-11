# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

import collections
import itertools
import re
from typing import List, Optional

from specfile.sections import Section

# valid tag names extracted from lib/rpmtag.h in RPM source
TAG_NAMES = [
    "Arch",
    "Archivesize",
    "Autoprov",
    "Autoreq",
    "Autoreqprov",
    "Basenames",
    "Bugurl",
    "Buildarchs",
    "Buildconflicts",
    "Buildhost",
    "Buildmacros",
    "Buildprereq",
    "Buildrequires",
    "Buildtime",
    "C",
    "Changelog",
    "Changelogname",
    "Changelogtext",
    "Changelogtime",
    "Classdict",
    "Conflictflags",
    "Conflictname",
    "Conflictnevrs",
    "Conflicts",
    "Conflictversion",
    "Cookie",
    "Dbinstance",
    "Defaultprefix",
    "Dependsdict",
    "Description",
    "Dirindexes",
    "Dirnames",
    "Distribution",
    "Disttag",
    "Disturl",
    "Docdir",
    "Dsaheader",
    "E",
    "Encoding",
    "Enhanceflags",
    "Enhancename",
    "Enhancenevrs",
    "Enhances",
    "Enhanceversion",
    "Epoch",
    "Epochnum",
    "Evr",
    "Excludearch",
    "Excludeos",
    "Exclusivearch",
    "Exclusiveos",
    "Filecaps",
    "Fileclass",
    "Filecolors",
    "Filedependsn",
    "Filedependsx",
    "Filedevices",
    "Filedigestalgo",
    "Filedigests",
    "Fileflags",
    "Filegroupname",
    "Fileinodes",
    "Filelangs",
    "Filelinktos",
    "Filemd5s",
    "Filemodes",
    "Filemtimes",
    "Filenames",
    "Filenlinks",
    "Fileprovide",
    "Filerdevs",
    "Filerequire",
    "Filesignaturelength",
    "Filesignatures",
    "Filesizes",
    "Filestates",
    "Filetriggerconds",
    "Filetriggerflags",
    "Filetriggerin",
    "Filetriggerindex",
    "Filetriggername",
    "Filetriggerpostun",
    "Filetriggerpriorities",
    "Filetriggerscriptflags",
    "Filetriggerscriptprog",
    "Filetriggerscripts",
    "Filetriggertype",
    "Filetriggerun",
    "Filetriggerversion",
    "Fileusername",
    "Fileverifyflags",
    "Fscontexts",
    "Gif",
    "Group",
    "Hdrid",
    "Headercolor",
    "Headeri18ntable",
    "Headerimage",
    "Headerimmutable",
    "Headerregions",
    "Headersignatures",
    "Icon",
    "Installcolor",
    "Installprefix",
    "Installtid",
    "Installtime",
    "Instfilenames",
    "Instprefixes",
    "License",
    "Longarchivesize",
    "Longfilesizes",
    "Longsigsize",
    "Longsize",
    "Modularitylabel",
    "N",
    "Name",
    "Nevr",
    "Nevra",
    "Nopatch",
    "Nosource",
    "Nvr",
    "Nvra",
    "O",
    "Obsoleteflags",
    "Obsoletename",
    "Obsoletenevrs",
    "Obsoletes",
    "Obsoleteversion",
    "Optflags",
    "Orderflags",
    "Ordername",
    "Orderversion",
    "Origbasenames",
    "Origdirindexes",
    "Origdirnames",
    "Origfilenames",
    "Os",
    "P",
    "Packager",
    "Patch",
    "Patchesflags",
    "Patchesname",
    "Patchesversion",
    "Payloadcompressor",
    "Payloaddigest",
    "Payloaddigestalgo",
    "Payloaddigestalt",
    "Payloadflags",
    "Payloadformat",
    "Pkgid",
    "Platform",
    "Policies",
    "Policyflags",
    "Policynames",
    "Policytypes",
    "Policytypesindexes",
    "Postin",
    "Postinflags",
    "Postinprog",
    "Posttrans",
    "Posttransflags",
    "Posttransprog",
    "Postun",
    "Postunflags",
    "Postunprog",
    "Prefixes",
    "Prein",
    "Preinflags",
    "Preinprog",
    "Prereq",
    "Pretrans",
    "Pretransflags",
    "Pretransprog",
    "Preun",
    "Preunflags",
    "Preunprog",
    "Provideflags",
    "Providename",
    "Providenevrs",
    "Provides",
    "Provideversion",
    "Pubkeys",
    "R",
    "Recommendflags",
    "Recommendname",
    "Recommendnevrs",
    "Recommends",
    "Recommendversion",
    "Recontexts",
    "Release",
    "Removepathpostfixes",
    "Removetid",
    "Requireflags",
    "Requirename",
    "Requirenevrs",
    "Requires",
    "Requireversion",
    "Rpmversion",
    "Rsaheader",
    "Sha1header",
    "Sha256header",
    "Sig_base",
    "Siggpg",
    "Sigmd5",
    "Sigpgp",
    "Sigsize",
    "Size",
    "Source",
    "Sourcepackage",
    "Sourcepkgid",
    "Sourcerpm",
    "Suggestflags",
    "Suggestname",
    "Suggestnevrs",
    "Suggests",
    "Suggestversion",
    "Summary",
    "Supplementflags",
    "Supplementname",
    "Supplementnevrs",
    "Supplements",
    "Supplementversion",
    "Transfiletriggerconds",
    "Transfiletriggerflags",
    "Transfiletriggerin",
    "Transfiletriggerindex",
    "Transfiletriggername",
    "Transfiletriggerpostun",
    "Transfiletriggerpriorities",
    "Transfiletriggerscriptflags",
    "Transfiletriggerscriptprog",
    "Transfiletriggerscripts",
    "Transfiletriggertype",
    "Transfiletriggerun",
    "Transfiletriggerversion",
    "Triggerconds",
    "Triggerflags",
    "Triggerin",
    "Triggerindex",
    "Triggername",
    "Triggerpostun",
    "Triggerprein",
    "Triggerscriptflags",
    "Triggerscriptprog",
    "Triggerscripts",
    "Triggertype",
    "Triggerun",
    "Triggerversion",
    "Url",
    "V",
    "Vcs",
    "Vendor",
    "Verbose",
    "Verifyscript",
    "Verifyscriptflags",
    "Verifyscriptprog",
    "Veritysignaturealgo",
    "Veritysignatures",
    "Version",
    "Xpm",
]


class Tag:
    """
    Class that represents spec file tag.

    Attributes:
        name: Name of the tag.
        value: Literal value of the tag as stored in the spec file.
    """

    def __init__(
        self,
        name: str,
        value: str,
        expanded_value: str,
        separator: str,
        preceding_lines: List[str],
    ) -> None:
        if not name or name.capitalize().rstrip("0123456789") not in TAG_NAMES:
            raise ValueError(f"Invalid tag name: '{name}'")
        self.name = name
        self.value = value
        self._expanded_value = expanded_value
        self._separator = separator
        self._preceding_lines = preceding_lines.copy()

    def __repr__(self) -> str:
        preceding_lines = repr(self._preceding_lines)
        return (
            f"Tag({self.name}, '{self.value}', '{self._expanded_value}', "
            f"'{self._separator}', {preceding_lines})"
        )

    @property
    def valid(self) -> bool:
        """Validity of the tag. A tag is valid if it 'survives' the expansion of the spec file."""
        return self._expanded_value is not None

    @property
    def expanded_value(self) -> str:
        """Value of the tag after expanding macros and evaluating all conditions."""
        return self._expanded_value

    @property
    def comments(self) -> List[str]:
        """List of comment lines associated with the tag."""
        comments = itertools.takewhile(
            lambda x: x.startswith("#"), reversed(self._preceding_lines)
        )
        return [c[1:] for c in reversed(list(comments))]


class Tags(collections.UserList):
    """
    Class that represents all tags in a certain %package section.

    Tags can be accessed by index or conveniently by name as attributes:
    ```
    # print name of the first tag
    print(tags[0].name)

    # set value of Url tag
    tags.url = 'https://example.com'

    # remove Source1 tag
    del tags.source1
    ```

    Attributes:
        data: List of individual tags.
    """

    def __init__(
        self, data: Optional[List[Tag]] = None, remainder: List[str] = []
    ) -> None:
        super().__init__()
        if data is not None:
            self.data = data.copy()
        self._remainder = remainder.copy()

    def __repr__(self) -> str:
        data = repr(self.data)
        remainder = repr(self._remainder)
        return f"Tags({data}, {remainder})"

    def __getattr__(self, name: str) -> Tag:
        try:
            return self.data[self.find(name)]
        except ValueError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: str) -> None:
        if name.capitalize().rstrip("0123456789") not in TAG_NAMES:
            return super().__setattr__(name, value)
        try:
            self.data[self.find(name)].value = value
        except ValueError:
            raise AttributeError(name)

    def __delattr__(self, name: str) -> None:
        if name.capitalize().rstrip("0123456789") not in TAG_NAMES:
            return super().__delattr__(name)
        try:
            del self.data[self.find(name)]
        except ValueError:
            raise AttributeError(name)

    def find(self, name: str) -> int:
        try:
            return next(
                iter(
                    i
                    for i in range(len(self.data))
                    if self.data[i].name.capitalize() == name.capitalize()
                )
            )
        except StopIteration:
            raise ValueError

    @staticmethod
    def parse(raw_section: Section, parsed_section: Optional[Section] = None) -> "Tags":
        """
        Parses a section into tags.

        Args:
            raw_section: Raw (unprocessed) section.
            parsed_section: The same section after parsing.

        Returns:
            Constructed instance of `Tags` class.
        """

        def regex_pattern(tag):
            name = re.escape(tag)
            index = r"\d?" if tag in ["Source", "Patch"] else ""
            return fr"^(?P<n>{name}{index})(?P<s>\s*:\s*)(?P<v>.+)"

        tag_regexes = [re.compile(regex_pattern(t), re.IGNORECASE) for t in TAG_NAMES]
        data = []
        buffer: List[str] = []
        for line in raw_section:
            m = next((m for m in (r.match(line) for r in tag_regexes) if m), None)
            if m:
                e = next(
                    (e for e in (m.re.match(pl) for pl in parsed_section or []) if e),
                    None,
                )
                expanded_value = e.group("v") if e else None
                data.append(
                    Tag(
                        m.group("n"), m.group("v"), expanded_value, m.group("s"), buffer
                    )
                )
                buffer = []
            else:
                buffer.append(line)
        return Tags(data, buffer)

    def reassemble(self) -> List[str]:
        """
        Reconstructs section data from tags.

        Returns:
            List of lines forming the reconstructed section data.
        """
        result = []
        for tag in self.data:
            result.extend(tag._preceding_lines)
            result.append(f"{tag.name}{tag._separator}{tag.value}")
        result.extend(self._remainder)
        return result
