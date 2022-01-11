# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT

import pytest

from specfile.sections import Section
from specfile.tags import Tag, Tags


def test_find():
    tags = Tags(
        [
            Tag("Name", "test", "test", ": ", []),
            Tag("Version", "0.1", "0.1", ": ", []),
            Tag("Release", "1%{?dist}", "1.fc35", ": ", []),
        ]
    )
    assert tags.find("version") == 1
    with pytest.raises(ValueError):
        tags.find("Epoch")


def test_parse():
    tags = Tags.parse(
        Section(
            "package",
            [
                "%global ver_major 1",
                "%global ver_minor 0",
                "",
                "Name:    test",
                "Version: %{ver_major}.%{ver_minor}",
                "Release: 1%{?dist}",
                "",
                "%if 0",
                "Epoch:   1",
                "%endif",
            ],
        ),
        Section(
            "package",
            [
                "",
                "",
                "",
                "Name:    test",
                "Version: 1.0",
                "Release: 1.fc35",
                "",
                "",
                "",
                "",
            ],
        ),
    )
    assert tags[1].name == "Version"
    assert tags[1].value == "%{ver_major}.%{ver_minor}"
    assert tags[1].valid
    assert tags[1].expanded_value == "1.0"
    assert tags[1].comments == []
    assert tags.epoch.name == "Epoch"
    assert not tags.epoch.valid


def test_reassemble():
    tags = Tags(
        [
            Tag(
                "Name",
                "test",
                "test",
                ":    ",
                ["%global ver_major 1", "%global ver_minor 0", ""],
            ),
            Tag("Version", "%{ver_major}.%{ver_minor}", "1.0", ": ", []),
            Tag("Release", "1%{?dist}", "1.fc35", ": ", []),
            Tag("Epoch", "1", "", ":   ", ["", "%if 0"]),
        ],
        ["%endif"],
    )
    assert tags.reassemble() == [
        "%global ver_major 1",
        "%global ver_minor 0",
        "",
        "Name:    test",
        "Version: %{ver_major}.%{ver_minor}",
        "Release: 1%{?dist}",
        "",
        "%if 0",
        "Epoch:   1",
        "%endif",
    ]
