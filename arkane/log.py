#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 16:01:33 2019

@author: mark
"""
import os.path
import logging
import shutil

from rmgpy.qm.qmdata import QMData
from rmgpy.qm.symmetry import PointGroupCalculator

class Log(object):
    """
    Represent a general log file.
    The attribute `path` refers to the location on disk of the log file of interest.
    A method is provided to determine whether it is a Gaussian, Molpro, or QChem type.
    """
    def __init__(self, path):
        self.path = path

    def getNumberOfAtoms(self):
        """
        Return the number of atoms in the molecular configuration used in
        the MolPro log file.
        """
        raise NotImplementedError("loadGeometry is not implemented for the Log class")

    def loadForceConstantMatrix(self):
        """
        Return the force constant matrix (in Cartesian coordinates) from the
        QChem log file. If multiple such matrices are identified,
        only the last is returned. The units of the returned force constants
        are J/m^2. If no force constant matrix can be found in the log file,
        ``None`` is returned.
        """
        raise NotImplementedError("loadGeometry is not implemented for the Log class")

    def loadGeometry(self):
        """
        Return the optimum geometry of the molecular configuration from the
        log file. If multiple such geometries are identified, only the
        last is returned.
        """
        raise NotImplementedError("loadGeometry is not implemented for the Log class")

    def loadConformer(self, symmetry=None, spinMultiplicity=0, opticalIsomers=None, label=''):
        """
        Load the molecular degree of freedom data from an output file created as the result of a
        QChem "Freq" calculation. As QChem's guess of the external symmetry number is not always correct,
        you can use the `symmetry` parameter to substitute your own value;
        if not provided, the value in the QChem output file will be adopted.
        """
        raise NotImplementedError("loadGeometry is not implemented for the Log class")

    def loadEnergy(self, frequencyScaleFactor=1.):
        """
        Load the energy in J/mol from a QChem log file. Only the last energy
        in the file is returned. The zero-point energy is *not* included in
        the returned value.
        """
        raise NotImplementedError("loadGeometry is not implemented for the Log class")

    def loadZeroPointEnergy(self,frequencyScaleFactor=1.):
        """
        Load the unscaled zero-point energy in J/mol from a QChem output file.
        """
        raise NotImplementedError("loadGeometry is not implemented for the Log class")

    def loadScanEnergies(self):
        """
        Extract the optimized energies in J/mol from a QChem log file, e.g. the
        result of a QChem "PES Scan" quantum chemistry calculation.
        """
        raise NotImplementedError("loadGeometry is not implemented for the Log class")

    def loadNegativeFrequency(self):
        """
        Return the imaginary frequency from a transition state frequency
        calculation in cm^-1.
        """
        raise NotImplementedError("loadGeometry is not implemented for the Log class")

    def get_optical_isomers_and_symmetry_number(self):
        """
        This method uses the symmetry package from RMG's QM module
        and returns a tuple where the first element is the number
        of optical isomers and the second element is the symmetry number.
        """
        coordinates, atom_numbers, mass = self.loadGeometry()
        unique_id = '0'  # Just some name that the SYMMETRY code gives to one of its jobs
        scr_dir = os.path.join(self.path, str('scratch'))  # Scratch directory that the SYMMETRY code writes its files in
        if not os.path.exists(scr_dir):
            os.makedirs(scr_dir)
        try:
            qmdata = QMData(
                groundStateDegeneracy=1,  # Only needed to check if valid QMData
                numberOfAtoms=len(atom_numbers),
                atomicNumbers=atom_numbers,
                atomCoords=(coordinates, str('angstrom')),
                energy=(0.0, str('kcal/mol'))  # Only needed to avoid error
            )
            settings = type(str(''), (), dict(symmetryPath=str('symmetry'), scratchDirectory=scr_dir))()  # Creates anonymous class
            pgc = PointGroupCalculator(settings, unique_id, qmdata)
            pg = pgc.calculate()
            if pg is not None:
                optical_isomers = 2 if pg.chiral else 1
                symmetry = pg.symmetryNumber
                logging.debug("Symmetry algorithm found {0} optical isomers and a symmetry number of {1}".format(optical_isomers,symmetry))
            else:
                logging.warning("Symmetry algorithm errored when computing optical isomers. Setting to 1")
                optical_isomers = 1
                symmetry = 1
            return optical_isomers, symmetry
        finally:
            shutil.rmtree(scr_dir)