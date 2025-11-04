#!/usr/bin/env python3
"""
BrainConnect - a flexible pipeline to integrate brain connectivity and spatial transcriptomics for downstream analysis
Complete workflow command line interface
"""

import argparse
import sys
import os
from . import __version__

def main():
    """Main command line entry function"""
    parser = create_parser()
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        try:
            args.func(args)
        except KeyboardInterrupt:
            print("\nOperation interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()

def create_parser():
    """Create command line parser - only creates parser, no heavy imports"""
    parser = argparse.ArgumentParser(
        description="BrainConnect - Complete neuronal data analysis workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Complete workflow examples:
  # 1. Download experimental data
  BrainConnect download --experiments data/experiments.csv --download-dir data/experiment_data --annotation data/annotation_25.nrrd --limit 10

  # 2. Preprocess experimental data
  BrainConnect preprocess --experiments data/experiments.csv --download-dir data/experiment_data --annotation data/annotation_25.nrrd --output-dir data/experiment_data/result

  # 3. Process SWC files
  BrainConnect swc --annotation data/annotation_25.nrrd --input data/orig_swc_data/ --output results/swc_results.csv

  # 4. Extract features
  BrainConnect feature --swc-results results/swc_results.csv --adjacency data/adjacency_matrix.csv --output results/features.csv

  # 5. Data fusion
  BrainConnect fusion --features results/features.csv --experiment-results data/experiment_data/result/merged_results.csv --output results/fusion_results.csv

  # 6. Train model
  BrainConnect model --fusion-results results/fusion_results.csv --gene-data data/gene_data.csv --output results/gene_importance.csv

Requirements:
  - Python 3.12+
  - Dependencies: pandas, numpy, tensorflow, pyswcloader, networkx

Version: {__version__}
        """
    )
    
    parser.add_argument(
        '-v', '--version', 
        action='version', 
        version=f'BrainConnect {__version__}'
    )
    
    # Create subcommand parsers
    subparsers = parser.add_subparsers(
        title='Workflow commands',
        dest='command',
        metavar='<command>'
    )
    
    # Add all subcommands
    add_download_parser(subparsers)
    add_preprocess_parser(subparsers)
    add_swc_parser(subparsers)
    add_feature_parser(subparsers)
    add_fusion_parser(subparsers)
    add_model_parser(subparsers)
    
    return parser

# Parser functions
def add_download_parser(subparsers):
    """Add data download subcommand"""
    parser_download = subparsers.add_parser('download', help='Download Allen experimental data')
    
    parser_download.add_argument('--experiments', '-e', required=True, help='Experimental data file path')
    parser_download.add_argument('--download-dir', required=True, help='Data download directory')
    parser_download.add_argument('--annotation', '-a', required=True, help='Brain annotation file path')
    parser_download.add_argument('--allen-tree', default='data/1.json', help='Allen brain tree file path')
    parser_download.add_argument('--acro-dict', default='data/1.json', help='Acronym dictionary file path')
    parser_download.add_argument('--limit', '-n', type=int, default=0, help='Download quantity limit (0 means download all)')
    
    parser_download.set_defaults(func=handle_download)

def add_preprocess_parser(subparsers):
    """Add data preprocessing subcommand"""
    parser_preprocess = subparsers.add_parser('preprocess', help='Preprocess experimental data')
    
    parser_preprocess.add_argument('--experiments', '-e', required=True, help='Experimental data file path')
    parser_preprocess.add_argument('--download-dir', required=True, help='Data download directory')
    parser_preprocess.add_argument('--annotation', '-a', required=True, help='Brain annotation file path')
    parser_preprocess.add_argument('--output-dir', required=True, help='Preprocessing results output directory')
    parser_preprocess.add_argument('--allen-tree', default='data/1.json', help='Allen brain tree file path')
    parser_preprocess.add_argument('--acro-dict', default='data/1.json', help='Acronym dictionary file path')
    parser_preprocess.add_argument('--use-projection-density', action='store_true', default=True, help='Use projection density data')
    
    parser_preprocess.set_defaults(func=handle_preprocess)

def add_swc_parser(subparsers):
    """Add SWC processing subcommand"""
    parser_swc = subparsers.add_parser('swc', help='SWC file processing and analysis')
    
    parser_swc.add_argument('--annotation', '-a', required=True, help='Brain annotation file path')
    parser_swc.add_argument('--input', '-i', required=True, help='Input SWC file directory path')
    parser_swc.add_argument('--output', '-o', required=True, help='Output results file path')
    parser_swc.add_argument('--resolution', '-r', type=float, default=25.0, help='Resolution parameter')
    parser_swc.add_argument('--allen-tree', default='data/1.json', help='Allen brain tree file path')
    parser_swc.add_argument('--acro-dict', default='data/1.json', help='Acronym dictionary file path')
    
    parser_swc.set_defaults(func=handle_swc)

def add_feature_parser(subparsers):
    """Add feature processing subcommand"""
    parser_feature = subparsers.add_parser('feature', help='Feature extraction and integration')
    
    parser_feature.add_argument('--swc-results', '-s', required=True, help='SWC processing results file path')
    parser_feature.add_argument('--adjacency', '-adj', required=True, help='Adjacency matrix file path')
    parser_feature.add_argument('--output', '-o', required=True, help='Output features file path')
    parser_feature.add_argument('--allen-tree', default='data/1.json', help='Allen brain tree file path')
    parser_feature.add_argument('--acro-dict', default='data/1.json', help='Acronym dictionary file path')
    parser_feature.add_argument('--progress-file', help='Progress save file path')
    
    parser_feature.set_defaults(func=handle_feature)

def add_fusion_parser(subparsers):
    """Add data fusion subcommand"""
    parser_fusion = subparsers.add_parser('fusion', help='Multimodal data fusion')
    
    parser_fusion.add_argument('--features', '-f', required=True, help='Features file path')
    parser_fusion.add_argument('--experiment-results', '-er', required=True, help='Experimental data results file path')
    parser_fusion.add_argument('--output', '-o', required=True, help='Output fusion results file path')
    parser_fusion.add_argument('--adjacency', default='data/Mouse_brain_adjacency_matrix.csv', help='Adjacency matrix file path')
    parser_fusion.add_argument('--allen-tree', default='data/1.json', help='Allen brain tree file path')
    parser_fusion.add_argument('--acro-dict', default='data/1.json', help='Acronym dictionary file path')
    parser_fusion.add_argument('--min-path-length', type=int, default=5, help='Minimum path length')
    
    parser_fusion.set_defaults(func=handle_fusion)

def add_model_parser(subparsers):
    """Add model operations subcommand"""
    parser_model = subparsers.add_parser('model', help='Model training and prediction')
    
    parser_model.add_argument('--fusion-results', '-f', required=True, help='Data fusion results file path')
    parser_model.add_argument('--gene-data', '-g', required=True, help='Gene data file path')
    parser_model.add_argument('--output', '-o', required=True, help='Output gene importance file path')
    parser_model.add_argument('--acro-dict', default='data/1.json', help='Acronym dictionary file path')
    parser_model.add_argument('--window-size', type=int, default=5, help='Sliding window size')
    parser_model.add_argument('--epochs', type=int, default=50, help='Training epochs')
    parser_model.add_argument('--batch-size', type=int, default=32, help='Batch size')
    
    parser_model.set_defaults(func=handle_model)

# Command handler functions
def handle_download(args):
    """Handle data download"""
    import pandas as pd
    import pyswcloader
    import os
    from .data_fusion import AllenDataFusion
    
    print("=" * 60)
    print("Starting Allen experimental data download")
    print("=" * 60)
    
    # Check experimental data file
    if not os.path.exists(args.experiments):
        print(f"Error: Experimental data file does not exist: {args.experiments}")
        return
    
    # Read experimental data
    all_experiments = pd.read_csv(args.experiments)
    total_experiments = len(all_experiments)
    
    # Apply quantity limit
    if args.limit > 0:
        experiments_to_download = all_experiments.head(args.limit)
        print(f"Downloading first {args.limit} experiments (out of {total_experiments})")
    else:
        experiments_to_download = all_experiments
        print(f"Downloading all {total_experiments} experiments")
    
    # Create temporary experiment file
    temp_experiments_file = os.path.join(args.download_dir, "temp_download_list.csv")
    os.makedirs(os.path.dirname(temp_experiments_file), exist_ok=True)
    experiments_to_download.to_csv(temp_experiments_file, index=False)
    
    # Load annotation data
    print(f"Loading annotation file: {args.annotation}")
    anno = pyswcloader.brain.read_nrrd(args.annotation)
    allen_brain_tree = pyswcloader.brain.allen_brain_tree(args.allen_tree)
    stl_acro_dict = pyswcloader.brain.acronym_dict(args.acro_dict)
    
    # Initialize fusion processor
    fusion_processor = AllenDataFusion(anno, allen_brain_tree, stl_acro_dict)
    
    # Create download directory
    os.makedirs(args.download_dir, exist_ok=True)
    
    # Download experimental data
    print("Downloading injection_fraction data...")
    fusion_processor.download_Allen_files(  
        csv_file_path=temp_experiments_file,
        download_dir=os.path.join(args.download_dir, "injection_fraction"),
        image_type="injection_fraction"
    )
    
    print("Downloading projection_density data...")
    fusion_processor.download_Allen_files(  
        csv_file_path=temp_experiments_file,
        download_dir=os.path.join(args.download_dir, "projection_density"),
        image_type="projection_density"
    )
    
    # Clean up temporary file
    if os.path.exists(temp_experiments_file):
        os.remove(temp_experiments_file)
    
    print("=" * 60)
    print("Data download completed!")
    print(f"Downloaded {len(experiments_to_download)} experimental datasets")
    print(f"Data saved in: {args.download_dir}")
    print("=" * 60)

def handle_preprocess(args):
    """Preprocess experimental data"""
    import pandas as pd
    import pyswcloader
    import os
    from .data_fusion import AllenDataFusion
    
    print("=" * 60)
    print("Starting experimental data preprocessing")
    print("=" * 60)
    
    # Check if data has been downloaded
    required_dirs = [
        os.path.join(args.download_dir, "injection_fraction"),
        os.path.join(args.download_dir, "projection_density")
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"Error: Data directory does not exist: {dir_path}")
            print("Please run download command first: BrainConnect download --help")
            return
    
    # Load annotation data
    print(f"Loading annotation file: {args.annotation}")
    anno = pyswcloader.brain.read_nrrd(args.annotation)
    allen_brain_tree = pyswcloader.brain.allen_brain_tree(args.allen_tree)
    stl_acro_dict = pyswcloader.brain.acronym_dict(args.acro_dict)
    
    # Initialize fusion processor
    fusion_processor = AllenDataFusion(anno, allen_brain_tree, stl_acro_dict)
    
    # Preprocess annotation data
    print("Preprocessing annotation data...")
    annot_labeled, area_masks, valid_areas = fusion_processor.preprocess_annotation_data()
    
    # Process experimental data
    print("Processing experimental data...")
    all_experiments = pd.read_csv(args.experiments)
    id_list = all_experiments['id'].tolist()
    
    results_df = fusion_processor.batch_process_experiments_sequential(
        experiment_ids=id_list,
        annot_labeled=annot_labeled,
        area_masks=area_masks,
        valid_areas=valid_areas,
        base_dir=args.download_dir,
        output_dir=args.output_dir,
        use_projection_density=args.use_projection_density
    )
    
    print("=" * 60)
    print("Experimental data preprocessing completed!")
    print(f"Results saved in: {args.output_dir}")
    print("=" * 60)

def handle_swc(args):
    """Process SWC files"""
    import pyswcloader
    import os
    from .swc_processor import BatchSWCProcessor
    
    print("=" * 60)
    print("Starting SWC file processing")
    print("=" * 60)
    
    # Check input directory
    if not os.path.exists(args.input):
        print(f"Error: Input directory does not exist: {args.input}")
        return
    
    # Original processing logic
    anno = pyswcloader.brain.read_nrrd(args.annotation)
    allen_brain_tree = pyswcloader.brain.allen_brain_tree(args.allen_tree)
    stl_acro_dict = pyswcloader.brain.acronym_dict(args.acro_dict)
    
    batch_processor = BatchSWCProcessor(anno, args.resolution)
    results = batch_processor.process_batch_folders(args.input)
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")
    
    # Check if output file already exists
    if os.path.exists(args.output):
        response = input(f"File {args.output} already exists, overwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Operation cancelled")
            return
    
    results.to_csv(args.output, index=False)
    print(f"Results saved to: {args.output}")

def handle_feature(args):
    """Handle feature integration"""
    import pandas as pd
    import pyswcloader
    from .feature_integrator import SWCPathProcessor
    
    print("=" * 60)
    print("Starting feature extraction and integration")
    print("=" * 60)
    
    # Original processing logic
    directed_df = pd.read_csv(args.adjacency, index_col=0)
    file = pd.read_csv(args.swc_results)
    allen_brain_tree = pyswcloader.brain.allen_brain_tree(args.allen_tree)
    stl_acro_dict = pyswcloader.brain.acronym_dict(args.acro_dict)
    
    processor_swc = SWCPathProcessor(allen_brain_tree, stl_acro_dict)
    keys_set = processor_swc.filter_problematic_nodes(directed_df, stl_acro_dict)
    combined_df = processor_swc.process_path_pipeline(file, keys_set)
    unique_pairs = processor_swc.build_representative_paths(combined_df,args.output)
    
    unique_pairs['replaced_path'] = unique_pairs['path'].apply(
        processor_swc.replace_nodes_with_acronyms
    )
    unique_pairs.to_csv(args.output, index=False)
    print(f"Feature results saved to: {args.output}")

def handle_fusion(args):
    """Handle data fusion"""
    import pandas as pd
    import pyswcloader
    import os
    from .data_fusion import AllenDataFusion
    from .feature_integrator import SWCPathProcessor

    print("=" * 60)
    print("Starting data fusion")
    print("=" * 60)
    
    # Check input files
    if not os.path.exists(args.features):
        print(f"Error: Features file does not exist: {args.features}")
        return
    if not os.path.exists(args.experiment_results):
        print(f"Error: Experimental data results file does not exist: {args.experiment_results}")
        return
    
    # Load annotation data
    anno = pyswcloader.brain.read_nrrd('data/annotation_25.nrrd')  # This may need adjustment
    allen_brain_tree = pyswcloader.brain.allen_brain_tree(args.allen_tree)
    stl_acro_dict = pyswcloader.brain.acronym_dict(args.acro_dict)
    
    # Initialize fusion processors
    fusion_processor = AllenDataFusion(anno, allen_brain_tree, stl_acro_dict)
    fusion_swc = SWCPathProcessor(allen_brain_tree, stl_acro_dict)

    # Data integration
    print("Integrating data...")
    unique_pairs = pd.read_csv(args.features)
    
    # Add annotated paths
    unique_pairs['replaced_path'] = unique_pairs['path'].apply(
        fusion_swc.replace_nodes_with_acronyms
    )
    unique_pairs['replaced_start_node'] = unique_pairs['replaced_path'].str.split('→').str[0]

    # Create matrices and integrate
    allen_data = fusion_processor.load_and_preprocess_allen_data(args.experiment_results)
    
    ipsi_matrix, contra_matrix = fusion_processor.create_ipsi_contra_matrices(allen_data)
    
    # Filter nodes
    directed_df = pd.read_csv(args.adjacency, index_col=0)
    keys_set = fusion_swc.filter_problematic_nodes(directed_df, stl_acro_dict)
    
    ipsi_filtered = fusion_processor.filter_matrix_nodes(ipsi_matrix, keys_set)
    contra_filtered = fusion_processor.filter_matrix_nodes(contra_matrix, keys_set)
    
    # Create hierarchical matrix
    ipsi_hierarchical = fusion_processor.create_hierarchical_matrix(ipsi_filtered)
    ipsi_processed = fusion_processor.filter_and_normalize_matrix(ipsi_hierarchical, percentile=75)
    
    # Integrate path data
    final_results = fusion_processor.integrate_paths_with_intensity(
        unique_pairs, ipsi_processed, min_path_length=args.min_path_length
    )
    
    # Save results
    final_results.to_csv(args.output, index=False)
    print(f"Fusion results saved to: {args.output}")

def handle_model(args):
    """Handle model training"""
    import numpy as np
    import pyswcloader
    from .model import SequenceDataProcessor
    
    print("=" * 60)
    print("Starting model training")
    print("=" * 60)
    
    # Load acronym dictionary
    stl_acro_dict = pyswcloader.brain.acronym_dict(args.acro_dict)
    
    # Initialize processor
    processor = SequenceDataProcessor(stl_acro_dict, args.gene_data)
    
    # Load and prepare data
    print("Loading and preparing data...")
    X, y_log, max_len, pca = processor.load_and_prepare_data(
        args.fusion_results, 
        window_size=args.window_size
    )
    
    # Split data
    node_train, node_test, strength_train, strength_test = processor.split_data(X, y_log)
    
    # Prepare final data
    gene_train, gene_test, init_strength_train, init_strength_test, strength_train_shift, strength_test_shift = processor.prepare_final_data(
        node_train, node_test, strength_train, strength_test, max_len
    )
    
    # Build model
    print("Building autoregressive model...")
    model = processor.build_true_autoregressive_model_with_k(
        max_len=args.window_size, 
        gene_embed_dim=64
    )
    
    # Train model
    print("Training model...")
    r2_callback = processor.MultiInputR2ScoreCallback(
        validation_data=([gene_test, init_strength_test], strength_test_shift)
    )
    
    history = model.fit(
        [gene_train, init_strength_train],
        strength_train_shift,
        validation_data=([gene_test, init_strength_test], strength_test_shift),
        epochs=args.epochs,
        batch_size=args.batch_size,
        callbacks=[r2_callback],
        verbose=1
    )
    
    # Calculate gene importance
    print("Calculating gene importance...")
    gene_all = np.concatenate([gene_train, gene_test], axis=0)
    init_strength_all = np.concatenate([init_strength_train, init_strength_test], axis=0)
    
    position_imp, dim_imp = processor.compute_gene_importance(
        model=model,
        dataset=(gene_all, init_strength_all),
        target_timestep=-1,
        n_samples=len(gene_all)
    )
    
    # Get original gene importance
    gene_importance, gene_importance_df = processor.get_gene_importance_from_pca(
        dimension_importance=dim_imp
    )
    
    # Save results
    gene_importance_df.to_csv(args.output, index=False)
    print(f"Gene importance results saved to: {args.output}")

if __name__ == "__main__":
    main()