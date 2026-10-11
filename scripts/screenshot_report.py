"""Render the sample weekly report to a PNG for the README (dev helper, optional).
Needs: pip install markdown, and wkhtmltoimage on the PATH."""
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
week = sys.argv[1] if len(sys.argv) > 1 else "2026-W34"
src = ROOT / "output" / "sample" / f"weekly_report_{week}.md"
html = markdown.markdown(src.read_text(encoding="utf-8"), extensions=["tables"])
css = """body{font-family:-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;color:#1f2328;max-width:980px;
margin:24px auto;padding:0 24px;font-size:15px;line-height:1.5;background:#fff}
h1{font-size:26px;border-bottom:1px solid #d1d9e0;padding-bottom:8px}h2{font-size:20px;border-bottom:1px solid #d1d9e0;
padding-bottom:6px;margin-top:28px}blockquote{margin:0;padding:4px 16px;border-left:4px solid #d1d9e0;color:#1f2328}
table{border-collapse:collapse;margin:12px 0;font-size:13.5px}th,td{border:1px solid #d1d9e0;padding:5px 10px}
th{background:#f6f8fa}tr:nth-child(2n) td{background:#f6f8fa}img{max-width:100%}em{color:#59636e}"""
out_html = ROOT / "output" / "sample" / "_preview.html"
out_html.write_text(f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{html}</body></html>",
                    encoding="utf-8")
png = ROOT / "docs" / "images" / "weekly_report.png"
subprocess.run(["wkhtmltoimage", "--quiet", "--enable-local-file-access", "--width", "1060", "--crop-h",
                "1500", str(out_html), str(png)], check=True)
out_html.unlink()
print(f"wrote {png}")
