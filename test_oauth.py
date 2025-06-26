#!/usr/bin/env python3
"""
Test script for Google Calendar OAuth integration
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import google.auth
        import google.oauth2.credentials
        import googleapiclient.discovery
        print("✅ Google API packages imported successfully")
    except ImportError as e:
        print(f"❌ Google API packages import failed: {e}")
        return False
    
    try:
        import cryptography
        print("✅ Cryptography package imported successfully")
    except ImportError as e:
        print(f"❌ Cryptography package import failed: {e}")
        return False
    
    try:
        from backend.oauth_handler import GoogleOAuthHandler
        from backend.google_calendar_service import GoogleCalendarService
        from backend.token_manager import TokenManager
        print("✅ Backend modules imported successfully")
    except ImportError as e:
        print(f"❌ Backend modules import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment configuration"""
    print("\n🧪 Testing environment configuration...")
    
    # Check if .env.local exists
    env_file = Path('.env.local')
    if not env_file.exists():
        print("❌ .env.local file not found")
        return False
    print("✅ .env.local file exists")
    
    # Check environment variables
    required_vars = [
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET',
        'OAUTH_REDIRECT_URI',
        'ENCRYPTION_KEY'
    ]
    
    missing_vars = []
    placeholder_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif value in ['your_google_client_id_here', 'your_google_client_secret_here', 
                      'PLACEHOLDER_CLIENT_SECRET', 'your_encryption_key_here']:
            placeholder_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    if placeholder_vars:
        print(f"❌ Placeholder values found in: {', '.join(placeholder_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_oauth_handler():
    """Test OAuth handler functionality"""
    print("\n🧪 Testing OAuth handler...")
    
    try:
        from backend.oauth_handler import GoogleOAuthHandler
        
        oauth_handler = GoogleOAuthHandler()
        print("✅ OAuth handler created successfully")
        
        # Test configuration
        if oauth_handler.is_configured():
            print("✅ OAuth handler is properly configured")
        else:
            print("❌ OAuth handler is not configured")
            config_status = oauth_handler.get_configuration_status()
            print(f"Configuration status: {config_status}")
            return False
        
        # Test auth URL generation
        try:
            auth_url, state = oauth_handler.generate_auth_url()
            print("✅ Auth URL generated successfully")
            print(f"Auth URL preview: {auth_url[:100]}...")
        except Exception as e:
            print(f"❌ Failed to generate auth URL: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ OAuth handler test failed: {e}")
        return False

def test_calendar_service():
    """Test Google Calendar service"""
    print("\n🧪 Testing Google Calendar service...")
    
    try:
        from backend.google_calendar_service import GoogleCalendarService
        
        calendar_service = GoogleCalendarService()
        print("✅ Calendar service created successfully")
        
        # Test configuration check
        if calendar_service.is_configured():
            print("✅ Calendar service is properly configured")
        else:
            print("❌ Calendar service is not configured")
            return False
        
        # Note: We can't test actual API calls without valid tokens
        print("✅ Calendar service basic functionality works")
        return True
        
    except Exception as e:
        print(f"❌ Calendar service test failed: {e}")
        return False

def test_token_manager():
    """Test token manager functionality"""
    print("\n🧪 Testing token manager...")
    
    try:
        from backend.token_manager import TokenManager
        
        token_manager = TokenManager()
        print("✅ Token manager created successfully")
        
        # Test encryption/decryption
        test_tokens = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'expires_in': 3600
        }
        
        # Test encryption
        encrypted = token_manager.encrypt_tokens(test_tokens)
        if encrypted:
            print("✅ Token encryption works")
        else:
            print("❌ Token encryption failed")
            return False
        
        # Test decryption
        decrypted = token_manager.decrypt_tokens(encrypted)
        if decrypted == test_tokens:
            print("✅ Token decryption works")
        else:
            print("❌ Token decryption failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Token manager test failed: {e}")
        return False

def test_streamlit_integration():
    """Test Streamlit integration"""
    print("\n🧪 Testing Streamlit integration...")
    
    try:
        # Check if streamlit apps can be imported
        import streamlit_app
        print("✅ Main Streamlit app can be imported")
        
        import streamlit_app_minimal
        print("✅ Minimal Streamlit app can be imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit integration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 TailorTalk OAuth Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Environment Test", test_environment),
        ("OAuth Handler Test", test_oauth_handler),
        ("Calendar Service Test", test_calendar_service),
        ("Token Manager Test", test_token_manager),
        ("Streamlit Integration Test", test_streamlit_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Your OAuth integration is ready.")
        print("\nNext steps:")
        print("1. Run: streamlit run streamlit_app.py")
        print("2. Navigate to Google Calendar section")
        print("3. Test the OAuth flow")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return False

def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        # Quick test - just imports and environment
        if test_imports() and test_environment():
            print("✅ Quick test passed")
            sys.exit(0)
        else:
            print("❌ Quick test failed")
            sys.exit(1)
    
    # Run all tests
    if run_all_tests():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
