#!/usr/bin/env python3
"""
Helper script for processing Tello drone images for 3D modeling.
This script helps organize, filter, and prepare images for photogrammetry software.
"""
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import shutil
import argparse

def organize_images(input_dir="photos", output_dir=None, session_prefix=None):
    """
    Organize images into a clean structure for photogrammetry processing
    
    Args:
        input_dir (str): Directory containing captured images
        output_dir (str, optional): Directory to organize images. If None, creates a timestamp-based subdirectory
        session_prefix (str, optional): Prefix for the session directory
    
    Returns:
        str: Path to the organized images directory
    """
    # Create output directory if not specified
    if not output_dir:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if session_prefix:
            session_name = f"{session_prefix}_{timestamp}"
        else:
            session_name = f"session_{timestamp}"
        output_dir = os.path.join("processed", session_name)
    
    # Create required directories
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "masked"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "filtered"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "final"), exist_ok=True)
    
    # Find all image files
    image_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(os.path.join(root, file))
    
    if not image_files:
        print(f"No images found in {input_dir}")
        return None
    
    print(f"Found {len(image_files)} images")
    
    # Copy images to output directory
    for i, img_path in enumerate(image_files):
        _, filename = os.path.split(img_path)
        new_path = os.path.join(output_dir, filename)
        shutil.copy2(img_path, new_path)
        print(f"Copied image {i+1}/{len(image_files)}: {filename}")
    
    print(f"Images organized in: {output_dir}")
    return output_dir

def filter_blurry_images(input_dir, threshold=100, move_to_filtered=True):
    """
    Filter out blurry images based on Laplacian variance
    
    Args:
        input_dir (str): Directory containing images to filter
        threshold (int): Laplacian variance threshold (lower = more blurry)
        move_to_filtered (bool): Whether to move blurry images to filtered directory or delete them
    
    Returns:
        list: List of paths to non-blurry images
    """
    print("Filtering blurry images...")
    
    filtered_dir = os.path.join(input_dir, "filtered")
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png')) and os.path.isfile(os.path.join(input_dir, f))]
    
    if not image_files:
        print("No images found to filter")
        return []
    
    # Results storage
    laplacian_scores = []
    good_images = []
    blurry_images = []
    
    # Process each image
    for img_file in image_files:
        img_path = os.path.join(input_dir, img_file)
        img = cv2.imread(img_path)
        
        if img is None:
            print(f"Could not read image: {img_file}")
            continue
            
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Calculate Laplacian variance (measure of image sharpness)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        score = np.var(laplacian)
        laplacian_scores.append((img_file, score))
        
        # Classify as good or blurry
        if score < threshold:
            blurry_images.append(img_path)
            if move_to_filtered:
                filtered_path = os.path.join(filtered_dir, img_file)
                shutil.move(img_path, filtered_path)
                print(f"Moved blurry image to filtered: {img_file} (Score: {score:.2f})")
            else:
                os.remove(img_path)
                print(f"Deleted blurry image: {img_file} (Score: {score:.2f})")
        else:
            good_images.append(img_path)
            print(f"Kept good image: {img_file} (Score: {score:.2f})")
    
    # Plot histogram of sharpness scores
    scores = [score for _, score in laplacian_scores]
    plt.figure(figsize=(10, 6))
    plt.hist(scores, bins=20)
    plt.axvline(x=threshold, color='r', linestyle='--', label=f'Threshold: {threshold}')
    plt.title("Image Sharpness Distribution")
    plt.xlabel("Laplacian Variance (Higher = Sharper)")
    plt.ylabel("Number of Images")
    plt.legend()
    plt.savefig(os.path.join(input_dir, "sharpness_histogram.png"))
    
    # Print summary
    print(f"\nSharpness filter summary:")
    print(f"Total images: {len(image_files)}")
    print(f"Good images: {len(good_images)}")
    print(f"Blurry images: {len(blurry_images)}")
    
    return good_images

def enhance_images(input_dir, output_dir=None):
    """
    Enhance images for better photogrammetry results
    
    Args:
        input_dir (str): Directory containing images to enhance
        output_dir (str, optional): Directory to save enhanced images. If None, uses input_dir/final
    
    Returns:
        str: Path to the enhanced images directory
    """
    if not output_dir:
        output_dir = os.path.join(input_dir, "final")
    
    os.makedirs(output_dir, exist_ok=True)
    
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png')) and os.path.isfile(os.path.join(input_dir, f))]
    
    if not image_files:
        print("No images found to enhance")
        return output_dir
    
    print(f"Enhancing {len(image_files)} images...")
    
    for img_file in image_files:
        img_path = os.path.join(input_dir, img_file)
        
        # Skip directories
        if os.path.isdir(img_path):
            continue
            
        # Skip non-image files
        if not img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
            
        # Read image
        img = cv2.imread(img_path)
        
        if img is None:
            print(f"Could not read image: {img_file}")
            continue
        
        # Apply enhancement techniques
        # 1. Contrast enhancement
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        enhanced_lab = cv2.merge((cl, a, b))
        enhanced_img = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        # 2. Sharpening
        kernel = np.array([[-1, -1, -1],
                           [-1,  9, -1],
                           [-1, -1, -1]])
        sharpened = cv2.filter2D(enhanced_img, -1, kernel)
        
        # Save the enhanced image
        output_path = os.path.join(output_dir, img_file)
        cv2.imwrite(output_path, sharpened)
        print(f"Enhanced: {img_file}")
    
    print(f"Image enhancement completed. Enhanced images saved to: {output_dir}")
    return output_dir

