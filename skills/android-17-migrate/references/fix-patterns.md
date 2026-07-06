# Fix Patterns — Android 17 Migration

One entry per auto-fixable issue. Apply using Edit tool (exact string replacement).
Issues marked MANUAL require developer action; include the guidance text verbatim.

---

## P1 — Bump compileSdk / targetSdk to 37

**Auto-fixable:** Conditional

1. Read the `build.gradle` / `build.gradle.kts` files to find where `compileSdk` and `targetSdk`
   are set.
2. If the values are **literal integers** in the build file → auto-fix them in place.
3. If they reference a **version catalog** or variable (e.g. `libs.versions.compileSdk`,
   `rootProject.ext.targetSdk`) → trace to the file that holds the literal, auto-fix there if
   unambiguous, otherwise print `[MANUAL]` with the exact file and line the developer must update.
4. **Do NOT touch `minSdk`** — that is the minimum supported Android version, unrelated to this
   migration.

---

## C1 — Update CameraX to 1.5.2+

**Auto-fixable:** Yes

**build.gradle (Groovy):**
```groovy
// BEFORE (example — version varies)
implementation "androidx.camera:camera-camera2:1.4.0"
implementation "androidx.camera:camera-core:1.4.0"
implementation "androidx.camera:camera-lifecycle:1.4.0"

// AFTER
implementation "androidx.camera:camera-camera2:1.5.2"
implementation "androidx.camera:camera-core:1.5.2"
implementation "androidx.camera:camera-lifecycle:1.5.2"
```

**build.gradle.kts (Kotlin DSL):**
```kotlin
// BEFORE
implementation("androidx.camera:camera-camera2:1.4.0")

// AFTER
implementation("androidx.camera:camera-camera2:1.5.2")
```

**libs.versions.toml:**
```toml
# BEFORE
camerax = "1.4.0"

# AFTER
camerax = "1.5.2"
```

**Edge cases:**
- If using a BOM, update the BOM version instead.
- Update ALL camera-* artifacts to the same version to avoid conflicts.
- If `1.6.0` is the latest stable, prefer that over `1.5.2`.

---

## H1 — Add ACCESS_LOCAL_NETWORK Permission

**Auto-fixable:** Yes — add before closing `</manifest>` tag or after other `<uses-permission>` entries.

```xml
<!-- ADD to AndroidManifest.xml -->
<uses-permission android:name="android.permission.ACCESS_LOCAL_NETWORK" />
```

Also add runtime permission request in the relevant Activity/Fragment:
```kotlin
// ADD — runtime request (the permission is in NEARBY_DEVICES group)
if (ActivityCompat.checkSelfPermission(this,
        "android.permission.ACCESS_LOCAL_NETWORK") != PackageManager.PERMISSION_GRANTED) {
    ActivityCompat.requestPermissions(this,
        arrayOf("android.permission.ACCESS_LOCAL_NETWORK"),
        REQUEST_LOCAL_NETWORK)
}
```

**Note:** Existing `NEARBY_DEVICES` permission holders won't be re-prompted. If `NEARBY_DEVICES` is
already declared, the user may already be covered — add the specific permission declaration anyway.

---

## H2 — Background Audio Foreground Service (MANUAL)

**Auto-fixable:** No

**Manual steps:**
1. Add `foregroundServiceType="mediaPlayback"` to your media service in `AndroidManifest.xml`:
   ```xml
   <service
       android:name=".YourMediaService"
       android:foregroundServiceType="mediaPlayback" />
   ```
2. Ensure `startForeground()` is called before any audio playback in background.
3. Declare the `FOREGROUND_SERVICE_MEDIA_PLAYBACK` permission:
   ```xml
   <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
   ```
4. If using `requestAudioFocus()` from background: wrap it in a foreground service call first.

---

## H3 — SMS OTP Migration (MANUAL)

**Auto-fixable:** No

**Manual steps:**
1. Add Google Play Services Auth dependency:
   ```kotlin
   implementation("com.google.android.gms:play-services-auth-api-phone:18.0.2")
   ```
