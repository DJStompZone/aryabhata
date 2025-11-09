import runpy
import sys
from aryabhata.main import main


def test_main_no_digits_default(capsys):
    main(["9"])
    out = capsys.readouterr().out.strip()
    # sqrt(9) = 3
    assert out == "3"


def test_main_with_digits_default(capsys):
    main(["82", "--digits", "3"])
    out = capsys.readouterr().out.strip()
    assert out.startswith("9.055")


def test_main_debug(capsys):
    main(["82", "--digits", "3", "--debug"])
    lines = capsys.readouterr().out.strip().splitlines()

    assert lines[0].startswith("9.055")

    assert "[scaled-root]" in lines[1]
    assert "[remainder]" in lines[2]
    assert "[identity]" in lines[3]


def test_module_executes_if_guard(capsys, monkeypatch):
    # simulate `python -m aryabhata 82 --digits 3`
    monkeypatch.setattr(sys, "argv", ["aryabhata", "82", "--digits", "3"])
    runpy.run_module("aryabhata.__main__", run_name="__main__")
    out = capsys.readouterr().out.strip()
    assert out.startswith("9.055")
