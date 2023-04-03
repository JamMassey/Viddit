from __future__ import annotations
from typing import List
import logging
from argparse import ArgumentParser
from dataclasses import dataclass, field
from pathlib import Path
from typing import OrderedDict

logger = logging.getLogger("discord")


def add_boolean_arg(parser: ArgumentParser, name: str, desc: str, default: bool = False) -> None:
    """Adds a boolean arg to the arg parser allowing --arg and --no-arg for True and False respectively
    Parameters
    ----------
    parser : ArgumentParser
        Arg parser to add the argument to
    name : str
        Name of the argument
    desc : str
        Description of the arg to add
    default : bool, optional
        Default value of the boolean flag, by default False
    """
    dest = name.replace("-", "_")
    group = parser.add_argument_group(f"{name} options:", desc)
    me_group = group.add_mutually_exclusive_group(required=False)
    me_group.add_argument(f"--{name}", dest=dest, action="store_true", help="(default)" if default else "")
    me_group.add_argument(
        f"--no-{name}",
        dest=dest,
        action="store_false",
        help="(default)" if not default else "",
    )
    parser.set_defaults(**{dest: default})


@dataclass
class Args:
    """Data Class for storing CL args"""

    log_level: int = logging.INFO
    console_log: bool = True
    subreddits: str = "Showerthoughts|LifeProTips"
    max_vids_per_subreddit: int = 1
    max_comments: int = 3
    local_mode: bool = False
    operating_sys: str = "linux"


def parse_args() -> Args:
    """Parses CL args into a Args object
    Returns
    -------
    Args
        Args object containing all the
    """
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "-ll",
        "--log-level",
        default=logging.DEBUG,
        type=int,
        dest="log_level",
        help="The log level of logging",
    )
    arg_parser.add_argument(
        "-sr",
        "--subreddits",
        type=str,
        default="Showerthoughts|LifeProTips",
        dest="subreddits",
        help="The subreddits to scrape",
    )
    arg_parser.add_argument(
        "-mv",
        "--max-vids-per-subreddit",
        type=int,
        default=1,
        dest="max_vids_per_subreddit",
        help="The max number of videos to scrape per subreddit",
    )
    arg_parser.add_argument(
        "-mc",
        "--max-comments",
        type=int,
        default=3,
        dest="max_comments",
        help="The max number of comments to scrape per video",
    )
    arg_parser.add_argument(
        "-os",
        "--operating-system",
        type=str,
        default="linux",
        dest="operating_sys",
        help="The operating system to run the program on",
    )
    add_boolean_arg(arg_parser, "local-mode", "Run in local mode", default=False)
    add_boolean_arg(arg_parser, "console-log", "Log to console", default=True)
    return Args(**OrderedDict(vars(arg_parser.parse_args())))
