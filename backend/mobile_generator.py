"""
MOBILE GENERATOR - React Native / Capacitor / Flutter APK Generation
Transforms GAAIUS blueprints into mobile apps (iOS/Android)
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import subprocess

@dataclass
class MobileConfig:
    """Configuration for mobile app generation"""
    project_id: str
    project_name: str
    app_id: str  # com.example.app
    version: str = "1.0.0"
    target: str = "react-native"  # "react-native", "flutter", "capacitor"
    platforms: List[str] = None  # ["android", "ios"]
    
    def __post_init__(self):
        if self.platforms is None:
            self.platforms = ["android", "ios"]


class MobileGenerator:
    """Generates native mobile apps from blueprints"""
    
    def generate_react_native(self, config: MobileConfig, project_path: Path, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Generate React Native app"""
        files = {}
        
        # package.json
        files["package.json"] = self._template_rn_package_json(config)
        
        # App.tsx
        files["App.tsx"] = self._template_rn_app_tsx(blueprint)
        
        # Screens
        for page in blueprint.get("pages", []):
            screen_name = page.get("name", "Home")
            files[f"src/screens/{screen_name}Screen.tsx"] = self._template_rn_screen(screen_name, page)
        
        # Navigation
        files["src/navigation/Navigation.tsx"] = self._template_rn_navigation(blueprint)
        
        # Components
        files["src/components/Header.tsx"] = self._template_rn_component("Header")
        files["src/components/Button.tsx"] = self._template_rn_component("Button")
        files["src/components/Card.tsx"] = self._template_rn_component("Card")
        
        # Services
        files["src/services/api.ts"] = self._template_rn_api_service()
        files["src/services/storage.ts"] = self._template_rn_storage_service()
        
        # Android config
        files["android/app/build.gradle"] = self._template_android_gradle(config)
        files["android/app/src/main/AndroidManifest.xml"] = self._template_android_manifest(config)
        files["android/app/google-services.json"] = self._template_google_services(config)
        
        # iOS config
        files["ios/Podfile"] = self._template_ios_podfile(config)
        files["ios/{project_name}/Info.plist"] = self._template_ios_info_plist(config)
        
        # Build scripts
        files["build-apk.sh"] = self._template_build_apk_script(config)
        files["build-ios.sh"] = self._template_build_ios_script(config)
        
        return files
    
    def generate_flutter(self, config: MobileConfig, project_path: Path, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Generate Flutter app"""
        files = {}
        
        # pubspec.yaml
        files["pubspec.yaml"] = self._template_flutter_pubspec(config)
        
        # Main.dart
        files["lib/main.dart"] = self._template_flutter_main(blueprint)
        
        # Screens
        for page in blueprint.get("pages", []):
            screen_name = page.get("name", "Home")
            files[f"lib/screens/{screen_name.lower()}_screen.dart"] = self._template_flutter_screen(screen_name, page)
        
        # Widgets
        files["lib/widgets/header.dart"] = self._template_flutter_widget("Header")
        files["lib/widgets/button.dart"] = self._template_flutter_widget("Button")
        
        # Services
        files["lib/services/api_service.dart"] = self._template_flutter_api_service()
        files["lib/services/storage_service.dart"] = self._template_flutter_storage_service()
        
        # Android config
        files["android/app/build.gradle"] = self._template_android_gradle_flutter(config)
        files["android/app/src/main/AndroidManifest.xml"] = self._template_android_manifest(config)
        
        # iOS config
        files["ios/Podfile"] = self._template_ios_podfile_flutter(config)
        files["ios/Runner/Info.plist"] = self._template_ios_info_plist(config)
        
        # Build scripts
        files["build-apk.sh"] = self._template_build_apk_flutter_script(config)
        files["build-ios.sh"] = self._template_build_ios_flutter_script(config)
        
        return files
    
    def generate_capacitor(self, config: MobileConfig, project_path: Path, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Generate Capacitor app (web wrapped as mobile)"""
        files = {}
        
        # Capacitor config
        files["capacitor.config.json"] = self._template_capacitor_config(config)
        
        # Package.json with Capacitor
        files["package.json"] = self._template_capacitor_package_json(config)
        
        # React components (reuse from web)
        files["src/App.tsx"] = self._template_capacitor_app(blueprint)
        files["src/main.tsx"] = self._template_capacitor_main()
        
        # Android config
        files["android/app/build.gradle"] = self._template_capacitor_android_gradle(config)
        files["android/app/src/main/AndroidManifest.xml"] = self._template_capacitor_android_manifest(config)
        
        # iOS config
        files["ios/App/App/Info.plist"] = self._template_capacitor_ios_info(config)
        
        # Build scripts
        files["build-apk.sh"] = self._template_build_capacitor_apk_script(config)
        
        return files
    
    # ============== REACT NATIVE TEMPLATES ==============
    
    def _template_rn_package_json(self, config: MobileConfig) -> str:
        return json.dumps({
            "name": config.project_name.lower().replace(" ", "-"),
            "version": config.version,
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-native": "^0.72.0",
                "@react-navigation/native": "^6.1.0",
                "@react-navigation/bottom-tabs": "^6.5.0",
                "@react-navigation/stack": "^6.3.0",
                "react-native-screens": "^3.20.0",
                "react-native-safe-area-context": "^4.5.0",
                "axios": "^1.6.0",
                "@react-native-async-storage/async-storage": "^1.18.0",
                "zustand": "^4.4.0",
                "react-native-svg": "^13.9.0",
                "react-native-gesture-handler": "^2.12.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.0",
                "@types/react-native": "^0.72.0",
                "typescript": "^5.0.0",
                "@react-native-community/eslint-config": "^3.2.0"
            },
            "scripts": {
                "android": "react-native run-android",
                "ios": "react-native run-ios",
                "build-android": "cd android && ./gradlew assembleRelease && cd ..",
                "build-ios": "cd ios && xcodebuild -scheme {project_name} -configuration Release && cd .."
            }
        }, indent=2)
    
    def _template_rn_app_tsx(self, blueprint: Dict[str, Any]) -> str:
        return """import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { SafeAreaView } from 'react-native-safe-area-context';
import Navigation from './src/navigation/Navigation';
import * as SplashScreen from 'expo-splash-screen';

const Tab = createBottomTabNavigator();

export default function App() {
  useEffect(() => {
    SplashScreen.hideAsync();
  }, []);

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <NavigationContainer>
        <Navigation />
      </NavigationContainer>
    </SafeAreaView>
  );
}
"""
    
    def _template_rn_screen(self, name: str, page: Dict[str, Any]) -> str:
        return f"""import React from 'react';
import {{ View, Text, StyleSheet, ScrollView }} from 'react-native';

export default function {name}Screen() {{
  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>{page.get('name', name)}</Text>
      {page.get('description', '')}
    </ScrollView>
  );
}}

const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    backgroundColor: '#fff',
    padding: 16,
  }},
  title: {{
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  }},
}});
"""
    
    def _template_rn_navigation(self, blueprint: Dict[str, Any]) -> str:
        pages = blueprint.get("pages", [])
        screen_imports = "\n".join([f"import {page['name']}Screen from '../screens/{page['name']}Screen';" for page in pages])
        
        return f"""import React from 'react';
import {{ createBottomTabNavigator }} from '@react-navigation/bottom-tabs';
import {{ createStackNavigator }} from '@react-navigation/stack';
{screen_imports}

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

export default function Navigation() {{
  return (
    <Tab.Navigator>
      {chr(10).join([f'<Tab.Screen name="{page["name"]}" component={{{page["name"]}Screen}} />' for page in pages])}
    </Tab.Navigator>
  );
}}
"""
    
    def _template_rn_component(self, name: str) -> str:
        return f"""import React from 'react';
import {{ View, Text, StyleSheet }} from 'react-native';

export default function {name}() {{
  return (
    <View style={styles.container}>
      <Text style={styles.text}>{name}</Text>
    </View>
  );
}}

const styles = StyleSheet.create({{
  container: {{
    padding: 16,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
  }},
  text: {{
    fontSize: 16,
    fontWeight: '500',
  }},
}});
"""
    
    def _template_rn_api_service(self) -> str:
        return """import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  get: (url: string) => apiClient.get(url),
  post: (url: string, data: any) => apiClient.post(url, data),
  put: (url: string, data: any) => apiClient.put(url, data),
  delete: (url: string) => apiClient.delete(url),
};

export default apiService;
"""
    
    def _template_rn_storage_service(self) -> str:
        return """import AsyncStorage from '@react-native-async-storage/async-storage';

export const storageService = {
  getItem: async (key: string) => {
    try {
      return await AsyncStorage.getItem(key);
    } catch (error) {
      console.error('Storage error:', error);
    }
  },
  setItem: async (key: string, value: string) => {
    try {
      await AsyncStorage.setItem(key, value);
    } catch (error) {
      console.error('Storage error:', error);
    }
  },
  removeItem: async (key: string) => {
    try {
      await AsyncStorage.removeItem(key);
    } catch (error) {
      console.error('Storage error:', error);
    }
  },
};

export default storageService;
"""
    
    def _template_android_gradle(self, config: MobileConfig) -> str:
        return f"""apply plugin: 'com.android.application'
apply plugin: 'kotlin-android'

android {{
    compileSdkVersion 33
    namespace "{config.app_id}"
    
    defaultConfig {{
        applicationId "{config.app_id}"
        minSdkVersion 21
        targetSdkVersion 33
        versionCode 1
        versionName "{config.version}"
    }}
    
    buildTypes {{
        release {{
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
}}

dependencies {{
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.navigation:navigation-fragment:2.5.0'
    implementation 'androidx.navigation:navigation-ui:2.5.0'
}}
"""
    
    def _template_android_manifest(self, config: MobileConfig) -> str:
        return f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{config.app_id}">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.{config.project_name.replace(' ', '')}">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""
    
    def _template_google_services(self, config: MobileConfig) -> str:
        return json.dumps({
            "type": "service_account",
            "project_id": config.project_id,
            "private_key_id": "key123",
            "client_email": f"firebase-adminsdk@{config.project_id}.iam.gserviceaccount.com",
        }, indent=2)
    
    def _template_ios_podfile(self, config: MobileConfig) -> str:
        return f"""platform :ios, '12.4'

target '{config.project_name.replace(" ", "")}' do
  pod 'React', :path => '../node_modules/react-native'
  pod 'React-Core', :path => '../node_modules/react-native/React'
  pod 'React-DevSupport', :path => '../node_modules/react-native/React'
  pod 'React-RCTActionSheet', :path => '../node_modules/react-native/Libraries/ActionSheetIOS'
  pod 'React-RCTAnimation', :path => '../node_modules/react-native/Libraries/NativeAnimation'
  pod 'React-RCTBlob', :path => '../node_modules/react-native/Libraries/Blob'
  pod 'React-RCTImage', :path => '../node_modules/react-native/Libraries/Image'
  pod 'React-RCTLinking', :path => '../node_modules/react-native/Libraries/LinkingIOS'
  pod 'React-RCTNetwork', :path => '../node_modules/react-native/Libraries/Network'
  pod 'React-RCTPushNotification', :path => '../node_modules/react-native/Libraries/PushNotificationIOS'
  pod 'React-RCTSettings', :path => '../node_modules/react-native/Libraries/Settings'
  pod 'React-RCTText', :path => '../node_modules/react-native/Libraries/Text'
  pod 'React-RCTVibration', :path => '../node_modules/react-native/Libraries/Vibration'
  pod 'React-RCTWebSocket', :path => '../node_modules/react-native/Libraries/WebSocket'

  target '{config.project_name.replace(" ", "")}Tests' do
    inherit! :search_paths
  end
end
"""
    
    def _template_ios_info_plist(self, config: MobileConfig) -> str:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>{config.app_id}</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>{config.project_name}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>{config.version}</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
        <key>NSExceptionDomains</key>
        <dict/>
    </dict>
    <key>NSCameraUsageDescription</key>
    <string>This app needs camera access</string>
    <key>NSPhotoLibraryUsageDescription</key>
    <string>This app needs photo library access</string>
    <key>UILaunchStoryboardName</key>
    <string>LaunchScreen</string>
    <key>UIMainStoryboardFile</key>
    <string>Main</string>
    <key>UIRequiredDeviceCapabilities</key>
    <array>
        <string>armv7</string>
    </array>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
    </array>
