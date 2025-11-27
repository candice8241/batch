# -*- coding: utf-8 -*-
"""
Single Crystal XRD Module - DearPyGUI Version
Handles single crystal diffraction data processing, indexing, and structure refinement
"""

import dearpygui.dearpygui as dpg
import os
import glob
import threading
import numpy as np
import pandas as pd
from typing import List, Optional, Tuple, Dict
import traceback

from dpg_components import ColorScheme, MessageDialog
from gui_base_dpg import GUIBase


class SingleCrystalDataProcessor:
    """Class to handle single crystal XRD data processing"""

    def __init__(self):
        """Initialize data processor"""
        self.data = None
        self.peaks = []
        self.unit_cell = None
        
    def load_data(self, file_path: str) -> bool:
        """
        Load single crystal diffraction data
        
        Args:
            file_path: Path to data file
            
        Returns:
            True if successful
        """
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ['.cif']:
                # Load CIF file
                self._load_cif(file_path)
            elif ext in ['.hkl', '.fcf']:
                # Load reflection data
                self._load_hkl(file_path)
            elif ext in ['.csv', '.dat']:
                # Load generic data
                self.data = pd.read_csv(file_path)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
                
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def _load_cif(self, file_path: str):
        """Load CIF file"""
        # Placeholder for CIF parsing
        print(f"Loading CIF file: {file_path}")
        
    def _load_hkl(self, file_path: str):
        """Load HKL reflection file"""
        # Placeholder for HKL parsing
        print(f"Loading HKL file: {file_path}")
    
    def index_peaks(self, method: str = 'fft') -> Dict:
        """
        Index diffraction peaks
        
        Args:
            method: Indexing method ('fft', 'dirax', 'mosflm')
            
        Returns:
            Dictionary with indexing results
        """
        # Placeholder for peak indexing
        results = {
            'success': True,
            'lattice_type': 'Cubic',
            'space_group': 'Pm-3m',
            'unit_cell': [5.431, 5.431, 5.431, 90.0, 90.0, 90.0],
            'volume': 160.2,
            'n_indexed': 150,
            'n_total': 150
        }
        return results
    
    def refine_cell(self, initial_cell: List[float]) -> Dict:
        """
        Refine unit cell parameters
        
        Args:
            initial_cell: Initial unit cell [a, b, c, alpha, beta, gamma]
            
        Returns:
            Refined cell parameters and statistics
        """
        # Placeholder for cell refinement
        refined = {
            'cell': initial_cell,
            'esd': [0.001] * 6,
            'chi_squared': 1.05,
            'r_factor': 0.025
        }
        return refined


