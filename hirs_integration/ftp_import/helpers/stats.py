import time

def fmt_date(sec):
    t = time.gmtime(sec)
    return f"{t.tm_year}/{t.tm_mon}/{t.tm_mday} {t.tm_hour}:{t.tm_min:02d}"

class Stats:
    time_start = None
    time_end = None
    errors = []
    rows_processed = 0
    rows_imported = 0
    warnings = []
    pending_users = []
    new_users = []
    files = []

    @property
    def runtime(self):
        if self.time_start and self.time_end:
            return int(round(self.time_end - self.time_start,0))
        return None

    def __str__(self):
        output = [
            f'\tStart Time:            {fmt_date(self.time_start)}',
            f'\tEnd Time:              {fmt_date(self.time_end)}',
            f'\tTotal Processing Time: {self.runtime}s',
            f'\tFiles Processed:       {len(self.files)}'
            f'\tRows Processed:        {self.rows_processed}',
            f'\tRows Imported:         {self.rows_imported}',
            f'\tPending Users:         {len(self.pending_users)}',
            f'\tNew users:             {len(self.new_users)}',
            f'\t# of Warning:          {len(self.warnings)}',
            f'\t# of Errors:           {len(self.errors)}'
        ]
        return "\n".join(output)

    @property
    def as_html(self):
        output = [
            "<body>",
            "<h1>FTP Import Summary</h3>",
            "<h3>Stats:</h3>",
            '<table style="border: None;">',
            f"<tr><td>Start Time</td><td>{fmt_date(self.time_start)}</td></tr>",
            f"<tr><td>End Time</td><td>{fmt_date(self.time_end)}</td></tr>",
            f"<tr><td>Processing Time</td><td>{self.runtime}s</td></tr>",
            f"<tr><td>Files Processed</td><td>{len(self.files)}</td></tr>",
            f"<tr><td>Rows Processed</td><td>{self.rows_processed}</td></tr>",
            f"<tr><td>Rows Imported</td><td>{self.rows_imported}</td></tr>",
            "</table>"
        ]

        if self.pending_users:
            output.append("<h3>Users Pending Import:</h3>")
            output.append("<ol>")
            for r in self.pending_users:
                output.append(f"<li>{r}</li>")
            output.append("</ol>")

        if self.new_users:
            output.append("<h3>New Users:</h3>")
            output.append("<ol>")
            for r in self.new_users:
                output.append(f"<li>{r}</li>")
            output.append("</ol>")

        if self.errors:
            output.append("<h3>Errors:</h3>")
            output.append("<ol>")
            for r in self.errors:
                output.append(f"<li>{r}</li>")
            output.append("</ol>")

        output.append("<h3>Files Processed:</h3>")
        output.append("<ol>")
        for r in self.files:
            output.append(f"<li>{r}</li>")
        output.append("</ol>")

        output.append("</body>")
        return "\n".join(output)

    @property
    def as_text(self):
        output = [
            "FTP Import Summary",
            "",
            "Stats:",
            f"  Start Time:      {fmt_date(self.time_start)}",
            f"  End Time:        {fmt_date(self.time_end)}",
            f"  Processing Time: {self.runtime}s",
            f"  Files Processed: {len(self.files)}",
            f"  Rows Processed:  {self.rows_processed}",
            f"  Rows Imported:   {self.rows_imported}",
        ]

        if self.pending_users:
            output.append("")
            output.append("")
            output.append("Users Pending Import:")
            for r in self.pending_users:
                output.append(f" - {r}")

        if self.new_users:
            output.append("")
            output.append("")
            output.append("New Users:")
            for r in self.new_users:
                output.append(f" - {r}")

        if self.errors:
            output.append("")
            output.append("")
            output.append("Errors:")
            for r in self.errors:
                output.append(f" - {r}")

        output.append("")
        output.append("")
        output.append("Files Processed:")
        for r in self.files:
            output.append(f" - {r}")

        return "\n".join(output)