</dict>
</plist>
"""
    
    def _template_build_apk_script(self, config: MobileConfig) -> str:
        return f"""#!/bin/bash
set -e

echo "🔨 Building Android APK for {config.project_name}..."

# Install dependencies
npm install

# Build APK
cd android
./gradlew assembleRelease
cd ..

# Output location
APK_PATH="android/app/build/outputs/apk/release/app-release.apk"

if [ -f "$APK_PATH" ]; then
    echo "✅ APK built successfully: $APK_PATH"
    echo "📦 Size: $(du -h $APK_PATH | cut -f1)"
else
    echo "❌ APK build failed"
    exit 1
fi
"""
    
    def _template_build_ios_script(self, config: MobileConfig) -> str:
        return f"""#!/bin/bash
set -e

echo "🔨 Building iOS app for {config.project_name}..."

# Install dependencies
npm install
cd ios
pod install
cd ..

# Build iOS app
cd ios
xcodebuild -scheme {config.project_name.replace(' ', '')} -configuration Release -derivedDataPath build
cd ..

echo "✅ iOS build completed"
echo "📱 Output: ios/build"
"""
    
    # ============== FLUTTER TEMPLATES ==============
    
    def _template_flutter_pubspec(self, config: MobileConfig) -> str:
        return f"""name: {config.project_name.lower().replace(' ', '_')}
