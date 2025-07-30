.. DNAvi documentation master file, created by
   sphinx-quickstart on Thu Jul 24 15:51:52 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Installation
===================



1. Download dependencies
^^^^^^^^^^^^^^^^^^

Please make sure you have installed **python => 3.12**. Next, download the required packages:

Through pip:

.. code-block::

       pip install argparse numpy pandas seaborn scipy matplotlib imageio scikit-image werkzeug

Through conda:

.. code-block::

    conda create --name dnavi argparse numpy pandas seaborn scipy matplotlib imageio werkzeug scikit-image
    conda activate dnavi


2. Install DNAvi
^^^^^^^^^^^^^^^^^^

Next, download the repository.

Use github CLI:

.. code-block::

    gh repo clone anjahess/DNAvi_light

Or wget:

.. code-block::

    wget https://github.com/anjahess/DNAvi_light/archive/refs/heads/main.zip

Unpack or move the DNAvi folder to your location of choice and you're ready to start.


3. Test if the installation worked
^^^^^^^^^^^^^^^^^^

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

   v0.1


Nice! You are ready to use DNAvi.