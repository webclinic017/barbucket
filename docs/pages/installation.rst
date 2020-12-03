Installation
============

Requirements
------------
    * Python >= 3.5
    * pipenv / pip

Download
--------
In your terminal, move to the target directory, then clone the repository to your local drive

.. code-block:: console

    git clone https://github.com/croidzen/barbucket ./barbucket

Alternatively, you can `download <https://github.com/croidzen/barbucket/archive/master.zip>`_ the whole project from the project page on github

Create virtual Python environment
---------------------------------
Open the project directory (containing the Pipfile) and create the virtual Python environment

.. code-block:: console

    pipenv shell
    pipenv install

Alternatively, you could use pip and venv

.. code-block:: console

    python3 -m venv barbucket-env
    source barbucket-env/bin/activate
    pip install -r requirements.txt

Check installation
------------------
Check if the installation was successfull

.. code-block:: console

    python barbucket --help