description: {config.project_name} - Generated with GAAIUS

publish_to: 'none'

version: {config.version}+1

environment:
  sdk: ">=3.0.0 <4.0.0"

dependencies:
  flutter:
    sdk: flutter
  
  http: ^1.1.0
  provider: ^6.0.0
  shared_preferences: ^2.1.0
  get_it: ^7.5.0
  intl: ^0.18.0
  cupertino_icons: ^1.0.2
  flutter_svg: ^2.0.5
  google_fonts: ^5.1.0
  firebase_core: ^2.14.0
  firebase_auth: ^4.7.0
  cloud_firestore: ^4.9.0
  firebase_storage: ^11.2.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  
  flutter_lints: ^2.0.0

flutter:
  uses-material-design: true
  
  assets:
    - assets/images/
    - assets/icons/
  
  fonts:
    - family: Poppins
      fonts:
        - asset: assets/fonts/Poppins-Regular.ttf
        - asset: assets/fonts/Poppins-Bold.ttf
          weight: 700
"""
    
    def _template_flutter_main(self, blueprint: Dict[str, Any]) -> str:
        return """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'GAAIUS App',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
"""
    
    def _template_flutter_screen(self, name: str, page: Dict[str, Any]) -> str:
        return f"""import 'package:flutter/material.dart';

