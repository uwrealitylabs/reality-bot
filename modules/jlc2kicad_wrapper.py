import argparse
import subprocess
import shutil
import zipfile
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class JLC2KiCadArguments:
    JLCPCB_parts: list[str]
    """List of JLCPCB part # from the components you want to create"""
    dir: Path = None
    """Base directory for output library files"""
    no_footprint: bool = None
    """Set to true if you do not want to create the footprint"""
    no_symbol: bool = None
    """Set to true if you do not want to create the symbol"""
    symbol_lib: str = None
    """Set symbol library name, default is 'default_lib'"""
    symbol_lib_dir: str = None
    """Set symbol library path, default is 'symbol' (relative to OUTPUT_DIR)"""
    footprint_lib: str = None
    """Set footprint library name, default is 'footprint'"""
    models: list[Literal["STEP", "WRL"]] = None
    """
    Select the 3D model you want to use. Default is STEP. If both are selected, only the STEP model will be added to 
    the footprint (the WRL model will still be generated alongside the STEP model). If you do    
    not want any model to be generated, set to empty list.
    """
    model_dir: Path = None
    """Set directory for storing 3d models, default is 'packages3d' (relative to FOOTPRINT_LIB)"""
    skip_existing: bool = None
    """Set to true if you want do not want to replace already existing footprints and symbols"""
    model_base_variable: str = None
    """
    Specify the base path of the 3D model using a path variable. If the specified variable starts with '$' it is used 
    'as-is', otherwise it is encapsulated: $(MODEL_BASE_VARIABLE)
    """
    logging_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = None
    """
    Set logging level. If DEBUG is used, the debug logs are only written in the log file if the option 'log_file' is 
    set
    """
    log_file: Path = None
    """Set if you want logs to be written in a file."""


def _run_jlc2kicad_cmd(args: JLC2KiCadArguments) -> bool:
    """
    Runs JLC2KiCadLib with given arguments

    :returns: Whether JLC2KiCadLib ran without error
    """
    subprocess_args: list = ["JLC2KiCadLib"]
    subprocess_args.extend(args.JLCPCB_parts)
    if args.dir:
        subprocess_args.extend(["-dir", args.dir])
    # TODO: use other arguments

    result = subprocess.run(subprocess_args, check=True, capture_output=True)
    return result.returncode == 0


def jlc_to_kicad(parts: list[str], output_dir: Path) -> bool:
    """
    Generates a component library for the given part numbers, writes them to the given output directory

    :returns: Whether component library was successfully generated
    """
    if output_dir.exists():
        shutil.rmtree(output_dir)
    return _run_jlc2kicad_cmd(JLC2KiCadArguments(
        JLCPCB_parts=parts,
        dir=output_dir
    ))


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", help="Where to write component library, defaults to './output'", type=Path)
    args = parser.parse_args()

    j2k_args = JLC2KiCadArguments(
        JLCPCB_parts=["C1337258"],
        dir=args.dir if args.dir else Path("output")
    )
    print(_run_jlc2kicad_cmd(j2k_args))


if __name__ == "__main__":
    _main()

