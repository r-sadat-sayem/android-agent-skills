<!-- ANDROID_VERSION: 37 -->
# Scan Targets — Android 17 Migration

One entry per breaking change. Run all greps from the project root.

---

## P1 — compileSdk / targetSdk Not Set to 37

**Severity:** REQUIRED (migration is incomplete without this)
**Affects:** All apps — without targetSdk=37 the Android 17 behavior changes are NOT active
**Auto-fixable:** Conditional (see fix-patterns.md P1)

```bash
# Source of truth: the build.gradle / build.gradle.kts files
grep -rn "compileSdk\|targetSdk\|compileSdkVersion\|targetSdkVersion" \
  --include="*.gradle" --include="*.gradle.kts" . | grep -v "build/" | grep -v "^Binary"
```

Positive match: any `compileSdk` or `targetSdk` value **other than 37**.

If the build file contains a version catalog reference (e.g. `libs.versions.compileSdk`) rather
than a literal integer, trace through to find where that value is defined and report both locations.
The fix target is wherever the literal integer lives.

---

## C1 — CameraX Version < 1.5.2

**Severity:** CRITICAL  
**Affects:** All apps on Android 17 devices (regardless of targetSdk)  
**Auto-fixable:** Yes

```bash
grep -rn "camerax\|camera-camera2\|camera-core\|camera-lifecycle\|camera-video\|camera-extensions" \
  --include="*.gradle" --include="*.gradle.kts" --include="*.toml" .
```

Positive match: any CameraX dependency with version `< 1.5.2` (e.g., `1.4.x`, `1.3.x`, `1.2.x`).  
Also check `libs.versions.toml` for version catalog entries like `camerax = "1.4.0"`.

---

## H1 — Missing ACCESS_LOCAL_NETWORK Permission

**Severity:** HIGH  
**Affects:** Apps targeting API 37+ that access LAN (mDNS, SSDP, UPnP, casting, local HTTP, IoT)  
**Auto-fixable:** Yes (add permission; detection of LAN usage is advisory)

```bash
# Check if LAN-related code exists
grep -rn "NsdManager\|WifiManager\|mDNS\|SSDP\|UPnP\|MulticastSocket\|DatagramSocket\|ServerSocket\|InetAddress\|localhost\|192\.168\|10\.\|172\." \
  --include="*.kt" --include="*.java" .

# Check if permission already declared
grep -n "ACCESS_LOCAL_NETWORK" app/src/main/AndroidManifest.xml 2>/dev/null || \
  find . -name "AndroidManifest.xml" -exec grep -l "ACCESS_LOCAL_NETWORK" {} \;
```

Positive match: LAN-related code found AND `ACCESS_LOCAL_NETWORK` not in any `AndroidManifest.xml`.

---

## H2 — Background Audio Without mediaPlayback FGS

**Severity:** HIGH  
**Affects:** Apps targeting API 37+ using background audio  
**Auto-fixable:** No (requires architecture review)

```bash
# Find MediaPlayer / ExoPlayer / MediaSession usage
grep -rn "MediaPlayer\|ExoPlayer\|MediaController\|AudioManager\|requestAudioFocus\|MediaSession" \
  --include="*.kt" --include="*.java" .

# Find foreground services and their types
grep -n "foregroundServiceType" $(find . -name "AndroidManifest.xml") 2>/dev/null
```

Positive match: audio API usage found AND no `foregroundServiceType="mediaPlayback"` service declared.

---

## H3 — SMS OTP via Direct Broadcast

**Severity:** HIGH  
**Affects:** Apps targeting API 37+ reading SMS directly for OTP  
**Auto-fixable:** No (requires migration to Retriever API)

```bash
grep -rn "SMS_RECEIVED\|Telephony.Sms\|SmsManager\|SmsMessage\|provider/sms\|content://sms" \
  --include="*.kt" --include="*.java" .
```

Positive match: direct SMS read found AND no `SmsRetriever` or `SmsUserConsent` usage found.

```bash
# Check if already using Retriever API
grep -rn "SmsRetriever\|SEND_PERMISSION\|com.google.android.gms.auth.api.phone" \
  --include="*.kt" --include="*.java" .
```

---

## H4 — BAL Deprecated Constant

**Severity:** HIGH  
**Affects:** Apps targeting API 37+  
**Auto-fixable:** Yes

```bash
grep -rn "MODE_BACKGROUND_ACTIVITY_START_ALLOWED\|BACKGROUND_ACTIVITY_START_ALLOWED" \
  --include="*.kt" --include="*.java" .
```

Positive match: any usage of the deprecated constant.

---

## M1 — Static Final Field Modification via Reflection

**Severity:** MEDIUM  
**Affects:** Apps targeting API 37+ (throws `IllegalAccessException` or crashes via JNI)  
**Auto-fixable:** No (requires refactoring)

```bash
grep -rn "getDeclaredField\|getDeclaredFields" --include="*.kt" --include="*.java" . | \
  grep -v "^Binary"
```

Then for each hit, check if `setAccessible(true)` and `set(` appear in nearby lines. Also check:

```bash
grep -rn "SetStaticLongField\|SetStaticIntField\|SetStaticBooleanField\|SetStaticObjectField\|SetStaticFloatField\|SetStaticDoubleField" \
  --include="*.c" --include="*.cpp" --include="*.h" .
```

---

## M2 — MessageQueue Internal Reflection