2. Replace direct `SMS_RECEIVED_ACTION` broadcast receiver with SMS Retriever:
   ```kotlin
   // BEFORE
   // BroadcastReceiver listening for android.provider.Telephony.SMS_RECEIVED
   
   // AFTER — SMS Retriever API
   val client = SmsRetriever.getClient(context)
   val task = client.startSmsRetriever()
   task.addOnSuccessListener {
       // Retriever started; register a BroadcastReceiver for
       // com.google.android.gms.auth.api.phone.SMS_RETRIEVED
   }
   ```
3. Your SMS must include the app hash. Use `AppSignatureHelper` to get the hash during development.
4. Alternatively use SMS User Consent API for any-sender OTPs.

---

## H4 — Replace Deprecated BAL Constant

**Auto-fixable:** Yes

```kotlin
// BEFORE
options.pendingIntentBackgroundActivityStartMode =
    ActivityOptions.MODE_BACKGROUND_ACTIVITY_START_ALLOWED

// AFTER
options.pendingIntentBackgroundActivityStartMode =
    ActivityOptions.MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE
```

---

## M1 — Static Final Field Reflection (MANUAL)

**Auto-fixable:** No

**Manual steps:**
1. Find every `getDeclaredField` call where the target field is `static final`.
2. Replace the field with a non-final mutable alternative:
   ```kotlin
   // BEFORE (breaks on API 37)
   companion object {
       val SOME_CONSTANT: String = "original"
   }
   // ...accessed via reflection and mutated...
   
   // AFTER — option A: non-final
   companion object {
       var someValue: String = "original"
   }
   
   // AFTER — option B: AtomicReference for thread safety
   companion object {
       val someRef = AtomicReference("original")
   }
   ```
3. For JNI `SetStatic<Type>Field` calls: refactor the native code to use a callback or global
   mutable state instead of modifying Java static finals from C/C++.

---

## M2 — MessageQueue Reflection (MANUAL)

**Auto-fixable:** No

**Manual steps:**
1. Remove all reflective access to `android.os.MessageQueue` private fields/methods.
2. If using `TestLooperManager` in tests, use the new public APIs instead:
   ```kotlin
   // BEFORE (reflects on private fields)
   val field = MessageQueue::class.java.getDeclaredField("mMessages")
   
   // AFTER — use public TestLooperManager APIs
   val tlm = instrumentation.acquireLooperManager(looper)
   tlm.peekWhen { msg -> msg.what == MY_MESSAGE }
   tlm.poll(MY_MESSAGE_TIMEOUT_MS)
   ```
3. For production code inspecting `MessageQueue`: redesign to use `Handler.post()` patterns
   or `Looper.myLooper()` public API only.

---

## M3 — System.load() setReadOnly Fix

**Auto-fixable:** Yes — add `setReadOnly()` call immediately before `System.load()`.

```kotlin
// BEFORE
System.load(nativeLibFile.absolutePath)

// AFTER
nativeLibFile.setReadOnly()  // must be read-only before loading
System.load(nativeLibFile.absolutePath)
```

**Edge case:** If the file path is a `String` not a `File`, wrap it:
```kotlin
val libFile = File(nativeLibPath)
libFile.setReadOnly()
System.load(libFile.absolutePath)
```

---

## M4 — BluetoothSocket RFCOMM Read Loop (MANUAL)

**Auto-fixable:** No

**Manual steps:**
```kotlin
// BEFORE — infinite loop on disconnect in API 37+
val inputStream = socket.inputStream
while (true) {
    val byte = inputStream.read()
    process(byte)
}

// AFTER — handle -1 return from disconnected socket
val inputStream = socket.inputStream
var byte: Int
while (inputStream.read().also { byte = it } != -1) {
    process(byte)
}
// Reaching here means socket was closed or remote disconnected
handleDisconnect()
```

Also handle `read(buffer)` variants:
```kotlin
// BEFORE
while (true) {
    val n = inputStream.read(buffer)
    process(buffer, n)
}

// AFTER
var n: Int
while (inputStream.read(buffer).also { n = it } != -1) {
    process(buffer, n)
}
```

---

## M5 — CP2 PII Columns — Use RawContacts (MANUAL)