class {name}Screen extends StatefulWidget {{
  const {name}Screen({{Key? key}}) : super(key: key);

  @override
  State<{name}Screen> createState() => _{name}ScreenState();
}}

class _{name}ScreenState extends State<{name}Screen> {{
  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: const Text('{page.get("name", name)}'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const SizedBox(height: 20),
            Text(
              '{page.get("name", name)}',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
          ],
        ),
      ),
    );
  }}
}}
"""
    
    def _template_flutter_widget(self, name: str) -> str:
        return f"""import 'package:flutter/material.dart';

class {name} extends StatelessWidget {{
  final String? title;

  const {name}({{Key? key, this.title}}) : super(key: key);

  @override
  Widget build(BuildContext context) {{
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(8),
        color: Colors.grey[200],
      ),
      child: Text(
        title ?? '{name}',
        style: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }}
}}
"""
    
    def _template_flutter_api_service(self) -> str:
        return """import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl = 'http://localhost:3001/api';

  static Future<dynamic> get(String endpoint) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl$endpoint'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('API Error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to load data: $e');
    }
  }

  static Future<dynamic> post(String endpoint, Map<String, dynamic> data) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl$endpoint'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(data),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        throw Exception('API Error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to post data: $e');
    }
  }
}
"""
    
    def _template_flutter_storage_service(self) -> str:
        return """import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static Future<void> saveString(String key, String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(key, value);
  }

  static Future<String?> getString(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(key);
  }

  static Future<void> remove(String key) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(key);
  }

  static Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}
