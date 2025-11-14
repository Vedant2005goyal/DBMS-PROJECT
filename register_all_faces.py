#!/usr/bin/env python3
"""
Register all student faces from the Celebrity Faces Dataset
This script registers faces for all students in the database
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.Face_Recognition import FaceRegistration

def register_all_faces():
    """Register all faces from the dataset"""
    
    print("=" * 70)
    print("📸 Registering Student Faces")
    print("=" * 70)
    print()
    
    # Initialize face registration
    try:
        facesys = FaceRegistration()
        print("✅ Face registration system initialized")
    except Exception as e:
        print(f"❌ Error initializing face registration: {e}")
        return
    
    # Dataset directory
    dataset_dir = os.path.join(os.path.dirname(__file__), 'Celebrity Faces Dataset')
    
    if not os.path.exists(dataset_dir):
        print(f"❌ Dataset directory not found: {dataset_dir}")
        return
    
    print(f"📁 Dataset directory: {dataset_dir}")
    print()
    
    # Map celebrity names to User_IDs
    celebrity_id_map = {
        'Angelina Jolie': 1,
        'Brad Pitt': 2,
        'Denzel Washington': 3,
        'Hugh Jackman': 4,
        'Jennifer Lawrence': 5,
        'Johnny Depp': 6,
        'Kate Winslet': 7,
        'Leonardo DiCaprio': 8,
        'Megan Fox': 9,
        'Natalie Portman': 10,
        'Nicole Kidman': 11,
        'Robert Downey Jr': 12,
        'Sandra Bullock': 13,
        'Scarlett Johansson': 14,
        'Tom Cruise': 15,
        'Tom Hanks': 16,
        'Will Smith': 17,
        'Osho': 18,
        'Khalil Gibran': 19,
        'Aditya Gupta': 20,
        'Vedant Goyal': 21,
        'Rushil Upadhyay': 22,
        'Nikunj Garg': 23,
        'Kusham Lata': 24
    }
    
    registered_count = 0
    skipped_count = 0
    error_count = 0
    
    # Get all directories in dataset
    content = os.listdir(dataset_dir)
    
    print("🔍 Scanning for faces to register...")
    print()
    
    for person_name in content:
        person_dir = os.path.join(dataset_dir, person_name)
        
        # Check if it's a directory and matches our map
        if os.path.isdir(person_dir) and person_name in celebrity_id_map:
            user_id = celebrity_id_map[person_name]
            
            # Check if already registered
            existing = facesys.check_existing_embeddings(user_id)
            if existing:
                print(f"⏭️  {person_name} (ID: {user_id}) - Already registered, skipping")
                skipped_count += 1
                continue
            
            # Find image files
            img_files = [f for f in os.listdir(person_dir) 
                        if f.lower().endswith(('.png', '.jpeg', '.jpg'))]
            
            if not img_files:
                print(f"⚠️  {person_name} (ID: {user_id}) - No image files found")
                error_count += 1
                continue
            
            # Use the first image found
            image_file = img_files[0]
            full_image_path = os.path.join(person_dir, image_file)
            
            print(f"📸 Registering {person_name} (ID: {user_id})...")
            print(f"   Image: {image_file}")
            
            try:
                result, message = facesys.register_person(
                    User_ID=user_id,
                    image_path=full_image_path,
                    show_preview=False  # Don't show preview in script
                )
                
                if result:
                    print(f"   ✅ {message}")
                    registered_count += 1
                else:
                    print(f"   ❌ {message}")
                    error_count += 1
            except Exception as e:
                print(f"   ❌ Error: {e}")
                error_count += 1
            
            print()
    
    print("=" * 70)
    print("📊 Registration Summary")
    print("=" * 70)
    print(f"✅ Registered: {registered_count}")
    print(f"⏭️  Skipped (already registered): {skipped_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📸 Total processed: {registered_count + skipped_count + error_count}")
    print()
    print("✅ Face registration complete!")
    print()
    print("🔄 Restart the API to load registered faces:")
    print("   docker-compose restart api")

if __name__ == "__main__":
    try:
        register_all_faces()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

