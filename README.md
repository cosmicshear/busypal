# BusyPal
Shows a busy indicator while a long process is running in the background. This way we can inform users that the terminal is still healthy and they just need to wait until the process finishes. 

*BusyPal* can be used for all sorts of ongoing processes that don't require anything to be written to *stdout/stderr*. The final status (success or failure) of the long-running operation will be reported at the end.

# Installation
pip install git+https://github.com/enourbakhsh/busypal

# Common Installation Issues
This package takes advantage of f-strings which were introduced with Python 3.6. In order python versions, an f-string will result in a syntax error.

In case `pip` gives you a `gcc` error while installing `psutil` in a `conda` environment, try `conda install psutil` before installing `SkyLink` ([source](https://github.com/ray-project/ray/issues/1340)).
