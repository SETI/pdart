from typing import Any, List, Optional, Tuple, Union

def ImagesToPics(
    filenames: List[str],
    directory: Optional[str] = None,
    replace: str = "all",
    proceed: bool = False,
    extension: str = "jpg",
    suffix: str = "",
    strip: Union[str, List[str]] = [],
    quality: int = 75,
    twobytes: bool = False,
    bands: Optional[Tuple[int, int]] = None,
    lines: Optional[Tuple[int, int]] = None,
    samples: Optional[Tuple[int, int]] = None,
    obj: Optional[int] = None,
    pointer: Union[str, List[str]] = ["IMAGE"],
    size: Optional[Tuple[int, int]] = None,
    scale: Optional[Tuple[float, float]] = (100.0, 100.0),
    frame: Optional[Tuple[int, int]] = None,
    wrap: bool = False,
    overlap: Optional[Tuple[float, float]] = (0.0, 0.0),
    gap_size: int = 1,
    gap_color: Union[str, Tuple[int, int, int]] = "white",
    hst: bool = False,
    valid: Optional[Tuple[int, int]] = None,
    limits: Optional[Tuple[int, int]] = None,
    percentiles: Optional[Tuple[int, int]] = None,
    trim: int = 0,
    trimzeros: bool = False,
    footprint: int = 0,
    histogram: bool = False,
    colormap: Optional[str] = None,
    below_color: Optional[str] = None,
    above_color: Optional[str] = None,
    invalid_color: Optional[str] = None,
    gamma: float = 1.0,
    tint: bool = False,
    display_upward: bool = False,
    display_downward: bool = False,
    rotate: Optional[str] = None,
    filter: Optional[str] = "NONE",
    zebra: bool = False,
    reuse: Optional[Tuple[Any, bool, Any]] = None,
) -> Any: ...
