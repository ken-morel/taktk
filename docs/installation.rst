Installation
============

taktk can be installed easily using pip or by cloning the GitHub repository. Choose the method that
best suits your needs.

Installing from PyPI
--------------------

The simplest way to install taktk is using pip. Open your terminal or command prompt and run:

.. code-block:: bash

    pip install taktk

This will install the latest stable version of taktk from the Python Package Index (PyPI).

Installing from GitHub
----------------------

If you want the latest development version or wish to contribute to taktk, you can install it
directly from the GitHub repository:

1. Clone the repository:

   .. code-block:: bash

       git clone https://github.com/ken-morel/taktk.git

2. Navigate to the cloned directory:

   .. code-block:: bash

       cd taktk

3. Install the package:

   .. code-block:: bash

       pip install .

   Or, if you want to install it in editable mode for development:

   .. code-block:: bash

       pip install -e .

.. note:: Note


  If you do not want to clone the repository you could use:

  .. code-block:: bash

    pip install git+https://github.com/ken-morel/taktk

Requirements
------------

taktk requires Python 3.6 or later. It also depends on tkinter, which is usually included with
Python installations. If you're using a minimal Python installation, you may need to install tkinter
separately. Some taktk features also depend on ttkbootstrap themes.

Verifying the Installation
--------------------------

After installation, you can verify that taktk is installed correctly by running:

.. code-block:: python

  import taktk
  print(taktk.__version__)

This should print the version number of taktk without any errors.

Next Steps
----------

Once you have taktk installed, you're ready to start building your GUI applications! Check out the
:doc:`quickstart` guide to create your first taktk application.

For more detailed information about using taktk, refer to the :doc:`tutorials/index` and
:doc:`api/index` sections of this documentation.