"""
    
    # ============== CAPACITOR TEMPLATES ==============
    
    def _template_capacitor_config(self, config: MobileConfig) -> str:
        return json.dumps({
            "appId": config.app_id,
            "appName": config.project_name,
            "webDir": "dist",
            "bundledWebRuntime": False,
            "plugins": {
                "SplashScreen": {
                    "launchShowDuration": 0
                }
            },
            "server": {
                "androidScheme": "https"
            }
        }, indent=2)
    
    def _template_capacitor_package_json(self, config: MobileConfig) -> str:
        return json.dumps({
            "name": config.project_name.lower().replace(" ", "-"),
            "version": config.version,
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview",
                "android": "cap sync android && cap open android",
                "ios": "cap sync ios && cap open ios",
                "build-android": "npm run build && cap sync android",
                "build-ios": "npm run build && cap sync ios"
            },
            "dependencies": {
                "@capacitor/core": "^5.0.0",
                "@capacitor/android": "^5.0.0",
                "@capacitor/ios": "^5.0.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            },
            "devDependencies": {
                "@capacitor/cli": "^5.0.0",
                "typescript": "^5.0.0",
                "vite": "^4.3.0"
            }
        }, indent=2)
    
    def _template_capacitor_app(self, blueprint: Dict[str, Any]) -> str:
        return """import { IonApp, setupIonicReact } from '@ionic/react';
import { StatusBar, Style } from '@capacitor/status-bar';
import { useEffect } from 'react';

setupIonicReact();

function App() {
  useEffect(() => {
    StatusBar.setStyle({ style: Style.Dark });
  }, []);

  return (
    <IonApp>
      <div className="ion-page">
        <ion-header>
          <ion-toolbar>
            <ion-title>GAAIUS Mobile App</ion-title>
          </ion-toolbar>
        </ion-header>
        <ion-content className="ion-padding">
          <h1>Welcome</h1>
          <p>Your mobile app is running!</p>
        </ion-content>
      </div>
    </IonApp>
  );
}

export default App;
"""
    
    def _template_capacitor_main(self) -> str:
        return """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import '@ionic/react/css/core.css'
