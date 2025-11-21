#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Advanced script for batch processing HDF5 diffraction images (with config file support)
Performs 1D integration using pyFAI and saves results in .xy format

Usage:
    python batch_integration_advanced.py                    # Use default config file
    python batch_integration_advanced.py config.ini         # Use specified config file
    python batch_integration_advanced.py --help             # Show help information

Author: Felicity’s Devoted Assistant 💕
"""

import os
import sys
import glob
import h5py
import numpy as np
import pyFAI
import fabio
import argparse
import configparser
from pathlib import Path
from tqdm import tqdm
from datetime import datetime


class BatchIntegrator:
    """Batch integration processor"""
    
    def __init__(self, poni_file, mask_file=None):
        """
        Initialize the integrator
        
        Args:
            poni_file (str): Path to calibration file (.poni)
            mask_file (str, optional): Path to mask file
        """
        self.ai = pyFAI.load(poni_file)
        print(f"✓ Successfully loaded calibration file: {poni_file}")
        print(f"  Detector: {self.ai.detector}")
        print(f"  Wavelength: {self.ai.wavelength*1e10:.4f} Å")
        print(f"  Sample-detector distance: {self.ai.dist*1000:.2f} mm")
        
        self.mask = None
        if mask_file and os.path.exists(mask_file):
            self.mask = self._load_mask(mask_file)
            print(f"✓ Successfully loaded mask file: {mask_file}")
            print(f"  Mask shape: {self.mask.shape}")
            print(f"  Masked pixels: {np.sum(self.mask)}")
        elif mask_file:
            print(f"⚠ Warning: Mask file not found: {mask_file}")
    
    def _load_mask(self, mask_file):
        """Load mask file"""
        ext = os.path.splitext(mask_file)[1].lower()
        
        if ext == '.npy':
            mask = np.load(mask_file)
        elif ext in ['.edf', '.tif', '.tiff', '.png']:
            mask = fabio.open(mask_file).data
        else:
            raise ValueError(f"Unsupported mask file format: {ext}")
        
        if mask.dtype != bool:
            mask = mask.astype(bool)
        
        return mask
    
    def _read_h5_image(self, h5_file, dataset_path=None, frame_index=0):
        """
        Read image data from HDF5 file
        
        Args:
            h5_file (str): Path to HDF5 file
            dataset_path (str, optional): Dataset path within HDF5
            frame_index (int): Frame index if multi-frame data
        
        Returns:
            numpy.ndarray: Image data
        """
        with h5py.File(h5_file, 'r') as f:
            if dataset_path is None:
                dataset_path = self._find_image_dataset(f)
            
            if dataset_path not in f:
                raise ValueError(f"Dataset not found in HDF5 file: {dataset_path}")
            
            data = f[dataset_path]
            
            if len(data.shape) == 3:
                if frame_index >= data.shape[0]:
                    raise ValueError(f"Frame index {frame_index} out of bounds (total frames: {data.shape[0]})")
                img_data = data[frame_index]
            else:
                img_data = data[()]
        
        return img_data
    
    def _find_image_dataset(self, h5_file_obj):
        """Automatically find image dataset path in HDF5"""
        common_paths = [
            '/entry/data/data',
            '/entry/instrument/detector/data',
            '/entry/data/image',
            '/data/data',
            '/data',
            '/image',
            'data',
        ]
        
        for path in common_paths:
            if path in h5_file_obj:
                return path
        
        def find_dataset(obj, path=''):
            if isinstance(obj, h5py.Dataset):
                if len(obj.shape) >= 2:
                    return path
            elif isinstance(obj, h5py.Group):
                for key in obj.keys():
                    result = find_dataset(obj[key], path + '/' + key)
                    if result:
                        return result
            return None
        
        result = find_dataset(h5_file_obj)
        if result:
            print(f"  Automatically found dataset: {result}")
            return result
        else:
            raise ValueError("No suitable image dataset found in HDF5 file")
    
    def integrate_single(self, h5_file, output_file, npt=2000, unit="2th_deg",
                        dataset_path=None, frame_index=0, **kwargs):
        """
        Integrate a single HDF5 file
        
        Args:
            h5_file (str): Input HDF5 file
            output_file (str): Output .xy file path
            npt (int): Number of points for integration
            unit (str): Output unit
            dataset_path (str, optional): Dataset path
            frame_index (int): Frame index (for multi-frame)
            **kwargs: Additional arguments to integrate1d
        """
        try:
            img_data = self._read_h5_image(h5_file, dataset_path, frame_index)
            
            result = self.ai.integrate1d(
                img_data,
                npt=npt,
                mask=self.mask,
                unit=unit,
                filename=output_file,
                **kwargs
            )
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def batch_integrate(self, input_pattern, output_dir, npt=2000, unit="2th_deg",
                        dataset_path=None, **kwargs):
        """Batch integration for multiple HDF5 files (no logging version)"""
        h5_files = sorted(glob.glob(input_pattern, recursive=True))
    
        if not h5_files:
            print(f"⚠ No matching files found: {input_pattern}")
            return
    
        print(f"\nFound {len(h5_files)} HDF5 files to process")
        print(f"Output directory: {output_dir}")
        print(f"Integration parameters: {npt} points, unit={unit}\n")
    
        os.makedirs(output_dir, exist_ok=True)
    
        success_count = 0
        failed_files = []
    
        for h5_file in tqdm(h5_files, desc="Processing"):
            basename = os.path.splitext(os.path.basename(h5_file))[0]
            output_file = os.path.join(output_dir, f"{basename}.xy")
    
            success, error_msg = self.integrate_single(
                h5_file, output_file, npt, unit, dataset_path, **kwargs
            )
    
            if success:
                success_count += 1
                print(f"✓ Success: {h5_file} -> {output_file}")
            else:
                failed_files.append((h5_file, error_msg))
                print(f"✗ Failed: {h5_file}\n  Error: {error_msg}")
    
        print(f"\n✓ Batch processing complete!")
        print(f"  Success: {success_count}/{len(h5_files)}")
        print(f"  Failed: {len(failed_files)}/{len(h5_files)}")
    
        if failed_files:
            print(f"\n⚠ Failed files preview:")
            for file, error in failed_files[:5]:
                print(f"  - {file}: {error}")
            if len(failed_files) > 5:
                print(f"  ...and {len(failed_files)-5} more failed files not shown")


def load_config(config_file):
    """Load config file"""
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    
    paths = {
        'poni_file': config.get('paths', 'poni_file'),
        'mask_file': config.get('paths', 'mask_file', fallback=None),
        'input_pattern': config.get('paths', 'input_pattern'),
        'output_dir': config.get('paths', 'output_dir'),
        'dataset_path': config.get('paths', 'dataset_path', fallback=None)
    }
    
    if paths['mask_file'] == '':
        paths['mask_file'] = None
    if paths['dataset_path'] == '':
        paths['dataset_path'] = None
    
    integration = {
        'npt': config.getint('integration', 'npt', fallback=2000),
        'unit': config.get('integration', 'unit', fallback='2th_deg'),
        'correctSolidAngle': config.getboolean('integration', 'correct_solid_angle', fallback=True),
        'polarization_factor': config.get('integration', 'polarization_factor', fallback='None')
    }
    
    if integration['polarization_factor'] == 'None':
        integration['polarization_factor'] = None
    else:
        integration['polarization_factor'] = float(integration['polarization_factor'])
    
    advanced = {
        'method': config.get('advanced', 'method', fallback='csr'),
        'safe': config.getboolean('advanced', 'safe', fallback=True),
        'normalization_factor': config.getfloat('advanced', 'normalization_factor', fallback=1.0)
    }
    
    return paths, integration, advanced

def run_batch_integration(
    poni_file,
    mask_file,
    input_pattern,
    output_dir,
    dataset_path=None,
    npt=2000,
    unit='2th_deg'
):
    """
    Run batch 1D integration using pyFAI

    Args:
        poni_file (str): Path to .poni calibration file
        mask_file (str): Path to mask file (can be None)
        input_pattern (str): Glob pattern to input HDF5 files
        output_dir (str): Output directory
        dataset_path (str, optional): HDF5 dataset path (autodetect if None)
        npt (int): Number of integration points
        unit (str): Output unit (e.g. '2th_deg', 'q_A^-1', etc.)
    """

    integration_kwargs = {
        'correctSolidAngle': True,
        'polarization_factor': None,
        'method': 'csr',
        'safe': True,
        'normalization_factor': 1.0
    }

    if not os.path.exists(poni_file):
        raise FileNotFoundError(f"Calibration file not found: {poni_file}")

    integrator = BatchIntegrator(poni_file, mask_file)

    integrator.batch_integrate(
        input_pattern=input_pattern,
        output_dir=output_dir,
        npt=npt,
        unit=unit,
        dataset_path=dataset_path,
        **integration_kwargs
    )
def main():
    """Main function: hardcoded version"""
    print("=" * 60)
    print("HDF5 Diffraction Image Batch Integration Script (Hardcoded Version)")
    print("=" * 60)

    run_batch_integration(
        poni_file=r'D:\HEPS\ID31\test\using.poni',
        mask_file=r'D:\HEPS\ID31\test\use.edf',
        input_pattern=r'D:\HEPS\ID31\test\input_dir\*.h5',
        output_dir=r'D:\HEPS\ID31\test\out_dir',
        dataset_path=None,
        npt=2000,
        unit='2th_deg'
    )


if __name__ == "__main__":
    main()