**Severity:** MEDIUM  
**Affects:** Apps targeting API 37+  
**Auto-fixable:** No

```bash
grep -rn "MessageQueue\|mMessages\|mNextBarrierToken" --include="*.kt" --include="*.java" . | \
  grep -i "getDeclaredField\|getDeclaredMethod\|reflect\|getField\|getMethod"
```

Or a two-step check:
```bash
grep -rn "getDeclaredField\|getDeclaredMethod" --include="*.kt" --include="*.java" . | \
  grep -i "message\|queue\|looper"
```

---

## M3 — System.load() Without setReadOnly()

**Severity:** MEDIUM  
**Affects:** Apps targeting API 37+ doing dynamic native library loading  
**Auto-fixable:** Yes (add `setReadOnly()` before `System.load()`)

```bash
grep -rn "System\.load\b" --include="*.kt" --include="*.java" .
```

For each hit, check if `setReadOnly()` appears within ±5 lines. If not, flag it.

---

## M4 — BluetoothSocket RFCOMM Read Loop Without EOF Check

**Severity:** MEDIUM  
**Affects:** Apps targeting API 37+ using Bluetooth RFCOMM  
**Auto-fixable:** No

```bash
grep -rn "BluetoothSocket\|BluetoothServerSocket\|RFCOMM" --include="*.kt" --include="*.java" .
```

For each file with BluetoothSocket usage, check for `inputStream.read()` in a loop without `!= -1`:

```bash
grep -rn "\.read()" --include="*.kt" --include="*.java" . | grep -v "!= -1\|>= 0\|== -1"
```

---

## M5 — CP2 PII Column Queries from Data Table

**Severity:** MEDIUM  
**Affects:** Apps targeting API 37+ querying Contacts  
**Auto-fixable:** No (requires query refactor)

```bash
grep -rn "ContactsContract\.Data\|ContactsContract.Data" --include="*.kt" --include="*.java" . | \
  grep -v "^Binary"
grep -rn "ACCOUNT_NAME\|ACCOUNT_TYPE\|ACCOUNT_TYPE_AND_DATA_SET" --include="*.kt" --include="*.java" .
```

Positive match: both `ContactsContract.Data` URI AND `ACCOUNT_NAME`/`ACCOUNT_TYPE` column in same file.

---

## M6 — ContactsContract.Data Without READ_CONTACTS

**Severity:** MEDIUM  
**Affects:** Apps targeting API 37+  
**Auto-fixable:** No

```bash
# Check for Data queries
grep -rn "ContactsContract\.Data\b" --include="*.kt" --include="*.java" .

# Check if READ_CONTACTS is declared
grep -n "READ_CONTACTS" $(find . -name "AndroidManifest.xml") 2>/dev/null
```

Positive match: `ContactsContract.Data` query found AND `READ_CONTACTS` not in manifest.

---

## M7 — Certificate Transparency Disabled or Not Configured

**Severity:** MEDIUM  
**Affects:** Apps targeting API 37+ (CT now mandatory)  
**Auto-fixable:** Yes (add CT config warning / remove disabled entries)

```bash
find . -name "network_security_config.xml" -exec grep -n "certificateTransparency\|cleartextTrafficPermitted" {} \;
```

Positive match: `certificateTransparency enabled="false"` found. Flag to review and remove.

---

## M8 — Large Screen Orientation / Resizability Lock

**Severity:** MEDIUM (HIGH for non-game apps)  
**Affects:** Apps targeting API 37+ on large screens (sw >= 600dp)  
**Auto-fixable:** Yes (remove the offending attributes with a warning)

```bash
grep -n "screenOrientation\|resizeableActivity\|minAspectRatio\|maxAspectRatio\|setRequestedOrientation" \
  $(find . -name "AndroidManifest.xml") 2>/dev/null

grep -rn "setRequestedOrientation" --include="*.kt" --include="*.java" .
```

Positive match: any of these constraints found. Check Play Store category first — game apps are exempt.

---

## L1 — usesCleartextTraffic in Manifest

**Severity:** LOW  
**Affects:** All apps (will be deprecated)  
**Auto-fixable:** Yes (migrate to network_security_config.xml)

```bash
grep -n "usesCleartextTraffic" $(find . -name "AndroidManifest.xml") 2>/dev/null
```

---

## L2 — NPU Library Without Feature Declaration

**Severity:** LOW  
**Affects:** Apps targeting API 37+ using ML/NPU  
**Auto-fixable:** Yes (add `uses-feature` to manifest)

```bash
# Detect NPU/ML library usage
grep -rn "LiteRT\|TensorFlowLite\|tflite\|NeuralNetworks\|NNAPI\|NnApiDelegate\|NpuDelegate" \
  --include="*.kt" --include="*.java" --include="*.gradle" --include="*.gradle.kts" .

# Check if feature already declared
grep -n "android.hardware.npu\|neural_processing_unit" \
  $(find . -name "AndroidManifest.xml") 2>/dev/null
```

Positive match: ML/NPU code found AND `android.hardware.npu` feature not in manifest.

---

## L3 — CameraX Without Version Pin (advisory)

**Severity:** LOW  
**Affects:** All apps  
**Auto-fixable:** Yes (add BOM or pin version)

Check if CameraX is referenced without explicit version (using BOM). If no BOM and no explicit version
`>= 1.5.2`, flag as informational.
