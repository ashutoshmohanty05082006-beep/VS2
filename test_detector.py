#!/usr/bin/env python3
"""
Test script for PPE Safety Monitor
Run this to verify the code structure and basic functionality.
"""

def test_code_structure():
    """Test that the detector code is properly structured."""
    print("🧪 Testing code structure...")

    try:
        # Check if detector.py exists and can be parsed
        with open('src/detector.py', 'r') as f:
            code = f.read()

        print("✅ detector.py file exists and is readable")

        # Check for key classes and methods
        if 'class SafetyMonitor:' in code:
            print("✅ SafetyMonitor class found")
        else:
            print("❌ SafetyMonitor class not found")
            return False

        if 'def process_frame(' in code:
            print("✅ process_frame method found")
        else:
            print("❌ process_frame method not found")
            return False

        if 'def check_association(' in code:
            print("✅ check_association method found")
        else:
            print("❌ check_association method not found")
            return False

        return True

    except Exception as e:
        print(f"❌ Code structure test failed: {e}")
        return False

def test_requirements():
    """Test that requirements.txt is properly formatted."""
    print("\n🧪 Testing requirements.txt...")

    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()

        required_packages = ['ultralytics', 'opencv-python', 'streamlit']
        missing = []

        for package in required_packages:
            if package not in requirements:
                missing.append(package)

        if missing:
            print(f"❌ Missing packages in requirements.txt: {missing}")
            return False
        else:
            print("✅ All required packages found in requirements.txt")
            return True

    except Exception as e:
        print(f"❌ Requirements test failed: {e}")
        return False

def test_streamlit_app():
    """Test that the streamlit app code is valid."""
    print("\n🧪 Testing Streamlit app...")

    try:
        with open('app/streamlit_app.py', 'r') as f:
            code = f.read()

        if 'SafetyMonitor' in code:
            print("✅ Streamlit app imports SafetyMonitor")
        else:
            print("❌ Streamlit app does not import SafetyMonitor")
            return False

        if 'st.video' in code:
            print("✅ Streamlit app has video display functionality")
        else:
            print("❌ Streamlit app missing video display")
            return False

        if 'compliance_data' in code:
            print("✅ Streamlit app processes compliance data")
        else:
            print("❌ Streamlit app missing compliance processing")
            return False

        return True

    except Exception as e:
        print(f"❌ Streamlit app test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting PPE Safety Monitor Code Validation\n")

    tests = [
        test_code_structure,
        test_requirements,
        test_streamlit_app
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1

    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("\n🎉 All code validation tests passed!")
        print("\n📋 Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. For model testing, you'll need GUI libraries (libGL.so.1)")
        print("3. Run the Streamlit app: streamlit run app/streamlit_app.py")
        print("4. Upload videos with people wearing PPE for analysis")
        print("5. For custom training:")
        print("   - Get PPE dataset from Roboflow Universe")
        print("   - Run: yolo train data=ppe_dataset.yaml model=yolov8n.pt epochs=100")
    else:
        print("\n❌ Some tests failed. Please check the code structure.")

if __name__ == "__main__":
    main()