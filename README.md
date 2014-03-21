Python unit test made easy
==========================

Sublime Pyunit is a port of nvie's [vim-pyunit](https://github.com/nvie/vim-pyunit.git) for Sublime Text 3. Since I switched back to Sublime Text as my main editor, I missed a lot for this python unit test runner. Hope someone else will be as happy as I am with Sublime Pyunit. 

# Feature List #
-------------
- Run a single test (Ctrl + F10)
- Run all tests (Ctrl + Option + F10)
- Navigate to the error code with up and down arrow
- Switch between source code and test code in a side-by-side panel (Ctrl + F9)
- Three choice of test organization styles (details is [here](https://github.com/nvie/vim-pyunit.git)):
    * Nose test organizaiton style (default).
    * Side-by-side test organization style.
    * Hiearchical test organization style.

Installation Instruction:
-------------------------
Prerequisite: Install the test runner package [nose](https://pypi.python.org/pypi/nose/) from PyPI.

1. Automatic installation via Package Control (not yet)
2. Manual installation via github
Clone the git repository directly into the Packages folder
git clone https://github.com/dnatag/SublimePyunit.git SublimePyunit

TODO list:
----------
- Red/Green bar for indications of test pass or failure 
- Test code snippets
- Flexible layout. Right now, the layout is code window on the left and the test panel on the right, while the message panel on the bottom. 
- Work with test runners other than nose like py.test

License
-------

You can use this under Simplified BSD License:

Copyright (c) 2014, Yi Xie All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