import '@ionic/react/css/normalize.css'
import '@ionic/react/css/structure.css'
import '@ionic/react/css/typography.css'
import '@ionic/react/css/palettes/dark.system.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
    
    def _template_capacitor_android_gradle(self, config: MobileConfig) -> str:
        return f"""apply plugin: 'com.android.application'

android {{
    namespace "{config.app_id}"
    compileSdkVersion 33

    defaultConfig {{
        applicationId "{config.app_id}"
        minSdkVersion 21
        targetSdkVersion 33
        versionCode 1
        versionName "{config.version}"
    }}

    buildTypes {{
        release {{
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
}}

dependencies {{
    implementation 'com.getcapacitor:core:5.0.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'com.google.android.material:material:1.9.0'
}}
"""
    
    def _template_capacitor_android_manifest(self, config: MobileConfig) -> str:
        return f"""<?xml version='1.0' encoding='utf-8'?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{config.app_id}">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/AppTheme">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""
    
    def _template_capacitor_ios_info(self, config: MobileConfig) -> str:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>
    <string>{config.app_id}</string>
    <key>CFBundleName</key>
    <string>{config.project_name}</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>CFBundleShortVersionString</key>
    <string>{config.version}</string>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
    </dict>
</dict>
</plist>
"""
    
    def _template_build_capacitor_apk_script(self, config: MobileConfig) -> str:
        return f"""#!/bin/bash
set -e

echo "🔨 Building Capacitor APK for {config.project_name}..."

# Build web assets
npm run build

# Sync to Android
npx cap sync android

# Build APK
cd android/app
./gradlew assembleRelease
cd ../../

APK_PATH="android/app/build/outputs/apk/release/app-release.apk"

if [ -f "$APK_PATH" ]; then
    echo "✅ APK built successfully: $APK_PATH"
    echo "📦 Size: $(du -h $APK_PATH | cut -f1)"
else
    echo "❌ APK build failed"
    exit 1
fi
"""
    
    def _template_android_gradle_flutter(self, config: MobileConfig) -> str:
        return f"""def localProperties = new Properties()
def localPropertiesFile = rootProject.file('local.properties')
if (localPropertiesFile.exists()) {{
    localPropertiesFile.withReader('UTF-8') {{ reader ->
        localProperties.load(reader)
    }}
}}

def flutterRoot = localProperties.getProperty('flutter.sdk')
if (flutterRoot == null) {{
    throw new GradleException("Flutter SDK not found. Define location with flutter.sdk in the local.properties file.")
}}

def flutterVersionCode = localProperties.getProperty('flutter.versionCode')
if (flutterVersionCode == null) {{
    flutterVersionCode = '1'
}}

def flutterVersionName = localProperties.getProperty('flutter.versionName')
if (flutterVersionName == null) {{
    flutterVersionName = '{config.version}'
}}

apply plugin: 'com.android.application'
apply plugin: 'kotlin-android'
apply from: "$flutterRoot/packages/flutter_tools/gradle/flutter.gradle"

android {{
    compileSdkVersion 33
    ndkVersion flutter.ndkVersion
    namespace "{config.app_id}"

    defaultConfig {{
        applicationId "{config.app_id}"
        minSdkVersion 21
        targetSdkVersion 33
        versionCode flutterVersionCode.toInteger()
        versionName flutterVersionName
    }}

    buildTypes {{
        release {{
            signingConfig signingConfigs.release
        }}
    }}
}}

flutter {{
    source = '../..'
}}
"""
    
    def _template_ios_podfile_flutter(self, config: MobileConfig) -> str:
        return """post_install do |installer|
  installer.pods_project.targets.each do |target|
    flutter_additional_ios_build_settings(target)
  end
end
"""
    
    def _template_build_apk_flutter_script(self, config: MobileConfig) -> str:
        return f"""#!/bin/bash
set -e

echo "🔨 Building Flutter APK for {config.project_name}..."

# Build APK
flutter build apk --release

APK_PATH="build/app/outputs/flutter-apk/app-release.apk"

if [ -f "$APK_PATH" ]; then
    echo "✅ APK built successfully: $APK_PATH"
    echo "📦 Size: $(du -h $APK_PATH | cut -f1)"
else
    echo "❌ APK build failed"
    exit 1
fi
"""
    
    def _template_build_ios_flutter_script(self, config: MobileConfig) -> str:
        return f"""#!/bin/bash
set -e

echo "🔨 Building Flutter iOS app for {config.project_name}..."

# Build iOS app
flutter build ios --release

echo "✅ iOS build completed"
echo "📱 Output: build/ios/iphoneos"
"""
