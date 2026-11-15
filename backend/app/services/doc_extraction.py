import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from .DocumentExtractor import DocumentExtractor, TextBlock
from .docx_extraction import DocxExtractor


class DocExtractor(DocumentExtractor):
    def extract(self, data: bytes) -> list[TextBlock]:
        executable = os.environ.get("LIBREOFFICE_EXECUTABLE") or shutil.which("soffice")
        if not executable:
            raise RuntimeError("Install LibreOffice and set LIBREOFFICE_EXECUTABLE to soffice")

        with TemporaryDirectory() as directory:
            workspace = Path(directory).resolve()
            source = workspace / "document.doc"
            source.write_bytes(data)
            converted = source.with_suffix(".docx")
            profile_uri = (workspace / "libreoffice-profile").as_uri()
            try:
                subprocess.run(
                    [
                        executable,
                        f"-env:UserInstallation={profile_uri}",
                        "--headless",
                        "--convert-to",
                        "docx:Office Open XML Text",
                        "--outdir",
                        str(workspace),
                        str(source),
                    ],
                    capture_output=True,
                    check=True,
                    timeout=30,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            except (OSError, subprocess.SubprocessError) as exc:
                raise RuntimeError("LibreOffice could not convert the .doc file") from exc
            if not converted.is_file():
                raise ValueError("LibreOffice did not produce a .docx file")
            return DocxExtractor().extract(converted.read_bytes())
