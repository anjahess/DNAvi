Installation
===================


Operating system
^^^^^^^^^^^^^^^^^^

Installation and testing of DNAvi has been performed for **Windows 10** and **Ubuntu 14.04.2 LTS**.

.. code-block::

    Suitable systems:
    Windows 10 Pro, Version 22H2        with Python 3.12.0 and Python 3.13
    Ubuntu 24.04.2 LTS                  with Python 3.13.5


Dependencies
^^^^^^^^^^^^^^^^^^

Please make sure you have installed **python => 3.13**. `Download Python <https://www.python.org/downloads/>`_.

.. code-block::

   python --version
   >> Python 3.13.5



Install through pip (recommended)
^^^^^^^^^^^^^^^^^^

You need python 3.12 or higher.

.. code-block::

    pip install dnavi



Test if the installation worked
""""""""""""""""""""""""""

.. code-block::

   dnavi --version

    Welcome to
          ____  _   _    _        _
         |  _ |  \ | |  / \__   _(_)
         | | | |  \| | / _ \ \ / / |
         | |_| | |\  |/ ___ \ V /| |
         |____/|_| \_/_/   \_\_/ |_|

    v0.0.0.1

Nice! You are ready to use DNAvi. Go to :doc:`/Quickstart` to try an example!



Step-by-step (alternative)
^^^^^^^^^^^^^^^^^^

First download the required packages ...

**Option 1:** Through pip.

* Note: the first time running DNAvi may take a bit longer due to matplotlib configuring

.. code-block::

    pip install numpy pandas seaborn scipy matplotlib imageio scikit-image werkzeug scikit-posthocs

**Option 2 (preferred):** Through conda. `Install Conda <https://www.anaconda.com/download/success/>`_.

* Tested on x64 Windows 10 Pro, Version 22H2 with Python 3.13.
* Tested on x64 Ubuntu 24.04.2 LTS, with Python 3.13.5
* Note: After installing and initiating conda, a restart is required.

.. code-block::

    conda create --name dnavi numpy pandas seaborn scipy matplotlib imageio werkzeug scikit-image -y
    conda activate dnavi
    conda install conda-forge::scikit-posthocs -y


Install DNAvi
""""""""""""""""""""""""""

Next, download the repository.

Use github CLI:

.. code-block::

    gh repo clone anjahess/DNAvi

Or wget:

.. code-block::

    wget https://github.com/anjahess/DNAvi/archive/refs/heads/main.zip

Unpack or move the DNAvi folder to your location of choice and you're ready to start.


Test if the installation worked
""""""""""""""""""""""""""

Go to DNAvi and call DNAvi.py to confirm it has been installed successfully:

.. code-block::

   cd /path/to/DNAvi
   python3 DNAvi.py --version

    Welcome to
          ____  _   _    _        _
         |  _ |  \ | |  / \__   _(_)
         | | | |  \| | / _ \ \ / / |
         | |_| | |\  |/ ___ \ V /| |
         |____/|_| \_/_/   \_\_/ |_|

    v0.0.0.1

Nice! You are ready to use DNAvi. Go to :doc:`/Quickstart` to try an example!