import os
import sys

if os.environ.get("PYTHONHASHSEED") != "0":                               # the order of sets must not differ between processes, or a
    os.environ["PYTHONHASHSEED"] = "0"                                     # run resumed or replayed in a new one is not the same run
    os.execv(sys.executable, [sys.executable, "-m", "cybertron2.engine", *sys.argv[1:]])

from cybertron2.engine.run import main  # noqa: E402

main()