**Auto-fixable:** No

**Manual steps:**
```kotlin
// BEFORE — ACCOUNT_NAME/ACCOUNT_TYPE removed from Data view in API 37+
val cursor = contentResolver.query(
    ContactsContract.Data.CONTENT_URI,
    arrayOf(ContactsContract.SyncColumns.ACCOUNT_NAME,
            ContactsContract.SyncColumns.ACCOUNT_TYPE),
    null, null, null
)

// AFTER — query RawContacts table instead
val cursor = contentResolver.query(
    ContactsContract.RawContacts.CONTENT_URI,
    arrayOf(
        ContactsContract.RawContacts._ID,
        ContactsContract.SyncColumns.ACCOUNT_NAME,
        ContactsContract.SyncColumns.ACCOUNT_TYPE
    ),
    null, null, null
)
// Then join with Data via RAW_CONTACT_ID column as needed
```

---

## M6 — Add READ_CONTACTS Permission (MANUAL)

**Auto-fixable:** No (adding the permission may change your privacy story — dev must decide)

**Manual steps:**
1. Add to `AndroidManifest.xml`:
   ```xml
   <uses-permission android:name="android.permission.READ_CONTACTS" />
   ```
2. Add runtime permission request in the relevant screen.
3. Alternative: migrate to the system Contact Picker (`ACTION_PICK_CONTACTS`) — no permission needed:
   ```kotlin
   val intent = Intent(ContactsContract.Intents.ACTION_PICK_CONTACTS)
   startActivityForResult(intent, REQUEST_PICK_CONTACT)
   ```

---

## M7 — Remove CT Disabled Config

**Auto-fixable:** Yes — remove the `certificateTransparency enabled="false"` line.

```xml
<!-- BEFORE — disabling CT is ignored in API 37 -->
<domain-config>
    <domain includeSubdomains="true">example.com</domain>
    <certificateTransparency enabled="false" />
</domain-config>

<!-- AFTER — CT is always on; remove the opt-out -->
<domain-config>
    <domain includeSubdomains="true">example.com</domain>
    <!-- certificateTransparency removed — ensure your cert is CT-logged -->
</domain-config>
```

**Note:** Ensure the server certificate is logged in a public CT log. Contact your CA if unsure.

---

## M8 — Remove Large Screen Orientation Locks

**Auto-fixable:** Yes — remove the offending attributes with a comment.

```xml
<!-- BEFORE — ignored on large screens (sw >= 600dp) in API 37 -->
<activity
    android:name=".MainActivity"
    android:screenOrientation="portrait"
    android:resizeableActivity="false" />

<!-- AFTER -->
<activity
    android:name=".MainActivity"
    android:configChanges="keyboard|keyboardHidden|navigation"
    android:recreateOnConfigChanges="keyboard|keyboardHidden|navigation" />
<!-- Note: Test on tablet/foldable. Use WindowSizeClass for adaptive layouts. -->
```

For `setRequestedOrientation()` calls in code — flag as MANUAL since removing them requires testing.

---

## L1 — Migrate usesCleartextTraffic

**Auto-fixable:** Yes — move config to network_security_config.xml and remove from manifest.

**Step 1:** In `AndroidManifest.xml`, replace `android:usesCleartextTraffic="true"` with NSC reference:
```xml
<!-- BEFORE -->
<application android:usesCleartextTraffic="true">

<!-- AFTER -->
<application android:networkSecurityConfig="@xml/network_security_config">
```

**Step 2:** Create (or update) `res/xml/network_security_config.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="false" />
    <!-- Add domain-specific overrides only if truly needed: -->
    <!-- <domain-config cleartextTrafficPermitted="true">
           <domain includeSubdomains="true">legacy.internal.example.com</domain>
         </domain-config> -->
</network-security-config>
```

---

## L2 — Declare NPU Feature Flag

**Auto-fixable:** Yes — add `uses-feature` to manifest.

```xml
<!-- ADD to AndroidManifest.xml inside <manifest> -->
<uses-feature
    android:name="android.hardware.npu"
    android:required="false" />
<!-- required="false" ensures the app isn't filtered out on non-NPU devices -->
```
