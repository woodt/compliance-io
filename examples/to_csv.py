import csv
from collections import defaultdict
from itertools import groupby

import click

from complianceio.opencontrol import OpenControl


@click.command()
@click.argument(
    "source",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, resolve_path=True),
)
@click.argument("dest", type=click.File("w"))
def main(source, dest):
    """
    Read the OpenControl repo at SOURCE and write a CSV file
    containing component narratives aggregated by
    control.
    """

    oc = OpenControl.load(source)

    statements = defaultdict(list)

    for component in oc.components:
        for control in component.satisfies:
            for statement in control.narrative:
                statements[control.control_key].append(statement)

    writer = csv.writer(dest, dialect="unix")
    for control in sorted(statements.keys()):
        for key, stmts_by_key in groupby(
            sorted(statements[control], key=lambda s: s.key or ""), lambda s: s.key
        ):
            text = "\n".join([s.text for s in stmts_by_key])
            if key:
                control_label = f"{control}.{key}"
            else:
                control_label = control
            writer.writerow((control_label, text.strip()))


if __name__ == "__main__":
    main()
