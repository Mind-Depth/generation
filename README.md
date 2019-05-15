# Generation

## Installation guide

#### 1 - Requirements

- python 3.7
- git
- A shell opened in the desired install location

#### *2 - Create a new directory (optional)*

As several ressources will be created, you may want a clean directory

```
mkdir panophobia
cd panophobia
```

#### 3 - Clone the different parts

```
git clone https://github.com/Mind-Depth/acquisition.git
git clone https://github.com/Mind-Depth/environnement_build.git
git clone https://github.com/Mind-Depth/generation.git
```

#### *4 - Start a virtualenv (optional)*

This will force dependencies to be installed next to the project

```
python -m venv .venv
.venv\Scripts\activate
```

#### 5 - Install the dependencies

```
pip install -r acquisition\requirements.txt
pip install -r acquisition\Middleware\py-test\requirements.txt
pip install -r generation\src\requirements.txt
```

#### 6 - You are ready to go !

You can start the program by executing this file

```
python generation\src\Launcher.py
```

#### *7 - Stop the virtualenv (optional)*

Not important if you want to close the shell anyway

```
.venv\Scripts\deactivate
```
