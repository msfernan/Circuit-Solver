# Circuit-Solver
Program that solves circuits that can be collapsed in series and parallel.

Project Readme file

In order to run this project install Python 2.76. Install an appropriate editor such as IDLE, KomodoEdit, Sublime etc.

Save the Project file and click run. The screen will appear.

The modules needed to be import into this Project are 
from Tkinter import *
import copy
import tkSimpleDialog
import tkMessageBox


High Level Description of the Project

The project is a basic circuit solver. 
The project can solve for circuits with a single voltage source.
They can solve for the net resistance and current across circuits that can be collapsed in series and parallel into a single net resistance.
i.e. where the formulae Rseries=R1+R2+…Rn and
1/Rparallel=1/R1 +1/R2 +…1/Rn.
The project cannot solve Bridge circuits.
