#!/usr/bin/env python3
"""Install pinned, official veraPDF CLI in an explicit isolated directory.

No system packages, GUI, binaries in git, or automatic metadata repair. Java is
a prerequisite. The archive hash pins the exact upstream release used by CI.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from zipfile import ZipFile

VERSION = "1.30.3"
URL = f"https://software.verapdf.org/releases/1.30/verapdf-greenfield-{VERSION}-installer.zip"
SHA256 = "b512bf24945503a33fc10738ecffc1f2dccaaf8593a448e94ee9ac86a9559a59"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    destination = args.output.resolve()
    executable = destination / "verapdf"
    if executable.exists():
        version = subprocess.check_output([str(executable), "--version"], text=True)
        if version.splitlines()[0] != f"veraPDF {VERSION}":
            raise SystemExit("Existing destination has a different veraPDF version")
        print(str(executable))
        return
    if destination.exists() and any(destination.iterdir()):
        raise SystemExit("Refusing to install over a nonempty directory")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="verapdf-install-", dir=destination.parent) as temporary:
        work = Path(temporary)
        archive = work / "installer.zip"
        with urllib.request.urlopen(URL, timeout=90) as response:
            archive.write_bytes(response.read())
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        if digest != SHA256:
            raise SystemExit(f"Upstream archive hash mismatch: {digest}")
        with ZipFile(archive) as files:
            member = f"verapdf-greenfield-{VERSION}/verapdf-izpack-installer-{VERSION}.jar"
            installer = work / "installer.jar"
            installer.write_bytes(files.read(member))
        root = ET.Element("AutomatedInstallation", langpack="eng")
        prefix = "com.izforge.izpack.panels."
        ET.SubElement(root, prefix + "htmlhello.HTMLHelloPanel", id="welcome")
        target = ET.SubElement(root, prefix + "target.TargetPanel", id="install_dir")
        ET.SubElement(target, "installpath").text = str(destination)
        packs = ET.SubElement(root, prefix + "packs.PacksPanel", id="sdk_pack_select")
        for index, name in enumerate(("veraPDF GUI", "veraPDF CLI", "veraPDF Documentation", "veraPDF Sample Plugins")):
            ET.SubElement(packs, "pack", index=str(index), name=name, selected=str(index == 1).lower())
        ET.SubElement(root, prefix + "install.InstallPanel", id="install")
        ET.SubElement(root, prefix + "finish.FinishPanel", id="finish")
        script = work / "auto.xml"
        ET.ElementTree(root).write(script, encoding="utf-8", xml_declaration=True)
        subprocess.run(["java", "-jar", str(installer), str(script)], check=True, timeout=90)
    version = subprocess.check_output([str(executable), "--version"], text=True)
    if version.splitlines()[0] != f"veraPDF {VERSION}":
        raise SystemExit("Installed validator version mismatch")
    (destination / "download-provenance.json").write_text(json.dumps({
        "url": URL, "sha256": SHA256, "version": VERSION,
        "profile": "Explicit --flavour ua1; default PDF/A is not used",
    }, indent=2) + "\n")
    print(str(executable))


if __name__ == "__main__":
    main()
