import logging


_logger = logging.getLogger(__name__)


class HtmlCorrector():
    def correct_ib_error_singlepage(self, html: str) -> str:
        """Website HTML contains structural errors that prevent parsing."""

        old_lines = html.splitlines()
        new_lines = []
        corrections = 0
        for line in old_lines:
            if (('        <td align="left" valign="middle">' in line)
                    and ("href" not in line)):
                line = line.replace("</a>", "")
                corrections += 1
            new_lines.append(line)
        html = "\n".join(new_lines)
        if corrections > 0:
            _logger.debug(f"Corrected IB HTML error in {corrections} lines.")
        else:
            _logger.debug(f"IB error for singlepage listings no longer "
                          f"present. Checked {len(old_lines)} lines.")
        return html

    def correct_ib_error_multipage(self, html: str) -> str:
        """Website HTML contains structural errors that prevent parsing."""

        if ("(click link for more details)</span></th>\n                       </th>"
                in html):
            html = html.replace(
                "(click link for more details)</span></th>\n                       </th>\n",
                "(click link for more details)</span></th>\n")
        else:
            _logger.debug(f"IB error for paginated listings no longer "
                          f"present. Checked {len(html.splitlines())} lines.")
        return html