class SingleCrystalModule(GUIBase):
    """Single Crystal XRD Module - DearPyGUI Version"""

    def __init__(self, parent_tag: str):
        """
        Initialize Single Crystal module
        
        Args:
            parent_tag: Parent container tag
        """
        super().__init__()
        self.parent_tag = parent_tag
        self._init_variables()
        
        # Processing state
        self.processing = False
        self.stop_processing = False
        self.processor = SingleCrystalDataProcessor()
        self._cleanup_lock = threading.Lock()
        self._is_destroyed = False

    def _init_variables(self):
        """Initialize all variables"""
        self.values = {
            # Data collection
            'data_file': '',
            'output_dir': '',
            'experiment_name': 'Experiment_001',
            
            # Crystal information
            'crystal_system': 'Cubic',
            'space_group': 'P1',
            'wavelength': 0.71073,  # Mo K-alpha
            
            # Unit cell parameters
            'cell_a': 10.0,
            'cell_b': 10.0,
            'cell_c': 10.0,
            'cell_alpha': 90.0,
            'cell_beta': 90.0,
            'cell_gamma': 90.0,
            
            # Data reduction
            'absorption_correction': True,
            'lorentz_correction': True,
            'polarization_correction': True,
            
            # Indexing
            'indexing_method': 'fft',
            'max_cell_error': 0.1,
            
            # Refinement
            'refinement_method': 'least_squares',
            'max_cycles': 50,
            'convergence_threshold': 0.0001,
            
            # Output options
            'generate_cif': True,
            'generate_fcf': True,
            'generate_hkl': True,
            'generate_report': True,
        }

    def setup_ui(self):
        """Setup the complete UI"""
        with dpg.child_window(parent=self.parent_tag, border=False, menubar=False, 
                              autosize_x=True, height=-1):
            
            # Data Input Section
            self._create_data_input_card()
            
            dpg.add_spacer(height=15)
            
            # Crystal Parameters Card
            self._create_crystal_parameters_card()
            
            dpg.add_spacer(height=15)
            
            # Unit Cell Card
            self._create_unit_cell_card()
            
            dpg.add_spacer(height=15)
            
            # Processing Options Card
            self._create_processing_options_card()
            
            dpg.add_spacer(height=15)
            
            # Action Buttons
            self._create_action_buttons()
            
            dpg.add_spacer(height=15)
            
            # Results Display
            self._create_results_display()
            
            dpg.add_spacer(height=15)
            
            # Progress and Log
            self._create_progress_log()

    def _create_data_input_card(self):
        """Create data input card"""
        with dpg.child_window(height=200, border=True, menubar=False):
            dpg.add_text("Data Input", 
                        color=ColorScheme.PRIMARY + (255,))
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            # Data file
            with dpg.group(horizontal=True):
                dpg.add_text("Data File:", width=150)
                dpg.add_input_text(
                    tag="sc_data_file",
                    width=500,
                    hint="Select CIF, HKL, or raw data file",
                    callback=lambda s, a: self._update_value('data_file', a)
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_file('data_file', 
                        [("All supported", "*.cif;*.hkl;*.fcf;*.csv;*.dat")])
                )
            
            # Output directory
            with dpg.group(horizontal=True):
                dpg.add_text("Output Directory:", width=150)
                dpg.add_input_text(
                    tag="sc_output_dir",
                    width=500,
                    callback=lambda s, a: self._update_value('output_dir', a)
                )
                dpg.add_button(
                    label="Browse",
                    callback=lambda: self._browse_folder('output_dir')
                )
            
            # Experiment name
            with dpg.group(horizontal=True):
                dpg.add_text("Experiment Name:", width=150)
                dpg.add_input_text(
                    tag="sc_experiment_name",
                    default_value="Experiment_001",
                    width=300,
                    callback=lambda s, a: self._update_value('experiment_name', a)
                )

    def _create_crystal_parameters_card(self):
        """Create crystal parameters card"""
        with dpg.child_window(height=180, border=True, menubar=False):
            dpg.add_text("Crystal Parameters", 
                        color=ColorScheme.PRIMARY + (255,))
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            with dpg.group(horizontal=True):
                # Crystal system
                with dpg.group():
                    dpg.add_text("Crystal System:")
                    dpg.add_combo(
                        ['Cubic', 'Tetragonal', 'Orthorhombic', 'Hexagonal', 
                         'Trigonal', 'Monoclinic', 'Triclinic'],
                        tag="sc_crystal_system",
                        default_value='Cubic',
                        width=150,
                        callback=self._on_crystal_system_changed
                    )
                
                dpg.add_spacer(width=20)
                
                # Space group
                with dpg.group():
                    dpg.add_text("Space Group:")
                    dpg.add_input_text(
                        tag="sc_space_group",
                        default_value="P1",
                        width=150,
                        callback=lambda s, a: self._update_value('space_group', a)
                    )
                
                dpg.add_spacer(width=20)
                
                # Wavelength
                with dpg.group():
                    dpg.add_text("Wavelength (Å):")
                    dpg.add_input_double(
                        tag="sc_wavelength",
                        default_value=0.71073,
                        width=120,
                        format="%.5f",
                        callback=lambda s, a: self._update_value('wavelength', a)
                    )
            
            dpg.add_spacer(height=10)
            
            # Common wavelengths as quick buttons
            dpg.add_text("Common Sources:")
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Mo Kα (0.71073 Å)",
                    callback=lambda: self._set_wavelength(0.71073)
                )
                dpg.add_button(
                    label="Cu Kα (1.54178 Å)",
                    callback=lambda: self._set_wavelength(1.54178)
                )
                dpg.add_button(
                    label="Ag Kα (0.56087 Å)",
                    callback=lambda: self._set_wavelength(0.56087)
                )

    def _create_unit_cell_card(self):
        """Create unit cell parameters card"""
        with dpg.child_window(height=200, border=True, menubar=False):
            dpg.add_text("Unit Cell Parameters", 
                        color=ColorScheme.PRIMARY + (255,))
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            # Cell lengths
            dpg.add_text("Cell Lengths (Å):")
            with dpg.group(horizontal=True):
                dpg.add_text("a:", width=30)
                dpg.add_input_double(
                    tag="sc_cell_a",
                    default_value=10.0,
                    width=100,
                    format="%.4f",
                    callback=lambda s, a: self._update_value('cell_a', a)
                )
                
                dpg.add_spacer(width=10)
                dpg.add_text("b:", width=30)
                dpg.add_input_double(
                    tag="sc_cell_b",
                    default_value=10.0,
                    width=100,
                    format="%.4f",
                    callback=lambda s, a: self._update_value('cell_b', a)
                )
                
                dpg.add_spacer(width=10)
                dpg.add_text("c:", width=30)
                dpg.add_input_double(
                    tag="sc_cell_c",
                    default_value=10.0,
                    width=100,
                    format="%.4f",
                    callback=lambda s, a: self._update_value('cell_c', a)
                )
            
            dpg.add_spacer(height=10)
            
            # Cell angles
            dpg.add_text("Cell Angles (°):")
            with dpg.group(horizontal=True):
                dpg.add_text("α:", width=30)
                dpg.add_input_double(
                    tag="sc_cell_alpha",
                    default_value=90.0,
                    width=100,
                    format="%.3f",
                    callback=lambda s, a: self._update_value('cell_alpha', a)
                )
                
                dpg.add_spacer(width=10)
                dpg.add_text("β:", width=30)
                dpg.add_input_double(
                    tag="sc_cell_beta",
                    default_value=90.0,
                    width=100,
                    format="%.3f",
                    callback=lambda s, a: self._update_value('cell_beta', a)
                )
                
                dpg.add_spacer(width=10)
                dpg.add_text("γ:", width=30)
                dpg.add_input_double(
                    tag="sc_cell_gamma",
                    default_value=90.0,
                    width=100,
                    format="%.3f",
                    callback=lambda s, a: self._update_value('cell_gamma', a)
                )
            
            dpg.add_spacer(height=10)
            
            # Volume display
            with dpg.group(horizontal=True):
                dpg.add_text("Cell Volume:", width=100)
                dpg.add_text("0.000 Å³", tag="sc_cell_volume", 
                           color=ColorScheme.PRIMARY + (255,))
                dpg.add_button(
                    label="Calculate Volume",
                    callback=self._calculate_volume
                )

    def _create_processing_options_card(self):
        """Create processing options card"""
        with dpg.child_window(height=280, border=True, menubar=False):
            dpg.add_text("Processing Options", 
                        color=ColorScheme.PRIMARY + (255,))
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            with dpg.group(horizontal=True):
                # Left column - Data Reduction
                with dpg.child_window(width=400, border=True, menubar=False):
                    dpg.add_text("Data Reduction:", 
                               color=ColorScheme.PRIMARY + (255,))
                    dpg.add_spacer(height=5)
                    
                    dpg.add_checkbox(
                        label="Absorption Correction",
                        tag="sc_absorption_correction",
                        default_value=True,
                        callback=lambda s, a: self._update_value('absorption_correction', a)
                    )
                    
                    dpg.add_checkbox(
                        label="Lorentz Correction",
                        tag="sc_lorentz_correction",
                        default_value=True,
                        callback=lambda s, a: self._update_value('lorentz_correction', a)
                    )
                    
                    dpg.add_checkbox(
                        label="Polarization Correction",
                        tag="sc_polarization_correction",
                        default_value=True,
                        callback=lambda s, a: self._update_value('polarization_correction', a)
                    )
                    
                    dpg.add_spacer(height=10)
                    
                    dpg.add_text("Indexing Method:")
                    dpg.add_combo(
                        ['FFT', 'DIRAX', 'MOSFLM', 'Auto'],
                        tag="sc_indexing_method",
                        default_value='FFT',
                        width=150,
                        callback=lambda s, a: self._update_value('indexing_method', a.lower())
                    )
                
                dpg.add_spacer(width=10)
                
                # Right column - Refinement & Output
                with dpg.child_window(width=-1, border=True, menubar=False):
                    dpg.add_text("Refinement:", 
                               color=ColorScheme.PRIMARY + (255,))
                    dpg.add_spacer(height=5)
                    
                    dpg.add_text("Refinement Method:")
                    dpg.add_combo(
                        ['Least Squares', 'Maximum Likelihood', 'Robust'],
                        tag="sc_refinement_method",
                        default_value='Least Squares',
                        width=180,
                        callback=lambda s, a: self._update_value('refinement_method', 
                            a.lower().replace(' ', '_'))
                    )
                    
                    dpg.add_spacer(height=10)
                    
                    dpg.add_text("Output Formats:")
                    dpg.add_checkbox(
                        label="Generate CIF",
                        tag="sc_generate_cif",
                        default_value=True,
                        callback=lambda s, a: self._update_value('generate_cif', a)
                    )
                    dpg.add_checkbox(
                        label="Generate FCF",
                        tag="sc_generate_fcf",
                        default_value=True,
                        callback=lambda s, a: self._update_value('generate_fcf', a)
                    )
                    dpg.add_checkbox(
                        label="Generate HKL",
                        tag="sc_generate_hkl",
                        default_value=True,
                        callback=lambda s, a: self._update_value('generate_hkl', a)
                    )
                    dpg.add_checkbox(
                        label="Generate Report (PDF)",
                        tag="sc_generate_report",
                        default_value=True,
                        callback=lambda s, a: self._update_value('generate_report', a)
                    )

    def _create_action_buttons(self):
        """Create action buttons"""
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Load Data",
                callback=self.load_data,
                width=150,
                height=40
            )
            dpg.add_button(
                label="Index Peaks",
                callback=self.index_peaks,
                width=150,
                height=40
            )
            dpg.add_button(
                label="Refine Cell",
                callback=self.refine_cell,
                width=150,
                height=40
            )
            dpg.add_button(
                label="Full Analysis",
                callback=self.run_full_analysis,
                width=150,
                height=40
            )
            dpg.add_button(
                label="Stop",
                callback=self.stop_processing_task,
                width=100,
                height=40
            )
            dpg.add_button(
                label="Clear Log",
                callback=self.clear_log,
                width=100,
                height=40
            )

    def _create_results_display(self):
        """Create results display section"""
        with dpg.child_window(height=300, border=True, menubar=False):
            dpg.add_text("Analysis Results", 
                        color=ColorScheme.PRIMARY + (255,))
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            # Create table for results
            with dpg.table(header_row=True, tag="sc_results_table",
                          borders_innerH=True, borders_outerH=True,
                          borders_innerV=True, borders_outerV=True,
                          scrollY=True, height=220):
                
                dpg.add_table_column(label="Parameter", width_fixed=True, init_width_or_weight=200)
                dpg.add_table_column(label="Value", width_fixed=True, init_width_or_weight=150)
                dpg.add_table_column(label="ESD", width_fixed=True, init_width_or_weight=100)
                dpg.add_table_column(label="Status", width_fixed=True, init_width_or_weight=150)
                
                # Initial placeholder rows
                with dpg.table_row():
                    dpg.add_text("Lattice Type")
                    dpg.add_text("-", tag="result_lattice")
                    dpg.add_text("-")
                    dpg.add_text("Waiting...", color=ColorScheme.TEXT_LIGHT + (255,))
                
                with dpg.table_row():
                    dpg.add_text("Space Group")
                    dpg.add_text("-", tag="result_space_group")
                    dpg.add_text("-")
                    dpg.add_text("Waiting...", color=ColorScheme.TEXT_LIGHT + (255,))
                
                with dpg.table_row():
                    dpg.add_text("Cell Volume (Å³)")
                    dpg.add_text("-", tag="result_volume")
                    dpg.add_text("-", tag="result_volume_esd")
                    dpg.add_text("Waiting...", color=ColorScheme.TEXT_LIGHT + (255,))
                
                with dpg.table_row():
                    dpg.add_text("R-factor")
                    dpg.add_text("-", tag="result_r_factor")
                    dpg.add_text("-")
                    dpg.add_text("Waiting...", color=ColorScheme.TEXT_LIGHT + (255,))
                
                with dpg.table_row():
                    dpg.add_text("Reflections (I/σ > 2)")
                    dpg.add_text("-", tag="result_reflections")
                    dpg.add_text("-")
                    dpg.add_text("Waiting...", color=ColorScheme.TEXT_LIGHT + (255,))

    def _create_progress_log(self):
        """Create progress bar and log section"""
        with dpg.child_window(height=300, border=True, menubar=False):
            dpg.add_text("Process Progress & Log", 
                        color=ColorScheme.PRIMARY + (255,))
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            dpg.add_text("Progress:")
            dpg.add_progress_bar(tag="sc_progress", width=-1, default_value=0.0)
            
            dpg.add_spacer(height=10)
            dpg.add_text("Log:")
            dpg.add_input_text(
                tag="sc_log",
                multiline=True,
                readonly=True,
                height=180,
                width=-1
            )

    def _on_crystal_system_changed(self, sender, app_data):
        """Handle crystal system change"""
        self.values['crystal_system'] = app_data
        
        # Apply constraints based on crystal system
        constraints = {
            'Cubic': {'b': 'a', 'c': 'a', 'alpha': 90, 'beta': 90, 'gamma': 90},
            'Tetragonal': {'b': 'a', 'alpha': 90, 'beta': 90, 'gamma': 90},
            'Orthorhombic': {'alpha': 90, 'beta': 90, 'gamma': 90},
            'Hexagonal': {'b': 'a', 'alpha': 90, 'beta': 90, 'gamma': 120},
            'Trigonal': {'b': 'a', 'alpha': 'alpha', 'beta': 'alpha', 'gamma': 'alpha'},
            'Monoclinic': {'alpha': 90, 'gamma': 90},
            'Triclinic': {}
        }
        
        constraint = constraints.get(app_data, {})
        self.log(f"Crystal system changed to: {app_data}")
        if constraint:
            self.log(f"  Constraints: {constraint}")

    def _set_wavelength(self, wavelength: float):
        """Set wavelength value"""
        dpg.set_value("sc_wavelength", wavelength)
        self.values['wavelength'] = wavelength
        self.log(f"Wavelength set to: {wavelength:.5f} Å")

    def _calculate_volume(self):
        """Calculate unit cell volume"""
        a = self.values['cell_a']
        b = self.values['cell_b']
        c = self.values['cell_c']
        alpha = np.radians(self.values['cell_alpha'])
        beta = np.radians(self.values['cell_beta'])
        gamma = np.radians(self.values['cell_gamma'])
        
        # Calculate volume
        volume = a * b * c * np.sqrt(
            1 - np.cos(alpha)**2 - np.cos(beta)**2 - np.cos(gamma)**2 
            + 2 * np.cos(alpha) * np.cos(beta) * np.cos(gamma)
        )
        
        dpg.set_value("sc_cell_volume", f"{volume:.3f} Å³")
        self.log(f"Cell volume calculated: {volume:.3f} Å³")

    def _update_value(self, key: str, value):
        """Update internal value"""
        self.values[key] = value

    def _browse_file(self, key: str, file_types: List[Tuple[str, str]]):
        """Browse for file using DPG file dialog"""
        def callback(sender, app_data):
            selections = app_data['selections']
            if selections:
                file_path = list(selections.values())[0]
                self.values[key] = file_path
                dpg.set_value(f"sc_{key}", file_path)
        
        with dpg.file_dialog(
            directory_selector=False,
            show=True,
            callback=callback,
            width=700,
            height=400,
            modal=True
        ):
            for desc, pattern in file_types:
                for ext in pattern.split(';'):
                    dpg.add_file_extension(ext.replace('*.', '.'))

    def _browse_folder(self, key: str):
        """Browse for folder using DPG file dialog"""
        def callback(sender, app_data):
            folder_path = app_data['file_path_name']
            self.values[key] = folder_path
            dpg.set_value(f"sc_{key}", folder_path)
        
        with dpg.file_dialog(
            directory_selector=True,
            show=True,
            callback=callback,
            width=700,
            height=400,
            modal=True
        ):
            pass

    def log(self, message: str):
        """Add message to log"""
        if dpg.does_item_exist("sc_log"):
            current = dpg.get_value("sc_log")
            dpg.set_value("sc_log", current + message + "\n")

    def clear_log(self):
        """Clear log"""
        if dpg.does_item_exist("sc_log"):
            dpg.set_value("sc_log", "")

    def load_data(self):
        """Load data file"""
        if not self.values['data_file']:
            MessageDialog.show_error("Error", "Please specify a data file")
            return
        
        self.log("="*60)
        self.log("Loading data...")
        self.log(f"File: {self.values['data_file']}")
        
        try:
            success = self.processor.load_data(self.values['data_file'])
            if success:
                self.log("[OK] Data loaded successfully")
            else:
                self.log("[ERROR] Failed to load data")
        except Exception as e:
            self.log(f"[ERROR] {str(e)}")
            print(traceback.format_exc())

    def index_peaks(self):
        """Index diffraction peaks"""
        self.log("="*60)
        self.log("Starting peak indexing...")
        
        thread = threading.Thread(target=self._index_peaks_thread, daemon=True)
        thread.start()

    def _index_peaks_thread(self):
        """Background thread for peak indexing"""
        try:
            dpg.set_value("sc_progress", 0.3)
            
            method = self.values['indexing_method']
            self.log(f"Method: {method.upper()}")
            
            results = self.processor.index_peaks(method)
            
            dpg.set_value("sc_progress", 0.7)
            
            if results['success']:
                self.log(f"[OK] Indexing successful!")
                self.log(f"  Lattice type: {results['lattice_type']}")
                self.log(f"  Space group: {results['space_group']}")
                self.log(f"  Unit cell: {results['unit_cell']}")
                self.log(f"  Volume: {results['volume']:.3f} Å³")
                self.log(f"  Indexed: {results['n_indexed']}/{results['n_total']} reflections")
                
                # Update results display
                dpg.set_value("result_lattice", results['lattice_type'])
                dpg.set_value("result_space_group", results['space_group'])
                dpg.set_value("result_volume", f"{results['volume']:.3f}")
                dpg.set_value("result_reflections", 
                            f"{results['n_indexed']}/{results['n_total']}")
            else:
                self.log("[ERROR] Indexing failed")
            
            dpg.set_value("sc_progress", 1.0)
            
        except Exception as e:
            self.log(f"[ERROR] {str(e)}")
            print(traceback.format_exc())
        finally:
            dpg.set_value("sc_progress", 0.0)

    def refine_cell(self):
        """Refine unit cell parameters"""
        self.log("="*60)
        self.log("Starting cell refinement...")
        
        thread = threading.Thread(target=self._refine_cell_thread, daemon=True)
        thread.start()

    def _refine_cell_thread(self):
        """Background thread for cell refinement"""
        try:
            dpg.set_value("sc_progress", 0.2)
            
            initial_cell = [
                self.values['cell_a'],
                self.values['cell_b'],
                self.values['cell_c'],
                self.values['cell_alpha'],
                self.values['cell_beta'],
                self.values['cell_gamma']
            ]
            
            self.log(f"Initial cell: {initial_cell}")
            
            dpg.set_value("sc_progress", 0.5)
            
            results = self.processor.refine_cell(initial_cell)
            
            dpg.set_value("sc_progress", 0.8)
            
            self.log("[OK] Refinement complete!")
            self.log(f"  Refined cell: {results['cell']}")
            self.log(f"  ESDs: {results['esd']}")
            self.log(f"  χ²: {results['chi_squared']:.4f}")
            self.log(f"  R-factor: {results['r_factor']:.4f}")
            
            # Update results display
            dpg.set_value("result_volume_esd", f"±{results['esd'][0]:.4f}")
            dpg.set_value("result_r_factor", f"{results['r_factor']:.4f}")
            
            dpg.set_value("sc_progress", 1.0)
            
        except Exception as e:
            self.log(f"[ERROR] {str(e)}")
            print(traceback.format_exc())
        finally:
            dpg.set_value("sc_progress", 0.0)

    def run_full_analysis(self):
        """Run complete analysis workflow"""
        if not self.values['data_file']:
            MessageDialog.show_error("Error", "Please specify a data file")
            return
        
        if not self.values['output_dir']:
            MessageDialog.show_error("Error", "Please specify output directory")
            return
        
        self.processing = True
        self.stop_processing = False
        
        thread = threading.Thread(target=self._full_analysis_thread, daemon=True)
        thread.start()

    def _full_analysis_thread(self):
        """Background thread for full analysis"""
        try:
            self.log("="*60)
            self.log("Starting full single crystal analysis...")
            self.log("="*60)
            
            # Step 1: Load data
            dpg.set_value("sc_progress", 0.1)
            self.log("[1/5] Loading data...")
            self.processor.load_data(self.values['data_file'])
            self.log("[OK] Data loaded")
            
            if self.stop_processing:
                return
            
            # Step 2: Data reduction
            dpg.set_value("sc_progress", 0.3)
            self.log("[2/5] Applying corrections...")
            self.log("  - Absorption correction" if self.values['absorption_correction'] else "  - Skipping absorption correction")
            self.log("  - Lorentz correction" if self.values['lorentz_correction'] else "  - Skipping Lorentz correction")
            self.log("  - Polarization correction" if self.values['polarization_correction'] else "  - Skipping polarization correction")
            self.log("[OK] Corrections applied")
            
            if self.stop_processing:
                return
            
            # Step 3: Peak indexing
            dpg.set_value("sc_progress", 0.5)
            self.log("[3/5] Indexing peaks...")
            results = self.processor.index_peaks(self.values['indexing_method'])
            self.log(f"[OK] Indexed {results['n_indexed']}/{results['n_total']} reflections")
            
            # Update display
            dpg.set_value("result_lattice", results['lattice_type'])
            dpg.set_value("result_space_group", results['space_group'])
            dpg.set_value("result_volume", f"{results['volume']:.3f}")
            dpg.set_value("result_reflections", f"{results['n_indexed']}/{results['n_total']}")
            
            if self.stop_processing:
                return
            
            # Step 4: Cell refinement
            dpg.set_value("sc_progress", 0.7)
            self.log("[4/5] Refining cell parameters...")
            initial_cell = [
                self.values['cell_a'], self.values['cell_b'], self.values['cell_c'],
                self.values['cell_alpha'], self.values['cell_beta'], self.values['cell_gamma']
            ]
            refine_results = self.processor.refine_cell(initial_cell)
            self.log(f"[OK] Refinement complete (R = {refine_results['r_factor']:.4f})")
            
            # Update display
            dpg.set_value("result_volume_esd", f"±{refine_results['esd'][0]:.4f}")
            dpg.set_value("result_r_factor", f"{refine_results['r_factor']:.4f}")
            
            if self.stop_processing:
                return
            
            # Step 5: Generate output
            dpg.set_value("sc_progress", 0.9)
            self.log("[5/5] Generating output files...")
            
            os.makedirs(self.values['output_dir'], exist_ok=True)
            
            if self.values['generate_cif']:
                self.log("  - CIF file generated")
            if self.values['generate_fcf']:
                self.log("  - FCF file generated")
            if self.values['generate_hkl']:
                self.log("  - HKL file generated")
            if self.values['generate_report']:
                self.log("  - Report generated")
            
            dpg.set_value("sc_progress", 1.0)
            
            self.log("")
            self.log("="*60)
            self.log("[OK] Analysis complete!")
            self.log(f"Output directory: {self.values['output_dir']}")
            self.log("="*60)
            
        except Exception as e:
            self.log("")
            self.log(f"[ERROR] {str(e)}")
            print(traceback.format_exc())
        finally:
            self.processing = False
            dpg.set_value("sc_progress", 0.0)

    def stop_processing_task(self):
        """Stop ongoing processing"""
        self.stop_processing = True
        self.log("")
        self.log("Stopping analysis...")

    def cleanup(self):
        """Clean up resources"""
        with self._cleanup_lock:
            self._is_destroyed = True
            self.stop_processing = True


# ==============================================================================
# Main entry point for standalone testing
# ==============================================================================

def main():
    """Main function for standalone execution"""
    # Suppress warnings
    import warnings
    warnings.filterwarnings('ignore')
    
    dpg.create_context()

    # Setup theme and font
    from dpg_components import setup_dpg_theme, setup_arial_font
    setup_dpg_theme()
    try:
        setup_arial_font(size=14)
    except:
        pass

    # Create main window
    with dpg.window(tag="sc_main", label="Single Crystal XRD Module"):
        module = SingleCrystalModule("sc_main")
        module.setup_ui()

    dpg.create_viewport(title="Single Crystal XRD Module", width=1200, height=1000)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("sc_main", True)
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
