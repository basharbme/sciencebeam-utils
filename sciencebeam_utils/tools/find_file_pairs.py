import argparse
import logging

from backports import csv  # pylint: disable=no-name-in-module

from six import text_type

from sciencebeam_utils.utils.csv import (
    csv_delimiter_by_filename,
    write_csv_rows
)

from sciencebeam_utils.beam_utils.io import (
    open_file,
    dirname,
    mkdirs_if_not_exists
)

from sciencebeam_utils.utils.file_path import (
    join_if_relative_path,
    relative_path
)

from sciencebeam_utils.utils.file_pairs import (
    find_file_pairs_grouped_by_parent_directory_or_name
)

from sciencebeam_utils.tools.tool_utils import (
    setup_logging,
    add_default_args,
    process_default_args
)


LOGGER = logging.getLogger(__name__)


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data-path', type=str, required=True,
        help='base data path'
    )
    parser.add_argument(
        '--source-pattern', type=str, required=True,
        help='source pattern'
    )
    parser.add_argument(
        '--xml-pattern', type=str, required=True,
        help='xml pattern'
    )
    parser.add_argument(
        '--out', type=str, required=True,
        help='output csv/tsv file'
    )

    parser.add_argument(
        '--use-relative-paths', action='store_true',
        help='create a file list with relative paths (relative to the data path)'
    )

    add_default_args(parser)

    return parser.parse_args(argv)


def save_file_pairs_to_csv(output_path, source_xml_pairs):
    mkdirs_if_not_exists(dirname(output_path))
    delimiter = csv_delimiter_by_filename(output_path)
    mime_type = 'text/tsv' if delimiter == '\t' else 'text/csv'
    with open_file(output_path, 'w', mime_type=mime_type) as f:
        writer = csv.writer(f, delimiter=text_type(delimiter))
        write_csv_rows(writer, [['source_url', 'xml_url']])
        write_csv_rows(writer, source_xml_pairs)
    LOGGER.info('written results to %s', output_path)


def to_relative_file_pairs(base_path, file_pairs):
    return (
        (relative_path(base_path, source_url), relative_path(base_path, xml_url))
        for source_url, xml_url in file_pairs
    )


def run(args):
    LOGGER.info('finding file pairs')
    source_xml_pairs = find_file_pairs_grouped_by_parent_directory_or_name([
        join_if_relative_path(args.data_path, args.source_pattern),
        join_if_relative_path(args.data_path, args.xml_pattern)
    ])

    if args.use_relative_paths:
        source_xml_pairs = to_relative_file_pairs(args.data_path, source_xml_pairs)

    source_xml_pairs = list(source_xml_pairs)

    save_file_pairs_to_csv(args.out, source_xml_pairs)


def main(argv=None):
    args = parse_args(argv)

    process_default_args(args)

    run(args)


if __name__ == '__main__':
    setup_logging()

    main()