def export_for_photogrammetry(input_dir, photogrammetry_type="general"):
    """
    Prepare a README with instructions for importing into photogrammetry software
    
    Args:
        input_dir (str): Directory containing prepared images
        photogrammetry_type (str): Type of photogrammetry project 
                                  (general, terrain, object, structure)
    """
    readme_path = os.path.join(input_dir, "README_PHOTOGRAMMETRY.txt")
    
    # Count total images
    final_dir = os.path.join(input_dir, "final")
    if os.path.exists(final_dir):
        image_count = len([f for f in os.listdir(final_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    else:
        image_count = len([f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    with open(readme_path, 'w') as f:
        f.write("PHOTOGRAMMETRY PROCESSING INSTRUCTIONS\n")
        f.write("=====================================\n\n")
        
        f.write(f"Project Type: {photogrammetry_type.title()}\n")
        f.write(f"Total Images: {image_count}\n")
        f.write(f"Preparation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("RECOMMENDED SOFTWARE OPTIONS:\n")
        f.write("----------------------------\n")
        f.write("1. Meshroom (Free, Open Source)\n")
        f.write("   - Website: https://alicevision.org/#meshroom\n")
        f.write("   - Good for: General photogrammetry, objects, small scenes\n\n")
        
        f.write("2. OpenDroneMap (Free, Open Source)\n")
        f.write("   - Website: https://www.opendronemap.org/\n")
        f.write("   - Good for: Aerial mapping, terrain modeling\n\n")
        
        f.write("3. Metashape (Commercial)\n")
        f.write("   - Website: https://www.agisoft.com/\n")
        f.write("   - Good for: Professional use, all types of photogrammetry\n\n")
        
        f.write("4. RealityCapture (Commercial)\n")
        f.write("   - Website: https://www.capturingreality.com/\n")
        f.write("   - Good for: High-quality, fast processing\n\n")
        
        f.write("IMPORT INSTRUCTIONS:\n")
        f.write("-------------------\n")
        f.write(f"1. Import all images from the 'final' directory: {final_dir}\n")
        f.write("2. For most software, use the highest quality settings for initial testing\n")
        f.write("3. Ensure adequate RAM is available (16GB+ recommended)\n")
        f.write("4. Expect processing to take several hours for high-quality results\n\n")
        
        if photogrammetry_type.lower() == "terrain":
            f.write("TERRAIN MAPPING TIPS:\n")
            f.write("-------------------\n")
            f.write("- Set coordinate system to match your region\n")
            f.write("- Use 'high' setting for point cloud density\n")
            f.write("- Consider decimating the mesh if too large\n")
            f.write("- Export as digital elevation model (DEM) for GIS applications\n\n")
        
        elif photogrammetry_type.lower() == "object":
            f.write("OBJECT RECONSTRUCTION TIPS:\n")
            f.write("-------------------------\n")
            f.write("- Enable 'close-range photogrammetry' option if available\n")
            f.write("- Use masking if the software supports it\n")
            f.write("- Set higher texture resolution for detailed objects\n")
            f.write("- Export as OBJ or FBX with textures for 3D applications\n\n")
        
        f.write("COMMON ISSUES AND SOLUTIONS:\n")
        f.write("---------------------------\n")
        f.write("1. Poor reconstruction: Add more overlapping images\n")
        f.write("2. Holes in model: Ensure complete coverage of all angles\n")
        f.write("3. Processing errors: Try adjusting feature matching settings\n")
        f.write("4. Not enough RAM: Reduce image resolution or use fewer images\n\n")
        
        f.write("OUTPUTS TO EXPECT:\n")
        f.write("-----------------\n")
        f.write("1. Point cloud (sparse and dense)\n")
        f.write("2. 3D mesh\n")
        f.write("3. Textured 3D model\n")
        f.write("4. Orthomosaic (for terrain)\n\n")
        
        f.write("For more information on photogrammetry techniques, visit:\n")
        f.write("https://www.opendronemap.org/odm/\n")
        f.write("https://alicevision.org/\n")
    
    print(f"Created photogrammetry instructions at: {readme_path}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process drone images for photogrammetry")
    parser.add_argument("--input", "-i", default="photos", help="Input directory containing raw drone photos")
    parser.add_argument("--output", "-o", default=None, help="Output directory for processed images")
    parser.add_argument("--session", "-s", default=None, help="Session name prefix")
    parser.add_argument("--blur-threshold", "-b", type=int, default=100, help="Blur detection threshold (lower = more strict)")
    parser.add_argument("--type", "-t", default="general", choices=["general", "terrain", "object", "structure"], help="Type of photogrammetry project")
    parser.add_argument("--organize-only", action="store_true", help="Only organize files without further processing")
    parser.add_argument("--enhance", action="store_true", help="Apply image enhancement (contrast, sharpening)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Organize images
    output_dir = organize_images(args.input, args.output, args.session)
    
    if not output_dir:
        print("No images to process. Exiting.")
        return
    
    if not args.organize_only:
        # Filter blurry images
        filter_blurry_images(output_dir, threshold=args.blur_threshold)
        
        # Enhance images if requested
        if args.enhance:
            enhance_images(output_dir)
    
    # Create export instructions
    export_for_photogrammetry(output_dir, args.type)
    
    print("\nImage processing completed successfully!")
    print(f"Processed images are in: {output_dir}")
    print(f"Instructions for photogrammetry software are in: {os.path.join(output_dir, 'README_PHOTOGRAMMETRY.txt')}")

if __name__ == "__main__":
    main() 